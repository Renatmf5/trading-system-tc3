#!/bin/bash
DIR="/home/ec2-user/Trading-App"
echo "AfterInstall: Instalando dependências"
sudo chown -R ec2-user:ec2-user ${DIR}
cd ${DIR}

# Instalar dependências Python usando pip
pip install -r requirements.txt