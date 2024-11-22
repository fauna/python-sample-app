import unittest
from datetime import datetime
from unittest import mock
from unittest.mock import Mock

import flask
from fauna import Document
from fauna.encoding import QuerySuccess
from flask import Flask

import app

from controllers.product_controller import create_product

app = Flask(__name__)

class TestProductController(unittest.TestCase):


    @mock.patch('controllers.product_controller.client')
    def test_create_product(self, mock_client):

        mock_response = Mock(QuerySuccess)
        mock_response.data = Document(id='1234', ts=datetime.now(), coll='Product')
        mock_client.query.return_value = mock_response

        # client = app.test_client()
        # with app.app_context():
        some_json = {'name': 'a', 'price': 1, 'description': 'b', 'stock': 11, 'category': 'electronics'}
        with app.test_request_context(data=flask.json.dumps(some_json), content_type='application/json') as request:
            response, status = create_product()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(status, 201)
            self.assertEqual(response.data, b'{"id":"1234"}\n')

if __name__ == '__main__':
    unittest.main()