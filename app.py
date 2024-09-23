from flask import Flask
from routes import products
from routes import orders
from routes import customers

app = Flask(__name__)

app.register_blueprint(products)
app.register_blueprint(orders)
app.register_blueprint(customers)

if __name__ == '__main__':
  app.run(debug=True)
