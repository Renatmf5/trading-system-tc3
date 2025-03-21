import pandas_ta as ta
import pandas as pd

def calcular_indicadores_xgboost(df, timeframe):
    if timeframe == '15m':
        df['ema_20_diff'] = ta.ema(df['close'], length=20) - df['close']
        df['atr_14'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        macd = ta.macd(df['close'])
        df['macd_diff'] = macd['MACD_12_26_9']
        df['macd_signal_diff'] = macd['MACDs_12_26_9']
        df['macd_hist'] = macd['MACDh_12_26_9']
        df['rsi_14'] = ta.rsi(df['close'], length=14)
        df['adx_14'] = ta.adx(df['high'], df['low'], df['close'], length=14)['ADX_14']
        bbands = ta.bbands(df['close'])
        df['bb_upper_diff'] = bbands['BBU_5_2.0'] - df['close']
        df['bb_middle_diff'] = bbands['BBM_5_2.0'] - df['close']
        df['bb_lower_diff'] = bbands['BBL_5_2.0'] - df['close']
        df['wma_14_diff'] = ta.wma(df['close'], length=14) - df['close']
        df['cci_20'] = ta.cci(df['high'], df['low'], df['close'], length=20)
        stc = ta.stc(df['close'])
        df['stc'] = stc['STC_10_12_26_0.5']
        df['roc_10'] = ta.roc(df['close'], length=10)
    return df

def calcular_indicadores_mlp(df, timeframe):
    if timeframe == '15m':
        df['sma_5_diff'] = ta.sma(df['close'], length=5) - df['close']
        df['sma_20_diff'] = ta.sma(df['close'], length=20) - df['close']
        df['sma_50_diff'] = ta.sma(df['close'], length=50) - df['close']
        stoch = ta.stoch(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch['STOCHk_14_3_3']
        df['stoch_d'] = stoch['STOCHd_14_3_3']
        # Garantir que o índice seja um índice de data/hora
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            df.index = pd.to_datetime(df.index)
            
        df['vwap_diff'] = ta.vwap(df['high'], df['low'], df['close'], df['volume']) - df['close']
        df['mfi'] = ta.mfi(df['high'], df['low'], df['close'], df['volume']).astype('float64')
        tsi = ta.tsi(df['close'])
        df['tsi_stoch'] = tsi['TSIs_13_25_13']
        adx = ta.adx(df['high'], df['low'], df['close'])
        df['dmi_plus'] = adx['DMP_14']
        df['dmi_minus'] = adx['DMN_14']
        df['adx'] = adx['ADX_14']
        df['psar'] = ta.psar(df['high'], df['low'], df['close'], af=0.03, max_af=0.2)['PSARl_0.03_0.2']
        df['psar'] = df['psar'].fillna(method='ffill')
        df['cmo'] = ta.cmo(df['close'])
        df['obv'] = ta.obv(df['close'], df['volume'])
        kc = ta.kc(df['high'], df['low'], df['close'])
        df['kc_upper'] = kc['KCLe_20_2'] - df['close']
        df['kc_mid'] = kc['KCBe_20_2'] - df['close']
        df['kc_lower'] = kc['KCUe_20_2'] - df['close']
        df['kc_upper_diff'] = kc['KCLe_20_2'] - kc['KCUe_20_2']
        df['kc_mid_diff'] = kc['KCLe_20_2'] - kc['KCBe_20_2']
    return df

def calcular_indicadores_lstm(df, timeframe):
    if timeframe == '15m':
        macd = ta.macd(df['close'])
        df['macd_diff_lstm'] = macd['MACD_12_26_9']
        df['macd_signal_lstm'] = macd['MACDs_12_26_9']
        df['macd_hist_lstm'] = macd['MACDh_12_26_9']
        df['rsi_14'] = ta.rsi(df['close'], length=14)
        df['willr_14'] = ta.willr(df['high'], df['low'], df['close'], length=14)
        donchian = ta.donchian(high=df['high'], low=df['low'], close=df['close'], length=20)
        df['donchian_lower'] = donchian['DCL_20_20'] - df['close']
        df['donchian_mid'] = donchian['DCM_20_20'] - df['close']
        df['donchian_high'] = donchian['DCU_20_20'] - df['close']
        df['donchuan_lower_diff'] = donchian['DCL_20_20'] - donchian['DCU_20_20']
        df['donchian_mid_diff'] = donchian['DCM_20_20'] - donchian['DCU_20_20']
        aroon = ta.aroon(df['high'], df['low'], length=14)
        df['aroon_up'] = aroon['AROONU_14']
        df['aroon_down'] = aroon['AROOND_14']
        df['chop'] = ta.chop(df['high'], df['low'], df['close'])
        df['supertrend'] = ta.supertrend(df['high'], df['low'], df['close'])['SUPERT_7_3.0']
        fisher = ta.fisher(df['high'], df['low'])
        df['fisher'] = fisher['FISHERT_9_1']
        df['zscore'] = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()

    return df

