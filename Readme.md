# Fauna Python sample app

This sample app shows how you can use [Fauna](https://fauna.com) in a
production application.

The app uses Python3.12 and the Fauna Python driver to create HTTP API
endpoints for an e-commerce store. The source code includes comments that highlight
best practices for the driver and Fauna Query Language (FQL) queries.

This README covers how to set up and run the app locally. For an overview of
Fauna, see the [Fauna
docs](https://docs.fauna.com/fauna/current/get_started/overview).

## Highlights
// TODO

## Requirements
// TODO

## Set up

// WIP

Initiate a new virtual environment 

```sh
python -m venv myenv
```

Activate the Virtual Environment

On Windows:

```sh
myenv\Scripts\activate
```

on Mac/Linux

```sh
source myenv/bin/activate
```

## Run the app

The app runs an HTTP API server. From the root directory, run:

```sh
python app.py
```

Once started, the local server is available at http://localhost:5000

## Make HTTP API requests

```

You can use the endpoints to make API requests that read and write data from
the `ECommerce` database.

For example, with the local server running in a separate terminal tab, run the
following curl request to the `POST /customers` endpoint. The request creates a
`Customer` collection document in the `ECommerce` database.

curl -v \
  http://localhost:5000/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Appleseed",
    "email": "alice.appleseed@example.com",
    "address": {
      "street": "87856 Mendota Court",
      "city": "Washington",
      "state": "DC",
      "postalCode": "20220",
      "country": "USA"
    }
  }'
```

You can view the documents for the collection in the [Fauna
Dashboard](https://dashboard.fauna.com/).

## Run tests

// TODO