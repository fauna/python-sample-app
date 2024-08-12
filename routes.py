from flask import Blueprint, jsonify

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
  return jsonify({"message": "To be implemented"})