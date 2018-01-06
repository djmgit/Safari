import aiml
import os

'''
if os.path.isfile("bot_brain.brn"):
    kernel.bootstrap(brainFile = "bot_brain.brn")
else:
    kernel.bootstrap(learnFiles = "std-startup.xml", commands = "load aiml b")
    kernel.saveBrain("bot_brain.brn")
'''

#kernel.saveBrain("bot_brain.brn")

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class Bot:
	def __init__(self):
		self.kernel = aiml.Kernel()
		self.kernel.bootstrap(learnFiles = os.path.join(APP_ROOT, 'std-startup.xml'), commands = "load aiml b")

	def execute_command(self):
		#execute command 
		pass

	def get_response(self, text):
		response = self.kernel.respond(text)
		final_response = {}

		if response == "":
			return {'type': "error"}
		
		response = response.split("*")
		response_type = response[0]

		final_response['type'] = response_type

		if response_type == "statement":
			final_response['reply'] = response[1]

		if response_type == "action":
			final_response['action'] = response[1]
			if len(response) == 3:
				final_response['param'] = response[2]

		return final_response

if __name__ == "__main__":
	bot = Bot()
	while True:
		print (bot.get_response(input(">>>")))