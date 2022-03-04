import boto3
import csv


dynamodb = boto3.resource(service_name='dynamodb',
                          aws_access_key_id="",
                          aws_secret_access_key="",
                          region_name="us-east-1",
                          endpoint_url="http://dynamodb.us-east-1.amazonaws.com")
table = dynamodb.Table('yelp-restaurants')

with open('restaurant_details.csv', newline='') as f:
    reader = csv.reader(f)
    restaurants = list(reader)

for restaurant in restaurants:  
    try:
	    table1 = {
	        'id': restaurant[0],
	        'name': restaurant[1],
	        'address': restaurant[2],
	        'coordinate_val': restaurant[3],
	        'display_phone': restaurant[4],
	        'genre': restaurants[5],
	        'price': restaurant[6],
	        'rating': restaurant[7],
	        'review_count': restaurant[8]
	    }                
	    
	    table.put_item(
	        Item={
	            'id': table1['id'],
	            'name': table1['name'],
	            'address': table1['address'],
	            'coordinate_val': table1['coordinate_val'],
	            'display_phone': table1['display_phone'],
		        'genre': table1['genre'],
		        'price': table1['price'],
		        'rating': table1['rating'],
		        'review_count': table1['review_count'],
	           }
	        )
	except:
		print(restaurant)
