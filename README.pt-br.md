🇧🇷 Português | [🇺🇸 English](README.md)

# Gemini Chatbot App

[![Python CI](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/pipeline_python.yaml/badge.svg)](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/pipeline_python.yaml)
[![Docker CI/CD](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/pipeline_docker.yaml/badge.svg)](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/pipeline_docker.yaml)
[![Release](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/release.yaml/badge.svg)](https://github.com/ntsation/gemini-chatbot-app/actions/workflows/release.yaml)

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

Ou via Compose: `docker compose up --build`. A imagem é multi-stage (runtime não-root), tem `HEALTHCHECK` contra o próprio endpoint `/_stcore/health` do Streamlit, e é escaneada com **Trivy** e publicada no **GHCR** a cada push em `main`.

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
├── docker/                # Dockerfile
└── .github/workflows/     # CI, build+scan+publish do Docker, release, deploy
```

## CI/CD

- **CI**: ruff (lint + format), mypy (estrito), pytest em matrix (3.11/3.12) com threshold de cobertura, smoke test real do Streamlit, e `pip-audit` contra o lockfile.
- **Release**: `python-semantic-release` cria uma nova tag e atualiza o `CHANGELOG.md` automaticamente a cada push em `main`.
- **Docker**: build multi-arch, scan com Trivy, publicação no GHCR com tags `latest`/semver/sha.
- **Deploy**: após um build Docker bem-sucedido em `main`, a imagem é implantada automaticamente em um container de longa duração.
