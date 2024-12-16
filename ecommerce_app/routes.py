from typing import Callable

from fauna import fql
from fauna.client import Client
from fauna.encoding import QuerySuccess
from fauna.errors import AbortError
from flask import Blueprint, jsonify, request, Response

from ecommerce_app.customer_controller import add_item_to_cart, get_or_create_cart, create_customer
from ecommerce_app.models.customer import Customer, to_customer
from ecommerce_app.models.order import Order, to_order
from ecommerce_app.models.product import Product, to_product
from ecommerce_app.order_controller import get_order_by_id, update_order
from ecommerce_app.product_controller import create_product, update_product

products = Blueprint('products', __name__)
orders = Blueprint('orders', __name__)
customers = Blueprint('customers', __name__)


# Initialize Fauna client
client = Client()


def jsonify_page(data: list, after: str, item_func: Callable) -> Response:
    return jsonify({'data': [item_func(**doc) for doc in data], 'next': after})


@products.route('/products', methods=['GET'])
def get_products():
    """
    By default, paginate over all products, the category query parameter allows you to return products by category.
    The nextToken query parameter returns subsequent pages of results.
    :return: A list of products, and (optionally) the next page token.
    """
    nextToken = request.args.get('nextToken')
    category = request.args.get('category')
    pageSize = request.args.get('pageSize', default=10, type=int)
    if nextToken:
        success: QuerySuccess = client.query(fql(
            "Set.paginate(${nextToken}).map(product => ${toProduct}",
            nextToken=nextToken, toProduct=to_product()))
        # Data is a dict not a page here.
        return jsonify_page(success.data['data'], success.data['after'], Product), 200
    elif category:
        categoryQuery = fql("Category.byName(${category}).first()", category=category)
        success: QuerySuccess = client.query(fql(
            "Product.byCategory(${category}).pageSize(${pageSize}).map(product => ${toProduct})",
            category=categoryQuery,
            pageSize=pageSize, toProduct=to_product()))
        return jsonify_page(success.data.data, success.data.after, Product), 200
    else:
        success: QuerySuccess = client.query(fql(
            "Product.sortedByCategory().pageSize(${pageSize}).map(product => ${toProduct})",
            pageSize=pageSize, toProduct=to_product()))
        return jsonify_page(success.data.data, success.data.after, Product), 200

# Use 'identity' rather than 'id', because 'id' is a reserved keyword in Python.

@products.route('/products/<identity>', methods=['GET'])
def get_product(identity: str):
    """Get the product with the given identity."""
    success: QuerySuccess = client.query(fql(
        "let product = Product.byId(${identity})\n${toProduct}",
        identity=identity, toProduct=to_product()))
    return jsonify(success.data)


@products.route('/products', methods=['POST'])
def new_product():
    """
    Create a new product with the given POST data. The required parameters are name, description, price, stock, and category.
    :return: The newly created product.
    """
    return create_product()


@products.route('/products/<identity>', methods=['PATCH'])
def products_by_id(identity):
    """Get the product with the given ID."""
    return update_product(identity)


@orders.route('/orders/<identity>', methods=['GET'])
def order_by_id(identity):
    """Get the order with the given identity."""
    return get_order_by_id(identity)


@orders.route('/orders/<identity>', methods=['PATCH'])
def update_order_by_id(identity: str):
    """Update an orders status, and optionally the payment method.
    The valid status transitions are defined in collections.fsl.
    """
    return update_order(identity)

@customers.route('/customers', methods=['POST'])
def new_customer():
    return create_customer()


@customers.route('/customers/<identity>/cart', methods=['POST'])
def create_or_get_cart(identity: str):
    """Return the cart for a customer, or create one if it doesn't exist."""
    return get_or_create_cart(identity)


@customers.route('/customers/<identity>/cart/item', methods=['POST'])
def add_to_cart(identity: str):
    """Add an item to the customers cart."""
    return add_item_to_cart(identity)


@customers.route('/customers/<identifier>', methods=['GET'])
def get_customer(identifier: str):
    """
    Get a customer by ID, or email
    :param identifier:  The ID, or email of the customer. If using email, set the query parameter "?key=email".
    :return:    The customer details.
    """
    key = request.args.get('key')
    abort_message = 'Customer not found.'
    customerQuery = fql('let customer = Customer.byId(${cust_id})', cust_id=identifier)
    if key == 'email':
        customerQuery = fql('let customer = Customer.byEmail(${email}).first()', email=identifier)
    try:
        success: QuerySuccess = client.query(fql(
            '${getCustomer}\n${checkNotNull}\n${toCustomer}',
            getCustomer=customerQuery, toCustomer=to_customer(),
            checkNotNull=fql("if (customer == null) abort(${abortMsg})", abortMsg=abort_message)))
        return jsonify(Customer(**success.data))
    except AbortError as err:
        if err.abort == abort_message:
            return jsonify({"message": abort_message, "status_code": 404}), 404


@customers.route('/customers/<identifier>/orders', methods=['GET'])
def get_customer_orders_route(identifier: str):
    """List all the orders for a customer."""
    nextToken = request.args.get("nextToken")
    pageSize = request.args.get('pageSize', default=10, type=int)
    if nextToken:
        success: QuerySuccess = client.query(fql(
            "Set.paginate(${nextToken}).map(order => ${toOrder})",
            nextToken=nextToken, toOrder=to_order()))
        # Data is a dict not a page here.
        return jsonify_page(success.data['data'], success.data['after'], Order)
    else:
        success: QuerySuccess = client.query(fql(
            "Order.byCustomer(${customer}).pageSize(${pageSize}).map(order => ${toOrder})",
            pageSize=pageSize,
            toOrder=to_order(),
            customer=fql("Customer.byId(${identifier})", identifier=identifier)))
        return jsonify_page(success.data.data, success.data.after, Order)


