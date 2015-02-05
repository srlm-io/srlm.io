---
layout: post
title: Sequelize Association Subquery Examples
---

[Sequelieze](http://sequelizejs.com/) is a great tool for database ORM mapping in Node.js, but it can have a pretty steep learning curve. In this post we go over some useful patterns related to subqueries in SQL, and their Sequelize equivelents.

## Background

We'll set up a pretty basic customer ordering system. We start with the Sequelize boilerplate:


``` js
'use strict';

var Sequelize = require('sequelize');
var sequelize = new Sequelize(/*database*/'test', /*username*/'test', /*password*/'test',
    {host: 'localhost', dialect: 'postgres'});
```

Then we create a simple Customer relation:

``` js
var Customer = sequelize.define('Customer', {
    firstName: {type: Sequelize.STRING},
    lastName: {type: Sequelize.STRING}
});
```

And a simple Order relation, and [associate](http://sequelize.readthedocs.org/en/latest/docs/associations/) them:

``` js
var Order = sequelize.define('Order', {
    amount: {type: Sequelize.FLOAT}
});

Customer.hasMany(Order, {constraints: true});
Order.belongsTo(Customer, {constraints: true});
```

And a handy print method so we can see what we get. Why don't we just `console.dir(results)`? Because Sequelize will wrap the results, and by calling `toJSON()` on each instance we get a much cleaner output.

``` js
function displayResults(results) {
    results.forEach(function (c) {
        console.dir(c.toJSON());
    });
    console.log('------------------------------------');
}
```

Finally, we put some data into our database and get ready for testing:

``` js
var firstCustomer;
var secondCustomer;

sequelize.sync({force: true})
    .then(function () {
        return Customer
            .create({firstName: 'Test', lastName: 'Testerson'});
    })
    .then(function (user1) {
        firstCustomer = user1;
        return Customer
            .create({firstName: 'Invisible', lastName: 'Hand'});
    })
    .then(function (user2) {
        secondCustomer = user2;
        return Order
            .create({CustomerId: firstCustomer.id, amount: 5});
    })
    .then(function () {
        return Order
            .create({CustomerId: firstCustomer.id, amount: 10});
    })
    .then(function () {
        return Order
            .create({CustomerId: firstCustomer.id, amount: 20})
    })
    .then(function () {
        return Order
            .create({CustomerId: secondCustomer.id, amount: 99});
    })
    /*
          Query testing code here
    */
    .then(function () {
        process.exit(0);
    });
```

And our package.json:

``` json
{
  "name": "sequelizedemo",
  "version": "0.0.1",
  "scripts": {
    "start": "nodejs index.js"
  },
  "dependencies": {
    "sequelize": "latest",
    "pg": "latest",
    "pg-hstore": "latest",
    "lodash": "latest"
  }
}
```

At this point you should be able to run the program (`nodejs index.js`) and not have any errors.

## Sequelize Subqueries

What if we want the total order amount for each user?

``` js
.then(function () {
    return Order.findAll({
        attributes: [
            [sequelize.fn('SUM', sequelize.col('amount')), 'totalAmount'],
            'CustomerId'],
        group: ['CustomerId']
    });
})
.then(displayResults)
```
``` sql
SELECT SUM("amount") AS "sum", "CustomerId" FROM "Orders" AS "Order" GROUP BY "CustomerId";
```

Of course, that's not really a subquery. But what if we wanted this information with the customer profile? Let's compose our SQL query by hand and have Sequelize execute it:

``` js
.then(function () {
    return sequelize.query(
        'SELECT *, (SELECT SUM("Orders"."amount") FROM "Orders" WHERE "Orders"."CustomerId" = "Customer"."id") AS "totalAmount" FROM "Customers" AS "Customer";',
        Customer,
        {raw: false}
    );
})
.then(displayResults)
```

This does a couple of things:

1. On the SQL side, for each result in the Customer table, it finds the `SUM` of Order's `amount` and stores it as `totalAmount`
2. The second [two parameters](http://sequelize.readthedocs.org/en/latest/api/sequelize/#querysql-callee-options-replacements-promise) tell Sequelize to wrap the raw database results into `Customer` objects, which will allow us to call instance methods on them.

While this works, it's not very flexible. We would much rather be able to do all sorts of complex where conditions and include options and sort by and orders, all without worrying about having to build the SQL ourselves.

So, let's make it an attribute on our query:

``` js
.then(function () {
    return Customer.findAll({
        attributes: Object.keys(Customer.attributes).concat([
            [
            sequelize.literal('(SELECT SUM("Orders"."amount") FROM "Orders" WHERE "Orders"."CustomerId" = "Customer"."id")'),
            'totalAmount'
            ]
        ])
    });
})
.then(displayResults)
```
``` sql
 SELECT "id", "firstName", "lastName", "createdAt", "updatedAt", (SELECT SUM("Orders"."amount") FROM "Orders" WHERE "Orders"."CustomerId" = "Customer"."id") AS "totalAmount" FROM "Customers" AS "Customer";
```

This produces the exact same result, but it's much cleaner. We could add in things like `where: {id: 2}` and still have the `totalAmount` in the result.

This example works because it tells Sequelize to put a [literal](http://sequelize.readthedocs.org/en/latest/api/sequelize/#literalval-sequelizeliteral) string into the output, and we set it up so that the extra subquery generated attribute is added onto the existing keys. The `Object.keys()` is required since Sequelize will filter by what's in the attribute list, and without the explicit key list the results would just include `totalAmount`.

Unfortunately, we can't take it one level further:

``` js
// Doesn't Work
.then(function(){
    return Customer.findAll({
        attributes: ['Customer.id'],
        include: [
            {
                model: Order,
                attributes: [[sequelize.fn('SUM', sequelize.col('amount')), 'totalAmount']]
            }
        ]
    })
})
.then(displayResults)
```
``` sql
SELECT "Customer"."id", "Customer"."id", "Orders"."id" AS "Orders.id", COUNT("amount") AS "Orders.cnt" FROM "Customers" AS "Customer" LEFT OUTER JOIN "Orders" AS "Orders" ON "Customer"."id" = "Orders"."CustomerId";
```

Notice that the SQL is completely messed up. Sequelize can't do everything.

Another trick is to add an instance method:

``` js
var Customer = sequelize.define('Customer', {
    firstName: {type: Sequelize.STRING},
    lastName: {type: Sequelize.STRING}
}, {
    instanceMethods: {
        getOrderSummary: function () {
            return Order.find({
                where: {
                    CustomerId: this.id
                },
                attributes: [[
                    sequelize.fn('SUM', sequelize.col('amount')), 
                    'totalAmount'
                    ]],
                group: ['CustomerId']
            });
        }
    }
});

 ...
 
.then(function () {
    return Customer.find({where: {id: 1}});
})
.then(function (customer) {
    return customer.getOrderSummary();
})
.then(function (customer) {
    console.dir(customer.toJSON());
})
```
```
{ totalAmount: 35 }
```

This does two seperate round trips to the database, which might be ok if you just want this extra information on occasion.

## Conclusion

I hope this helps you better use associations and subqueries in Sequelize.
