#!/bin/bash
DIR="/home/ec2-user/trading-app"
LOG_FILE="/home/ec2-user/trading-app/deploy.log"

echo "AfterInstall: Iniciando script" | tee -a ${LOG_FILE}
sudo chown -R ec2-user:ec2-user ${DIR}
cd ${DIR} || { echo "Erro: Não foi possível acessar o diretório ${DIR}" | tee -a ${LOG_FILE}; exit 1; }

# Criar ambiente virtual e instalar dependências
echo "AfterInstall: Criando ambiente virtual" | tee -a ${LOG_FILE}
python3 -m venv venv || { echo "Erro: Falha ao criar o ambiente virtual" | tee -a ${LOG_FILE}; exit 1; }
source venv/bin/activate || { echo "Erro: Falha ao ativar o ambiente virtual" | tee -a ${LOG_FILE}; exit 1; }

echo "AfterInstall: Instalando dependências" | tee -a ${LOG_FILE}
pip install -r requirements.txt || { echo "Erro: Falha ao instalar dependências" | tee -a ${LOG_FILE}; exit 1; }

# Criar arquivo de serviço systemd para a aplicação
echo "AfterInstall: Criando arquivo de serviço systemd" | tee -a ${LOG_FILE}
sudo bash -c 'cat <<EOF > /etc/systemd/system/trading-app.service
[Unit]
Description=First trading Application
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/trading-app
ExecStart=/home/ec2-user/trading-app/venv/bin/python /home/ec2-user/trading-app/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# Recarregar systemd para aplicar as mudanças
echo "AfterInstall: Recarregando systemd" | tee -a ${LOG_FILE}
sudo systemctl daemon-reload || { echo "Erro: Falha ao recarregar o systemd" | tee -a ${LOG_FILE}; exit 1; }v