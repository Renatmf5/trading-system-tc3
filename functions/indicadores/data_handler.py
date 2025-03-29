from stable_baselines3 import PPO
import tensorflow as tf
import pandas as pd
import io
import joblib
from functions.indicadores import *
from services.binance_client import client
import boto3
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import json
import numpy as np
import tempfile

def buscar_modelo_no_s3(symbol, model_path, modelo = 'pkl'):

    s3 = boto3.client('s3')
    try:
        # Construir a Key do modelo
        key = f'models/{symbol}/{model_path}'
        response = s3.get_object(Bucket='models-bucket-tc3', Key=key)
        content = response['Body'].read()
        
        # Verificar o tipo de modelo e carregar adequadamente
        if modelo == 'keras':
            # Criar um arquivo temporário para salvar o modelo
            with tempfile.NamedTemporaryFile(suffix='.keras') as temp_file:
                temp_file.write(content)  # Escrever o conteúdo no arquivo temporário
                temp_file.flush()  # Garantir que os dados sejam gravados
                model = tf.keras.models.load_model(temp_file.name)  # Carregar o modelo Keras
        else:
            model = joblib.load(io.BytesIO(content))  # Carregar modelo joblib
        
        print(f"Modelo carregado com sucesso: {key}")
        return model
    except Exception as e:
        print(f"Erro ao buscar o modelo no S3: {e}")
        return None

def carregar_modelo_ppo_do_s3(symbol, model_path):

    s3 = boto3.client('s3')
    try:
        # Construir a Key do modelo
        key = f'models/{symbol}/{model_path}'
        
        # Obter o objeto do S3
        response = s3.get_object(Bucket='models-bucket-tc3', Key=key)
        content = response['Body'].read()
        
        # Carregar o modelo PPO da memória
        model = PPO.load(io.BytesIO(content))
        print(f"Modelo PPO carregado com sucesso: {key}")
        return model
    except Exception as e:
        print(f"Erro ao carregar o modelo PPO do S3: {e}")
        return None

def ler_parametros_scaler_do_s3(symbol, scaler_path):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket='models-bucket-tc3', Key=f'models/{symbol}/scaler/{symbol}_{scaler_path}')
        content = response['Body'].read()
        scaler = joblib.load(io.BytesIO(content))
        
        # Verificar o tipo do scaler
        if isinstance(scaler, StandardScaler):
            print(f"Scaler carregado: StandardScaler para {symbol}")
            return scaler
        elif isinstance(scaler, MinMaxScaler):
            print(f"Scaler carregado: MinMaxScaler para {symbol}")
            return scaler
        else:
            print("O objeto carregado não é um scaler válido.")
            return None
    except Exception as e:
        print(f"Erro ao obter parâmetros do scaler do S3: {e}")
        return None
    
def process_candles(symbol, data_path, timeframe):
    
    data_path = calcular_retorno_candle(data_path)
    data_path = calcular_indicadores_xgboost(data_path, timeframe)
    data_path = calcular_indicadores_mlp(data_path, timeframe)
    data_path = calcular_indicadores_lstm(data_path, timeframe)
    data_path = calcular_volatilidade_adp_volumes_direcional(data_path, timeframe)
    data_path = detectar_proximidade_topo_fundo(data_path, timeframe)
    data_path = gerar_sinal(data_path, timeframe)
    data_path = data_path.dropna()
    # drop coluna open_time
    data_path = data_path.drop(columns=['open_time'])
    
    xgboost_scaler = ler_parametros_scaler_do_s3(symbol, 'xgboost_scaler.pkl')
    lstm_scaler = ler_parametros_scaler_do_s3(symbol, 'lstm_scaler.pkl')
    mlp_scaler = ler_parametros_scaler_do_s3(symbol, 'mlp_scaler.pkl')
    ppo_scaler = ler_parametros_scaler_do_s3(symbol, 'ppo_scaler.pkl')

    
    selected_columns_XGBoost = ['ema_20_diff','atr_14','macd_diff','macd_signal_diff', 'macd_hist','rsi_14','adx_14', 'bb_upper_diff','bb_middle_diff', 'bb_lower_diff', 'wma_14_diff', 'cci_20','stc','roc_10','mean_proportion_BTC','std_proportion_BTC','passado_1','passado_2','passado_3','proportion_taker_BTC', 'z_score_BTC' ,'proximo_topo_curto','proximo_fundo_curto','proximo_topo_medio','proximo_fundo_medio','proximo_topo_longo','proximo_fundo_longo']
    
    last_row_xgboost = data_path[selected_columns_XGBoost]
    last_row_xgboost_scaled = xgboost_scaler.transform(last_row_xgboost)
    
    selected_columns_LSTM = ['macd_diff_lstm','macd_signal_lstm','macd_hist_lstm','rsi_14', 'willr_14','donchian_lower','donchian_mid', 'donchian_high','donchuan_lower_diff', 'donchian_mid_diff', 'aroon_up','aroon_down','chop','fisher','zscore','mean_proportion_BTC','std_proportion_BTC','passado_1','passado_2','passado_3','proportion_taker_BTC', 'z_score_BTC',  'proximo_topo_curto','proximo_fundo_curto','proximo_topo_medio','proximo_fundo_medio','proximo_topo_longo','proximo_fundo_longo']
    
    last_row_lstm = data_path[selected_columns_LSTM]    
    last_row_lstm_scaled = lstm_scaler.transform(last_row_lstm)
        
        
    selected_columns_MLP = ['sma_5_diff','sma_20_diff','sma_50_diff', 'stoch_k','stoch_d','vwap_diff', 'mfi','tsi_stoch','dmi_plus','dmi_minus','adx','psar','cmo','obv','kc_upper','kc_mid','kc_lower','kc_upper_diff','kc_mid_diff','mean_proportion_BTC','std_proportion_BTC','passado_1','passado_2','passado_3','proportion_taker_BTC', 'z_score_BTC','proximo_topo_curto','proximo_fundo_curto','proximo_topo_medio','proximo_fundo_medio','proximo_topo_longo','proximo_fundo_longo']
    
    last_row_mlp = data_path[selected_columns_MLP]
    last_row_mlp_scaled = mlp_scaler.transform(last_row_mlp)
    
     # Adicionar as colunas de probabilidades e preços ao input do PPO
    selected_columns_RL_PPO = [
        'sma_5_diff', 'sma_20_diff', 'sma_50_diff', 'ema_20_diff', 
        'mean_proportion_BTC', 'std_proportion_BTC', 'proportion_taker_BTC', 
        'z_score_BTC', 'cci_20', 'stc', 'roc_10', 'cmo', 'obv', 
        'mfi', 'tsi_stoch', 'dmi_plus', 'dmi_minus', 'adx']
    last_row_ppo = data_path[selected_columns_RL_PPO]
    last_row_ppo_scaled = ppo_scaler.transform(last_row_ppo)
    
    data_low_high_close = data_path[['low','high','close']].reset_index(drop=True)
    return last_row_xgboost_scaled, last_row_lstm_scaled, last_row_mlp_scaled, data_low_high_close, last_row_ppo_scaled
    '''
   # Carregar o scaler do S3 e aplicar na last_row
    scaler = ler_parametros_scaler_do_s3(symbol)
    if scaler:
        last_row = last_row.astype(float)  # Certifique-se de que os dados estão no formato correto
        last_row_scaled = scaler.transform([last_row])
        result = predict(symbol, last_row_scaled)
        return target, result
    else:
        return None
    '''


def get_historical_kliness(symbol, interval, limit=760):
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
        
        last_row_xgboost_scaled, last_row_lstm_scaled, last_row_mlp_scaled, data_low_high_close, last_row_ppo_scaled = process_candles(symbol=symbol, data_path=klines, timeframe=interval)
        action = preparar_dados_chama_models(last_row_xgboost_scaled, last_row_lstm_scaled, last_row_mlp_scaled, data_low_high_close, last_row_ppo_scaled)
        
        return action
    except Exception as e:
        print(f"Erro ao obter dados históricos: {e}")
        return None
      

def preparar_dados_chama_models(data_path_xgb,data_path_lstm,data_path_mlp, data_low_high_close, data_path_ppo, alpha=1.0):
    # Garantir que o DataFrame tenha pelo menos 29 registros para o LSTM
    ensemble_scaler = ler_parametros_scaler_do_s3('BTCUSDT', 'ensemble_scaler.pkl')
    
    if len(data_path_lstm) < 29:
        raise ValueError("O DataFrame precisa ter pelo menos 29 registros para o LSTM.")
    
    data_path_lstm = pd.DataFrame(data_path_lstm)
    data_path_xgb = pd.DataFrame(data_path_xgb)
    data_path_mlp = pd.DataFrame(data_path_mlp)
    data_path_ppo = pd.DataFrame(data_path_ppo)
    #cortar o dataframe e manter apenas as ultimas 30 linhas
    data_path_lstm = data_path_lstm[-30:]
    data_path_xgb = data_path_xgb[-30:]
    data_path_mlp = data_path_mlp[-30:]
    data_low_high_close = data_low_high_close[-15:]
    data_path_ppo = data_path_ppo[-15:]
    # Renomear colunas do data Path ppo
    data_path_ppo.columns = ['sma_5_diff', 'sma_20_diff', 'sma_50_diff', 'ema_20_diff', 
        'mean_proportion_BTC', 'std_proportion_BTC', 'proportion_taker_BTC', 
        'z_score_BTC', 'cci_20', 'stc', 'roc_10', 'cmo', 'obv', 
        'mfi', 'tsi_stoch', 'dmi_plus', 'dmi_minus', 'adx']
    
    
    # Lista para armazenar as previsões
    lstm_preds = []
    mlp_preds = []
    xgboost_preds = []
    
    lstm_model = buscar_modelo_no_s3('BTCUSDT', 'lstm/lstm_classification_model.keras','keras')
    mlp_model = buscar_modelo_no_s3('BTCUSDT', 'mlp/mlp_classification_model.pkl')
    xgboost_model = buscar_modelo_no_s3('BTCUSDT', 'xgboost/xgboost_regressor_model.pkl')
    ensemble_model = buscar_modelo_no_s3('BTCUSDT', 'ensemble/ensemble_model.keras', 'keras')
    rl_ppo_model = carregar_modelo_ppo_do_s3('BTCUSDT', 'rl_ppo/ppo_trading_model.zip')
    
    # Gerar 15 previsões consecutivas
    for i in range(15):
        # Selecionar as últimas 15 linhas para o LSTM
        lstm_input = data_path_lstm.iloc[i:i+15]
        lstm_input = np.expand_dims(lstm_input.to_numpy(), axis=0)  # Agora o formato será (1, 15, 28)
        lstm_pred = lstm_model.predict(lstm_input)
        
        
        # Selecionar a última linha para o MLP e XGBoost
        last_row_mlp = data_path_mlp.iloc[[i+14]]
        last_row_xgb = data_path_xgb.iloc[[i+14]]
        
        mlp_pred = mlp_model.predict_proba(last_row_mlp)
        mlp_probabilities = mlp_pred[:, 1]
        
        xgboost_pred = xgboost_model.predict(last_row_xgb)
        probabilities_xgboost = 1 / (1 + np.exp(-alpha * xgboost_pred))
        
        lstm_preds.append(np.squeeze(lstm_pred))
        mlp_preds.append(mlp_probabilities)
        xgboost_preds.append(probabilities_xgboost)
    
    # Combinar as previsões para o ensemble
    meta_x_predict = np.column_stack((lstm_preds, xgboost_preds,mlp_preds))
    
    meta_x_predict = ensemble_scaler.transform(meta_x_predict)
    
    ensemble_preds = ensemble_model.predict(meta_x_predict)
    
    # pegar valor de close do ultimo candle
    close = data_low_high_close.iloc[-1]['close']
    
        
    # Combinar as previsões com as colunas do DataFrame original
    ppo_input = pd.DataFrame(meta_x_predict, columns=['pred_lstm_proba', 'pred_xgb_proba', 'pred_mlp_proba'])
    ppo_input['ensemble_signal'] = ensemble_preds
    # Adicionar colunas do data_path_ppo ao ppo_input
    ppo_input = pd.concat([ppo_input, data_path_ppo.reset_index(drop=True)], axis=1)
    
    # Definir as colunas esperadas e a ordem correta
    required_columns = [
        'sma_5_diff', 'sma_20_diff', 'sma_50_diff', 'ema_20_diff', 
        'mean_proportion_BTC', 'std_proportion_BTC', 'proportion_taker_BTC', 
        'z_score_BTC', 'cci_20', 'stc', 'roc_10', 'cmo', 'obv', 
        'mfi', 'tsi_stoch', 'dmi_plus', 'dmi_minus', 'adx', 
        'pred_lstm_proba', 'pred_xgb_proba', 'pred_mlp_proba', 
        'ensemble_signal'
    ]

    # Garantir que o ppo_input contenha somente as colunas esperadas e na ordem correta
    ppo_input = ppo_input[required_columns]
    
    action, _states = rl_ppo_model.predict(ppo_input, deterministic=True)
    
    print(action)
    
    return action, close