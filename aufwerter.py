import os
import paypalrestsdk
import logging
import json
import mysql.connector
from flask import Flask, render_template, request, Response
from flask_cors import CORS


# INITIALIZE FLASK

# base urls for production and debug
base_url = os.getenv("AUFWERTER_BASE_URL")
#base_url = "http://127.0.0.1:5000"

app = Flask(__name__)
CORS(app)

# INITIALIZE DATABASE

# get credentials from environment url
db_url = os.getenv("ASTAPRINT_DATABASE_URL")
db_url_split = db_url.split(':')
db_user = db_url_split[1].replace("/", "")
db_pw = db_url_split[2].split("@")[0]
db_host = db_url_split[2].split("@")[1]
db_port = db_url_split[3].split("/")[0]
db_name = db_url_split[3].split("/")[1]

# create connection for later
cnx = mysql.connector.connect(
    user=db_user, password=db_pw, host=db_host, port=db_port, database=db_name)
cursor = cnx.cursor()

# INITIALIZE PAYPAL

# credentials are loaded from environment variables
# `source environ.sh` in your shell to get them
client_id = os.getenv("PAYPAL_CLIENT_ID")
client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": client_id,
    "client_secret": client_secret},)


# ROUTES

# landing page with selection of credits
""" @app.route("/")
def home():
    return render_template("home.html") """

# creates a paypal payment for the value provided in the url
@app.route("/create/<value>")
def create(value):
    try:
        intvalue = int(value)
        user_id = int(request.args['user_id'])
    except (ValueError, TypeError) as err:
        print("could not parse proper int from url, ", err)
        return Response(status=400, response="not a number")
    print("Creating transaction for {}.00€".format(intvalue))
    if check_value(intvalue):
        approval_url = create_payment("{}.00".format(intvalue), user_id)
        print(" token: ", approval_url.split("=").pop())
        return json.dumps({"link": approval_url})
    else:
        return Response(status=400, response="number not valid for creating payment")


# route that gets called after successful payment and finally executes the payment
@app.route("/success")
def success():
    try:
        payment_id = request.args.get("paymentId")
        token = request.args.get("token")
        payer_id = request.args.get("PayerID")
        user_id = 12345  # TODO
    except:
        print("not enough valid query arguments")
        return Response(status=400, response="not enough query parameters specified for this")

    stuff = "Completing payment:\n payment_id: {},\n token: {},\n payer_id: {}".format(
        payment_id, token, payer_id)
    print(stuff)

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        print("Payment executed successfully")
        add_transaction = ("INSERT INTO journal "
                           "(user_id, credit, value, description, created) "
                           "VALUES ({}, {}, {}, {}, {})".format(user_id, "", "", "", ""))
        return render_template("success.html", id=payment.id)
    else:
        print(payment.error)  # Error Hash
        return Response(status=500, response="error while executing payment {}".format(payment_id))


@app.route("/cancel")
def cancel():
    try:
        token = request.args.get("token")
    except:
        print("no valid query arguments supplied")
        return Response(status=400, response="not enough query parameters specified for this")

    print("Cancelled payment:\n token: ", token)

    return render_template("cancel.html")


# FUNCTIONS

# creates paypal payment for specified price in dotted decimal format
# returns corresponding approval_url aka the buying link
def create_payment(price, user_id):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": "{}/success".format(base_url),
            "cancel_url": "{}/cancel".format(base_url),
        },
        "transactions": [
            {
                "item_list": {
                    "items": [{
                        "name": "top-{}-up".format(price),
                        "sku": "item",
                        "price": price,
                        "currency": "EUR",
                        "quantity": 1},
                    ],
                },
                "amount": {
                    "total": price,
                    "currency": "EUR",
                },
                "description": "Eine Aufladung von {}€ für deinen AStA Copyservice Account",
                "custom": user_id,
                "payment_options": {
                    "allowed_payment_method": "INSTANT_FUNDING_SOURCE"
                },
            }
        ]})

    if payment.create():
        print("Payment created successfully:")
    else:
        print(payment.error)

    for link in payment.links:
        if link.rel == "approval_url":
            approval_url = str(link.href)
            return approval_url


# check integer values for existence in natural numbers
# return true if integer is okay to create payment with
def check_value(value):
    if value < 1:
        return False
    return True
