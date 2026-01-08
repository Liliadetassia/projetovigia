import requests
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# ==========================================
# CONFIGURAÇÕES SEGURAS
# ==========================================
# Busca os valores definidos no seu arquivo .env
URL_EVO = os.getenv("EVO_URL_TEXT")
API_KEY = os.getenv("EVO_APIKEY")
TELEFONE = os.getenv("NUMERO_PADRAO")

# Validação simples para não rodar se faltar algo
if not URL_EVO or not API_KEY:
    print("❌ ERRO: Variáveis de ambiente não encontradas. Verifique o arquivo .env")
    exit()

payload = {
    "number": TELEFONE,
    "text": "🤖 Teste de Conexão SPIA: Se chegou, estamos online!",
    "options": {
        "delay": 1200,
        "presence": "composing"
    }
}

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

print(f"📡 Tentando enviar para: {URL_EVO}")

try:
    response = requests.post(URL_EVO, json=payload, headers=headers)
    
    print("\n--- RESPOSTA DO SERVIDOR ---")
    print(f"Status Code: {response.status_code}") # 200 ou 201 é sucesso
    print(f"Corpo da Resposta: {response.text}")
    
    if response.status_code == 201 or response.status_code == 200:
        print("✅ SUCESSO! Verifique seu WhatsApp.")
    else:
        print("❌ ERRO! Analise a mensagem acima.")

except Exception as e:
    print(f"❌ ERRO GRAVE DE CONEXÃO: {e}")