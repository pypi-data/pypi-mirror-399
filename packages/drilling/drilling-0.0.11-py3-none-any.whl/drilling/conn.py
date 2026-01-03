from sqlalchemy import create_engine, text
from sshtunnel import SSHTunnelForwarder

# Google APIs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import json

try: 
    from drilling.context_sources import *
    from drilling.context import *
except: 
    from context_sources import *
    from context import *

def db_connection(params: dict):
    # Cria conexão com banco de dados, com suporte a túnel SSH se necessário.

    # Global
    gb_ssh = PARAMS.get('EnableSSH', None)
    if gb_ssh is None:
        gb_ssh = params["SSH"]["Habilited"]

    # Banco
    db_dialect = params["Dialect"]
    db_protocol = params["Protocol"] + "://"
    db_host = params["Server"]
    db_port = params["Port"]
    db_user = params["User"]
    db_password = params["Pass"]
    db_name = params["Database"]
    db_driver = params["Driver"] or ""

    # SSH
    shh = gb_ssh
    ssh_host = params["SSH"].get("Host", "")
    ssh_port = params["SSH"].get("Port", 22)
    ssh_user = params["SSH"].get("User", "")
    ssh_password = str(params["SSH"].get("Pass", ""))

    if shh:
        tunnel = SSHTunnelForwarder(
            (ssh_host, 22),
            ssh_username=ssh_user,
            ssh_password=ssh_password,
            remote_bind_address=(db_host, db_port),  # ajuste se necessário
            local_bind_address=('127.0.0.1', 0)
        )
        tunnel.start()

        ssh_tunnel = tunnel
        db_host = "127.0.0.1"
        db_port = ssh_tunnel.local_bind_port

    if db_dialect in ['PostgreSQL', 'SQLServer']:
        db_host = db_host
        db_port = db_port
        db_url = f"@{db_host}:{db_port}/"
        db_credentials = f"{db_user}:{db_password}"
        conn_str = f"{db_protocol}{db_credentials}{db_url}{db_name}{db_driver}"
        
        engine = create_engine(conn_str)
        conn = engine.connect()
        return engine, conn

def gdrive_connection(params: dict):
    DRIVE_CRED = CONTEXT['BASE_PATH'] / 'archives' 
    OAUTH_FILE = DRIVE_CRED / params['Secret']  # caminho para sua chave JSON
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials_path = OAUTH_FILE
    scopes = SCOPES 
    service = None

    with open(credentials_path, "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, scopes=scopes)

    # Criar serviço da API
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return service


class Connect():

    def __init__(self, parameters):

        if not isinstance(parameters, dict):
            parameters = ConPrm(parameters)

        self.params = parameters

        # Objetos internos
        self.engine = None
        self.conn = None
        self.ssh_tunnel = None

    def __enter__(self):
        if self.params['Type'] == 'Database': self.engine, self.conn = db_connection(self.params)
        elif self.params['Type'] == 'Drive': self.conn = gdrive_connection(self.params)
        return self.conn
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.params['Type'] == 'Database':
            if self.conn: self.conn.close()
            if self.engine: self.engine.dispose()
            if self.ssh_tunnel: self.ssh_tunnel.stop()
        elif self.params['Type'] == 'Drive':
            self.conn = None
        
if __name__ == "__main__":

    # Exemplo de uso para testes locais com sqlite em memória
    with Connect('Drive') as conn:
        print(conn)
        
        results = conn.files().list(
            q=f"'1M6RHKhYKHk8bKWVrwZEVVkuixAF-hOCe' in parents and trashed = false",
            fields="files(id, name, mimeType)"
        ).execute()

        print(results.get('files', []))
        #result = conn.execute(text("SELECT 'success' as attempt"))
        #for row in result:
            #print(row)