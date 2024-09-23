from flask import Blueprint, jsonify
from controllers.product_controller import list_products, create_product, update_product
from controllers.order_controller import get_order_by_id, get_or_create_cart

products = Blueprint('products', __name__)
orders = Blueprint('orders', __name__)

"""

Get a page of products. If a category query parameter is provided, return only products in that category.
If no category query parameter is provided, return all products. The results are paginated with a default
page size of 10. If a nextToken is provided, return the next page of products corresponding to that token.
@route {GET} /products
@queryParam {string} category
@queryparam nextToken
@queryparam pageSize
@returns { results: Product[], nextToken: string }

"""
@products.route('/products', methods=['GET'])
def listroducts():
  return list_products()

@products.route('/products', methods=['POST'])
def new_product():
  return create_product()

@products.route('/products/<id>', methods=['PATCH'])
def edit_product(id):
  return update_product(id)

@orders.route('/orders/<id>', methods=['GET'])
def order_by_id(id):
  return get_order_by_id(id)

@orders.route('/customers/<id>/cart', methods=['POST'])
def create_or_get_cart(id):
    return jsonify({'message': 'Not implemented'}), 501