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

	response ={}

	if action == 'location':
		# return location of place defined by param
		response['location'] = get_location(param)
		response['place_searched'] = param
	if action == 'info':
		# return info
		response['info'] = get_info(param)
		response['place_searched'] = param
	if action == 'suggest':
		# return suggestion
		response['suggestion'] = get_suggestion()

	return response

def get_location(param):
	# extract location
	return 'location'

def get_info(param):
	# extract info
	return 'info'

def get_suggestion():
	# generate suggestion
	return 'suggestion'

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

