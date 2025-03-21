import pandas as pd
import numpy as np

def calcular_retorno_candle(df):
    df['retorno_candle'] = df['close'].pct_change().round(2)
    return df


def gerar_sinal(df, timeframe):
    # criar condição de valor de alvo_base com base no timeframe
    if timeframe == '15m':
        alvo_base = 3
    
    passado_1 = []
    passado_2 = []
    passado_3 = []
    
    for i in range(len(df)):
        # Calcular os retornos passados fixos para 5, 10 e 15 candles
        if i - 5 >= 0:
            passado_1.append((df['close'].iloc[i] / df['close'].iloc[i - 5]) - 1)
        else:
            passado_1.append(np.nan)
        
        if i - 10 >= 0:
            passado_2.append((df['close'].iloc[i] / df['close'].iloc[i - 10]) - 1)
        else:
            passado_2.append(np.nan)
        
        if i - 15 >= 0:
            passado_3.append((df['close'].iloc[i] / df['close'].iloc[i - 15]) - 1)
        else:
            passado_3.append(np.nan)
    
    df['passado_1'] = passado_1
    df['passado_2'] = passado_2
    df['passado_3'] = passado_3
    
    # Dropar linhas com valores NaN
    df = df.dropna()
    
    return df

# Exemplo de uso
# df = pd.read_csv('seu_arquivo.csv')
# df = gerar_sinal(df, '15m')
# print(df.head())

def calcular_volatilidade_adp_volumes_direcional(df, timeframe):
    # Calcular a volatilidade adaptada para volumes em BTC e USDT
    if timeframe == '15m':
        df['mean_volume'] = df['volume'].rolling(window=96).mean()
        df['std_volume'] = df['volume'].rolling(window=96).std()
        df['proportion_taker_BTC'] = df['taker_buy_base_asset_volume'] / df['volume']
        df['mean_proportion_BTC'] = df['proportion_taker_BTC'].rolling(window=192).mean()
        df['std_proportion_BTC'] = df['proportion_taker_BTC'].rolling(window=192).std()
        df['volatilidade'] = df['close'].pct_change().rolling(window=720).std()
        
    # Calcular o z-score (desvio em relação à média) para identificar desvios significativos
    df['z_score_BTC'] = (df['proportion_taker_BTC'] - df['mean_proportion_BTC']) / df['std_proportion_BTC']
    
     # Calcular a média móvel exponencial do volume
    df['ema_volume'] = df['volume'].ewm(span=20, adjust=False).mean()
    
    # Calcular a média móvel exponencial da volatilidade
    df['ema_volatilidade'] = df['volatilidade'].ewm(span=20, adjust=False).mean()
       
    # Ao final tornar a coluna index devolta para um id sequencial
    df = df.reset_index(drop=True)
    return df

def detectar_proximidade_topo_fundo(df, timeframe):
    if timeframe == '15m':
        curto = 96
        medio = 192
        longo = 672
        margem = 0.003
    
    # Detectar proximidade de topo curto
    df['proximo_topo_curto'] = ((df['close'] < df['high'].rolling(window=curto).max()) & 
                                (abs(df['close'] - df['high'].rolling(window=curto).max()) / df['high'].rolling(window=curto).max() <= margem)).astype(int)
    
    # Detectar proximidade de fundo curto
    df['proximo_fundo_curto'] = ((df['close'] > df['low'].rolling(window=curto).min()) & 
                                 (abs(df['close'] - df['low'].rolling(window=curto).min()) / df['low'].rolling(window=curto).min() <= margem)).astype(int)
    
    # Detectar proximidade de topo médio
    df['proximo_topo_medio'] = ((df['close'] < df['high'].rolling(window=medio).max()) & 
                                (abs(df['close'] - df['high'].rolling(window=medio).max()) / df['high'].rolling(window=medio).max() <= margem)).astype(int)
    
    # Detectar proximidade de fundo médio
    df['proximo_fundo_medio'] = ((df['close'] > df['low'].rolling(window=medio).min()) & 
                                 (abs(df['close'] - df['low'].rolling(window=medio).min()) / df['low'].rolling(window=medio).min() <= margem)).astype(int)
    
    # Detectar proximidade de topo longo
    df['proximo_topo_longo'] = ((df['close'] < df['high'].rolling(window=longo).max()) & 
                                (abs(df['close'] - df['high'].rolling(window=longo).max()) / df['high'].rolling(window=longo).max() <= margem)).astype(int)
    
    # Detectar proximidade de fundo longo
    df['proximo_fundo_longo'] = ((df['close'] > df['low'].rolling(window=longo).min()) & 
                                 (abs(df['close'] - df['low'].rolling(window=longo).min()) / df['low'].rolling(window=longo).min() <= margem)).astype(int)
    
    return df