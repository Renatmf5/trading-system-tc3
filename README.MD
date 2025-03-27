# Projeto de Trading Automatizado com Binance

Este projeto é uma aplicação de trading automatizado que utiliza dados de mercado da Binance para realizar análises e executar operações de compra e venda de criptomoedas. Ele combina diversos modelos de machine learning e deep learning de nossa propriedade, indicadores técnicos e integração com APIs para tomar decisões de trading.
O acesso a esses modelos pré treinados estão sendo feitos via load do modelo num bucketS3 do projeto.

---

## Estrutura do Projeto

- **`main.py`**: Arquivo principal que conecta ao WebSocket da Binance, processa os dados recebidos e envia sinais de trading para uma API FastAPI a qual faz o controle das ordens e historico de trades atraves de uma alimentação desses dadso em um RDS  Postgres do projeto.
- **`data_handler.py`**: Contém funções para manipulação de dados, carregamento de modelos de machine learning e processamento de candles.
- **`comumind.py`**: Implementa cálculos de indicadores técnicos usados para modelos de machine learning.
- **`customind.py`**: Contém funções personalizadas para cálculos de retornos, volatilidade e detecção de padrões de mercado.
- **`binance_client.py`**: Configura o cliente da Binance para acessar dados de mercado e executar operações.

---

## Funcionalidades

- Conexão com WebSocket da Binance para receber dados em tempo real.
- Processamento de candles e cálculo de indicadores técnicos.
- Integração com modelos de machine learning (XGBoost, LSTM, MLP, Ensemble e PPO).
- Carregamento de modelos e scalers diretamente do Amazon S3.
- Envio de sinais de trading para uma API FastAPI.
- Detecção de padrões de mercado, como proximidade de topos e fundos.

**Funções principais do programa**:

- buscar_modelo_no_s3(symbol, model_path, modelo='pkl')
  - Descrição: Carrega um modelo de machine learning armazenado no Amazon S3.
  - Parâmetros:
    - symbol: Símbolo do ativo (ex.: BTCUSDT).
    - model_path: Caminho do modelo no bucket S3.
    - modelo: Tipo do modelo (pkl para modelos serializados com joblib ou keras para modelos TensorFlow/Keras).
  - Retorno: O modelo carregado ou None em caso de erro.

- carregar_modelo_ppo_do_s3(symbol, model_path)
  - Descrição: Carrega um modelo PPO (Proximal Policy Optimization) armazenado no Amazon S3.
  - Parâmetros:
    - symbol: Símbolo do ativo.
    - model_path: Caminho do modelo PPO no bucket S3.
  - Retorno: O modelo PPO carregado ou None em caso de erro.

- process_candles(symbol, data_path, timeframe)
  - Descrição: Processa os candles recebidos, calcula indicadores técnicos, aplica scalers e prepara os dados para os modelos de machine learning.
  - Parâmetros:
    - symbol: Símbolo do ativo.
    - data_path: DataFrame com os dados de candles.
    - timeframe: Intervalo de tempo dos candles (ex.: 15m).
  - Retorno: Dados escalados para os modelos XGBoost, LSTM e MLP, além de dados de preços (low, high, close).

- get_historical_kliness(symbol, interval, limit=760)
  - Descrição: Obtém dados históricos de candles da Binance, processa os dados e realiza previsões.
  - Parâmetros:
    - symbol: Símbolo do ativo.
    - interval: Intervalo de tempo dos candles.
    - limit: Número de candles a serem buscados (padrão: 760).
  - Retorno: Ação prevista pelo modelo e preço de fechamento.

- preparar_dados_chama_models(data_path_xgb, data_path_lstm, data_path_mlp, data_low_high_close, alpha=1.0)
  - Descrição: Prepara os dados para os modelos de machine learning, realiza previsões e combina os resultados em um ensemble.
  - Parâmetros:
    - data_path_xgb: Dados processados para o modelo XGBoost.
    - data_path_lstm: Dados processados para o modelo LSTM.
    - data_path_mlp: Dados processados para o modelo MLP.
    - data_low_high_close: Dados de preços (low, high, close).
    - alpha: Parâmetro de ajuste para o modelo XGBoost.
  - Retorno: Ação prevista pelo modelo PPO e preço de fechamento.
---

## Pré-requisitos

Certifique-se de ter os seguintes itens instalados:

- Python 3.10 ou superior
- Conta na Binance com chaves de API configuradas
- Dependências listadas no arquivo `requirements.txt`

---

## Instalação

1. Clone o repositório:
```bash
-  git clone https://github.com/Renatmf5/trading-system-tc3.git
-  cd trading-system-tc3
```
2. Instale as dependências:
```bash
- pip install -r requirements.txt
```