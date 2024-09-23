from flask import Blueprint, jsonify
from controllers.product_controller import list_products, create_product

products = Blueprint('products', __name__)


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