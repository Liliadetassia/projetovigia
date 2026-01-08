import cv2
import base64
import time
import datetime
import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential


# Carrega as variáveis do arquivo .env
load_dotenv()

# ==========================================
# CONFIGURAÇÕES SEGURAS
# ==========================================
# Busca o token no arquivo .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ENDPOINT = os.getenv("ENDPOINT_AI")
MODEL_NAME = "gpt-4o-mini"

# Validação para não travar se esquecer a chave
if not GITHUB_TOKEN:
    print("❌ ERRO: Token do GitHub não encontrado no arquivo .env")
    exit()


client = ChatCompletionsClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(GITHUB_TOKEN),
)

def gerar_relatorio_tatico(imagem_cv2):
    """
    Envia a imagem para a IA e solicita uma análise de segurança pública.
    """
    print("\n🚨 SPIA: PROCESSANDO IMAGEM... AGUARDE ANÁLISE TÁTICA.")
    
 
    _, buffer = cv2.imencode('.jpg', imagem_cv2)
    imagem_base64 = base64.b64encode(buffer).decode('utf-8')
    url_imagem = f"data:image/jpeg;base64,{imagem_base64}"

    # --- PROMPT DE ENGENHARIA PARA SEGURANÇA ---
    
    prompt_sistema = """
    Você é o módulo central de visão computacional do sistema 'SPIA' (Policiamento por Inteligência Artificial).
    Sua função é analisar imagens de câmeras de segurança e identificar riscos à ordem pública.
    
    Analise a imagem friamente e gere um relatório JSON (sem formatação de código) com:
    1. 'elementos': O que você vê (Pessoas, objetos, veículos).
    2. 'comportamento': O que está acontecendo (Parado, Correndo, Agressão, Acidente).
    3. 'objetos_interesse': Destaque se houver (Armas, Facas, Celulares, Capacetes). Se não houver, diga "Nenhum".
    4. 'nivel_risco': BAIXO, MÉDIO ou ALTO.
    5. 'protocolo': Ação sugerida para a viatura (Ex: Apenas observar, Abordagem preventiva, Acionar resgate).

    Seja breve, técnico e direto. Use linguagem policial/militar.
    """

    try:
        response = client.complete(
            messages=[
                SystemMessage(content=prompt_sistema),
                UserMessage(content=[
                    {"type": "text", "text": "Analise esta cena imediatamente."},
                    {"type": "image_url", "image_url": {"url": url_imagem}}
                ]),
            ],
            model=MODEL_NAME,
            temperature=0.4, 
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ ERRO DE COMUNICAÇÃO COM O NÚCLEO: {e}"

webcam = cv2.VideoCapture(0) 

font = cv2.FONT_HERSHEY_SIMPLEX

print("------------------------------------------------")
print("🛡️ SISTEMA VIGIA - MÓDULO VISUAL INICIADO")
print("⌨️  Pressione [ESPAÇO] para analisar a cena.")
print("❌ Pressione [ESC] para encerrar patrulha.")
print("------------------------------------------------")

while webcam.isOpened():
    success, frame = webcam.read()
    if not success:
        print("Erro ao ler câmera.")
        break

    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    cv2.putText(display_frame, f"SPIA REC :: {agora}", (10, 30), font, 0.7, (0, 255, 0), 2)
    cv2.putText(display_frame, "STATUS: MONITORANDO", (10, 450), font, 0.6, (0, 255, 0), 2)
    
   
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2
    cv2.line(display_frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 1)
    cv2.line(display_frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 1)

    cv2.imshow("SISTEMA VIGIA - CAM 01", display_frame)

    key = cv2.waitKey(1)

    if key == 27:
        break
    
   
    elif key == 32:
     
        cv2.putText(display_frame, "ANALISANDO...", (center_x - 80, center_y - 50), font, 1, (0, 0, 255), 3)
        cv2.imshow("SISTEMA VIGIA - CAM 01", display_frame)
        cv2.waitKey(100) 

      
        relatorio = gerar_relatorio_tatico(frame)
        
        print("\n" + "="*50)
        print("📄 RELATÓRIO DE INTELIGÊNCIA ARTIFICIAL")
        print("="*50)
        print(relatorio)
        print("="*50 + "\n")

webcam.release()
cv2.destroyAllWindows()