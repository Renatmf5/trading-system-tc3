#!/bin/bash
DIR="/home/ec2-user/trading-app"
echo "AfterInstall: Iniciando script" | tee -a /home/ec2-user/trading-app/deploy.log
sudo chown -R ec2-user:ec2-user ${DIR}
cd ${DIR} || { echo "Erro: Não foi possível acessar o diretório ${DIR}"; exit 1; }

# Criar ambiente virtual e instalar dependências
echo "AfterInstall: Criando ambiente virtual" | tee -a /home/ec2-user/trading-app/deploy.log
python3 -m venv venv || { echo "Erro: Falha ao criar o ambiente virtual"; exit 1; }
source venv/bin/activate || { echo "Erro: Falha ao ativar o ambiente virtual"; exit 1; | tee -a /home/ec2-user/trading-app/deploy.log }

echo "AfterInstall: Instalando dependências"
pip install -r requirements.txt || { echo "Erro: Falha ao instalar dependências"; exit 1; }

# Criar arquivo de serviço systemd para a aplicação
echo "AfterInstall: Criando arquivo de serviço systemd" | tee -a /home/ec2-user/trading-app/deploy.log
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
echo "AfterInstall: Recarregando systemd"
sudo systemctl daemon-reload || { echo "Erro: Falha ao recarregar o systemd"; exit 1; }