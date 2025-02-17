import pandas as pd
import io
import joblib
from functions.indicadores import *
from services.binance_client import client
import boto3
from sklearn.preprocessing import StandardScaler
import json


def predict(symbol, last_row_scaled):
    sagemaker_client = boto3.client('sagemaker-runtime')
    endpoint_name = f'{symbol}-endpoint'  # Substitua pelo nome do seu endpoint

    try:
        # Converta last_row_scaled para CSV
        csv_data = ','.join(map(str, last_row_scaled[0]))
        
        response = sagemaker_client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Body=csv_data
        )
        result = json.loads(response['Body'].read().decode())
        return result
    except Exception as e:
        print(f"Erro ao invocar o endpoint do SageMaker: {e}")
        return None 


def ler_parametros_scaler_do_s3(symbol):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket='models-bucket-tc3', Key=f'models/{symbol}/scaler/{symbol}_scaler.pkl')
        content = response['Body'].read()
        scaler = joblib.load(io.BytesIO(content))
        if isinstance(scaler, StandardScaler):
            return scaler
        else:
            print("O objeto carregado não é um StandardScaler.")
            return None
    except Exception as e:
        print(f"Erro ao obter parâmetros do scaler do S3: {e}")
        return None
    
def process_candles(symbol, data_path, timeframe):
    
    data_path = calcular_retorno_candle(data_path)
    data_path = calcular_volatilidade_candles(data_path, timeframe)
    data_path = calcular_indicadores_tendencia(data_path, timeframe)
    data_path = calcular_indicadores_momentum(data_path, timeframe)
    data_path = calcular_indicadores_volatilidade(data_path, timeframe)
    data_path = calcular_indicadores_volume(data_path, timeframe)
    data_path = calcular_volatilidade_adp_volumes_direcional(data_path, timeframe)
    data_path = data_path.dropna()
    # Dropar colunas open_time open high low close
    data_path = data_path.drop(columns=['open_time', 'open', 'high', 'low', 'close'])
    
    target = 4 * data_path['volatilidade'].iloc[-1].round(4)
    
    last_row = data_path.iloc[-1]
    
   # Carregar o scaler do S3 e aplicar na last_row
    scaler = ler_parametros_scaler_do_s3(symbol)
    if scaler:
        last_row = last_row.astype(float)  # Certifique-se de que os dados estão no formato correto
        last_row_scaled = scaler.transform([last_row])
        result = predict(symbol, last_row_scaled)
        return target, result
    else:
        return None



def get_historical_kliness(symbol, interval, limit=300):
    try:
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        klines = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
        'taker_buy_quote_asset_volume', 'ignore'
        ])
        klines = klines[['open_time', 'open', 'high', 'low', 'close', 'volume', 'number_of_trades', 'taker_buy_base_asset_volume']]
            # Converter colunas para tipos numéricos
        klines['open'] = pd.to_numeric(klines['open'], errors='coerce')
        klines['high'] = pd.to_numeric(klines['high'], errors='coerce')
        klines['low'] = pd.to_numeric(klines['low'], errors='coerce')
        klines['close'] = pd.to_numeric(klines['close'], errors='coerce')
        klines['volume'] = pd.to_numeric(klines['volume'], errors='coerce')
        klines['number_of_trades'] = pd.to_numeric(klines['number_of_trades'], errors='coerce')
        klines['taker_buy_base_asset_volume'] = pd.to_numeric(klines['taker_buy_base_asset_volume'], errors='coerce')
        
        # Converter timestamp para data e hora
        klines['open_time'] = pd.to_datetime(klines['open_time'], unit='ms')
        
        target, result = process_candles(symbol=symbol, data_path=klines, timeframe=interval)
        
        return target, result
    except Exception as e:
        print(f"Erro ao obter dados históricos: {e}")
        return None
      
