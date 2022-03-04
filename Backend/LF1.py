import json
import boto3
import re
import os
import datetime
import time

sqs = boto3.client('sqs')
queue = 'https://sqs.us-east-1.amazonaws.com/615428498621/Dining'
ok_stat = 200
bad_stat = 400
not_found = 404


def lambda_handler(event, context):
    type = "ElicitSlot"
    result = get_slots(event['currentIntent']['slots'])
    response = {
        "dialogAction": {}
    }
    if result["status"] != ok_stat:
        response['dialogAction']['type'] = 'ElicitSlot'
        response['dialogAction']['intentName'] = 'DiningSuggestionsIntent'
        response['dialogAction']['slots'] = event['currentIntent']['slots']
        response['dialogAction']['slotToElicit'] = result["slotToElicit"]
        if result["status"] == bad_stat:
            response['dialogAction']['message'] = dict()
            response['dialogAction']['message']['contentType'] = 'PlainText'
            response['dialogAction']['message']['content'] = result["message"]
    else:
        sendToSQS(event['currentIntent']['slots'])
        response['dialogAction']['type'] = 'Close'
        response['dialogAction']['fulfillmentState'] = 'Fulfilled'
        response['dialogAction']['message'] = dict()
        response['dialogAction']['message']['contentType'] = 'PlainText'
        response['dialogAction']['message']['content'] = 'Perfect! Expect my suggestions shortly.'
    return response


def get_slots(Slots):
    slotsNotFulfilled = None
    slots = ['Location', 'Cuisine', 'People', 'Date', 'Time', 'Email']
    for name in slots:
        if not Slots.get(name):
            slotsNotFulfilled = name
            return {"status": not_found, "slotToElicit": name, "message": ""}
        response = validate_values(slots, name, Slots[name])
        if response['status'] != ok_stat:
            return {"status": bad_stat, "slotToElicit": name, "message": response["message"]}
    return {"status": ok_stat, "slotToElicit": slotsNotFulfilled, "message": ""}



def validate_values(slots, name, value):
    response = {"status": ok_stat, "message": ""}
    if name == "Location":
        if value.lower() not in ['new york', 'ny', 'new york city', 'nyc', 'manhattan']:
            response = {"status": bad_stat, "message": "Unfortunately, we only serve in New York City"}
    elif name == "Cuisine":
        if value.lower() not in ['indian', 'mexican', 'chinese', 'japanese', 'korean']:
            response = {"status": bad_stat,
                        "message": "Please select a cuisine from the following options: Indian, Mexican, Chinese, Japanese and Korean"}
    elif name == "People":
        if int(value) not in range(1, 21):
            response = {"status": bad_stat, "message": "The number of people should be greater than 0 and less than 20"}
    elif name == "Date":
        if datetime.datetime.strptime(value, '%Y-%m-%d').date() < datetime.datetime.now().date():
            response = {"status": bad_stat, "message": "Sorry, time travel to the past does not exist yet! Please provide a day/date in the future"}
    elif name == "Email":
        if '@' not in value:  
            response = {"status": bad_stat, "message": "The email address provided is incorrect"}
    return response


def sendToSQS(slots):
   
    
    Location = slots['Location']
    Cuisine = slots['Cuisine']
    People = slots['People']
    Date = slots['Date']
    Time = slots['Time']
    Email = slots['Email']
    
    response = sqs.send_message(
        QueueUrl=queue,
        MessageAttributes={
                    'Cuisine': {
                        'DataType': 'String',
                        'StringValue': Cuisine
                    },
                    'Location': {
                        'DataType': 'String',
                        'StringValue': Location
                    },
                    'People': {
                        'DataType': 'String',
                        'StringValue': People
                    },
                    'Date': {
                        'DataType': 'String',
                        'StringValue': Date
                    },
                    'Time': {
                        'DataType': 'String',
                        'StringValue': Time
                    },
                    'Email': {
                        'DataType': 'String',
                        'StringValue': Email
                    }
            
        },
        MessageBody=("user"),
    )


