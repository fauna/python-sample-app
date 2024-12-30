from typing import Callable

from fauna import fql
from fauna.client import Client
from fauna.encoding import QuerySuccess
from fauna.errors import AbortError
from flask import Blueprint, jsonify, request, Response

from ecommerce_app.customer_controller import add_item_to_cart, get_or_create_cart, create_customer
from ecommerce_app.models.customer import Customer, customerResponse
from ecommerce_app.models.order import Order, order_summary
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

@products.route('/products/<product_id>', methods=['GET'])
def get_product(product_id: str):
    """Get the product with the given identity."""
    success: QuerySuccess = client.query(fql(
        "let product = Product.byId(${productId})\n${toProduct}",
        productId=product_id, toProduct=to_product()))
    return jsonify(success.data)


@products.route('/products', methods=['POST'])
def post_products():
    """
    Create a new product with the given POST data. The required parameters are name, description, price, stock, and category.
    :return: The newly created product.
    """
    return create_product()


@products.route('/products/<order_id>', methods=['PATCH'])
def patch_product(order_id):
    """Update the product with the given ID."""
    return update_product(order_id)


@orders.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get the order with the given identity."""
    return get_order_by_id(order_id)


@orders.route('/orders/<order_id>', methods=['PATCH'])
def patch_order(order_id: str):
    """Update an orders status, and optionally the payment method.
    The valid status transitions are defined in collections.fsl.
    """
    return update_order(order_id)

@customers.route('/customers', methods=['POST'])
def post_customers():
    return create_customer()


@customers.route('/customers/<customer_id>/cart', methods=['POST'])
def get_customer_cart(customer_id: str):
    """Return the cart for a customer, or create one if it doesn't exist."""
    return get_or_create_cart(customer_id)


@customers.route('/customers/<customer_id>/cart/item', methods=['POST'])
def post_customer_cart_item(customer_id: str):
    """Add an item to the customers cart."""
    return add_item_to_cart(customer_id)


@customers.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id: str):
    """
    Get a customer by ID, or email
    :param customer_id:  The ID, or email of the customer. If using email, set the query parameter "?key=email".
    :return:    The customer details.
    """
    key = request.args.get('key')
    abort_message = 'Customer not found.'
    customerQuery = fql('let customer = Customer.byId(${customerId})', customerId=customer_id)
    if key == 'email':
        customerQuery = fql('let customer = Customer.byEmail(${email}).first()', email=customer_id)
    try:
        success: QuerySuccess = client.query(fql(
            '${getCustomer}\n${checkNotNull}\n${customerResponse}',
            getCustomer=customerQuery, customerResponse=customerResponse(),
            checkNotNull=fql("if (customer == null) abort(${abortMsg})", abortMsg=abort_message)))
        return jsonify(Customer(**success.data))
    except AbortError as err:
        if err.abort == abort_message:
            return jsonify({"message": abort_message, "status_code": 404}), 404


@customers.route('/customers/<customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id: str):
    """List all the orders for a customer."""
    nextToken = request.args.get("nextToken")
    pageSize = request.args.get('pageSize', default=10, type=int)
    if nextToken:
        success: QuerySuccess = client.query(fql(
            "Set.paginate(${nextToken}).map(order => ${toOrder})",
            nextToken=nextToken, toOrder=order_summary()))
        # Data is a dict not a page here.
        return jsonify_page(success.data['data'], success.data['after'], Order)
    else:
        success: QuerySuccess = client.query(fql(
            "Order.byCustomer(Customer.byId(${customerId})).pageSize(${pageSize}).map(order => ${orderSummary})",
            pageSize=pageSize, orderSummary=order_summary(), customerId=customer_id))
        return jsonify_page(success.data.data, success.data.after, Order)


