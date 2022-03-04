from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
import boto3
import random
import logging
from boto3.dynamodb.conditions import Key
import requests
from botocore.exceptions import ClientError


aws_access_key_id = AKIAY6STFUS6YT2W2AXC
aws_secret_access_key = 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


def findRestaurantFromElasticSearch(cuisine):
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    #awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    awsauth = ('restaurant-es','Restaurant@123')
    host = 'search-restaurant-es-26n4yztnz25scofxictuq7u464.us-east-1.es.amazonaws.com'
    index = 'restaurants'
    url = 'https://' + host + '/' + index + '/_search'
    query = {
        "size": 1600,
        "query": {
            "query_string": {
                "default_field": "genres",
                "query": cuisine
            }
        }
    }
    headers = { "Content-Type": "application/json" }
    response = requests.get(url,auth=awsauth, headers=headers, data=json.dumps(query))
    res = response.json()
    noOfHits = res['hits']['total']
    hits = res['hits']['hits']
    buisinessIds = []
    for hit in hits:
        buisinessIds.append(str(hit['_source']['id']))
    return random.sample(buisinessIds, 3)



def getRestaurantFromDb(restaurantIds):
    res = []
    client = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
    table = client.Table('yelp-restaurants')
    for id in restaurantIds:
        response = table.query(
        KeyConditionExpression=Key('id').eq(id))
        
        res.append(response)
        z = []
        for val in res:
            z.append([val['Items'][0]['name'],val['Items'][0]['address']])
    return z



def sendEmail(restaurants,recommendationRequest):
    
    ses_client = boto3.client("ses", region_name="us-east-1")
    
    CUISINE=recommendationRequest['Cuisine']['stringValue']
    PEOPLE=recommendationRequest['People']['stringValue']
    DATE=recommendationRequest['Date']['stringValue']
    TIME=recommendationRequest['Time']['stringValue']
    
    SUBJECT = "Restaurant Recommendations for you!"
    BODY_TEXT = "Hello! Here are my " + str(CUISINE) + " restaurant suggestions for " + str(PEOPLE) + " people, for " + str(DATE) + " at " + str(TIME) + "\n\n" + "1. " + str(restaurants[0][0]) + ", located at " + str(restaurants[0][1]) + "\n\n" + "2. " + str(restaurants[1][0]) + ", located at " + str(restaurants[1][1]) + "\n\n" + "3. " + str(restaurants[2][0]) + ", located at " + str(restaurants[2][1]) + "\n\n" + "Enjoy your meal!"
    CHARSET = "UTF-8"

    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                "gandhiakshit07@gmail.com",
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": BODY_TEXT,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": SUBJECT,
            },
        },
        Source="gandhiakshit99@gmail.com",
    )   
   
        


def lambda_handler(event, context):
    
    recommendationRequest = event['Records'][0]['messageAttributes']
    cuisine=recommendationRequest['Cuisine']['stringValue']
    
    ids = findRestaurantFromElasticSearch(cuisine)
    restaurants = getRestaurantFromDb(ids)
    
    response = sendEmail(restaurants,recommendationRequest)
    
    return {
        'statusCode': 200,
        'body': response
    }