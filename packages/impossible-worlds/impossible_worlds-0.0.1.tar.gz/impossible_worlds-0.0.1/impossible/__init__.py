import requests
import json

class UfoneManager:
    def __init__(self):
        self.base_url = "https://ufone-indol.vercel.app/api"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def gen_otp(self, phone, user_id):
        try:
            url = f"{self.base_url}/gen"
            params = {"phone": phone, "id": str(user_id)}
            resp = requests.get(url, params=params, headers=self.headers)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

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
