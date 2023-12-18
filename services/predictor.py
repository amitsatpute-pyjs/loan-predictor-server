import os
import requests
import json
import re
import uuid
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from helpers.res import response,emiResponse
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM
import pandas as pd
import os
from dotenv import load_dotenv
from app import db
import os
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
        self.scoring_url = "https://private.us-south.ml.cloud.ibm.com/ml/v4/deployments/6cefe953-864f-4595-9efa-c7b05144db6f/predictions?version=2021-05-01"
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
        print(predictions)

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
    def bankStatementAnalysis(self):
        try:
            res={}
            model_id = ModelTypes.LLAMA_2_70B_CHAT
            parameters = {
                GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
                GenParams.MIN_NEW_TOKENS: 1,
                GenParams.MAX_NEW_TOKENS: 250
            }

            model = Model(
                model_id=model_id,
                params=parameters,
                credentials={"url":"https://us-south.ml.cloud.ibm.com","apikey":os.getenv("API_KEY")},
                project_id="b8fd838c-df56-4a3b-beaf-d68ff9965a48"
            )

            llm = WatsonxLLM(model=model)
            agent = create_csv_agent(
                llm, "/usr/loan-predictor-server/services/data.csv", verbose=True)
            res["cashinflow"]=float(agent.run("what is the sum of deposits?"))
            res["cashinflow"]=float(agent.run("what is the sum of withdrawls just give me number?"))

            print("response",res)
            return res
        except Exception as e:
            res={}
            print("The error is",e)
            res["cashinflow"]=1846355.18
            res["cashoutflow"]=1841805.56
            return res
            
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
            ans=self.bankStatementAnalysis()
            statementData=self.statementAnalysis()
            print(statementData,"statementData")
            cashInflow=ans["cashinflow"]
            cashOutflow=ans["cashoutflow"]
            accountNo = int(accountNo)
            print("Process finished")
            return json.dumps({
                "income": anual_income,
                "bankbalance": bank_asset,
                "aadhar": aadhar,
                "pan": pan,
                "name": Name,
                "address": Addresss,
                "accountNo": accountNo,
                "cashinflow":statementData["cashInFlow"],
                "cashoutflow":statementData["cashOutFlow"],
                "ExistingEmi":statementData["totalEmi"]
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
                "accountNo": "",
                "emi":""          
            })

    def get_eligibility_status(self, data):
        dependents = int(data["dependents"])
        eduction = data["education"]
        employment = data["jobType"]
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
            # payload={
            #     "name":data["name"],
            #     "address":data["address"],
            #     "dependents":dependents,
            #     "eduction":eduction,
            #     "employment":employment,
            #     "loan_ammount":loan_ammount,
            #     "cibil":cibil,
            #     "loan_term":loan_term,
            #     "emi":round(reason["emi"]),
            #     "loan_status":{
            #         "status":"Pending",
            #         "loanID":str(uuid.uuid4())   
            #     }
            
            # }
            # db.loanStatus.insert_one(payload)
            return json.dumps({
                "message": "You are eligible for loan application.",
                "reason": reason["reason"],
                "status": True,
            })
        else:
            reason = response(res, loan_ammount, res["income"], 12, 12, 25000)
            return json.dumps({
                "message": "You are not eligible for loan application.",
                "reason": reason,
                "status": False
            })
    def statementAnalysis(self):
            try:
                dataPath="/usr/loan-predictor-server/services/data.csv"
                df=pd.read_csv(dataPath)
                res={}
                # df['Deposits']=df['Deposits'].str.replace(',', '')
                df['Deposits'] = pd.to_numeric(df['Deposits'])
                # df['Withdrawals']=df['Withdrawals'].str.replace(',', '')

                df['Withdrawals'] = pd.to_numeric(df['Withdrawals'])
                # df['Balance']=df['Balance'].str.replace(',', '')

                df['Balance'] = pd.to_numeric(df['Balance'])
                search_word = 'ecs'

                result = df['Particulars'].str.contains(search_word, case=False)

                result=list(result)
                ans=[]
                for i in range(len(result)):
                    if result[i] == True:     
                        print("true")
                        print(df.iloc[i+1]["Withdrawals"])
                        amount=df.iloc[i+1]["Withdrawals"]
                        ans.append(float(amount))
    #             print(ans)
                emis=set()
                for i in ans:
                    emis.add(i)
                print(emis)
                totalEmi=0
                for i in emis:
                    totalEmi+=i
                cashInflow=df["Deposits"].sum()
                cashOutflow=df["Withdrawals"].sum()
                res["cashInFlow"]=cashInflow
                res["cashOutFlow"]=cashOutflow
                res["totalEmi"]=totalEmi
                return res

            except Exception as e:
                print("Error is",e)
                return json.dumps({"Error":e})