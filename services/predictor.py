import os
import requests
import json
import re
from helpers.res import response,emiResponse
from dotenv import load_dotenv

load_dotenv()


class Predictor:
    # Singleton class
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Predictor, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.token_url = "https://iam.cloud.ibm.com/identity/token"
        self.scoring_url = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/8c6d6928-bb3f-404b-ae28-77fb005d5c87/predictions?version=2021-05-01"
        self.model_url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"
        self.token = ""

    def get_token(self):
        print(self.api_key, "*******************")
        token_response = requests.post(self.token_url, data={
                                       "apikey": self.api_key, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        self.token = token_response.json()["access_token"]

    def predict(self, inputs):
        self.get_token()
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + self.token}
        payload_scoring = {"input_data": [{"fields": ["no_of_dependents", "education", "self_employed",
                                                      "income_anum", "loan_ammount", "loan_term", "cibil_score", "bank_asset_value"], "values": [inputs]}]}
        response_scoring = requests.post(
            self.scoring_url, json=payload_scoring, headers=headers)
        predictions = response_scoring.json()

        return predictions["predictions"][0]["values"][0][0]

    def extract_info(self, text, question):
        self.get_token()
        payload = json.dumps({
            "model_id": "google/flan-ul2",
            "input": "Answer the following question using only information from the article. Article: ###"+text+".### \\n\\nQuestion:\\n" + question+"",
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 100,
                "min_new_tokens": 0,
                "stop_sequences": [],
                "repetition_penalty": 2
            },
            "project_id": "b8fd838c-df56-4a3b-beaf-d68ff9965a48"
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+self.token
        }
        response = requests.request(
            "POST", self.model_url, headers=headers, data=payload)
        print(response)
        summary = response.json()
        print(summary)
        return summary["results"][0]["generated_text"]

    def get_data_from_llm(self, text):
        try:
            income = self.extract_info(text, "what is salary of this month?")
            input = re.sub(",", '', income)
            ans = re.findall(r"\d+\.\d+", input)
            income = int(float(ans[0]))
            anual_income = income * 12
            bank_asset = self.extract_info(
                text, "what is the Closing balance?")
            input = re.sub(",", '', bank_asset)
            ans = re.findall(r"\d+\.\d+", input)
            bank_asset = int(float(ans[0]))
            aadhar = self.extract_info(
                text, "what is the Aadhaar number which is of 12 digits or characters and not in capital letters,not the Enrollment no or VID?")
            pan = self.extract_info(
                text, "give me the PAN or e-Permenant number or value which is of 10 characters all are in capital letters from income tax department?")
            Name = self.extract_info(
                text, "give me the  full Name from aadhar or pan?")
            Addresss = self.extract_info(text, "give me the  Address?")
            accountNo = self.extract_info(text, "give the bank account no?")
            accountNo = int(accountNo)
            print("Process finished")
            return json.dumps({
                "income": anual_income,
                "bankbalance": bank_asset,
                "aadhar": aadhar,
                "pan": pan,
                "name": Name,
                "address": Addresss,
                "accountNo": accountNo
            })
        except Exception as e:
            print(e)
            return json.dumps({               
                "income":"",
                "bankbalance": "",
                "aadhar": "",
                "pan": "",
                "name": "",
                "address": "",
                "accountNo": ""            
            })

    def get_eligibility_status(self, data):
        dependents = int(data["dependents"])
        eduction = 1
        employment = 1
        anual_income = int(data["income"])
        loan_ammount = int(data["loanAmount"])
        loan_term = int(data["loanTerm"])
        cibil = int(data["cibil"])
        bank_balance = int(data["bankbalance"])
        features = [dependents, eduction, employment, anual_income,
                    loan_ammount, loan_term, cibil, bank_balance]
        print("******", features)

        prediction = self.predict(features)
        print(prediction)
        res = data
        res["loan_status"] = prediction
        res['anual_income'] = anual_income
        if prediction == 0:
            reason=emiResponse(res,loan_term,cibil,loan_ammount)
            return json.dumps({
                "message": "You are eligible for loan application.",
                "reason": reason,
                "status": True
            })
        else:
            reason = response(res, loan_ammount, res["income"], 12, 12, 25000)
            return json.dumps({
                "message": "You are not eligible for loan application.",
                "reason": reason,
                "status": False
            })
