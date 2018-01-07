from flask import Flask, redirect, url_for, request, jsonify, render_template, g
from flask_cors import CORS
from bot_core import bot
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import os
import random
import requests
import json

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE_ACCESS_TOKEN = 'EAAZAhVq30VgsBAHso3u2Cw0uvD6ZALwg7SvucmFNclGEW1dlc3DOoaSMxT83Re0uU3CcHDY1QIcdxtHzCwUvpBQcx1S38E8LmvwzMbhtgyKroDkhU5qMh9d85qZBKLjJIE1J82YsWU9cffnoRPYPYzz5byfwucrTg4kED3178JhGdijVH1d'
VERIFY_TOKEN = 'verify'

app = Flask(__name__)
CORS(app)
if os.environ.get('DATABASE_URL') is None:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/deep'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = "THIS IS SECRET"

db = SQLAlchemy(app)

class Spots(db.Model):
    __tablename__ = 'spots'

    id = db.Column('spot_id', db.Integer, primary_key=True)
    name = db.Column(db.String)
    location = db.Column(db.String)
    info = db.Column(db.String)
    special_attraction = db.Column(db.String)
    things_to_do = db.Column(db.String)
    time_to_visit = db.Column(db.String)
    near_by_places = db.Column(db.String)
    similar_places = db.Column(db.String)
    how_to_reach = db.Column(db.String)
    lat = db.Column(db.String)
    lon = db.Column(db.String)

    def __init__(self, name='', location='', info='', special_attraction='', things_to_do='', time_to_visit='', near_by_places='', similar_places='', how_to_reach='', lat='', lon=''):
        self.name = name
        self.location = location
        self.info = info
        self.lat = lat
        self.lon = lon
        self.special_attraction = special_attraction
        self.things_to_do = things_to_do
        self.time_to_visit = time_to_visit
        self.near_by_places = near_by_places
        self.similar_places = similar_places
        self.how_to_reach = how_to_reach

db.create_all();

class SpotTableView(ModelView):

	# Admin view for Spot tab;e
    can_create = True
    can_view_details = True
    column_searchable_list = ['name']
    edit_modal = True
    column_filters = ['name']

# setup admin

admin = Admin(app, name='Safari', template_mode='bootstrap3')
admin.add_view(SpotTableView(Spots, db.session))

chatbot = bot.Bot()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/api/chat')
def chat():
	q = request.args.get('q')
	response = chatbot.get_response(q)

	if response['type'] == 'error':
		reply = {}
		ans = noinfo_response()
		reply['reply'] = ans[1]
		reply['ANSWER_FOUND'] = ans[0]
		final_response = {}
		final_response['reply'] = reply
		final_response['status'] = 'error'
		return jsonify(final_response)
 
	return create_response(response.get('type'), response.get('action'), response.get('param'))

# method for checking webhook authenticity
@app.route('/webhook', methods=['GET'])
def handle_verification():
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        print("Verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong token")
        return "Error, wrong validation token"

# method to handle messages coming from facebook
@app.route('/webhook', methods=['POST'])
def handle_message():
    '''
    Handle messages sent by facebook messenger to the applicaiton
    '''
    data = request.get_json()

    if data["object"] == "page":
        for entry in data["entry"]:
            '''for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):

                    sender_id = messaging_event["sender"]["id"]        
                    recipient_id = messaging_event["recipient"]["id"]  
                    message_text = messaging_event["message"]["text"]  
                    send_message_response(sender_id, 'hello this is safari')'''
            webhook_event = entry['messaging'][0]
            sender_id = webhook_event['sender']['id']
            message = webhook_event['message']['text']

            response = chatbot.get_response(message)

            if response['type'] == 'error':
            	send_message(sender_id, noinfo_response[1])

            res = create_response(response.get('type'), response.get('action'), response.get('param'))
            send_message(sender_id, res['reply']['reply'])

    return "ok"

def send_message(sender_id, message_text):
    '''
    Sending response back to the user using facebook graph API
    '''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": PAGE_ACCESS_TOKEN},

        headers={"Content-Type": "application/json"},

        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))

def create_response(rtype, action, param):
	response = {}

	if rtype == 'statement':
		reply = {}
		reply['reply'] = param
		reply['reply_type'] = 'answer'
		response['reply'] = reply
		print (param)

	if rtype == 'action':
		response['reply'] = execute_action(action, param.lower())

	response['status'] = 'success'

	return jsonify(response)

def execute_action(action, param):
	
	#execute the action here

	response = {}

	if action == 'location':
		# return location of place defined by param
		reply = get_location(param)
		response['reply'] = reply[1]
		response['place_searched'] = param
		response['reply_type'] = 'map'
		response['answer_found'] = reply[0]

		if reply[0] == 'ANSWER_FOUND_YES':
			response['lat'] = reply[2]
			response['lon'] = reply[3]

	if action == 'info':
		# return info
		reply = get_info(param)
		response['reply'] = reply[1]
		response['place_searched'] = param
		response['reply_type'] = 'info'
		response['answer_found'] = reply[0]

	if action == 'suggest':
		# return suggestion
		response['reply'] = get_suggestion()

	if action == 'special':
		# return special attraction
		reply = get_sp_attr(param)
		response['reply'] = reply[1]
		response['place_searched'] = param
		response['reply_type'] = 'special_attraction'
		response['answer_found'] = reply[0]

	if action == 'activity':
		# return things to do
		reply = get_things_to_do(param)
		response['reply'] = reply[1]
		response['place_searched'] = param
		response['reply_type'] = 'things_to_do'
		response['answer_found'] = reply[0]

	if action == 'tov':
		# return time to visit
		reply = get_time_to_visit(param)
		response['reply'] = reply[1]
		response['place_searched'] = param
		response['reply_type'] = 'time_of_visit'
		response['answer_found'] = reply[0]

	if action == 'nearby':
		# return nearby places
		reply = get_near_by_places(param)
		response['reply'] = reply[1]
		response['place_searched'] = param
		response['reply_type'] = 'nearby_places'
		response['answer_found'] = reply[0]

	if action == 'similar':
		# return similar places
		reply = get_similar_places(param)
		response['reply'] = reply[1]
		response['place_searched'] = param
		response['reply_type'] = 'similar_places'
		response['answer_found'] = reply[0]

	if action == 'reach':
		# return means to travel to destination
		reply = get_how_to_reach(param)
		response['reply'] = reply[1]
		response['place_searched'] = param
		response['reply_type'] = 'how_to_reach'
		response['answer_found'] = reply[0]

	return response

def get_location(param):
	# extract location
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		return 'ANSWER_FOUND_YES', item.location, item.lat, item.lon
	else:
		return noinfo_response()

def get_info(param):
	# extract info
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'Here is some info on ' + param + '. ' + item.info
		return 'ANSWER_FOUND_YES', response
	else:
		return noinfo_response()

def get_sp_attr(param):
	# extract special attraction
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'Following are some special attractions of ' + param + '. ' + item.special_attraction
		return 'ANSWER_FOUND_YES', response
	else:
		return noinfo_response()

def get_things_to_do(param):
	# extract things to do
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'Here are some things which you might consider doing at ' + param + '. ' + item.things_to_do
		return 'ANSWER_FOUND_YES', response
	else:
		return noinfo_response()

def get_time_to_visit(param):
	# extract time to visit
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'You may consider visiting ' + param + 'during ' + item.time_to_visit
		return 'ANSWER_FOUND_YES', response
	else:
		return noinfo_response()

def get_near_by_places(param):
	# extract info
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'Here are some places close to ' + param + '. ' + item.near_by_places
		return 'ANSWER_FOUND_YES', response
	else:
		return noinfo_response()

def get_similar_places(param):
	# extract info
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items
		response = 'Here are some places which are similar to ' + param + '. ' + item.similar_places
		return 'ANSWER_FOUND_YES', response
	else:
		return noinfo_response()

def get_how_to_reach(param):
	# extract how to reach
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = item.how_to_reach
		return 'ANSWER_FOUND_YES', response
	else:
		return noinfo_response()

def get_suggestion():
	# generate suggestion
	return 'suggestion'

def noinfo_response():
	response_list = [
		"Sorry! I cannot answer that",
		"I don't know, I am still learning",
		"I don't have an answer for that, I have yet a long way to go",
		"I am afraid I do not have a suitable answer for this",
		"I have no answer for this now, but someday I shall learn!"
	];

	return 'ANSWER_FOUND_NO', response_list[random.randint(0, 4)]

# start the server
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

