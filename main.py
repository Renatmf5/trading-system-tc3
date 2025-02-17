import json
import threading
import time
import requests
import os
from functions.indicadores.data_handler import get_historical_kliness
from websocket import WebSocketApp


def on_message(ws, message):
    #global last_order_price, last_order_side
        # Verificar a variável de ambiente para determinar a URL do endpoint
    environment = os.getenv('ENV', 'development')
    if environment == 'production':
        api_url = 'http://localhost:80/api/v1'
        print("Ambiente de produção")
    else:
        api_url = 'http://localhost:80/api/v1'
        print("Ambiente de dev")
    data = json.loads(message)
    
    if 'k' in data:
        candle = data['k']
        is_candle_closed = candle['x']        
        
        if is_candle_closed:
            print('Nova vela de 1 hora fechada:')
            time.sleep(1.5)
            # Fazer a chamada ao endpoint da FastAPI
            target, result = get_historical_kliness("BTCUSDT", "1h")
            
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
            """
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
    websocket_url = "wss://fstream.binance.com/ws/btcusdt@kline_1h"
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
        print("Script interrompido pelo usuárioo")