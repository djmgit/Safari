from flask import Flask, redirect, url_for, request, jsonify, render_template, g
from flask_cors import CORS
from bot_core import bot

chatbot = bot.Bot()

app = Flask(__name__)
app.config['SECRET_KEY'] = "THIS IS SECRET"

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/api/chat')
def chat():
	text = request.args.get('text')
	response = chatbot.get_response(text)
	return jsonify(response)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

