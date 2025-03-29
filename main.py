import json
import threading
import time
import requests
import os
import numpy as np
from functions.indicadores.data_handler import get_historical_kliness
from websocket import WebSocketApp


def on_message(ws, message):
    #global last_order_price, last_order_side
        # Verificar a variável de ambiente para determinar a URL do endpoint
    environment = os.getenv('ENV', 'development')
    if environment != 'development':
        api_url = 'https://api.grupo-ever-rmf.com/api/v1'

    else:
        # URL da API em ambiente de desenvolvimento
        api_url =  'http://localhost:8000/api/v1'
        #api_url = 'https://api.grupo-ever-rmf.com/api/v1'

    data = json.loads(message)
    
    if 'k' in data:
        candle = data['k']
        is_candle_closed = candle['x']        
        
        if is_candle_closed:
            print('Nova vela de 15 minutos fechada:')
            time.sleep(1.5)
            # Fazer a chamada ao endpoint da FastAPI
            action, close = get_historical_kliness("BTCUSDT", "15m")
            
            payload = {
            "action": str(action.tolist() if isinstance(action, np.ndarray) else action),
            "close": close.tolist() if isinstance(close, np.ndarray) else close
            }
            
            try:
                # Fazer a chamada POST para a API
                response = requests.post(f"{api_url}/manageTrading/SendTrade", json=payload)
                
                # Verificar a resposta da API
                if response.status_code == 200:
                    response_data = response.json()
                    print({response_data.get('message')})
                else:
                    print(f"Erro ao enviar dados para a API: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Erro ao chamar a API: {e}")
            """
            try:
                response = requests.get(f"{api_url}/manageOrders/getOpenPositions", params={"symbol": "BTCUSDT"})
                if response.status_code == 200:
                    print("Chamada ao endpoint da FastAPI bem-sucedida.")
                    if not response.json():
                        open_order = requests.get(f"{api_url}/manageOrders/OpenPosition", params={"symbol": "BTCUSDT", "prediction": result, "target": target})
                else:
                    print(f"Erro ao chamar o endpoint da FastAPI: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Erro ao chamar o endpoint da FastAPI: {e}")
            
            #open_orders = get_open_positions("BTCUSDT")
            if not open_orders:
                if historical_klines.iloc[-1]['open_time'] != candle['t']:
                    historical_klines = historical_klines[:-1]  # Remove o último registro do DataFrame
                process_candles(historical_klines)
            """
            
            
def on_error(ws, error):
    print(f"Erro: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Conexão fechada com código {close_status_code} e mensagem: {close_msg}")
    print("Tentando reconectar em 5 segundos...")
    time.sleep(5)
    connect_websocket()

def on_open(ws):
    print("Conexão estabelecida")

def connect_websocket():
    websocket_url = "wss://fstream.binance.com/ws/btcusdt@kline_15m"
    ws = WebSocketApp(websocket_url,
                      on_open=on_open,
                      on_message=on_message,
                      on_error=on_error,
                      on_close=on_close)
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

if __name__ == "__main__":
    connect_websocket()
    try:
        while True:
            time.sleep(1)  # Mantenha o script em execução
    except KeyboardInterrupt:
        print("Script interrompido pelo usuário")