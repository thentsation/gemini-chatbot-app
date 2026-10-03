🇧🇷 Português | [🇺🇸 English](README.md)

# Gemini Chatbot App

Um chatbot em Streamlit para os modelos Gemini do Google, com memória de conversa de verdade, seletor de modelo, feedback por mensagem e um fluxo "traga sua própria chave" para que qualquer pessoa possa testar sem que você pague pelo uso alheio.

> Artigo completo (a jornada de protótipo a produto) em [Português](ARTIGO.md) / [English](ARTIGO.en-us.md).

## Funcionalidades

- **Memória de conversa real** — construído sobre a `Chat` session do `google-genai`, então o modelo realmente lembra das mensagens anteriores em vez de responder cada uma isoladamente.
- **Seletor de modelo** — alterne entre `gemini-3.8-flash`, `gemini-2.5-flash`, `gemini-2.5-pro` e `gemini-3.1-pro-preview` na barra lateral; a troca reinicia a sessão de forma limpa.
- **BYOK por padrão** — cada visitante cola a própria chave do Google na barra lateral (nunca é salva em disco nem registrada em log); defina `GOOGLE_API_KEY` como secret no servidor para pular esse passo.
- **Feedback persistido por mensagem** — avalie qualquer resposta do assistente ("Útil" / "Parcialmente útil" / "Não relevante"); as avaliações sobrevivem a reruns e reaparecem quando o histórico é re-renderizado.
- **Tratamento de erros amigável** — chave inválida, cota excedida e modelo indisponível viram uma mensagem clara em vez de um stack trace.

## Pré-requisitos

- Python 3.11+
- Uma chave de API do Google ([gere a sua aqui](https://aistudio.google.com/apikey))

## Instalação

```bash
git clone https://github.com/ntsation/gemini-chatbot-app.git
cd gemini-chatbot-app
make install
```

## Uso

```bash
make run
```

Acesse `http://localhost:8501`, cole sua chave de API na barra lateral, escolha um modelo e comece a conversar.

### Docker

```bash
make docker-build
make docker-run
```

A imagem é multi-stage (runtime não-root) e tem `HEALTHCHECK` contra o próprio endpoint `/_stcore/health` do Streamlit. O `docker-compose.yml` é o compose de produção usado pelo Jenkins (labels do Traefik, sem portas publicadas, `GOOGLE_API_KEY` vinda de `/opt/apps/gemini-chatbot-app/.env` no servidor).

## Configuração

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `GOOGLE_API_KEY` | Não | Se definida, o app usa essa chave para todo mundo e pula o campo na sidebar (modo "chave do servidor"). Deixe vazia para BYOK. |

## Desenvolvimento

```bash
make lint        # ruff check
make format      # ruff format
make typecheck    # mypy (estrito)
make test         # pytest
make coverage     # pytest com relatório de cobertura
```

Os testes incluem unitários por módulo e um teste de ponta a ponta usando o utilitário oficial `AppTest` do Streamlit, que simula o app inteiro (sidebar, chat input, feedback, limpar conversa) com o SDK `google-genai` mockado — sem precisar de chave real nem de chamada de rede.

## Estrutura do repositório

```
├── src/                   # código do app (components/services/utils + entrypoint)
├── tests/                 # testes unitários + smoke test do app inteiro via AppTest
├── config/                # requirements pinados + lockfile
└── docker/                # Dockerfile
```

## CI/CD

CI e deploy rodam no Jenkins da plataforma (`Jenkinsfile` → `appPipeline` da Shared Library `platform`, repo devops-platform), disparados por webhooks. Sem GitHub Actions.

- **PRs e branches** — validação do contrato; `docker build --target test` (`ruff check`, `ruff format --check`, `mypy`, `pytest` com cobertura ≥90% em Python 3.11 e 3.12, app Streamlit exercitado de ponta a ponta pelo `AppTest`, versões das ferramentas no `config/requirements-dev.txt`); `pip-audit` no `config/requirements.lock`; Trivy (CRITICAL/HIGH) na imagem de runtime.
- **main** — tudo acima e depois build, smoke test, push para o OCIR, deploy atrás do Traefik em https://gemini-chatbot.137-131-175-7.sslip.io com rollback automático, release com o python-semantic-release (versão, CHANGELOG, tag e release no GitHub) e rebuild do portfolio. Também é reconstruída toda segunda para pegar patches de segurança.
- **Dependências** — Renovate (job `platform/renovate` no Jenkins, `renovate.json` → preset do devops-platform): atualizações diárias, manutenção semanal do lockfile, issue "Dependency Dashboard" e auto-merge de patch/minor depois que o Jenkins aprova.

