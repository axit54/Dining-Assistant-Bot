import json
import boto3

def lambda_handler(event, context):
  
  lexClient = boto3.client('lex-runtime')
  
  lexResponse = lexClient.post_text(
      botName='DiningConcierge', 
      botAlias='Prod', 
      userId='amg', 
      inputText=event['messages'][0]['unstructured']['text']
    )
  
  response = {
     "headers": {
            'Access-Control-Allow-Headers' : 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },

    "messages": [
      {
        "type": "unstructured",
        "unstructured": {
          "id": 1,
          "text":  lexResponse['message']
        }
      }
    ]
  }
  
  return response
  
