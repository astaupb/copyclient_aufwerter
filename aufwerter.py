import os
import paypalrestsdk
import logging
import json
from flask import Flask, render_template, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
@app.route("/")
def home():
    return render_template("home.html")

# creates a paypal payment for the value provided in the url
@app.route("/create/<value>")
def create(value):
    try:
        intvalue = int(value)
    except (ValueError, TypeError) as err:
        print("could not parse proper int from url, ", err)
        return Response(status=400, response="not a number")
    print("Creating transaction for {}.00€".format(intvalue))
    if check_value(intvalue):
        approval_url = create_payment("{}.00".format(intvalue))
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
    except:
        print("not enough valid query arguments")

    stuff = "payment_id: {}, token: {}, payer_id: {}".format(
        payment_id, token, payer_id)
    print(stuff)
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        print("Payment executed successfully")
        return "Payment successful"
    else:
        print(payment.error)  # Error Hash
        return "Error"


@app.route("/cancel")
def cancel():
    try:
        token = request.args.get("token")
    except:
        print("no valid query arguments supplied")

    print(token)

    return "Ayy, got cancelled"


# FUNCTIONS

# creates paypal payment for specified price in dotted decimal format
# returns corresponding approval_url aka the buying link
def create_payment(price):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://127.0.0.1:5000/success",
            "cancel_url": "http://127.0.0.1:5000/cancel"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "item",
                    "sku": "item",
                    "price": price,
                    "currency": "EUR",
                    "quantity": 1}]},
            "amount": {
                "total": price,
                "currency": "EUR"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print("payment created successfully")
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
