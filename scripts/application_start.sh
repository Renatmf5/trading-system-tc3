#!/bin/bash
DIR="/home/ec2-user/trading-app"

echo "ApplicationStart: Iniciando a aplicação" | tee -a /home/ec2-user/trading-app/deploy.log

# Adicionar ~/.local/bin ao PATH
export PATH=$PATH:/home/ec2-user/.local/bin
echo "PATH atualizado: $PATH" | tee -a /home/ec2-user/trading-app/deploy.log

# Conceder permissões
sudo chmod -R 777 ${DIR}

# Navegar para o diretório da aplicação
cd ${DIR}

# Definir variável de ambiente
export ENV=production

# Verificar se o uvicorn está no PATH
echo "Verificando se o uvicorn está no PATH" | tee -a /home/ec2-user/trading-app/deploy.log
which uvicorn | tee -a /home/ec2-user/trading-app/deploy.log

# Aplicar setcap ao binário do Python
PYTHON_BIN=$(readlink -f $(which python3))
sudo setcap 'cap_net_bind_service=+ep' $PYTHON_BIN
echo "Permissões setcap aplicadas ao Python" | tee -a /home/ec2-user/trading-app/deploy.log

# Executar o comando uvicorn para iniciar a aplicação FastAPI em segundo plano e redirecionar a saída para um arquivo de log
echo "ApplicationStart: Iniciando o serviço trading-app"
sudo systemctl start trading-app.service
sudo systemctl enable trading-app.service