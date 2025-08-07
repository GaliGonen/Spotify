from flask import Flask, request

app = Flask(__name__)

@app.route('/callback')
def callback():
    return "✅ Callback received!", 200
