#!/bin/bash
DIR="/home/ec2-user/Trading-App"

echo "ApplicationStart: Iniciando a aplicação" | tee -a /home/ec2-user/Trading-App/deploy.log

# Adicionar ~/.local/bin ao PATH
export PATH=$PATH:/home/ec2-user/.local/bin
echo "PATH atualizado: $PATH" | tee -a /home/ec2-user/Trading-App/deploy.log

# Conceder permissões
sudo chmod -R 777 ${DIR}

# Navegar para o diretório da aplicação
cd ${DIR}

# Definir variável de ambiente
export ENV=production

# Verificar se o uvicorn está no PATH
echo "Verificando se o uvicorn está no PATH" | tee -a /home/ec2-user/Trading-App/deploy.log
which uvicorn | tee -a /home/ec2-user/Trading-App/deploy.log

# Aplicar setcap ao binário do Python
PYTHON_BIN=$(readlink -f $(which python3))
sudo setcap 'cap_net_bind_service=+ep' $PYTHON_BIN
echo "Permissões setcap aplicadas ao Python" | tee -a /home/ec2-user/Trading-App/deploy.log

# Executar o comando main.py
nohup python3 main.py > /dev/null 2>&1 &
echo "Comando main executado" | tee -a /home/ec2-user/Trading-App/deploy.log