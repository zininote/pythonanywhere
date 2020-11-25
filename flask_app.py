
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
import counter

app = Flask(__name__)

@app.route('/')
def route_index():
    return 'Hi there~'

@app.route('/counter')
def route_counter():
    return counter.render()
