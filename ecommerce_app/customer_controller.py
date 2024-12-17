import dataclasses

from flask import jsonify, request
from fauna import fql
from fauna.client import Client
from fauna.errors import FaunaException
from fauna.encoding import QuerySuccess
import urllib.parse

from ecommerce_app.models.customer import Address, customerResponse
from ecommerce_app.models.order import order_response

# Initialize Fauna client
client = Client(typecheck=False)


def create_customer():
    customer_data = request.get_json()
    required = set(('name', 'email', 'address'))
    difference = required - set(customer_data.keys())
    if difference:
        return jsonify({'message': f'Missing required field(s) {difference}'}), 400
    try:
        Address(**customer_data['address'])
    except TypeError:
        diff = set([field.name for field in dataclasses.fields(Address)]) - set(customer_data['address'].keys())
        return jsonify({'message': f'Missing required field(s) {diff}'})
    success = client.query(fql('let customer = Customer.create(${newCustomer})\n${customerResponse}',
                               newCustomer=customer_data, customerResponse=customerResponse()))
    return jsonify(success.data), 201


def add_item_to_cart(customer_id):
    # Extract product name and quantity from the request body
    data = request.get_json()
    product_name = data.get('productName')
    quantity = data.get('quantity')

    # Basic validation for product and quantity
    if not product_name or quantity is None:
        return jsonify({'message': 'Missing product name or quantity.'}), 400

    # Construct the FQL query to add or update the cart item
    query = fql("let order = createOrUpdateCartItem(${customerId}, ${productName}, ${quantity})\n${orderResponse}",
        customerId=customer_id, productName=product_name, quantity=quantity, orderResponse=order_response()
    )

    # Execute the query
    res: QuerySuccess = client.query(query)

    # Return the updated cart as JSON
    return jsonify(res.data), 200


def get_or_create_cart(customer_id: str):
    # Build the FQL query to get or create the cart for the customer
    query = fql(" let order = getOrCreateCart(${customerId}) ${orderResponse}",
        customerId=customer_id, orderResponse=order_response())

    # Execute the query
    res: QuerySuccess = client.query(query)
    cart = res.data

    # Return the cart as JSON
    return jsonify(cart), 200

