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
