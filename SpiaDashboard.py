import streamlit as st
import cv2
import base64
import requests
import pandas as pd
import json
import time
import re
import os
from dotenv import load_dotenv
from datetime import datetime
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# ==========================================
# 1. CONFIGURAÇÕES (HARDCODED / FIXAS)
# ==========================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ENDPOINT_AI = os.getenv("ENDPOINT_AI")
EVO_URL_TEXT = os.getenv("EVO_URL_TEXT")
EVO_APIKEY = os.getenv("EVO_APIKEY")
NUMERO_PADRAO = os.getenv("NUMERO_PADRAO", "") # Se não tiver, fica vazio

# Validação de Segurança
if not GITHUB_TOKEN or not EVO_APIKEY:
    st.error("⚠️ ERRO DE CONFIGURAÇÃO: Chaves de API não encontradas. Configure as Variáveis de Ambiente na Coolify ou no arquivo .env.")
    st.stop()

# ==========================================
# 2. FUNÇÕES DO SISTEMA
# ==========================================

def limpar_telefone(telefone):
    """Remove parenteses, traços e espaços, deixando só numeros"""
    if not telefone: return ""
    return re.sub(r'\D', '', telefone)

def enviar_whatsapp_com_foto(mensagem, risco, numero_para_envio, imagem_bytes):
    """
    Envia a FOTO capturada + TEXTO de alerta.
    Troca automaticamente a URL de /sendText para /sendMedia.
    """
    
    # Validação de Risco
    riscos_perigosos = ["ALTO", "MEDIO", "MÉDIO"]
    if risco.upper() not in riscos_perigosos:
        return False, "Situação segura. Nenhuma mensagem enviada."
    
    # Validação de Número
    if not numero_para_envio or len(numero_para_envio) < 10:
        return False, "Número de telefone inválido."

    # --- PASSO 1: Preparar a Imagem (Base64) ---
    imagem_b64 = base64.b64encode(imagem_bytes).decode('utf-8')

    # --- PASSO 2: Ajustar a URL para aceitar Mídia ---
    # A Evolution tem endpoints diferentes para Texto e Mídia.
    # Se a URL configurada for sendText, trocamos para sendMedia.
    if "sendText" in EVO_URL_TEXT:
        url_media = EVO_URL_TEXT.replace("sendText", "sendMedia")
    else:
        url_media = EVO_URL_TEXT # Tenta usar a que está se não tiver o padrão

    headers = {
        "apikey": EVO_APIKEY,
        "Content-Type": "application/json"
    }
    
    # --- PASSO 3: Montar o Pacote (Payload) ---
    # Formato específico para enviar imagem com legenda
    payload = {
        "number": numero_para_envio,
        "media": imagem_b64,
        "mediatype": "image",
        "mimetype": "image/jpeg",
        "caption": f"🚨 *ALERTA SPIA - RISCO {risco} DETECTADO*\n\n{mensagem}",
        "fileName": "evidencia_spia.jpg",
        "options": {
            "delay": 1200,
            "presence": "composing"
        }
    }
    
    try:
        print(f"📡 Enviando foto para: {url_media} | Destino: {numero_para_envio}")
        response = requests.post(url_media, json=payload, headers=headers)
        
        # Aceita 200 (OK) ou 201 (Criado)
        if response.status_code in [200, 201]:
            return True, f"Foto enviada para {numero_para_envio}!"
        else:
            return False, f"Erro EvoAPI: {response.text}"
    except Exception as e:
        return False, f"Erro de conexão: {e}"

def analisar_imagem_ai(imagem_bytes):
    """Envia para o GPT-4o-mini e retorna um JSON"""
    try:
        client = ChatCompletionsClient(
            endpoint=ENDPOINT_AI,
            credential=AzureKeyCredential(GITHUB_TOKEN),
        )
        
        imagem_base64 = base64.b64encode(imagem_bytes).decode('utf-8')
        url_imagem = f"data:image/jpeg;base64,{imagem_base64}"

        prompt = """
        Você é o sistema SPIA. Analise a imagem para segurança pública.
        Responda EXCLUSIVAMENTE um JSON válido neste formato (sem ```json):
        {
            "situacao": "Resumo curto do que está acontecendo",
            "risco": "BAIXO, MEDIO ou ALTO",
            "acao": "Ação recomendada (Ex: Chamar SAMU, Abordar, Monitorar)",
            "detalhes": "Descrição técnica da cena"
        }
        """

        response = client.complete(
            messages=[
                SystemMessage(content=prompt),
                UserMessage(content=[{"type": "text", "text": "Analise."}, {"type": "image_url", "image_url": {"url": url_imagem}}]),
            ],
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.replace("```json", "").replace("```", "")
        return json.loads(content)
    except Exception as e:
        return {"situacao": "Erro na IA", "risco": "ERRO", "acao": str(e), "detalhes": ""}

# ==========================================
# 3. INTERFACE (FRONTEND)
# ==========================================

st.set_page_config(page_title="SPIA Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ SPIA - Sistema de Policiamento por IA")
st.markdown("**Obs:**")

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("📡 Configuração de Alerta")

# Campo para o usuário digitar o número
telefone_usuario = st.sidebar.text_input(
    "WhatsApp para Alerta (55+DDD+Numero)", 
    value=NUMERO_PADRAO,
    help="Digite o número que receberá a foto e o relatório."
)
# Limpa o número para garantir que a API aceite
telefone_limpo = limpar_telefone(telefone_usuario)

st.sidebar.divider()
st.sidebar.success("Servidor IA: ONLINE")
st.sidebar.info(f"API Conectada: {EVO_URL_TEXT.split('/')[2]}")
modo_automatico = st.sidebar.checkbox("Modo Vigilância Automática (Simulação)")


# --- ÁREA PRINCIPAL ---
col1, col2 = st.columns([2, 1])

if 'historico' not in st.session_state:
    st.session_state['historico'] = []

with col1:
    st.subheader("📷 Monitoramento em Tempo Real")
    
    img_file = st.camera_input("Capturar Evidência")

    if img_file is not None:
        
        bytes_data = img_file.getvalue()
        
        with st.spinner('🤖 SPIA Analisando padrões biométricos e comportamentais...'):
            
            # 1. Chama a IA
            dados_analise = analisar_imagem_ai(bytes_data)
            
            nivel_risco = dados_analise.get("risco", "BAIXO")
            
            cor_alerta = "green"
            if nivel_risco == "MEDIO": cor_alerta = "orange"
            if nivel_risco == "ALTO": cor_alerta = "red"
            
            # Mostra resultado na tela
            st.markdown(f":{cor_alerta}[### ⚠️ NÍVEL DE RISCO: {nivel_risco}]")
            st.write(f"**Situação:** {dados_analise['situacao']}")
            st.write(f"**Ação Recomendada:** {dados_analise['acao']}")
            
            # 2. Chama o Envio de WhatsApp (FOTO + TEXTO)
            enviado = False
            msg_log = ""

            if telefone_limpo:
                enviado, msg_log = enviar_whatsapp_com_foto(
                    f"Situação: {dados_analise['situacao']}\nAção: {dados_analise['acao']}", 
                    nivel_risco,
                    telefone_limpo, # Envia para o número do input
                    bytes_data      # Envia a foto capturada
                )
            else:
                msg_log = "Sem número definido"
            
            # Feedback Visual
            if enviado:
                st.toast(f"🚨 FOTO E ALERTA ENVIADOS PARA {telefone_limpo}!", icon="📲")
            elif nivel_risco in ["MEDIO", "ALTO"]:
                st.error(f"Falha no envio: {msg_log}")
            
            # 3. Salva no histórico
            evento = {
                "Horario": datetime.now().strftime("%H:%M:%S"),
                "Risco": nivel_risco,
                "Situacao": dados_analise['situacao'],
                "Destino": telefone_limpo if telefone_limpo else "N/A",
                "Notificacao": "✅ Foto Enviada" if enviado else "❌ Falha"
            }
            st.session_state['historico'].insert(0, evento) 

with col2:
    st.subheader("📊 Estatísticas da Sessão")
    
    # --- NOVO BLOCO DE ORIENTAÇÃO (Inserido Aqui) ---
    st.caption("""
    **Para validar se o sistema funciona como o projeto SPIA/Vigia propõe, tente simular estas situações na frente da câmera e clique em Take photo. Se estiver mobile, insira também seu numero na barra lateral esquerda clicando no ícone >> para envio da foto e mensagem:**
    
    **1. Cenário "Normalidade":**
    - **Ação:** Fique parado olhando para a câmera, sem nada nas mãos.
    - **Resultado Esperado:** A IA deve relatar "Comportamento: Estático/Normal", "Risco: BAIXO", você não receberá notificação no celular.
    
    **2. Cenário "Objeto Suspeito":**
    - **Ação:** Segure um objeto como se fosse uma arma (secador, furadeira ou apontar o dedo).
    - **Resultado Esperado:** A IA deve relatar "Risco: MÉDIO ou ALTO" e enviar o alerta no seu celular que você inseriu no menu lateral.
    """)
    st.divider()
    # ------------------------------------------------
    
    df = pd.DataFrame(st.session_state['historico'])
    
    if not df.empty:
        total_ocorrencias = len(df)
        risco_alto = len(df[df['Risco'] == 'ALTO'])
        
        m1, m2 = st.columns(2)
        m1.metric("Ocorrências", total_ocorrencias)
        m2.metric("Alertas Críticos", risco_alto, delta_color="inverse")
        
        st.divider()
        st.write("📜 **Log de Eventos Recentes**")
        st.dataframe(df, hide_index=True)
    else:
        st.info("Aguardando primeira análise...")

st.markdown("---")
st.caption("Desenvolvido por Lilia de Tássia para o Projeto SPIA/Vigia - Integração IA + IoT + EvoAPI")