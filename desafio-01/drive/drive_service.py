from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from datetime import datetime
from dotenv import load_dotenv
import io, json, os, uuid

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_drive_service():
    creds = autenticar()
    return build('drive', 'v3', credentials=creds)

def extrair_file_id(link):
    return link.split("/d/")[1].split("/")[0]

def baixar_json(file_id):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    file_data = request.execute()

    return json.loads(file_data)

def autenticar():
    BASE_DIR = get_base_dir()
    CAMINHO_CREDENCIAL = os.path.join(BASE_DIR, "credenciais_oauth.json")
    TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CAMINHO_CREDENCIAL, SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds

def gerar_nome_arquivo(identificador=None):
    if not identificador:
        identificador = str(uuid.uuid4())

    agora = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{identificador}_{agora}.json"

def upload_json(dados, identificador=None):
    service = get_drive_service()
    json_bytes = json.dumps(dados, indent=2, ensure_ascii=False).encode("utf-8")

    PASTA_ID = os.getenv("PASTA_ID")
    
    if not PASTA_ID:
        raise ValueError("PASTA_ID não configurado no .env")

    nome_arquivo = gerar_nome_arquivo(identificador)

    file_metadata = {
        'name': nome_arquivo,
        'parents': [PASTA_ID]
    }

    media = MediaIoBaseUpload(
        io.BytesIO(json_bytes),
        mimetype='application/json'
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return {
        "file_id": file.get('id'),
        "nome_arquivo": nome_arquivo
    }