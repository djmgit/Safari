from flask import Flask, redirect, url_for, request, jsonify, render_template, g
from flask_cors import CORS
from bot_core import bot
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import os

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
    lat = db.Column(db.String)
    lon = db.Column(db.String)

    def __init__(self, name, location, info, lat, lon):
        self.name = name
        self.location = location
        self.info = info
        self.lat = lat
        self.lon = lon

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

	response['status'] = 'success'
	return response

def get_location(param):
	# extract location
	item = Spots.query.filter_by(name=param).all()[0]
	return item['location']

def get_info(param):
	# extract info
	item = Spots.query.filter_by(name=param).all()[0]
	response = 'Here is some info on ' + param + '. ' + item['info']
	return response

def get_sp_attr(param):
	# extract special attraction
	item = Spots.query.filter_by(name=param).all()[0]
	response = 'Following are some special attractions of ' + param + '. ' + item['special_attraction']
	return response

def get_things_to_do(param):
	# extract things to do
	item = Spots.query.filter_by(name=param).all()[0]
	response = 'Here are some things which you might consider doing at ' + param + '. ' + item['things_to_do']
	return response

def get_time_to_visit(param):
	# extract time to visit
	item = Spots.query.filter_by(name=param).all()[0]
	response = 'You may consider visiting ' + param + 'during ' + item['time_to_visit']
	return response

def get_near_by_places(param):
	# extract info
	item = Spots.query.filter_by(name=param).all()[0]
	response = 'Here are some places close to ' + param + '. ' + item['near_by_places']
	return response

def get_similar_places(param):
	# extract info
	item = Spots.query.filter_by(name=param).all()[0]
	response = 'Here are some places which are similar to ' + param + '. ' + item['similar_places']
	return response

def get_suggestion():
	# generate suggestion
	return 'suggestion'

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

