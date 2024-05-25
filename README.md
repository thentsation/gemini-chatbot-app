# Chat GPT Pessoal

## Visão Geral
Essa é uma aplicação de chatbot interativa desenvolvida com Streamlit, permitindo aos usuários se comunicar com diferentes modelos de linguagem, como o OpenAI GPT e o Llama2, para obter respostas úteis. 

O sistema é configurável e apresenta uma interface amigável, proporcionando uma experiência personalizada.

## Funcionalidades
 - **Interface Intuitiva**: Interface de usuário baseada em Streamlit.

- **Escolha de Modelos de Linguagem**: Suporte para GPT-3.5, GPT-4 e Llama2.
- **Gerenciamento de Mensagens**: Histórico de conversas armazenado e exibido na interface.

- **Cálculo de Custos**: Monitoramento e exibição do custo das interações com o modelo GPT da OpenAI.

- **Limpeza de Conversas**: Opção para limpar o histórico de mensagens.

## Requisitos
- Python 3.7+
- Bibliotecas: 
    - streamlit 
    - dotenv
    - langchain
# Instalação
1. Clone o repositório:
    ````
    git clone https://github.com/ntsation/chat_llama.git
    cd chat_llama
    ````

2. Crie um ambiente virtual:
    ```python -m venv env
    source env/bin/activate  # No Windows use `env\Scripts\activate
    ```
3. Instale as dependências:
    ```
    pip install -r requirements.txt
    ```
4. Configure as variáveis de ambiente:

    **Crie um arquivo .env na raiz do projeto e adicione suas chaves de API e outras configurações necessárias.**

## Uso
Execute a aplicação Streamlit:
```
streamlit run app.py
```
Abra o navegador e acesse: http://localhost

##  Estrutura do Código
- init_page: Configura a página principal da aplicação.
- init_messages: Inicializa e gerencia as mensagens da sessão do usuário.
- select_llm: Permite ao usuário escolher e configurar o modelo de linguagem.
- get_answer: Processa as mensagens e retorna a resposta gerada pelo modelo.
- find_role: Identifica o tipo de uma mensagem.
- convert_langchainschema_to_dict: Converte uma lista de mensagens para uma lista de dicionários.
- llama_v2_prompt: Converte uma lista de dicionários em um formato compatível com o modelo Llama2.
- main: Função principal que configura e executa a aplicação.


## Modelo 
Baixar modelo Llama2 para o ambiente local:
```
wget https://huggingface.co/localmodels/Llama-2-7B-Chat-ggml/resolve/main/llama-2-7b-chat.ggmlv3.q2_K.bin
```
