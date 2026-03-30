# Desafio Hyperautomação – Portal da Transparência

## Objetivo

Automatizar a coleta de dados de pessoas físicas no Portal da Transparência, salvando os resultados em:
- Google Drive (arquivo JSON)
- Google Sheets (registro estruturado)

A API permite iniciar o processamento e consultar posteriormente os dados coletados.

---

## Decisões Técnicas do Backend

### 1. Endpoint único para processamento (POST)

**POST /pessoafisica**

- O backend identifica automaticamente se o valor é nome, CPF ou NIS
- Redução de duplicação de código  
  - Múltiplos endpoints como `/nome`, `/cpf`, `/nis` fariam a mesma coisa
- API mais simples e consistente
- Melhor aderência ao padrão REST

---

### 2. Endpoints de consulta (GET)

- `GET /pessoafisica/nome`
- `GET /pessoafisica/cpf`
- `GET /pessoafisica/nis`

---

### 3. Separação entre processamento e consulta

- **POST** → executa o bot e salva os dados  
- **GET** → apenas consulta dados já processados  

Evita reprocessamento desnecessário e melhora performance.

---

### 4. Processamento em background

O bot é executado em segundo plano:

```python
background_tasks.add_task(processar_pessoa, identificador)
```

## Fluxo da Aplicação

### 1. Iniciar processamento

```bash
POST /pessoafisica?identificador=12345678900
```
- **Resposta:**
```json
{
  "id": "uuid-gerado",
  "status": "processando",
  "mensagem": "Coleta iniciada com sucesso"
}
```
### 2. Processamento interno

- Executa o bot (Playwright)
- Acessa o Portal da Transparência
- Extrai os dados
- Gera JSON
- Salva no Google Drive
- Registra no Google Sheets  

---

### 3. Consulta dos dados

**GET**

A API:

- Identifica o tipo (nome, CPF ou NIS)
- Busca o registro no Google Sheets
- Recupera o JSON do Google Drive
- Retorna os dados  

---

### 4. Registro resumido

Registro salvo no **Google Sheets** (`sheets_service.py`):

- ID  
- Nome  
- CPF  
- NIS  
- Data/Hora  
- Link do arquivo  

---

### 5. Resposta da API

- Dados coletados  
- ID do arquivo no Drive  
- Nome do JSON gerado  

## Estrutura do Projeto

```bash
desafio-01/
├── api/
│   ├── main.py
│   └── pessoas_fisica_routes.py
├── bot.py
├── drive/
│   └── drive_service.py
├── sheets/
│   └── sheets_service.py
├── credenciais_oauth.json       # não subir
├── credenciais_service.json     # não subir
├── token.json                   # gerado automaticamente
├── venv/                        # não subir
├── .env                         # não subir
├── requirements.txt
└── README.md
```
- api/ -> endpoints FastAPI
- drive/ -> upload JSON para Google Drive
- sheets/ -> grava dados no Google Sheets

---

## Variáveis de Ambiente (.env)

O projeto utiliza variáveis sensíveis via `.env`.

### Exemplo

```env
SPREADSHEET_ID=seu_id_da_planilha
```

## Tecnologias

- Python 3.x  
- FastAPI  
- Playwright (automação web)  
- Google Drive API (OAuth)  
- Google Sheets API (Service Account)  

### Bibliotecas auxiliares

- `uuid`  
- `datetime`  
- `json`  
- `os`  
- `io`  

---

## Instalação

```bash
git clone <repo_url>
cd desafio-01

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Instalar navegadores para Playwright
playwright install
```

## Configuração de Credenciais

### Google Sheets (Service Account)

1. Criar Service Account no Google Cloud  
2. Baixar `credenciais_service.json`  
3. Compartilhar a planilha com o `client_email` da Service Account  

---

### Google Drive (OAuth)

1. Criar OAuth Client no Google Cloud  
2. Salvar `credenciais_oauth.json` na raiz  
3. Na primeira execução:
   - Fazer login manual  
   - O `token.json` será gerado automaticamente  

## Como Rodar

Após instalar as dependências, execute o servidor FastAPI com o comando:

```bash
cd desafio-01
uvicorn api.main:app --reload
```

O servidor será iniciado em:

```bash
http://localhost:8000
```

## Acessando a API (Swagger)

1. Abra o navegador e acesse:

```bash
http://localhost:8000/docs
```
2. Você verá a interface interativa do Swagger (gerada pelo FastAPI)

3. Para testar:

### POST

- Clique em `POST /pessoafisica`
- Clique em **"Try it out"**
- Preencha o parâmetro com nome, CPF ou NIS
- Clique em **"Execute"**

### GET

- Clique em:
  - `GET /pessoafisica/nome`
  - `GET /pessoafisica/cpf`
  - `GET /pessoafisica/nis`
- Clique em **"Try it out"**
- Preencha o parâmetro
- Clique em **"Execute"**

## Execução do Bot (Importante)

Durante a execução, o bot pode exigir algumas interações manuais:

### CAPTCHA

Caso apareça o CAPTCHA no site do Portal da Transparência:

1. Resolva manualmente no navegador aberto pelo bot  
2. Volte ao terminal  
3. Pressione **ENTER** para continuar a execução  

## Autenticação Google Drive (Primeira execução)

Na primeira vez que rodar:

1. Será aberta uma janela de login do Google  
2. Faça login com sua conta  
3. Autorize o acesso  

---

Após isso:

- Um arquivo `token.json` será salvo  
- Nas próximas execuções não será necessário logar novamente até encerrar o servidor  

## Resultado Final

Após a execução completa:

- Os dados são retornados na API  
- Um arquivo JSON é salvo no Google Drive  
- Um registro é inserido no Google Sheets com:

  - ID  
  - Nome  
  - CPF  
  - NIS  
  - Data/Hora  
  - Link do arquivo  

## Exemplo de Uso da API (Endpoints)

### Consulta por nome

```bash
GET /pessoafisica/nome?nome=<nome_da_pessoa>
```
### Consulta por CPF

```bash
GET /pessoafisica/cpf?cpf=<cpf_da_pessoa>
```

### Consulta por NIS

```bash
GET /pessoafisica/nis?nis=<nis_da_pessoa>
```
### Exemplo de Resposta

```json
{
  "dados": [
    {
      "nome": "JOÃO DA SILVA",
      "cpf": "12345678900",
      "nis": "123456789",
      "location": "SP - São Paulo",
      "recurso_tipo": "Auxílio Emergencial",
      "valor_total_recebido": "R$ 2.400,00",
      "detalhes": [
        {
          "mes_disponibilizacao": "01/2023",
          "parcela": "1",
          "uf": "SP",
          "municipio": "São Paulo",
          "enquadramento": "Critério X",
          "valor": "R$ 400,00",
          "observacao": ""
        }
      ],
      "img_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ],
  "drive_file_id": "1a2b3c4d5e6f",
  "nome_arquivo": "12345678900_20260323_173500.json"
}
```

---

## Limitações Conhecidas

Devido às proteções do site e limitações de autenticação do Google, algumas etapas requerem interação manual.  
Em um ambiente produtivo, seriam utilizadas soluções como Service Accounts completas e serviços de resolução de CAPTCHA.

- CAPTCHA: execução headless não funciona totalmente, podendo exigir intervenção manual  
- Drive OAuth: abre janela de login na primeira execução  
- Drive compartilhado: arquivos são salvos em pasta pessoal atualmente  

---

## Melhorias Futuras

- Execução 100% headless  
- Service Account para Drive (evitar OAuth manual)  
- Automação do CAPTCHA  
- Logging detalhado e retries  
- Containerização (Docker)  
- Deploy em cloud (AWS/GCP)  