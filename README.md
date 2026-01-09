# 🛡️ SPIA - Sistema de Policiamento por Inteligência Artificial

---
## 🛡️ Nota de Segurança e Histórico

Este repositório é uma versão pública (Public Release) do meu projeto originalmente desenvolvido em meu ambiente privado. 
O histórico de commits anteriores foi resetado para garantir a segurança de credenciais sensíveis (Azure Keys, Evolution API Tokens) que foram migrados para Variáveis de Ambiente neste deploy, portanto este projeto não terá histórico dos commits, pretendo avançar nele e deixar algo mais robusto.

> **Projeto Vigia:** Monitoramento inteligente, análise de risco em tempo real e despacho automático de ocorrências via WhatsApp.

## 📋 Sobre o Projeto

O **SPIA** é uma Prova de Conceito (PoC) desenvolvida para modernizar a segurança pública. Diferente de câmeras tradicionais que apenas gravam, o SPIA atua como um **agente ativo**:

1.  **Vê:** Captura imagens em tempo real via Webcam/CCTV.
2.  **Pensa:** Utiliza Visão Computacional e LLMs (GPT-4o) para entender o contexto da cena (ex: diferenciar uma pessoa correndo por esporte de uma fuga).
3.  **Age:** Classifica o nível de risco e, se for crítico, envia um alerta imediato com foto e relatório para a viatura mais próxima via WhatsApp.

## 🚀 Funcionalidades

-   📸 **Visão Computacional:** Interface tática com sobreposição de dados (HUD).
-   🧠 **Análise Semântica:** Identificação de armas, brigas, acidentes ou comportamentos suspeitos.
-   📊 **Dashboard Operacional:** Painel Web interativo construído com Streamlit.
-   📲 **Alertas em Tempo Real:** Integração com **Evolution API** para envio de mensagens automáticas no WhatsApp quando o risco é **MÉDIO** ou **ALTO**.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Frontend:** Streamlit
* **Processamento de Imagem:** OpenCV
* **Inteligência Artificial:** OpenAI (GPT-4o-mini)
* **Mensageria:** Evolution API v2.3.7 (WhatsApp Gateway)
* **Infraestrutura:** Docker & Coolify

## ⚙️ Instalação e Configuração

### Pré-requisitos
* Python instalado.
* Uma instância da **Evolution API** rodando (Local ou Servidor).
* Token do **OpenAI** (para acesso ao GPT-4o).

## Como testar meu Protótipo (Cenários)
Para validar se o sistema funciona como o projeto SPIA/Vigia propõe, tente simular estas situações na frente da câmera e aperte Espaço:

Cenário "Normalidade":

Ação: Fique parado olhando para a câmera, sem nada nas mãos.

Resultado Esperado: A IA deve relatar "Comportamento: Estático/Normal", "Risco: BAIXO", "Protocolo: Apenas observar".

Cenário "Objeto Suspeito":

Ação: Segure um objeto como se fosse uma arma (pode ser um secador de cabelo, uma furadeira, ou até apontar o dedo).

Resultado Esperado: A IA deve detectar o objeto no campo objetos_interesse e possivelmente elevar o risco para MÉDIO ou ALTO, sugerindo "Abordagem" ou "Verificação".

Cenário "Acidente/Emergência":

Ação: Pegue um objeto cortante(faca), e simule ou deite no chão como se estivesse passando mal/desmaiado.

Resultado Esperado: A IA deve identificar "Indivíduo caído" ou "Postura de colapso" e sugerir "Protocolo: Acionar Resgate/SAMU".

Por que isso é tecnicamente relevante?
Este código demonstra a capacidade de Interpretação Semântica de Cenas. Enquanto sistemas antigos apenas detectam "tem movimento", o meu sistema entende o que é o movimento (ex: alguém correndo vs. alguém caindo). 

## Observação

Neste projeto optei em usar a coolify somente porque tenho projetos meus rodando nele, mas se quiser pode optar em usar portainer ou outro de sua preferência. 
