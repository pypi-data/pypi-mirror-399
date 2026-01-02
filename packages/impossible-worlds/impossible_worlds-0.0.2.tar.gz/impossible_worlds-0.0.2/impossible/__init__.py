import requests
import json
import base64  # <--- یہ لائن لازمی ہے

class UfoneManager:
    def __init__(self):
        # ---------------------------------------------------------
        # 👇 یہاں ہم نے لنک کو چھپا دیا ہے (Base64 Encoded)
        # ---------------------------------------------------------
        self._s = "aHR0cHM6Ly91Zm9uZS1pbmRvbC52ZXJjZWwuYXBwL2FwaQ=="
        
        # اب کوڈ خود اسے ڈی کوڈ کر کے اصلی لنک بنائے گا
        self.base_url = base64.b64decode(self._s).decode('utf-8')
        
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    # باقی سارا کوڈ ویسا ہی رہے گا...
    def gen_otp(self, phone, user_id):
        try:
            url = f"{self.base_url}/gen" # <--- یہ خود بخود ڈیکوڈڈ لنک استعمال کرے گا
            params = {"phone": phone, "id": str(user_id)}
            resp = requests.get(url, params=params, headers=self.headers)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    # ... (باقی سارے فنکشنز سیم رہیں گے) ...
    # ... verify_otp, check_daily, check_spin, claim_reward ...
    
    # Verify OTP
    def verify_otp(self, phone, otp, user_id):
        try:
            url = f"{self.base_url}/verfy"
            params = {"phone": phone, "otp": otp, "id": str(user_id)}
            resp = requests.get(url, params=params, headers=self.headers)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def check_daily(self, phone, user_id, token, sub_token):
        return self._send_post("daily", phone, user_id, token, sub_token)

    def check_spin(self, phone, user_id, token, sub_token):
        return self._send_post("spin", phone, user_id, token, sub_token)

    def claim_reward(self, phone, user_id, token, sub_token, value, ap_id="", day="", day_identifier=""):
        try:
            url = f"{self.base_url}/claimreal"
            payload = {
                "phone": phone, "deviceId": str(user_id),
                "token": token, "subToken": sub_token,
                "value": value, "apId": ap_id,
                "day": day, "dayIdentifier": day_identifier 
            }
            resp = requests.post(url, json=payload, headers=self.headers)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def _send_post(self, endpoint, phone, user_id, token, sub_token):
        try:
            url = f"{self.base_url}/{endpoint}"
            payload = {
                "phone": phone, "deviceId": str(user_id),
                "token": token, "subToken": sub_token
            }
            resp = requests.post(url, json=payload, headers=self.headers)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

ufone = UfoneManager()