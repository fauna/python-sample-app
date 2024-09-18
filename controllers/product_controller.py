from flask import jsonify, request
from fauna import fql
from fauna.client import Client
from fauna.errors import FaunaException
import urllib.parse

# Initialize Fauna client
client = Client()

def list_products():
    # Extract query parameters
    category = request.args.get('category')
    nextToken = request.args.get('nextToken')
    pageSize = request.args.get('pageSize', default=10, type=int)

    # Decode the nextToken from the query parameter, if it exists
    decodedNextToken = urllib.parse.unquote(nextToken) if nextToken else None

    try:
        queryFragment = ''

        if category is not None:
          queryFragment = fql('Product.byCategory(Category.byName(${category}).first())', category=category)
        else:
          queryFragment = fql('Product.byCategory(Category.byName(${category}).first()).pageSize(${pageSizeNumber})', pageSizeNumber=pageSize)

        res = client.query(fql('''
          ${queryFragment}                    
        ''', queryFragment=queryFragment))

        # Extract the data and the nextToken from the response
        page = res.data

        # Extract the 'data' attribute from each Document
        results = []
        for product in page:
          # Convert the Document object to a dictionary
          results.append({
            'id': product.id,
            'name': product.get('name'),
            'description': product.get('description'),
            'price': product.get('price'),
            'stock': product.get('stock')
          })

        return jsonify({'data': results })
    except FaunaException as e:
        # Handle Fauna exceptions
        return jsonify({'error': str(e)}), 500
