import pandas as pd
import numpy as np

def calcular_retorno_candle(df):
    df['retorno_candle'] = df['close'].pct_change().round(2)
    return df


def calcular_volatilidade_adp_volumes_direcional(df, timeframe):
    # Calcular a volatilidade adaptada para volumes em BTC e USDT
    if timeframe == '1d':
        df['mean_volume'] = df['volume'].rolling(window=7).mean()
        df['std_volume'] = df['volume'].rolling(window=7).std()
        # Criar a proporção entre 'taker_buy_base_asset_volume' (BTC) e volume total (BTC)
        df['proportion_taker_BTC'] = df['taker_buy_base_asset_volume'] / df['volume']
        # Calcular a média histórica da proporção BTC e USDT
        df['mean_proportion_BTC'] = df['proportion_taker_BTC'].rolling(window=14).mean()
        # Calcular o desvio padrão histórico das proporções
        df['std_proportion_BTC'] = df['proportion_taker_BTC'].rolling(window=14).std()
        df['volatilidade'] = df['close'].pct_change().rolling(window=30).std()

    if timeframe == '4h':
        df['mean_volume'] = df['volume'].rolling(window=14).mean()
        df['std_volume'] = df['volume'].rolling(window=14).std()
        df['proportion_taker_BTC'] = df['taker_buy_base_asset_volume'] / df['volume']
        df['mean_proportion_BTC'] = df['proportion_taker_BTC'].rolling(window=28).mean()
        df['std_proportion_BTC'] = df['proportion_taker_BTC'].rolling(window=28).std()
        df['volatilidade'] = df['close'].pct_change().rolling(window=42).std()
        
    if timeframe == '1h':
        df['mean_volume'] = df['volume'].rolling(window=24).mean()
        df['std_volume'] = df['volume'].rolling(window=24).std()
        df['proportion_taker_BTC'] = df['taker_buy_base_asset_volume'] / df['volume']
        df['mean_proportion_BTC'] = df['proportion_taker_BTC'].rolling(window=48).mean()
        df['std_proportion_BTC'] = df['proportion_taker_BTC'].rolling(window=48).std()
        df['volatilidade'] = df['close'].pct_change().rolling(window=180).std()
        
    # Calcular o z-score (desvio em relação à média) para identificar desvios significativos
    df['z_score_BTC'] = (df['proportion_taker_BTC'] - df['mean_proportion_BTC']) / df['std_proportion_BTC']
    
    # Ao final tornar a coluna index devolta para um id sequencial
    df = df.reset_index(drop=True)
    return df
