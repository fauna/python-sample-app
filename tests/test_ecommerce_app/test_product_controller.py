import unittest
from dataclasses import asdict
from unittest import mock
from unittest.mock import Mock

import flask
from fauna.encoding import QuerySuccess

from ecommerce_app.product_controller import create_product, update_product
from ecommerce_app.models.category import Category
from ecommerce_app.models.product import Product

from ecommerce_app.app import app

class TestProductController(unittest.TestCase):

    @mock.patch('ecommerce_app.product_controller.client')
    def test_create_product(self, mock_client):

        mock_response = Mock(QuerySuccess)
        product = asdict(Product(id='1234', name='a', price=1, description='b', category=Category(name='electronics', id='123', description='c'), stock=11))

        mock_response.data = product
        mock_client.query.return_value = mock_response

        input_json = product.copy()
        input_json['category'] = product['category']['name']
        del input_json['id']

        with app.test_request_context(data=flask.json.dumps(input_json), content_type='application/json') as request:
            response, status = create_product()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(status, 201)
            self.assertEqual(len(response.data), 127)
            self.assertTrue("\"id\":\"1234\"", response.data)

    @mock.patch('ecommerce_app.product_controller.client')
    def test_update_product(self, mock_client):

        mock_response = Mock(QuerySuccess)
        product = asdict(Product(id='1234', name='a', price=1, description='b', category=Category(name='electronics', id='123', description='c'), stock=11))

        mock_response.data = product
        mock_client.query.return_value = mock_response

        input_json = {'price': 2}

        with app.test_request_context(data=flask.json.dumps(input_json), content_type='application/json') as request:
            response, status = update_product(product['id'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(status, 200)
            self.assertEqual(len(response.data), 127)
            self.assertTrue("\"id\":\"1234\"", response.data)