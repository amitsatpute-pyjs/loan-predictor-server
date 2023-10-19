from celery import Celery
import requests
import redis
import json
import time
import os
from services.predictor import Predictor

app = Celery("tasks", backend=f'redis://{os.getenv("REDIS_HOST")}:{ os.getenv("REDIS_PORT")}/0',
             broker=f'redis://{os.getenv("REDIS_HOST")}:{ os.getenv("REDIS_PORT")}/0')
app.conf.broker_connection_retry_on_startup = True
rds = redis.Redis(host=os.getenv("REDIS_HOST"),
                  port=int(os.getenv("REDIS_PORT")), db=1)
headers = {'Content-Type': 'application/json'}

llm = Predictor()


@app.task()
def get_info_from_docs(_data, callback_api, rds_task_id):
    # training operation
    print("ulr:", callback_api)
    print("rds task::", rds_task_id)
    result = llm.get_data_from_llm(text=_data)
    # time.sleep(4)
    # result ={
    #         "income": 9999,
    #         "bankbalance": 9955,
    #         "aadhar": 98765432145,
    #         "pan": "DFER4567U",
    #         "name": "User test",
    #         "address": "Pune, Maharashtra",
    #         "accountNo": 40097587451
    #     }
    # For callback
    print("Result::", result)
    task_id = rds.get(rds_task_id).decode("utf-8")
    print(task_id, "*****")
    # url = callback_api
    url = f'http://{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}/callback_result'
    result = json.loads(result)
    result["task_id"] = task_id
    requests.post(url, data=json.dumps(result), headers=headers)
    return result


@app.task()
def generating_loan_eligibilty_status(_data, callback_api, rds_task_id):
    # loan status operation
    print(_data, "Data is ***********")
    result = llm.get_eligibility_status(data=_data)
    # time.sleep(4)
    # result = {
    #             "message": "You are eligible for loan application.",
    #             "reason": "",
    #             "status": True
    #         }
    # For callback
    task_id = rds.get(rds_task_id).decode("utf-8")
    url = callback_api
    result = json.loads(result)

    result["task_id"] = task_id
    requests.post(url, data=json.dumps(result), headers=headers)
    return result
