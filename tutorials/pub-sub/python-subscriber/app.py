#
# Copyright 2021 The Dapr Authors
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import flask
from flask import request, jsonify
from flask_cors import CORS
import json
import sys


app = flask.Flask(__name__)
CORS(app)

WINDOW_SIZE = 12 # Tamaño de la ventana deslizante
LOOKAHEAD_SIZE = 4 # Tamaño de la zona de búsqueda adelante

def compress_lzss(data):
    result = ''
    i = 0
    while i < len(data):
        match_length = 0
        match_offset = 0
        for j in range(1, min(LOOKAHEAD_SIZE, len(data)-i)+1):
            window_start = max(0, i-WINDOW_SIZE)
            substring = data[i:i+j]
            for k in range(window_start, i):
                offset = i - k
                window_substring = data[k:k+j]
                if window_substring == substring and len(window_substring) > match_length:
                    match_length = len(window_substring)
                    match_offset = offset
        if match_length > 0:
            # Codificar una coincidencia
            match_code = (match_offset << 4) | (match_length-1)
            result += chr(match_code)
            i += match_length
        else:
            # Codificar un carácter individual
            char_code = ord(data[i])
            if char_code >= 0x20 and char_code <= 0x7E:
                # Carácter imprimible ASCII
                result += chr(char_code)
            else:
                # Carácter no imprimible
                result += chr(0x7F)
                result += chr(char_code)
            i += 1
    return result



@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [{'pubsubname': 'pubsub', 'topic': 'A', 'route': 'A'}, {'pubsubname': 'pubsub', 'topic': 'C', 'route': 'C'}]
    return jsonify(subscriptions)

@app.route('/A', methods=['POST'])
def a_subscriber():
    print(f'A: {request.json}', flush=True)
    #Antes de comprimir, se llama a un calificador de textos
    with DaprClient() as client:
    # Publish an event/message using Dapr PubSub
    result = client.publish_event(
        pubsub_name='pubsub',
        topic_name='textcheck',
        data=json.dumps(textcheck),
        data_content_type='application/json',
    )
    # compressed = 'NO'
    #print('Received message "{}" on topic "{}" has been compressed to the following text: "{}"'.format(request.json['data']['message'], request.json['topic'],compressed), flush=True)
    return result

@app.route('/C', methods=['POST'])
def c_subscriber():
    print(f'C: {request.json}', flush=True)
    print('Received message "{}" on topic "{}"'.format(request.json['data']['message'], request.json['topic']), flush=True)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/textcheck', methods=['POST'])
def textcheck_subscriber():
    print(f'C: {request.json}', flush=True)
    if request.json['data']['message'].contains("Ingeniero")
        with DaprClient() as client:
        # Publish an event/message using Dapr PubSub
        result = client.publish_event(
            pubsub_name='pubsub',
            topic_name='RECHAZO',
            data=json.dumps(RECHAZO),
            data_content_type='application/json',
        )
        return result
    else
        compressed = compress_lzss(request.json['data']['message'])
        print('Received message "{}" on topic "{}" has been compressed to the following text: "{}"'.format(request.json['data']['message'], request.json['topic'],compressed), flush=True)
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}     

@app.route('/RECHAZO', methods=['POST'])
def textcheck_subscriber():
    print(f'C: {request.json}', flush=True)
    print('Se rechazo la solicitud por escribir un token prohibido'), flush=True)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}           

app.run(port=5001)
