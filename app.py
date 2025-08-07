from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Home page is working."

@app.route('/callback')
def callback():
    return "OAuth callback received!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
