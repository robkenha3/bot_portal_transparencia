from fastapi import APIRouter, BackgroundTasks
from ..bot import rodar_bot
from ..drive.drive_service import upload_json, baixar_json, extrair_file_id
from ..sheets.sheets_service import salvar_no_sheets, buscar_por_nome, buscar_por_cpf, buscar_por_nis
import uuid

pessoa_fisica_router = APIRouter(prefix="/pessoafisica", tags=["Pessoa Fisica"])

def processar_pessoa(identificador: str):
    resultado = rodar_bot(identificador)

    if not resultado or isinstance(resultado, dict):
        print("Erro no processamento:", resultado)
        return

    file_info = upload_json(resultado, identificador=identificador)

    pessoa = resultado[0]

    salvar_no_sheets(
        nome=pessoa.get("nome"),
        cpf=pessoa.get("cpf"),
        nis=pessoa.get("nis"),
        file_id=file_info["file_id"]
    )

@pessoa_fisica_router.post("/", summary="Processa uma pessoa")
def identificador(identificador: str, background_tasks: BackgroundTasks):
    """
    Este endpoint recebe um identificador (nome, CPF ou NIS)
    e inicia o processamento do bot.
    """
    process_id = str(uuid.uuid4())

    background_tasks.add_task(processar_pessoa, identificador)

    return {
        "id": process_id,
        "status": "processando",
        "mensagem": "Coleta iniciada com sucesso"
    }
    

@pessoa_fisica_router.get("/nome")
def get_nome(nome: str):
    link = buscar_por_nome(nome)

    if not link:
        return {"status": f"Foram encontrados 0 resultados para o termo {nome}"}

    file_id = extrair_file_id(link)
    dados = baixar_json(file_id)

    return {
        "status": "concluido",
        "dados": dados
    }

@pessoa_fisica_router.get("/cpf")
def get_cpf(cpf: str):
    link = buscar_por_cpf(cpf)

    if not link:
        return {"status": "Não foi possível retornar os dados no tempo de resposta solicitado"}

    file_id = extrair_file_id(link)
    dados = baixar_json(file_id)

    return {
        "status": "concluido",
        "dados": dados
    }

@pessoa_fisica_router.get("/nis")
def get_nis(nis: str):
    link = buscar_por_nis(nis)

    if not link:
        return {"status": "Não foi possível retornar os dados no tempo de resposta solicitado"}

    file_id = extrair_file_id(link)
    dados = baixar_json(file_id)

    return {
        "status": "concluido",
        "dados": dados
    }