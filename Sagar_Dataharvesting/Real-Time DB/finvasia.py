import time
from api_helper import ShoonyaApiPy, get_time
from pyotp import TOTP 

def on_ticks(ws, ticks):
    # This function will be called whenever live data is received
    print("Ticks: ", ticks)

def on_connect(ws, response):
    # This function will be called once WebSocket is connected
    # You can subscribe to instruments here
    ws.subscribe('NSE', 'RELIANCE-EQ')

def on_close(ws, code, reason):
    # This function will be called when the WebSocket closes
    print(f"WebSocket closed: {code}, {reason}")

def fetch_live_data_websocket():
    api = ShoonyaApiPy()

    # Replace these with your credentials
    userid = 'FA132927'
    password = 'Pegasus@12'
    twoFA = '3I35ZWDLE42X76567WK27H4724LOPB72'
    vendor_code = 'FA132927_U'
    api_secret = '3d0352bb078243b341db9dc52c084d0e'
    imei = 'abc1234'

    try:
        # Login to the API
        twoFA = TOTP(twoFA).now()
        print(twoFA)
        response = api.login(userid=userid, 
                  password=password, 
                  twoFA=twoFA, 
                  vendor_code=vendor_code, 
                  api_secret=api_secret, 
                  imei=imei)
        print(response)
        # Set WebSocket event handlers
        api.set_on_ticks(on_ticks)
        api.set_on_connect(on_connect)
        api.set_on_close(on_close)

        # # Connect to WebSocket
        api.connect_ws()

        # # Keep the WebSocket connection alive
        # while True:
            # time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping the WebSocket connection...")

    finally:
        # Logout from the API
        # api.logout()
        pass

if __name__ == "__main__":
    fetch_live_data_websocket()
