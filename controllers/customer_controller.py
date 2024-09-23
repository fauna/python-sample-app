from flask import jsonify, request
from fauna import fql
from fauna.client import Client
from fauna.errors import FaunaException
from fauna.encoding import QuerySuccess
import urllib.parse

# Initialize Fauna client
client = Client(typecheck=False)

def add_item_to_cart(customer_id):
    # Extract product name and quantity from the request body
    data = request.get_json()
    product_name = data.get('productName')
    quantity = data.get('quantity')

    # Basic validation for product and quantity
    if not product_name or quantity is None:
        return jsonify({'message': 'Missing product name or quantity.'}), 400

    try:
        # Construct the FQL query to add or update the cart item
        query = fql(
            '''
            let order = createOrUpdateCartItem(${customer_id}, ${product_name}, ${quantity})
            {
              id: order?.id,
              payment: order?.payment,
              createdAt: order?.createdAt.toString(),
              status: order?.status,
              total: order?.total,
              customer: {
                id: order?.customer?.id,
                name: order?.customer?.name,
                email: order?.customer?.email,
                address: order?.customer?.address
              },
              items: order?.items.toArray().map(item => {
                product: {
                  id: item?.product?.id,
                  name: item?.product?.name,
                  price: item?.product?.price,
                  description: item?.product?.description,
                  stock: item?.product?.stock,
                  category: {
                    id: item?.product?.category?.id,
                    name: item?.product?.category?.name,
                    description: item?.product?.category?.description
                  }
                },
                quantity: item?.quantity
              }),
            }
            ''',
            customer_id=customer_id,
            product_name=product_name,
            quantity=quantity
        )

        # Execute the query
        res: QuerySuccess = client.query(query)
        print(res.data)

        # Return the updated cart as JSON
        return jsonify(res.data), 200

    except FaunaException as e:
        # Handle Fauna-specific errors
        if 'document_not_found' in str(e):
            return jsonify({'message': f"No customer with id '{customer_id}' exists."}), 404
        elif 'abort' in str(e):
            return jsonify({'message': e.message}), 400
        else:
            return jsonify({'error': str(e)}), 500

def get_customer_orders(customer_id):
    # Extract pagination parameters from the request query
    next_token = request.args.get('nextToken')
    page_size = request.args.get('pageSize', default=10, type=int)

    # Decode the nextToken if provided
    decoded_next_token = urllib.parse.unquote(next_token) if next_token else None

    try:
        # Construct the FQL query to retrieve orders for the customer
        query = fql(
            '''
            let customer = Customer.byId(${customer_id})!
            let orders = Order.byCustomer(customer).pageSize(${page_size}).map(order => {
                id: order?.id,
                payment: order?.payment,
                createdAt: order?.createdAt.toString(),
                status: order?.status,
                total: order?.total,
                items: order?.items?.toArray().map(item => {
                    product: {
                        id: item?.product.id,
                        name: item?.product?.name,
                        price: item?.product?.price,
                        description: item.product?.description,
                        stock: item.product?.stock,
                        category: {
                            id: item?.product?.category?.id,
                            name: item?.product?.category?.name,
                            description: item?.product?.category?.description
                        }
                    },
                    quantity: item?.quantity
                }),
                customer: {
                    id: order?.customer?.id,
                    name: order?.customer?.name,
                    email: order?.customer?.email,
                    address: order?.customer?.address
                }
            })
            orders
            ''',
            customer_id=customer_id,
            page_size=page_size
        )

        # Execute the query
        res: QuerySuccess = client.query(query)
        orders_page = res.data

        # If pagination is supported, return the next token as well
        encoded_next_token = orders_page.get('after', None)

        # Return the orders and the next token (if available)
        return jsonify({
            'results': orders_page['data'],
            'nextToken': urllib.parse.quote(encoded_next_token) if encoded_next_token else None
        }), 200

    except FaunaException as e:
        # Handle Fauna-specific errors
        if 'document_not_found' in str(e):
            return jsonify({'message': f"No customer with id '{customer_id}' exists."}), 404
        else:
            return jsonify({'error': str(e)}), 500

def get_or_create_cart(customer_id):
    try:
        # Build the FQL query to get or create the cart for the customer
        query = fql(
            '''
            let order = getOrCreateCart(${customer_id})
            {
              id: order?.id,
              payment: order?.payment,
              createdAt: order?.createdAt.toString(),
              status: order?.status,
              total: order?.total,
              customer: {
                id: order?.customer?.id,
                name: order?.customer?.name,
                email: order?.customer?.email,
                address: order?.customer?.address
              },
              items: order?.items.toArray().map(item => {
                quantity: item.quantity,
                product: {
                  id: item.product?.id,
                  name: item.product?.name,
                  price: item.product?.price,
                  description: item.product?.description,
                  stock: item.product?.stock,
                  category: {
                    id: item.product?.category?.id,
                    name: item.product?.category?.name,
                    description: item.product?.category?.description
                  }
                }
              })
            }
            ''',
            customer_id=customer_id
        )

        # Execute the query
        res: QuerySuccess = client.query(query)
        cart = res.data

        # Return the cart as JSON
        return jsonify(cart), 200

    except FaunaException as e:
        # Handle Fauna-specific errors
        if 'document_not_found' in str(e):
            return jsonify({'message': f"No customer with id '{customer_id}' exists."}), 404
        else:
            return jsonify({'error': str(e)}), 500
