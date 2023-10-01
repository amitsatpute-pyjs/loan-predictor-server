from celery import Celery
import requests
import redis


app = Celery("tasks",backend='redis://localhost:6379/0',broker='redis://localhost:6379/0')
app.conf.broker_connection_retry_on_startup = True
rds = redis.Redis(host='localhost', port=6379, db=1)

@app.task()
def generating_vector_db(data,callback_api,rds_task_id):
    # training operation 
    # 
    # For callback   
    task_id = rds.get(rds_task_id).decode("utf-8")   
    url = callback_api+f"/{str(task_id)}"    
    requests.get(url)
    return {"status":"Done"}
