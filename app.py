from flask import Flask
from routes import products
from routes import orders

app = Flask(__name__)

app.register_blueprint(products)
app.register_blueprint(orders)

if __name__ == '__main__':
  app.run(debug=True)
