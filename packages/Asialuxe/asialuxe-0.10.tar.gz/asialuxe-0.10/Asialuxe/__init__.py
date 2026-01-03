import json
import requests

class Asialuxe():

    def __init__(self):
        self.url = "https://b2b.asialuxe.uz"
        self.api_url = "https://api.asialuxe.app"
        self.headers = {}
        self.headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        self.headers['Content-Type'] = ""

        self.UAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
        self.req = requests.Session()
        self.req.headers.update({'User-Agent': self.UAgent})
        self.req.get(url=f"{self.url}/login", headers = self.headers, timeout = 15)
        self.token = ""

    def login(self, email, password):
        payload = {
            "phone_or_email": email,
            "password": password
        }
        self.headers['Accept'] = "application/json, text/plain, */*"
        self.headers['Content-Type'] = "application/json"

        response = self.req.post(url=f"{self.api_url}/v1/user/b2b-sign-in", headers = self.headers, json = payload, timeout = 15)

        if isinstance(response.json(), dict):
            response_json = response.json()
            if response_json.get("message") == "success":
                self.token = response_json.get("data", {}).get("token", "")
                self.req.headers.update({'Authorization': f"Bearer {self.token}"})
                return response_json

        return {"status": "error", "status_code": response.status_code, "headers": response.headers, "response": response.text}

    def userDetail(self, timeout_limit=1200):
        response_json = {}
        self.headers['Accept'] = "application/json, text/plain, */*"
        self.headers['Content-Type'] = "application/json"
        response = self.req.get(url=f"{self.api_url}/v1/user/get-me?include=userDetail", headers = self.headers, timeout = timeout_limit)
        if response.status_code in [200, 201]:
            if isinstance(response.json(), dict):
                response_json = response.json()
        return response_json

    def searchTickets(self, ROUTES = [], ADT = 1, CHD = 0, INF = 0, INS = 0, service_class = "E", charter = True, currency = "", timeout_limit=1200):
        payload = {
            "onlyCharter": 1 if charter else 0,
            "product_id": 1,
            "adult_qnt": ADT,
            "child_qnt": CHD,
            "infant_qnt": INF,
            "class": service_class,
            "currency": currency,
            "in_one_days": 0,
            "charter_three_days": 0,
            "only_baggage": 0,
            "sorting_price": 1,
            "directions": ROUTES
        }
        response_json = {}
        self.headers['Accept'] = "application/json, text/plain, */*"
        self.headers['Content-Type'] = "application/json"
        response = self.req.post(url=f"{self.api_url}/v1/tickets/search?platform=web_b2b", headers = self.headers, json = payload, timeout = timeout_limit)
        if response.status_code in [200, 201]:
            if isinstance(response.json(), dict):
                response_json = response.json()
        return response_json


    def getOffers(self, request_json):
        if (request_json.get('message') == "ok"):
            request_id = request_json.get('data', {}).get("request_id", "")
            timeout_limit = request_json.get('data', {}).get("limit", 60)
            if request_id:
                params = {
                    "request_id": request_id,
                    "pagination": "true",
                    "platform": "web_b2b",
                    "sort": "price",
                    "only_baggage": "0",
                    "page": "1"
                }
                self.headers['Accept'] = "application/json, text/plain, */*"
                self.headers['Content-Type'] = "application/json"
                response = self.req.get(url=f"{self.api_url}/v1/tickets/get-offers", headers = self.headers, params = params, timeout = timeout_limit)
                if response.status_code in [200, 201]:
                    if isinstance(response.json(), dict):
                        response_json = response.json()
                        return response_json

        return {"status": "error", "status_code": response.status_code, "headers": response.headers, "response": response.text}
    
    
    def checkFlight(self, request_json, timeout_limit=1200):
        payload = request_json
        self.headers['Accept'] = "application/json, text/plain, */*"
        self.headers['Content-Type'] = "application/json"
        response = self.req.post(url=f"{self.api_url}/v1/flight/check", headers = self.headers, json = payload, timeout = timeout_limit)
        if response.status_code in [200, 201]:
            if isinstance(response.json(), dict):
                response_json = response.json()
                return response_json
        return {"status": "error", "status_code": response.status_code, "headers": response.headers, "response": response.text}
    
    
    def bookFlight(self, request_json, timeout_limit=1200):
        payload = request_json
        self.headers['Accept'] = "application/json, text/plain, */*"
        self.headers['Content-Type'] = "application/json"
        response = self.req.post(url=f"{self.api_url}/v1/flight/book?platform=web_b2b", headers = self.headers, json = payload, timeout = timeout_limit)
        if response.status_code in [200, 201]:
            if isinstance(response.json(), dict):
                response_json = response.json()
                return response_json
        return {"status": "error", "status_code": response.status_code, "headers": response.headers, "response": response.text}
    
    
    def cancelFlight(self, request_json, timeout_limit=1200): 
        params = request_json
        self.headers['Accept'] = "application/json, text/plain, */*"
        self.headers['Content-Type'] = "application/json"
        response = self.req.get(url=f"{self.api_url}/v1/flight/cancel/{params}", headers = self.headers, timeout = timeout_limit)
        if response.status_code in [200, 201]:
            if isinstance(response.json(), dict):
                response_json = response.json()
                return response_json
        return {"status": "error", "status_code": response.status_code, "headers": response.headers, "response": response.text}

    def supportTicket(self, request_json, timeout_limit=1200): 
        payload = request_json
        self.headers['Accept'] = "application/json, text/plain, */*"
        self.headers['Content-Type'] = "application/json"
        response = self.req.post(url=f"{self.api_url}/v1/support/ticket-open", headers = self.headers, json = payload, timeout = timeout_limit)
        if response.status_code in [200, 201]:
            if isinstance(response.json(), dict):
                response_json = response.json()
                return response_json
        return {"status": "error", "status_code": response.status_code, "headers": response.headers, "response": response.text}

    
    def orderFlight(self, request_json, timeout_limit=1200): 
        order_id = request_json.get("order_id", "")
        params = {
            "include": "passengers.books.flight,directions,passengers.books,passengers"
        }
        self.headers['Accept'] = "application/json, text/plain, */*"
        self.headers['Content-Type'] = "application/json"
        response = self.req.get(url=f"{self.api_url}/v1/flight/order/{order_id}", headers = self.headers, params = params, timeout = timeout_limit)
        if response.status_code in [200, 201]:
            if isinstance(response.json(), dict):
                response_json = response.json()
                return response_json
        return {"status": "error", "status_code": response.status_code, "headers": response.headers, "response": response.text}