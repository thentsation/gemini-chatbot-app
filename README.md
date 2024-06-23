# Chatbot com Gemini (Google)

Este é um aplicativo de chatbot baseado em texto que utiliza o modelo de linguagem da API Google Generative AI (genai) para gerar respostas a partir das entradas do usuário.

## Como usar

1. Instalação:
   - Certifique-se de ter o Python instalado em sua máquina.
   - Instale as dependências do projeto executando `pip install -r requirements.txt`.

2. Configuração da chave da API do Google:
   - Antes de executar o aplicativo, você precisa obter uma chave da API do Google.
   - Link do Gemini API <https://ai.google.dev/>
   - Insira sua chave da API do Google quando solicitado ao executar o aplicativo.

3. Execução do aplicativo:
   - Execute o aplicativo com o comando `streamlit run app.py`.
   - O aplicativo será aberto em seu navegador.

4. Interagindo com o chatbot:
   - Na interface do aplicativo, digite uma mensagem na caixa de texto.
   - Clique no botão "Enviar" para enviar sua mensagem.
   - O chatbot responderá com uma mensagem gerada pelo modelo de linguagem da Google Generative AI.

## Dependências

- streamlit
- google.generativeai
- textwrap
- IPython

Certifique-se de ter essas dependências instaladas antes de executar o aplicativo.
