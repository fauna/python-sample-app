from flask import jsonify, request
from fauna import fql
from fauna.client import Client
from fauna.errors import FaunaException
from fauna.encoding import QuerySuccess

# Initialize Fauna client
client = Client()

def get_order_by_id(id):
    try:
        # Build the FQL query to retrieve the order by ID
        query = fql(
            '''
            let order = Order.byId(${id})!
            {
              id: order.id,
              payment: order.payment,
              createdAt: order.createdAt.toString(),
              status: order.status,
              total: order.total,
              customer: {
                id: order.customer?.id,
                name: order.customer?.name,
                email: order.customer?.email,
                address: order.customer?.address
              },
              items: order.items.toArray().map(item => {
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
                },
                quantity: item.quantity
              }),
            }
            ''',
            id=id
        )

        # Execute the query
        res: QuerySuccess = client.query(query)
        order = res.data

        print(order)
        # Return the order as JSON
        return jsonify(order), 200

    except FaunaException as e:
        # Handle Fauna-specific errors
        if 'document_not_found' in str(e):
            return jsonify({'message': f"No order with id '{id}' exists."}), 404
        elif 'invalid_argument' in str(e):
            return jsonify({'message': f"Invalid id '{id}' provided."}), 400
        else:
            return jsonify({'error': str(e)}), 500


def update_order(id):
    # Extract status and payment fields from the request body
    data = request.get_json()
    status = data.get('status')
    payment = data.get('payment', {})

    try:
        # Construct the FQL query to update the order
        query = fql(
            '''
            let order = Order.byId(${id})!
            // Validate the order status transition if a status is provided
            if (${status} != null) {
                validateOrderStatusTransition(order.status, ${status})
            }
            // If the order status is not "cart" and a payment is provided, throw an error
            if (order.status != "cart" && ${payment} != null) {
                abort("Cannot update payment information after an order has been placed.")
            }
            // Update the order with the new status and payment information
            order.update({
                status: ${status},
                payment: ${payment}
            })
            {
                id: order?.id,
                payment: order?.payment,
                createdAt: order?.createdAt.toString(),
                status: order?.status,
                total: order?.total,
                items: order?.items.toArray().map(item => {
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
                    },
                    quantity: item.quantity
                }),
                customer: {
                    id: order?.customer?.id,
                    name: order?.customer?.name,
                    email: order?.customer?.email,
                    address: order?.customer?.address
                }
            }
            ''',
            id=id,
            status=status,
            payment=payment
        )

        # Execute the query
        res: QuerySuccess = client.query(query)
        order = res.data

        # Return the updated order as JSON
        return jsonify(order), 200

    except FaunaException as e:
        # Handle Fauna-specific errors
        if 'document_not_found' in str(e):
            return jsonify({'message': f"No order with id '{id}' exists."}), 404
        elif 'abort' in str(e):
            return jsonify({'message': e.message}), 400
        else:
            return jsonify({'error': str(e)}), 500