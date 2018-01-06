from flask import Flask, redirect, url_for, request, jsonify, render_template, g
from flask_cors import CORS
from bot_core import bot
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

chatbot = bot.Bot()

app = Flask(__name__)
app.config['SECRET_KEY'] = "THIS IS SECRET"

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
	if action == 'info':
		# return info
		response['info'] = get_info(param)
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

