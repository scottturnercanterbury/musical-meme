from flask import Flask

app = Flask(__name__)



@app.route("/")

def hello():

   return "Hello World!"

@app.route("/test1")

def test1():

  return "Well it is different!"

if __name__ == '__main__':

   app.run()