from fauna.errors import FaunaError
from flask import Flask, jsonify, request
from ecommerce_app.routes import products
from ecommerce_app.routes import orders
from ecommerce_app.routes import customers

app = Flask(__name__)

app.register_blueprint(products)
app.register_blueprint(orders)
app.register_blueprint(customers)

@app.errorhandler(FaunaError)
def handle_fauna_exception(exc: FaunaError):
    err_dict = {'http_status': exc.status_code, 'code': exc.code, 'message': exc.message}
    if exc.code == 'document_not_found':
        return jsonify({"message": f"Document not found at {request.path}", "status_code": 404}), 404
    if hasattr(exc, 'summary'):
        err_dict['summary'] = exc.summary
    if exc.constraint_failures:
        constraint_failures = []
        for cf in exc.constraint_failures:
            failure = {'message': cf.message, 'paths': cf.paths }
            if cf.name:
                failure['name'] = cf.name
            constraint_failures.append(failure)
        return jsonify(constraint_failures), 409
    if exc.abort:
        return jsonify({'message': exc.abort, 'status_code': exc.status_code}), exc.status_code

    return jsonify(err_dict), exc.status_code

if __name__ == '__main__':
    app.run(debug=True)
