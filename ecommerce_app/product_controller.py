from typing import Any, Callable

from flask import jsonify, request
from fauna import fql
from fauna.client import Client
from fauna.encoding import QuerySuccess

from ecommerce_app.models.product import product_response

# Initialize Fauna client
client = Client()

def extract_field(key: str, fields: dict[str, Any], data: dict[str, Any], func: Callable = str) -> None:
    if key in data:
        fields[key] = func(data.get(key))


def create_product():
    # Extract fields from the request body.
    data = request.get_json()
    fields = {}
    extract_field('name', fields, data)
    extract_field('price', fields, data, int)
    extract_field('description', fields, data)
    extract_field('stock', fields, data, int)
    extract_field('category', fields, data)

    # Basic validation: Ensure all required fields are present
    required = set(('name', 'price', 'description', 'stock', 'category'))
    difference = required - set(fields.keys())
    if difference:
        return jsonify({'message': f'Missing required field(s) {difference}'}), 400


    # Build the FQL query with parameter substitution
    query = fql(
        '''
        let fields = ${fields}
        let category = Category.byName(fields.category).first()
        if (category == null) abort("Category does not exist.")
        let product = Product.create({name: fields.name, price: fields.price, category: category, stock: fields.stock, description: fields.description})
        ${toProduct}
        ''',
        fields=fields, toProduct=product_response()
    )
    # Execute the query
    res: QuerySuccess = client.query(query)
    # Return the product, stripping out any unnecessary fields
    return jsonify(res.data), 201


def update_product(product_id):
    # Extract fields from the request body
    data = request.get_json()
    fields = {}
    extract_field('name', fields, data)
    extract_field('price', fields, data, int)
    extract_field('description', fields, data)
    extract_field('stock', fields, data, int)
    category_name = data.get('category')

    if not fields and not category_name:
        return jsonify({'message': 'At least one field must be updated.'}), 400

    # Construct the query to update the product in Fauna.
    # There are potentially two `product.update` statements, but it's performant since it all runs in
    # one query and is executed as a single transaction server-side.
    update_category = fql('''
        let cat = Category.byName(${categoryName}).first()
        if (cat == null) abort("Category does not exist.")
        product.update({category: cat})''', categoryName=category_name) if category_name else fql('')
    query = fql(
        '''
        let product = Product.byId(${id})!
        ${category}
        product.update(${fields})
        ${toProduct}
        ''',
        id=product_id, fields=fields, toProduct=product_response(), category=update_category)

    # Execute the query
    success: QuerySuccess = client.query(query)
    return jsonify(success.data), 200