from flask import jsonify, request
from fauna import fql
from fauna.client import Client
from fauna.errors import FaunaException
from fauna.encoding import QuerySuccess

# Initialize Fauna client
client = Client()

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
