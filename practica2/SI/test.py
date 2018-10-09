from flask import Flask 
import json
app = Flask(__name__)

@app.route('/')
def index():
	return "<html><p>Hello Maria</p></html>"

if __name__ == '__main__':
	app.run(debug = True)