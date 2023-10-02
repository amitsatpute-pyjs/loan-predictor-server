from celery import Celery
import requests
import redis
import json
import time


app = Celery("tasks",backend='redis://localhost:6379/0',broker='redis://localhost:6379/0')
app.conf.broker_connection_retry_on_startup = True
rds = redis.Redis(host='localhost', port=6379, db=1)
headers = {'Content-Type': 'application/json'}

@app.task()
def generating_vector_db(_data,callback_api,rds_task_id):
    # training operation 
    time.sleep(5)
    # For callback   
    task_id = rds.get(rds_task_id).decode("utf-8")   
    url = callback_api   
    response = {"task_id":task_id,"status":"Done"}
    requests.post(url,data=json.dumps(response),headers=headers)
    return response

@app.task()
def generating_loan_eligibilty_status(_data,callback_api,rds_task_id):
    # loan status operation 
    time.sleep(5)
    # For callback   
    task_id = rds.get(rds_task_id).decode("utf-8")   
    url = callback_api  
    response = {
        "task_id":task_id,
        "message": "You are eligible for loan application.",
        "reason":  "",
        "status":True
    }
    requests.post(url,data=json.dumps(response), headers=headers)
    return response
