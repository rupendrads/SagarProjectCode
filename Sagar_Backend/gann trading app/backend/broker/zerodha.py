import requests
import pyotp
from jugaad_trader import Zerodha
# class Zerodha:
#     def __init__(self):
#         self.base_url = "https://api.kite.trade"
#         self.session = requests.Session()
#         self.user_id = None
#         self.password = None
#         self.twofa = None
#         self.enc_token = None

#     def login_step1(self):
#         data = {
#             "user_id": self.user_id,
#             "password": self.password
#         }
#         response = self.session.post(f"{self.base_url}/login", data=data)
#         json_res = response.json()
#         return json_res
    
#     def login_step2(self, json_res):
#         data = {
#             "user_id": self.user_id,
#             "request_id": json_res["request_id"],
#             "twofa_value": self.twofa
#         }
#         response = self.session.post(f"{self.base_url}/login", data=data)
#         json_res_1 = response.json()
#         return json_res_1

def zerodha_login(creds):
    kite = Zerodha()
    kite.user_id=creds['user_id']
    kite.password = creds['password']
    json_res = kite.login_step1()
    print(creds['totp_key'])
    twofa = pyotp.TOTP(creds['totp_key']).now()
    kite.twofa=twofa
    json_res_1 = kite.login_step2(json_res)
    kite.enc_token = kite.r.cookies['enctoken']
    return kite