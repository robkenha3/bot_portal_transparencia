from google.oauth2 import service_account
from datetime import datetime
from dotenv import load_dotenv
import gspread, os, uuid, re

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_client():
    BASE_DIR = get_base_dir()
    CAMINHO_CREDENCIAL = os.path.join(BASE_DIR, "credenciais_service.json")

    creds = service_account.Credentials.from_service_account_file(
        CAMINHO_CREDENCIAL,
        scopes=SCOPES
    )

    return gspread.authorize(creds)

def get_sheet():
    client = get_client()

    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID não configurado no .env")

    return client.open_by_key(SPREADSHEET_ID).sheet1

def buscar_por_nome(nome):
    sheet = get_sheet()
    dados = sheet.get_all_values()

    for linha in dados[1:]:
        nome_sheet = linha[1]
        if nome_sheet.lower() == nome.lower():
            return linha[5]

    return None

def buscar_por_cpf(cpf):
    sheet = get_sheet()
    dados = sheet.get_all_values()
    cpf_limpo = re.sub(r"\D", "", cpf)

    if not cpf_limpo.isdigit():
        return None 

    for linha in dados[1:]:
        cpf_sheet = linha[2]
        cpf_sheet_limpo = re.sub(r"\D", "", cpf_sheet)

        if cpf_sheet_limpo == cpf_limpo:
            return linha[5]

    return None

def buscar_por_nis(nis):
    sheet = get_sheet()
    dados = sheet.get_all_values()
    nis_limpo = re.sub(r"\D", "", nis)

    if not nis_limpo.isdigit():
        return None 
    
    for linha in dados[1:]:
        nis_sheet = linha[3]
        nis_sheet_limpo = re.sub(r"\D", "", nis_sheet)

        if nis_sheet_limpo == nis_limpo:
            return linha[5]

    return None

def salvar_no_sheets(nome, cpf, nis, file_id):
    sheet = get_sheet()
    identificador = str(uuid.uuid4())
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    link_drive = f"https://drive.google.com/file/d/{file_id}/view"

    sheet.append_row([
        identificador,
        nome,
        cpf,
        nis,
        data_hora,
        link_drive
    ])