import json
from server import Server
from flask import jsonify, request
from flask_cors import cross_origin
from celery.result import AsyncResult
import uuid
from helpers.processDocs import process
import os
from services.mongo import MongoClient

server = Server(__name__)

rds = server.redis
celery = server.celery
app = server.app
socket = server.socketio
callback_api = f"http://{os.getenv('SERVER_HOST')}:{os.getenv('SERVER_PORT')}/api/callback_result"

mongo = MongoClient()
db = mongo.db


@app.route('/api/uploadfiles', methods=['POST'])
@cross_origin()
def upload_files():
    rds_task_id = str(uuid.uuid4())
    if 'files' not in request.files:
        return jsonify({"message": "No file uploaded"})
    files = request.files.getlist('files')

    # for testing
    for file in files:
        print(file.filename)

    # LLM operation
    text = process(uploaded_files=files)
    # print("*******:", text)
    kwargs = {"_data": text, "callback_api": callback_api,
              "rds_task_id": rds_task_id}
    task = celery.send_task("tasks.get_info_from_docs", kwargs=kwargs)
    # ------

    # for handling callback api
    rds.set(rds_task_id, task.id)
    return jsonify({"taskId": task.id})

# Executes after celery task done -> Callback API


@app.route('/api/callback_result', methods=['POST'])
def callback_result():
    print("call back called")
    data = request.get_json()
    socket.emit(str(data["task_id"]), data)
    return jsonify("done")


@app.route('/api/getinfo', methods=['GET'])
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


@app.route('/api/getloanstatus', methods=['POST'])
@cross_origin()
def get_loan_status():
    rds_task_id = str(uuid.uuid4())
    # it will come from uploaded docs
    req_data = request.get_json()

    data = "appended data"
    kwargs = {"_data": req_data, "callback_api": callback_api,
              "rds_task_id": rds_task_id}
    task = celery.send_task(
        "tasks.generating_loan_eligibilty_status", kwargs=kwargs)
    # ------

    # for handling callback api
    rds.set(rds_task_id, task.id)
    return jsonify({"taskId": task.id})


# Instead of this API , I used socket-> for avoiding multiple request from client
@app.route("/api/task/<task_id>", methods=["GET"])
@cross_origin()
def get_result(task_id):
    result = AsyncResult(task_id, app=celery)
    response_data = {
        "taskId": task_id,
        "taskStatus": result.status,
        "taskResult": result.result
    }

    return jsonify(response_data)

# OTP verify


@app.route("/api/verifyotp", methods=["POST"])
@cross_origin()
def verify_otp():
    data = request.get_json()
    if data["otp"] == 9999:
        status = True
    else:
        status = False
    response_data = {
        "status": status

    }

    return jsonify(response_data)

@app.route("/api/verifyadmin", methods=["POST"])
@cross_origin()
def verify_otp():
    data = request.get_json()
    if data["password"] == "admin":
        status = True
    else:
        status = False
    response_data = {
        "status": status

    }

    return jsonify(response_data)


@app.route('/api/updateloanstatus', methods=['POST'])
@cross_origin()
def updateLoanStatus():
    try:
        data = request.get_json()
        db.loan_status.update_one({"loanId": data["loanId"]}, {
                                  "$set": {"loanStatus": data["status"]}})
        return jsonify({
            "status": "Success"
        })
    except Exception as e:
        print("Error in saving data")


@app.route('/api/applyloan', methods=['POST'])
@cross_origin()
def applyloan():
    try:
        data = request.get_json()
        print(data, "*******")
        data["loanId"] = str(uuid.uuid4())
        data["loanStatus"] = "Pending"
        print("db name::", db.name)
        id = db.loan_status.insert_one(data).inserted_id
        record = db.loan_status.find_one({"_id": id})
        print("id::", record)

        return jsonify({
            "loanId": record["loanId"]
        })
    except Exception as e:
        print("Error in saving data", e)
        return jsonify({
            "error": str(e)
        })


@app.route('/api/getloanapplications', methods=['GET'])
@cross_origin()
def getloanapplications():
    try:
        applications = db.loan_status.find({}, {"_id": 0})
        data = list(applications)
        return jsonify(data)
    except Exception as e:
        print("Error in returning applications data")
        return jsonify({
            "error": str(e)
        })


@app.route('/api/getloaniddetails/<id>', methods=['GET'])
@cross_origin()
def getloaniddetails(id):
    try:
        applications = db.loan_status.find({"loanId": id}, {"_id": 0})
        data = list(applications)
        return jsonify(data)
    except Exception as e:
        print("Error in returning applications data")
        return jsonify({
            "error": str(e)
        })


@app.route('/api/trackloanid/<id>', methods=['GET'])
@cross_origin()
def trackloan(id):
    try:
        applications = db.loan_status.find({"loanId": id})
        data = list(applications)
        if len(data) > 0:
            status = data[0]["loanStatus"]
            return jsonify({
                "status": status
            })
        else:
            return jsonify({
                "status": "record not found"
            })

    except Exception as e:
        print("Error in returning applications data")
        return jsonify({
            "error": str(e)
        })


if __name__ == '__main__':
    server.run()
