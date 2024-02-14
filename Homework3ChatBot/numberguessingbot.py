## channel.py - a simple message channel
##

from flask import Flask, request, render_template, jsonify
import json
import requests
import datetime
import random 


# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db

HUB_URL = 'http://localhost:5555'
HUB_AUTHKEY = '1234567890'
CHANNEL_AUTHKEY = '0691871'
CHANNEL_NAME = "Number Guessing Bot"
CHANNEL_ENDPOINT = "http://localhost:5004" # don't forget to adjust in the bottom of the file
CHANNEL_FILE = 'messages.json'
randomtbg = random.randint(1,100)
default_message_displayed = True

@app.cli.command('register')
def register_command():
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT

    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({
            "name": CHANNEL_NAME,
            "endpoint": CHANNEL_ENDPOINT,
            "authkey": CHANNEL_AUTHKEY}))

    if response.status_code != 200:
        print("Error creating channel: "+str(response.status_code))
        return

def check_authorization(request):
    global CHANNEL_AUTHKEY
    # check if Authorization header is present
    if 'Authorization' not in request.headers:
        return False
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify({'name':CHANNEL_NAME}),  200

# GET: Return list of messages
@app.route('/', methods=['GET'])
def home_page():
    global default_message_displayed 

    if not check_authorization(request):
        return "Invalid authorization", 400

    # Fetch channels from server
    messages = read_messages()

    # Display the default welcome message only if it hasn't been displayed before
    if default_message_displayed:
        default_message = {'content': 'Welcome to the channel! Try guessing my random number between 1 and 100!', 'sender': 'Bot', 'timestamp': str(datetime.datetime.now())}
        messages.append(default_message)
        default_message_displayed = False  # Set the flag to indicate the default message has been displayed

    # Return messages including the default message
    return jsonify(messages), 200

# POST: Send a message
@app.route('/', methods=['POST'])
def send_message():
    
    
    # fetch channels from server
    # check authorization header
    if not check_authorization(request):
        return "Invalid authorization", 400

    # check if message is present
    message = request.json
    if not message:
        return "No message", 400
    if not 'content' in message:
        return "No content", 400
    if not 'sender' in message:
        return "No sender", 400
    if not 'timestamp' in message:
        return "No timestamp", 400

    # Reverse the content of the message
    
    reversed_content = message['content'][::-1]

    # add message to messages with reversed content
    messages = read_messages()
    messages.append({'content': message['content'], 'sender': message['sender'], 'timestamp': message['timestamp']})
    number = int(message['content'])
    if randomtbg == number:
        messages.append({'content':"That's my Number! Nice guessing!", 'sender':'Number Guessing Bot', 'timestamp':message['timestamp']})
        save_messages(messages)
    else:
        if randomtbg >= number:
            messages.append({'content':"Wrong! My number is higher!", 'sender':'Number Guessing Bot', 'timestamp':message['timestamp']})
            save_messages(messages)
        else: 
            messages.append({'content':"Wrong! My number is lower!", 'sender':'Number Guessing Bot', 'timestamp':message['timestamp']}) 
            save_messages(messages)

    

    return "OK", 200

def read_messages():
    global CHANNEL_FILE
    try:
        f = open(CHANNEL_FILE, 'r')
    except FileNotFoundError:
        return []
    try:
        messages = json.load(f)
    except json.decoder.JSONDecodeError:
        messages = []
    f.close()
    return messages

def save_messages(messages):
    global CHANNEL_FILE
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)

# Start development web server
if __name__ == '__main__':
    app.run(port=5004, debug=True)
