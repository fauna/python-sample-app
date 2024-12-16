# Fauna Python sample app

This sample app shows how you can use [Fauna](https://fauna.com) in a
production application.

The app uses Python 3 and the Fauna Python driver to create HTTP API
endpoints for an e-commerce store. The source code includes comments that highlight
best practices for the driver and Fauna Query Language (FQL) queries.

This README covers how to set up and run the app locally. For an overview of
Fauna, see the [Fauna
docs](https://docs.fauna.com/fauna/current/get_started/overview).

## Highlights
The sample app demonstrates using several Fauna features:

- **[Document type
  enforcement](https://docs.fauna.com/fauna/current/learn/schema/#type-enforcement):**
  Collection schemas enforce a structure for the app's documents. Fauna rejects
  document writes that don't conform to the schema, ensuring data consistency.
  [Zero-downtime
  migrations](https://docs.fauna.com/fauna/current/learn/schema/#schema-migrations)
  let you safely change the schemas at any time.

- **[Relationships](https://docs.fauna.com/fauna/current/learn/query/relationships/):**
  Normalized references link documents across collections. The app's queries use
  [projection](https://docs.fauna.com/fauna/current/reference/fql/projection/)
  to dynamically retrieve linked documents, even when deeply nested. No complex
  joins, aggregations, or duplication needed.

- **[Computed
  fields](https://docs.fauna.com/fauna/current/learn/schema/#computed-fields):**
  Computed fields dynamically calculate their values at query time. For example,
  each customer's `orders` field uses a query to fetch a set of filtered orders.
  Similarly, each order's `total` is calculated at query time based on linked
  product prices and quantity.

- **[Constraints](https://docs.fauna.com/fauna/current/learn/schema/#unique-constraints):**
  The app uses constraints to ensure field values are valid. For example, the
  app uses unique constraints to ensure each customer has a unique email address
  and each product has a unique name. Similarly, check constraints ensure each
  customer has only one cart at a time and that product prices are not negative.

- **[User-defined functions
  (UDFs)](https://docs.fauna.com/fauna/current/learn/data-model/user-defined-functions/):**
  The app uses UDFs to store business logic as reusable queries. For example,
  the app uses a `checkout()` UDF to process order updates. `checkout()` calls
  another UDF, `validateOrderStatusTransition()`, to validate `status`
  transitions for orders.

## Requirements
To run the app, you'll need:

- A [Fauna account](https://dashboard.fauna.com/register). You can sign up for a
  free account at https://dashboard.fauna.com/register.

- Python 3.9 or later 

- [Fauna CLI](https://docs.fauna.com/fauna/current/tools/shell/) v3.0.0 or later.

  To install the CLI, run:

    ```sh
    npm install -g fauna-shell@latest
    ```

You should also be familiar with basic Fauna CLI commands and usage. For an
overview, see the [Fauna CLI
docs](https://docs.fauna.com/fauna/current/tools/shell/).

## Setup

1. Clone the repo and navigate to the `python-sample-app` directory:

    ```sh
    git clone git@github.com:fauna/python-sample-app.git
    cd python-sample-app
    ```
2. Setup a Python virtual environment, and install the requirements:

    ```
   python3 -m venv venv
   source ./venv/bin/activate
   pip install -r requirements.txt
   ```

3. Log in to Fauna using the Fauna CLI:

    ```sh
    fauna cloud-login
    ```

   When prompted, enter:

    * **Endpoint name:** `cloud` (Press Enter)
    * **Email address:** The email address for your Fauna account.
    * **Password:** The password for your Fauna account.
    * **Which endpoint would you like to set as default?** The `cloud-*`
      endpoint for your preferred region group. For example, to use the US
      region group, use `cloud-us`.

   The command requires an email and password login. If you log in to Fauna
   using GitHub or Netlify, you can enable email and password login using the
   [Forgot Password](https://dashboard.fauna.com/forgot-password) workflow.

4. Use the Fauna CLI to create the `ECommercePython` database:

    ```sh
    fauna create-database ECommercePython
    ```

5. Create a
   [`.fauna-project`](https://docs.fauna.com/fauna/current/tools/shell/#proj-config)
   config file for the project:

   ```sh
   fauna project init
   ```

   When prompted, enter:

    * `schema` as the schema directory.
    * `dev` as the environment name.
    * The default endpoint.
    * `ECommercePython` as the database.

6.  Push the `.fsl` files in the `schema` directory to the `ECommercePython`
    database:

    ```sh
    fauna schema push
    ```

    When prompted, accept and stage the schema.

7.  Check the status of the staged schema:

    ```sh
    fauna schema status
    ```

8.  When the status is `ready`, commit the staged schema to the database:

    ```sh
    fauna schema commit
    ```

    The commit applies the staged schema to the database. The commit creates the
    collections and user-defined functions (UDFs) defined in the `.fsl` files of the
    `schema` directory.

9. Create a key with the `server` role for the `ECommercePython` database:

    ```sh
    fauna create-key --environment='' ECommercePython server
    ```

   Copy the returned `secret`. The app can use the key's secret to authenticate
   requests to the database.

## Run the app

The app runs an HTTP API server. From the root directory, run:

```sh
cd ecommerce_app
FAUNA_SECRET=<secret> python -m flask run
```

Once started, the local server is available at http://localhost:5000

The script `./tests/validate.sh` has some example HTTP requests.


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

Python unit tests:
```sh
python3 -m unittest discover -s tests
```