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

- Python 3.9 or later.

- [Fauna CLI v4 beta](https://docs.fauna.com/fauna/current/build/cli/v4/) or later.
    - [Node.js](https://nodejs.org/en/download/) v20.x or later.

  To install the CLI, run:

    ```sh
    npm install -g fauna-shell@">=4.0.0-beta"
    ```

## Setup

1. Clone the repo and navigate to the `python-sample-app` directory:

    ```sh
    git clone git@github.com:fauna/python-sample-app.git
    cd python-sample-app
    ```
2. Setup a Python virtual environment, and install the requirements:

    ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. If you haven't already, log in to Fauna using the Fauna CLI:

    ```sh
    fauna login
    ```

4. Use the Fauna CLI to create the `ECommercePython` database:

    ```sh
    # Replace 'us' with your preferred Region Group:
    # 'us' (United States), 'eu' (Europe), or `global` (available to Pro accounts and above).
    fauna database create \
      --name ECommercePython \
      --database us
    ```

5.  Push the `.fsl` files in the `schema` directory to the `ECommercePython`
    database:

    ```sh
    # Replace 'us' with your Region Group.
    fauna schema push \
      --database us/ECommercePython
    ```

    When prompted, accept and stage the schema.

6.  Check the status of the staged schema:

    ```sh
    fauna schema status \
      --database us/ECommercePython
    ```

7.  When the status is `ready`, commit the staged schema to the database:

    ```sh
    fauna schema commit \
      --database us/ECommercePython
    ```

    The commit applies the staged schema to the database. The commit creates the
    collections and user-defined functions (UDFs) defined in the `.fsl` files of the
    `schema` directory.

8. Create a key with the `server` role for the `ECommercePython` database:

    ```sh
    fauna query "Key.create({ role: 'server' })" \
      --database us/ECommercePython
    ```

   Copy the returned `secret`. The app can use the key's secret to authenticate
   requests to the database.

## Add sample data

The app includes a seed script that adds sample documents to the
`ECommercePython` database. From the root directory, run:

```sh
chmod +x ./scripts/seed.sh
FAUNA_SECRET=<secret> ./scripts/seed.sh
```

You can view documents created by the script in the [Fauna
Dashboard](https://dashboard.fauna.com/).

## Run the app

The app runs an HTTP API server. From the root directory, run:

```sh
cd ecommerce_app
FAUNA_SECRET=<secret> python3 -m flask run
```

Once started, the local server is available at http://localhost:5000

## Make HTTP API requests

You can use the endpoints to make API requests that read and write data from
the `ECommercePython` database.

For example, with the local server running in a separate terminal tab, run the
following curl request to the `POST /customers` endpoint. The request creates a
`Customer` collection document in the `ECommercePython` database.

```sh
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
  }' | jq .
```

You can view the documents for the collection in the [Fauna
Dashboard](https://dashboard.fauna.com/).

## Expand the app

You can further expand the app by adding fields and endpoints.

As an example, the following steps adds a computed `totalPurchaseAmt` field to
Customer documents and related API responses:

1. Navigate to the project's root directory:

    ```sh
    cd ..
    ```

    If the app server is running, stop the server by pressing Ctrl+C.

2. If you haven't already, add the sample data:

    ```sh
    FAUNA_SECRET=<secret> ./scripts/seed.sh
    ```

3. In `schema/collections.fsl`, add the following `totalPurchaseAmt` computed
   field definition to the `Customer` collection:

    ```diff
    collection Customer {
      ...
      // Use a computed field to get the set of Orders for a customer.
      compute orders: Set<Order> = (customer => Order.byCustomer(customer))

    + // Use a computed field to calculate the customer's cumulative purchase total.
    + // The field sums purchase `total` values from the customer's linked Order documents.
    + compute totalPurchaseAmt: Number = (customer => customer.orders.fold(0, (sum, order) => {
    +   let order: Any = order
    +   sum + order.total
    + }))
      ...
    }
    ...
    ```

   Save `schema/collections.fsl`.

4.  Push the updated `.fsl` files in the `schema` directory to the `ECommercePython`
    database to stage the changes:

    ```sh
    fauna schema push \
      --database us/ECommercePython
    ```

    When prompted, accept and stage the schema.

5.  Check the status of the staged schema:

    ```sh
    fauna schema status \
      --database us/ECommercePython
    ```

6.  When the status is `ready`, commit the staged schema changes to the
    database:

    ```sh
    fauna schema commit \
      --database us/ECommercePython
    ```

7. In `ecommerce_app/models/customer.py`, add the `totalPurchaseAmt` field to
   the `Customer` class and `customerResponse()` method:

    ```diff
    @dataclass
    class Customer:
        id: str
        name: str
        email: str
        address: Address
        cart: Optional[Order]
    +   totalPurchaseAmt: int


    def customerResponse() -> Query:
    +    return fql("{id: customer.id, name: customer?.name, email: customer?.email, address: customer?.address, cart: ${getCart}, totalPurchaseAmt: customer?.totalPurchaseAmt}",
                  getCart=fql('if (customer?.cart != null) {id: customer?.cart?.id} else null'))
    ```

    Save `src/routes/customers/customers.controller.ts`.

    Customer-related endpoints use this template to project Customer
    document fields in responses.

7. Start the app server:

    ```sh
    cd ecommerce_app
    FAUNA_SECRET=<secret> python3 -m flask run
    ```

8.  With the local server running in a separate terminal tab, run the
    following curl request to the `POST /customers` endpoint:

    ```sh
    curl -v http://localhost:5000/customers/999 | jq .
    ```

    The response includes the computed `totalPurchaseAmt` field:

    ```json
    {
      "address": {
        "city": "Amsterdam",
        "country": "Netherlands",
        "postalCode": "1015BT",
        "state": "North Holland",
        "street": "Herengracht"
      },
      "cart": {
        "id": "417802633891286089"
      },
      "email": "fake@fauna.com",
      "id": "999",
      "name": "Valued Customer",
      "totalPurchaseAmt": 36000
    }
    ```

## Run unit tests
Some example unit tests in the `tests/` directory show how you can test a Python Flask app that uses Fauna.
```sh
python3 -m unittest discover -s tests
```
