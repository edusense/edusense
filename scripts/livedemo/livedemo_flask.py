from flask import Flask, request,jsonify
import json
app = Flask(__name__)

runs_dict = dict()

@app.route('/add_camera',methods=['GET'])
def add_camera_session():
    if request.method == 'GET':
        rmq_exchange = request.args['rmq_exchange']
        rmq_routing_key =request.args['rmq_routing_key']
        camera_url = request.args['camera_url']
        runs_dict.update({camera_url:{
            'rmq_exchange':rmq_exchange,
            'rmq_routing_key':rmq_routing_key
        }})
    print("Add Camera: current runs:", runs_dict)
    return "success"

@app.route('/remove_camera',methods=['GET'])
def remove_camera_session():
    if request.method == 'GET':
        camera_url = request.args['camera_url']
        if camera_url in runs_dict:
            del runs_dict[camera_url]
    print("Remove Camera: current runs:", runs_dict)
    return "success"


@app.route('/get_camera_queue',methods=['GET'])
def send_camera_queue():
    camera_url=None
    if request.method == 'GET':
        camera_url =request.args['ip_address']
    print("RUNS DICT:",runs_dict)
    response = jsonify({"exchange_name":runs_dict[camera_url]['rmq_exchange'],
                       "routing_key":runs_dict[camera_url]['rmq_routing_key']})
    print(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

app.run(port=8888, host='0.0.0.0')