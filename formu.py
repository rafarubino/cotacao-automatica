import streamlit as st
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Definindo os escopos e ID da planilha
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1SbBkuxGIvnww__aw74fiLu1dx9XXJuLGq9KOBYIq-o0"  # Apenas a parte ID
RANGE_NAME = "fornecedores!A:D"  # Altere o nome da aba se necessário

# Função para inicializar as credenciais do Google
def init_google_sheets():
    # Carregar as credenciais diretamente do Streamlit Secrets
    creds_json = st.secrets["google_creds"]  # Acessando a seção 'google_creds' no secrets.toml
    
    if not creds_json:
        raise ValueError("A variável de segredo 'google_creds' não foi encontrada ou está vazia.")
    
    try:
        # Converte a string JSON para um dicionário
        creds_dict = json.loads(creds_json)
        
        # Cria as credenciais usando o dicionário
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except Exception as e:
        raise ValueError(f"Erro ao criar credenciais do Google: {e}")
    
    return creds

# Função para salvar os dados na planilha do Google Sheets
def salvar_dados(produto, valor):
    creds = init_google_sheets()  # Inicializando as credenciais
    try:
        service = build("sheets", "v4", credentials=creds)

        # Identificar a data e hora atuais
        data_atual = datetime.now().strftime("%Y-%m-%d")
        hora_atual = datetime.now().strftime("%H:%M:%S")

        # Preparar os dados para envio
        valores = [[data_atual, hora_atual, produto, valor]]
        body = {
            "values": valores
        }

        # Adiciona os dados à planilha
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption="RAW",
            body=body
        ).execute()
        st.write("Dados salvos na planilha com sucesso!")
    except HttpError as err:
        st.write("Erro ao salvar na planilha:", err)

# Código do Streamlit
st.title("Formulário de Cotação")
st.write("Este formulário tem o intuito de automatizar o processo de cotação")

# Selecionar o produto
st.header("Produto")
produto = st.selectbox('Selecione o produto', ['NENHUM', 'mussarela', 'presunto', 'mortadela'])
if produto:
    st.write('Opção selecionada: ', produto)

# Definir o preço
st.header("Preço")
valor = st.slider(f"Quanto custa o kg de {produto}: ", 0.0, 100.0)
if valor:
    st.write("Valor selecionado: ", valor, " reais")

# Botão para enviar resposta
if st.button("Clique para enviar a resposta"):
    salvar_dados(produto, valor)
    st.write("Enviado!")
