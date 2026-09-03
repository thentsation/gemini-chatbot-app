🇧🇷 Português | [🇺🇸 English](ARTIGO.en-us.md)

# De protótipo a produto: produtizando um chatbot Streamlit para o Gemini

Como um chatbot de fim de semana — sem testes, sem memória de conversa e rodando numa SDK já deprecada — virou um app com CI/CD completo, deploy automatizado e uma correção que muda o produto de verdade: ele agora lembra da conversa.

## O ponto de partida

O projeto era sete arquivos Streamlit: uma sidebar para colar a API key, um componente de chat, e a chamada para `google-generativeai`. Funcionava para uma demo rápida, mas escondia dois bugs de produto que só aparecem quando alguém realmente usa o app:

1. **O histórico desaparecia.** `st.session_state.messages` era populado a cada mensagem, mas nada no topo do app percorria essa lista para re-desenhá-la. A cada rerun do Streamlit — que acontece a cada interação — só a última troca ficava visível na tela. Um chat que "esquecia" visualmente tudo antes da última mensagem.
2. **O chat não tinha memória nenhuma.** Cada pergunta virava uma chamada isolada a `model.generate_content(prompt)`. O modelo nunca via as mensagens anteriores — a UI parecia uma conversa contínua, mas por trás cada resposta partia do zero.

Além disso: zero testes, zero CI, `requirements.txt` sem versão fixa (com `IPython` listado e nunca usado em lugar nenhum), e — a descoberta mais relevante do processo — a biblioteca usada, `google-generativeai`, está oficialmente marcada como `Development Status :: 7 - Inactive` no PyPI. O próprio README dela recomenda migrar para o `google-genai`.

Este artigo é o caminho de lá até um app com cara de produto.

## Primeira parada: consertar o que já existia

Antes de qualquer feature nova, os dois bugs.

### Histórico de verdade

A correção é simples de descrever e fácil de esquecer: no topo de `chat_interface`, percorrer `st.session_state.messages` e redesenhar cada mensagem com `st.chat_message` antes de processar uma nova entrada. Depois de qualquer resposta nova, um `st.rerun()` explícito normaliza o estado — a mensagem que acabou de ser gerada some da renderização "ao vivo" e reaparece, junto com o widget de feedback, vinda do loop de histórico. Um único caminho de renderização, sem duplicação de lógica.

### Memória via SDK, não reinventada

A tentação seria montar manualmente uma lista de turnos e reenviá-la a cada chamada. Mas o próprio SDK já resolve isso: `client.chats.create(model=...)` devolve um objeto `Chat` que mantém o histórico internamente — bastava guardar essa sessão em `st.session_state` e trocar `generate_content` por `chat.send_message()`. A sessão é recriada só quando a chave ou o modelo mudam, então trocar de modelo no meio da conversa reinicia de forma limpa em vez de misturar contextos.

### A migração de SDK que não estava no plano original

Ao pesquisar a API de chat multi-turn, o PyPI do `google-generativeai` mostrou o aviso de descontinuação. Trocar de SDK no meio de uma produtização não seria imediato se a API fosse muito diferente — mas o guia oficial de migração mostra que a troca é quase mecânica:

```python
# antes (google-generativeai, deprecado)
genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat()
chat.send_message(prompt)

# depois (google-genai)
client = genai.Client(api_key=key)
chat = client.chats.create(model='gemini-3.8-flash')
chat.send_message(prompt)
```

Junto da troca, os modelos disponíveis também mudaram — a geração 3.x (`gemini-3.8-flash`, `gemini-3.1-pro-preview`) já convive com a 2.5, então o seletor de modelo na sidebar oferece as duas gerações.

## As features: dar cara de produto ao app

Com a base corrigida, o resto foi fechar lacunas que separam um protótipo de algo publicável.

- **Seletor de modelo.** Um `st.selectbox` na sidebar com quatro opções, do mais rápido ao de maior qualidade — trocar de modelo recria a sessão de chat automaticamente.
- **BYOK com feedback imediato.** A chave continua sendo colada pelo visitante (nada fica salvo no servidor), mas agora é validada assim que configurada — uma chamada leve a `client.models.list()` — em vez de só falhar silenciosamente na primeira mensagem. Se `GOOGLE_API_KEY` estiver definida no ambiente, a sidebar pula o campo e mostra um aviso de "chave do servidor".
- **Erros que fazem sentido.** `APIError` do SDK é traduzido para mensagens específicas por código HTTP — chave inválida, modelo indisponível, cota excedida — em vez de um `RuntimeError` genérico.
- **Feedback que persiste.** O sistema de feedback original nem tinha `key` nos widgets — ao renderizar mais de uma mensagem, os widgets colidiriam. Agora cada mensagem tem sua própria avaliação, guardada em `st.session_state.feedback_log` com timestamp, e reaparece como legenda ao rolar o histórico.
- **Título e ícone na aba.** Um detalhe pequeno que faltava por completo: `st.set_page_config` nunca era chamado.

## Testando um app Streamlit de verdade

Testar UI costuma ser o ponto fraco de protótipos assim. A saída não foi mockar tudo manualmente — o próprio Streamlit expõe `streamlit.testing.v1.AppTest`, que executa o app inteiro (sem subir servidor) e permite interagir com os widgets como um usuário faria. Com o SDK do Gemini trocado por um fake na fixture do pytest, dá para simular a jornada completa: configurar a chave, mandar duas mensagens seguidas e confirmar que a primeira continua na tela (o teste que teria pego o bug 1 direto), dar feedback numa resposta e confirmar que sobrevive a um novo turno, e verificar que um erro de API não corrompe o histórico.

Complementando, testes unitários isolados cobrem `config.py` (fallback de variável de ambiente), `services/response.py` e `services/google_api.py` (mapeamento de erros e cache de sessão) e `utils/state_manager.py`.

## Lições

1. **Bug de produto nem sempre é bug de código.** As duas falhas mais importantes aqui não geravam exceção nenhuma — o app "funcionava". Só ficavam óbvias usando o chat como um usuário usaria, mensagem após mensagem.
2. **Verificar a saúde da dependência é parte do trabalho.** Nenhuma documentação antiga avisaria que `google-generativeai` virou "Inactive" — só apareceu ao consultar o próprio PyPI durante a migração de API de chat.
3. **Testar Streamlit não precisa de Selenium.** `AppTest` roda em milissegundos e testa comportamento real de rerun — exatamente a categoria de bug que testes unitários isolados não pegam.
4. **BYOK bem feito é UX, não só segurança.** Validar a chave no momento em que ela é configurada, e não só na primeira mensagem, evita que o visitante escreva um parágrafo só para descobrir que colou a chave errada.

## Estado final

- 28 testes, 100% de cobertura em `src/`, threshold de 90% bloqueando no CI
- ruff (lint + format) e mypy (`disallow_untyped_defs`) limpos, rodando a cada push
- CI em matrix de Python, smoke test real do Streamlit (`/_stcore/health`), imagem Docker escaneada com Trivy e publicada no GHCR
- Versionamento automático via `python-semantic-release` — toda mudança em `main` vira uma tag e uma entrada no `CHANGELOG.md`
- Deploy automatizado: build → GHCR → espelhamento para OCIR → SSH na instância → smoke test HTTP
