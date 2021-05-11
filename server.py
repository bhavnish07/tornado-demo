from abc import ABC, ABCMeta
from typing import Optional, Awaitable

import tornado
import psycopg2
from tornado import web, ioloop, gen
from config import config

params = config()


# This Handler used to render index.html
class MainRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("home.html")


# This Handler will List all entries from DB
class ListRequestHandler(tornado.web.RequestHandler):
    @gen.coroutine  # decorator to use yield to return next value
    def get(self):
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        yield cur.execute('select * from customer order by customer_id desc')  # fetching data from DB
        self.render('customer.html', cur=cur)


# This Handler will create a entry in DB
class CreateRequestHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        first = self.get_argument("first")
        last = self.get_argument("last")
        if first and last:
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            sql = "INSERT INTO customer (first_name, last_name) VALUES (%s, %s)"
            yield cur.execute(sql, (first, last))  # inserting values into DB
            conn.commit()
            conn.close()
        self.render('create_request.html', first=first, last=last)


if __name__ == "__main__":
    # Controller confurigation
    app = tornado.web.Application([
        (r"/customer/", ListRequestHandler),
        (r"/customer", ListRequestHandler),
        (r"/create", CreateRequestHandler),
        (r"/", MainRequestHandler),
    ])

    # Defining on which port application will run
    port = 8883
    app.listen(port)
    print(f"Application is listening on  {port}")
    tornado.ioloop.IOLoop.current().start()
