
from server import Server
from flask import jsonify, request
from flask_cors import cross_origin
from celery.result import AsyncResult
import uuid

server = Server(__name__)

rds = server.redis
celery = server.celery
app = server.app
socket = server.socketio

@app.route('/uploadfiles', methods=['POST'])
@cross_origin()
def upload_files():
    rds_task_id = str(uuid.uuid4())
    if 'files' not in request.files:
        return jsonify({"message": "No file uploaded"})
    files = request.files.getlist('files')

    for file in files:      
        print(file.filename)

    #LLM operation
    data = "appended data"   
    kwargs={"data":data,"callback_api":"http://127.0.0.1:5000/callback_result", "rds_task_id":rds_task_id}
    task = celery.send_task("tasks.generating_vector_db",kwargs=kwargs)
    #------ 
           
    #for handling callback api
    rds.set(rds_task_id,task.id)  
    return jsonify({"taskId":task.id}) 

# Executes after celery task done -> Callback API
@app.route('/callback_result/<task_id>', methods=['GET'])
def callback_result(task_id):   
    print("socket called")
    socket.emit(str(task_id),1)
    return jsonify("done")

@app.route('/getinfo', methods=['GET'])
@cross_origin()
def get_info():
    # it will come from uploaded docs
    response = {
        "income": "789456",
        "bankBalace": "789654123",
        "name": "hello",
        "address": "pune",
        "accountNumber": "9865324400",
        "pan": "dfwrt5678i",
        "aadhar": "999999999999"
    }

    return jsonify(response)


@app.route('/getLoanStatus', methods=['GET'])
@cross_origin()
def get_loan_status():
    # it will come from uploaded docs
    response = {
        "status": "approved/not approved",
        "reason":  "reason in case of loan rejection"
    }

    return jsonify(response)

# Instead of this API , I used socket-> for avoiding multiple request from client
@app.route("/task/<task_id>", methods=["GET"])
@cross_origin()
def get_result(task_id):
    result = AsyncResult(task_id,app=celery)   
    response_data = {
        "taskId": task_id,
        "taskStatus": result.status,
        "taskResult": result.result
    }

    return jsonify(response_data)
    

if __name__ == '__main__':
    server.run()
