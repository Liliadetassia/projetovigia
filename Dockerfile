# Usa uma imagem leve do Python 3.11
FROM python:3.11-slim

# Define a pasta de trabalho
WORKDIR /app

# Instala dependências do sistema (CORRIGIDO: libgl1 no lugar de libgl1-mesa-glx)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY . .

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar o SPIA
CMD ["streamlit", "run", "SpiaDashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]