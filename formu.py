import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import schedule
import time

# Definindo os escopos e ID da planilha
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1SbBkuxGIvnww__aw74fiLu1dx9XXJuLGq9KOBYIq-o0"  # ID da planilha
RANGE_CONTATOS = "contatos!A:B"  # Aba com nomes e e-mails
RANGE_DADOS = "fornecedores!A:E"  # Aba para salvar as respostas

# Função para obter as credenciais da conta de serviço
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
def salvar_dados(nome, produto, valor):
    creds = init_google_sheets()
    try:
        service = build("sheets", "v4", credentials=creds)

        # Identificar a data e hora atuais
        data_atual = datetime.now().strftime("%Y-%m-%d")
        hora_atual = datetime.now().strftime("%H:%M:%S")

        # Preparar os dados para envio
        valores = [[nome, data_atual, hora_atual, produto, valor]]
        body = {"values": valores}

        # Adiciona os dados à planilha
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_DADOS,
            valueInputOption="RAW",
            body=body
        ).execute()
        st.write("Dados salvos na planilha com sucesso!")
    except HttpError as err:
        st.write("Erro ao salvar na planilha:", err)

# Função para enviar e-mails com o link
def enviar_emails():
    creds = init_google_sheets()
    service = build("sheets", "v4", credentials=creds)

    # Ler a aba de contatos
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_CONTATOS
        ).execute()
        contatos = result.get('values', [])

        if not contatos:
            st.write("Nenhum contato encontrado na planilha.")
            return

        # Configurar envio de e-mails
        for contato in contatos:
            nome = contato[0]
            email = contato[1]

            mensagem = f"""
            Olá, {nome}!

            Por favor, acesse o link abaixo para preencher o formulário de cotação:

            https://cotacao-automatica-5hpk8r8hupe4mmuez6qgag.streamlit.app/

            Atenciosamente,
            Sua equipe.
            """
            msg = MIMEText(mensagem)
            msg['Subject'] = "Formulário de Cotação"
            msg['From'] = "seu_email@gmail.com"
            msg['To'] = email

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login("seu_email@gmail.com", "sua_senha")
                server.sendmail(msg['From'], [msg['To']], msg.as_string())

        st.write("E-mails enviados com sucesso!")
    except HttpError as err:
        st.write("Erro ao acessar a planilha de contatos:", err)

# Código do Streamlit
st.image("feriozzi_logo.png", width=100)
st.title("Formulário de Cotação")
st.write("Este formulário tem o intuito de automatizar o processo de cotação.")

# Coletar o nome do fornecedor
st.header("Nome")
nome = st.text_input("Digite seu nome:")

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
    salvar_dados(nome, produto, valor)
    st.write("Enviado!")

# Agendar envio semanal
schedule.every(1).minutes.do(enviar_emails)

# Executar agendador
while True:
    schedule.run_pending()
    time.sleep(1)
