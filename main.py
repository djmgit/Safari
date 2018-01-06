from flask import Flask, redirect, url_for, request, jsonify, render_template, g
from flask_cors import CORS
from bot_core import bot
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import os
import random

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

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
		return jsonify({'reply': 'Sorry I cannot answer this :(', 'status': 'error'})
	return create_response(response.get('type'), response.get('action'), response.get('param'))

def create_response(rtype, action, param):
	response = {}

	if rtype == 'statement':
		response['reply'] = param
		print (param)

	if rtype == 'action':
		response['reply'] = execute_action(action, param)

	response['status'] = 'success'

	return jsonify(response)

def execute_action(action, param):
	
	#execute the action here

	response = {}

	if action == 'location':
		# return location of place defined by param
		response['reply'] = get_location(param)
		response['place_searched'] = param

	if action == 'info':
		# return info
		response['reply'] = get_info(param)
		response['place_searched'] = param

	if action == 'suggest':
		# return suggestion
		response['reply'] = get_suggestion()

	if action == 'special':
		# return special attraction
		response['reply'] = get_sp_attr(param)
		response['place_searched'] = param

	if action == 'activity':
		# return things to do
		response['reply'] = get_things_to_do(param)
		response['place_searched'] = param

	if action == 'tov':
		# return time to visit
		response['reply'] = get_time_to_visit(param)
		response['place_searched'] = param

	if action == 'nearby':
		# return nearby places
		response['reply'] = get_near_by_places(param)
		response['place_searched'] = param

	if action == 'similar':
		# return similar places
		response['reply'] = get_similar_places(param)
		response['place_searched'] = param

	if action == 'reach':
		# return means to travel to destination
		response['reply'] = get_how_to_reach(param)
		response['place_searched'] = param

	return response

def get_location(param):
	# extract location
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		return item.location
	else:
		return noinfo_response()

def get_info(param):
	# extract info
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'Here is some info on ' + param + '. ' + item.info
		return response
	else:
		return noinfo_response()

def get_sp_attr(param):
	# extract special attraction
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'Following are some special attractions of ' + param + '. ' + item.special_attraction
		return response
	else:
		return noinfo_response()

def get_things_to_do(param):
	# extract things to do
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'Here are some things which you might consider doing at ' + param + '. ' + item.things_to_do
		return response
	else:
		return noinfo_response()

def get_time_to_visit(param):
	# extract time to visit
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'You may consider visiting ' + param + 'during ' + item.time_to_visit
		return response
	else:
		return noinfo_response()

def get_near_by_places(param):
	# extract info
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = 'Here are some places close to ' + param + '. ' + item.near_by_places
		return response
	else:
		return noinfo_response()

def get_similar_places(param):
	# extract info
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items
		response = 'Here are some places which are similar to ' + param + '. ' + item.similar_places
		return response
	else:
		return noinfo_response()

def get_how_to_reach(param):
	# extract how to reach
	items = Spots.query.filter_by(name=param).all()
	if len(items) != 0:
		item = items[0]
		response = item.how_to_reach
		return response
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

	return response_list[random.randint(0, 4)]

# start the server
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

