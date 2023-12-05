## Create a simple flask application
from flask import Flask,render_template,request,redirect,url_for

## create the flask app
app=Flask(__name__)


## create the flask routes
@app.route('/')
def home():
    return "<h2>Hello, World!</h2>"

if __name__=='__main__':
    app.run(debug=True)


