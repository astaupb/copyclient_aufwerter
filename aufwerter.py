import os
import paypalrestsdk
import logging
from flask import Flask, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ROUTES

# landing page with selection of credits
@app.route("/")
def home():
    return render_template("home.html")

# creates a paypal payment for the value provided in the url
@app.route("/create/<transaction_height>")
def create(transaction_height):
    print("Creating transaction for {}.00€".format(transaction_height))
    if int(transaction_height) >= 1:
        approval_url = create_payment("{}.00".format(transaction_height))
        return approval_url


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
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox or live
        "client_id": client_id,
        "client_secret": client_secret},)

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
            # Convert to str to avoid Google App Engine Unicode issue
            # https://github.com/paypal/rest-api-sdk-python/pull/58
            approval_url = str(link.href)
            return approval_url
