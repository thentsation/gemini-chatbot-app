🇧🇷 Português | [🇺🇸 English](ARTIGO.en-us.md)

# Um chatbot de fim de semana que eu não larguei mais

Comecei isso num sábado só pra ver se dava pra colar uma UI no Gemini em uma tarde. Deu. O problema é que só percebi, dias depois, que o chat "esquecia" tudo e rodava em cima de uma biblioteca que a própria Google já tinha abandonado.

## Por que Streamlit e não outra coisa

Eu queria a distância mais curta possível entre "tenho uma API key do Gemini" e "tenho uma tela onde conversar com ela". Streamlit resolve isso em sete arquivos: uma sidebar pra colar a chave, um componente de chat, uma chamada pra `google-generativeai`. Rodei, funcionou, fechei o notebook satisfeito. Só fui usar o app de verdade — mandando mais de uma mensagem seguida — alguns dias depois.

## Os dois bugs que só aparecem quando você usa o próprio app

Nenhum dos dois derrubava o processo. Nenhum aparecia nos logs. Só apareciam se eu, como usuário, tentasse ter uma conversa de verdade.

**O histórico sumia visualmente.** `st.session_state.messages` recebia cada mensagem nova certinho, mas nada no topo do app percorria essa lista pra redesenhar as anteriores. Como o Streamlit reexecuta o script inteiro a cada interação, só a última troca ficava na tela — um chat que esquecia tudo antes da penúltima linha, mesmo com o dado intacto por trás.

**O chat não tinha memória nenhuma.** Isso era mais grave: cada pergunta virava uma chamada isolada a `model.generate_content(prompt)`. Visualmente parecia uma conversa; para o modelo, cada resposta nascia do zero, sem nenhuma pergunta anterior no contexto.

A correção do primeiro bug é do tipo fácil de esquecer: no topo de `chat_interface`, percorrer `st.session_state.messages` e redesenhar cada uma com `st.chat_message` antes de processar entrada nova, e fechar com um `st.rerun()` explícito depois de qualquer resposta — a mensagem recém-gerada some do render "ao vivo" e reaparece, com o widget de feedback junto, vinda do loop de histórico. Um caminho de renderização só, sem lógica duplicada.

Para a memória, resisti à tentação de montar manualmente uma lista de turnos e reenviar tudo a cada chamada — o SDK já resolve isso. `client.chats.create(model=...)` devolve um objeto `Chat` que guarda o histórico internamente; bastou guardar essa sessão em `st.session_state` e trocar `generate_content` por `chat.send_message()`. A sessão só é recriada quando a chave ou o modelo mudam, então trocar de modelo no meio da conversa reseta de forma limpa em vez de misturar contexto de modelos diferentes.

## Descobri no meio do caminho que a SDK estava morta

Pesquisando como funcionava a API de chat multi-turn, esbarrei no aviso no PyPI: `google-generativeai` está marcado `Development Status :: 7 - Inactive`, com o próprio README recomendando migrar para `google-genai`. Não estava nos meus planos trocar de SDK no meio da produtização, mas o guia oficial de migração mostra que é quase mecânico:

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

De brinde, os modelos disponíveis também tinham mudado — a geração 3.x (`gemini-3.8-flash`, `gemini-3.1-pro-preview`) já convive com a 2.5, então deixei o seletor da sidebar oferecer as duas.

## Dando cara de produto ao que era um script

Com os dois bugs resolvidos, o resto foi fechar as lacunas que separam "funciona pra mim" de algo que eu mandaria pra outra pessoa usar:

- **Seletor de modelo** — `st.selectbox` na sidebar, do mais rápido ao de maior qualidade, recriando a sessão de chat automaticamente ao trocar.
- **BYOK que avisa na hora, não só na primeira mensagem.** A chave continua sendo colada pelo visitante (nada fica salvo no servidor), mas agora uma chamada leve a `client.models.list()` valida assim que ela é configurada. Se `GOOGLE_API_KEY` já estiver no ambiente, a sidebar nem pede — mostra um aviso de "chave do servidor".
- **Erros que dizem algo útil.** `APIError` do SDK vira mensagem específica por código HTTP — chave inválida, modelo indisponível, cota excedida — em vez de um `RuntimeError` genérico que eu mesmo teria que debugar depois.
- **Feedback que sobrevive ao próximo turno.** Os widgets de feedback originais nem tinham `key` — com mais de uma mensagem na tela, colidiam entre si. Agora cada mensagem guarda sua avaliação em `st.session_state.feedback_log`, com timestamp, e reaparece como legenda ao rolar o histórico.
- **Título e ícone na aba.** `st.set_page_config` simplesmente nunca tinha sido chamado.

## Testando Streamlit sem inventar moda

Testar UI costuma ser onde eu relaxo em projeto pessoal — e é exatamente onde os dois bugs originais estavam escondidos. Em vez de mockar tudo manualmente, usei `streamlit.testing.v1.AppTest`, que roda o app inteiro sem subir servidor e permite interagir com os widgets como um usuário faria. Com o SDK trocado por um fake na fixture do pytest, dá pra simular a jornada completa: configurar a chave, mandar duas mensagens seguidas e confirmar que a primeira continua na tela (o teste que teria pego o bug do histórico de cara), dar feedback numa resposta e confirmar que ele sobrevive a um novo turno, verificar que um erro de API não corrompe nada.

Por baixo disso, testes unitários isolados cobrem `config.py` (fallback de variável de ambiente), `services/response.py` e `services/google_api.py` (mapeamento de erros e cache de sessão) e `utils/state_manager.py`.

## O que fica desse projeto

Bug de produto nem sempre é bug de código — os dois problemas mais sérios aqui nunca lançaram uma exceção; só ficavam óbvios usando o chat como alguém usaria de verdade, mensagem após mensagem. E verificar a saúde de uma dependência virou hábito depois disso: nenhuma documentação antiga ia me avisar que a biblioteca tinha virado "Inactive" — só descobri consultando o PyPI enquanto pesquisava outra coisa. `AppTest` também me convenceu de que testar Streamlit não precisa de Selenium nem de fingir que é E2E — roda em milissegundos e pega exatamente esse tipo de bug de rerun que teste unitário isolado não vê.

## Como o repositório está hoje

28 testes, 100% de cobertura em `src/`, com threshold de 90% bloqueando no CI. `ruff` (lint + format) e `mypy` (`disallow_untyped_defs`) limpos a cada push, rodando em matrix de Python. O pipeline faz um smoke test real do Streamlit (`/_stcore/health`), escaneia a imagem Docker com Trivy antes de publicar no GHCR, versiona sozinho via `python-semantic-release` (toda mudança na `main` vira tag e entrada no `CHANGELOG.md`), e termina com deploy automatizado: build → GHCR → espelhamento para OCIR → SSH na instância → smoke test HTTP.
