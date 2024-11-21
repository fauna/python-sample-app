import urllib

from flask import jsonify, request
from fauna import fql
from fauna.client import Client
from fauna.errors import FaunaException
from fauna.encoding import QuerySuccess

# Initialize Fauna client
client = Client()

def create_product():
    # Extract fields from the request body.
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    stock = data.get('stock')
    category_name = data.get('category')

    # Basic validation: Ensure all required fields are present
    if not all([name, price is not None, description is not None, stock is not None, category_name]):
        return jsonify({'message': 'Missing required fields.'}), 400

    # Convert price and stock to appropriate types
    try:
        price = int(price)
        stock = int(stock)
    except ValueError:
        return jsonify({'message': 'Price must be a number and stock must be an integer.'}), 400

    try:
        # Build the FQL query with parameter substitution
        query = fql(
            '''
            let category = Category.byName(${category_name}).first()
            if (category == null) abort("Category does not exist.")
            let args = {
                name: ${name},
                price: ${price},
                stock: ${stock},
                description: ${description},
                category: category
            }
            let product = Product.create(args)
            product
            ''',
            category_name=category_name,
            name=name,
            price=price,
            stock=stock,
            description=description
        )

        # Execute the query
        res: QuerySuccess = client.query(query)
        doc = res.data

        print(doc)

        result = {}
        result['id'] = doc.id
        for key in doc:
            if key != 'category':
              result[key] = doc[key]

        print(result)

        # Return the product, stripping out any unnecessary fields
        return jsonify(result), 201

    except FaunaException as e:
        # Handle Fauna exceptions
        return jsonify({'error': str(e)}), 500

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
          queryFragment = fql(
            '''
            Product.byCategory(Category.byName(${category}).first()).pageSize(${pageSize})
            .map(product => {
                    let product: Any = product
                    let category: Any = product.category
                    {
                        id: product.id,
                        name: product.name,
                        description: product.description,
                        price: product.price,
                        stock: product.stock,
                        category: {
                            id: category.id,
                            name: category.name,
                            description: category.description
                        }
                    }
              })
            ''', category=category, pageSize=pageSize)
        else:
          queryFragment = fql('''
            Product.sortedByCategory().pageSize(${pageSize})
            .map(product => {
                let product: Any = product
                let category: Any = product.category
                {
                    id: product.id,
                    name: product.name,
                    description: product.description,
                    price: product.price,
                    stock: product.stock,
                    category: {
                        id: category.id,
                        name: category.name,
                        description: category.description
                    }
                }
            })  
          ''', 
          pageSize=pageSize)
        res = client.query(fql('''
          ${queryFragment}                    
        ''', queryFragment=queryFragment))

        # Extract the data and the nextToken from the response
        page = res.data

        # # Extract the 'data' attribute from each Document
        results = page.data

        return jsonify({'data': results })
    except FaunaException as e:
        # Handle Fauna exceptions
        return jsonify({'error': str(e)}), 500


# TODO: Fix the FQL query to update the product
def update_product(id):
    # Extract fields from the request body
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    stock = data.get('stock')
    category_name = data.get('category')

    # Validate that the required fields are provided
    if all([price is None, description is None, stock is None, name is None, category_name is None]):
        return jsonify({'message': 'No fields to update provided.'}), 400

    # Convert price and stock to appropriate types, if they are provided
    try:
        if price is not None:
            price = int(price)
        if stock is not None:
            stock = int(stock)
    except ValueError:
        return jsonify({'message': 'Price must be a number and stock must be an integer.'}), 400
    
    print(id)

    try:
        # Construct the query to update the product in Fauna
        query = fql(
            '''
            let product = Product.byId(${id})!
            let category = if (${category_name} != null) {
                let cat = Category.byName(${category_name}).first()
                if (cat == null) abort("Category does not exist.")
                cat
            } else {
                product.category
            }

            let fields = {}
            if (${name} != null) fields.name = ${name}
            if (${price} != null) fields.price = ${price}
            if (${description} != null) fields.description = ${description}
            if (${stock} != null) fields.stock = ${stock}

            if (category != null) fields.category = category

            product.update(fields)
            product {
                id,
                name,
                price,
                description,
                stock,
                category {
                    id,
                    name,
                    description
                }
            }
            ''',
            id=id,
            name=name,
            price=price,
            description=description,
            stock=stock,
            category_name=category_name,

        )

        # Execute the query
        res: QuerySuccess = client.query(query)
        product = res.data

        print(product)

        # Update the product fields if they are provided


        # Return the updated product
        return jsonify({ id: product.id }), 200

    except FaunaException as e:
        # TODO: Actually handle exceptions, not strings here :)
        # Handle Fauna exceptions
        if 'document_not_found' in str(e):
            return jsonify({'message': f"No product with id '{id}' exists."}), 404
        elif 'Category does not exist' in str(e):
            return jsonify({'message': 'Category does not exist.'}), 400
        elif 'constraint_failure' in str(e):
            return jsonify({'message': 'A product with that name already exists.'}), 409
        else:
            return jsonify({'error': str(e)}), 500