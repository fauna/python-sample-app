import unittest
from dataclasses import asdict
from unittest import mock
from unittest.mock import Mock

import flask
from fauna import Page
from fauna.encoding import QuerySuccess

from ecommerce_app.app import app
from ecommerce_app.models.category import Category
from ecommerce_app.models.product import Product
from ecommerce_app.routes import get_products


class TestProductController(unittest.TestCase):

    @mock.patch('ecommerce_app.routes.client')
    def test_get_products(self, mock_client):

        mock_response = Mock(QuerySuccess)
        product = asdict(Product(id='1234', name='a', price=1, description='b', category=Category(name='electronics', id='123', description='c'), stock=11))
        mock_response.data = Page(data=[product], after='abcdef')
        mock_client.query.return_value = mock_response
        with app.test_request_context(data=flask.json.dumps({'category': 'books'}),
                                      content_type='application/json') as request:

            response, status = get_products()
            self.assertEqual(len(response.data), 154)
            self.assertTrue(b"abcdef" in response.data)
            self.assertEqual(status, 200)

