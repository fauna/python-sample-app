from flask import jsonify, request
from fauna import fql
from fauna.client import Client
from fauna.encoding import QuerySuccess

from ecommerce_app.models.order import order_response

# Initialize Fauna client
client = Client()

def get_order_by_id(order_id):
    query = fql("let order = Order.byId(${id})!\n${orderResponse}", id=order_id, orderResponse=order_response())

    # Execute the query
    success: QuerySuccess = client.query(query)
    # Return the order as JSON
    return jsonify(success.data), 200


def update_order(order_id):
    # Extract status and payment fields from the request body
    data = request.get_json()
    status = data.get('status')
    payment = data.get('payment', {})

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
        ${orderResponse}
        ''',
        id=order_id, status=status, payment=payment, orderResponse=order_response()
    )

    # Execute the query
    res: QuerySuccess = client.query(query)
    # Return the updated order as JSON
    return jsonify(res.data), 200