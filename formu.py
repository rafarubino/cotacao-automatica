import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

# Definindo os escopos e ID da planilha
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1SbBkuxGIvnww__aw74fiLu1dx9XXJuLGq9KOBYIq-o0"  # apenas a parte ID
RANGE_NAME = "fornecedores!A:D"  # altere o nome da aba se necessário

# Função para obter as credenciais da conta de serviço a partir de st.secrets
def init_google_sheets():
    google = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    
    creds = Credentials.from_service_account_info(google)
    return creds

# Função para salvar os dados na planilha
def salvar_dados(produto, valor):
    creds = init_google_sheets()  # Inicializa as credenciais
    try:
        service = build("sheets", "v4", credentials=creds)  # Conecta com a API do Google Sheets

        # Identificar a data e hora atuais ajustando o horário
        data_atual = datetime.now().strftime("%Y-%m-%d")
        hora_atual = (datetime.now() - timedelta(hours=3)).strftime("%H:%M:%S")

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
        st.write("Dados salvos na planilha com sucesso!")  # Mensagem de sucesso
    except HttpError as err:
        st.write("Erro ao salvar na planilha:", err)  # Mensagem de erro

# Código do Streamlit
st.image("feriozzi_logo.png", width = 300)
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
