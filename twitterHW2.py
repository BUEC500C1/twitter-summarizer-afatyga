#EC500 HW 2
#Alex Fatyga

import keys
import tweepy

import io
import os
import urllib.request as req
import json

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

from datetime import datetime
# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%Y-%m-04")


def getImgDescription(file_name):
	client = vision.ImageAnnotatorClient()

#Loads the image into memory
	file_name = os.path.abspath(file_name)
	with io.open(file_name, 'rb') as image_file:
		content = image_file.read()
	image = types.Image(content=content)

    # Performs label detection on the image file
	response = client.label_detection(image=image)
	labels = response.label_annotations
	imgDescrip = "The following is detected: "
	length = len(labels)
	count = 0
	for label in labels:
	    imgDescrip = imgDescrip + label.description
	    count = count + 1
	    if ( count < (length -1 )):
	    	imgDescrip = imgDescrip + ", "
	    if (count == length - 1):
	    	imgDescrip = imgDescrip + " and "
	imgDescrip = imgDescrip + "."
	image = types.Image(content=content)
	response = client.face_detection(image=image)
	faces = response.face_annotations
	# Names of likelihood from google.cloud.vision.enums

	likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                   		'LIKELY', 'VERY_LIKELY')
	faceDet = ""
	numFace = 0
	for face in faces:
		numFace = numFace + 1
		if (likelihood_name[face.anger_likelihood] == "VERY_LIKELY" or likelihood_name[face.anger_likelihood] == "LIKELY"):
			faceDet = faceDet + " Anger is detected in face " + str(numFace) + "." 
		if (likelihood_name[face.joy_likelihood] == "VERY_LIKELY" or likelihood_name[face.joy_likelihood] == "LIKELY"):
			faceDet = faceDet + " Joy is detected in face " + str(numFace) + "."
		if (likelihood_name[face.surprise_likelihood] == "VERY_LIKELY" or likelihood_name[face.surprise_likelihood] == "LIKELY"):
			faceDet = faceDet + " Surprise is detected in face " + str(numFace) + "."

	return imgDescrip, faceDet


def getMsgs(username):

	if not isinstance(username,str): #can only input string
		return 0
	auth = tweepy.OAuthHandler(keys.key, keys.secretKey) #using key from keys file - blank in github
	auth.set_access_token(keys.accessToken, keys.accessTokenSecret)
	tweets = ""
	api = tweepy.API(auth)
	num = 0
	#use the following 2 lines for writing to json
	data = {}
	data['tweets'] = []
	try:	#will be an error if the username is valid
		for status in tweepy.Cursor(api.user_timeline,username).items(20): #gets past 20 tweets
			    
			tweetDateTime = str(status.created_at)
			dateTime = tweetDateTime.split()
			if (dateTime[0] == dt_string):
				#print(status.text)
				#print(status.user.screen_name)
				tweets = tweets + "\n" + status.text
				try:
					for link in status.entities['media']:
						url = str(link['media_url'])
						num = num +1
						file_name = "image_name" + str(num) + ".jpg"

						req.urlretrieve(url, file_name)
						labels, faceDet = getImgDescription(file_name)

						tweets = tweets + "\n" + labels + faceDet
						data['tweets'].append({
						'user': str(status.user.screen_name),
						'created at': str(status.created_at),
						'text': str(status.text),
						'media': {
							'labels': labels,
							'emotions detected': faceDet
						}

						})

				except (NameError, KeyError):        
					pass
					data['tweets'].append({
						'user': str(status.user.screen_name),
						'created at': str(status.created_at),
						'text': str(status.text) 
						})
#		print(tweets)
#		print(data)
		with open ('tweets.json', 'w') as outfile:
			json.dump(data, outfile)
		return 1
	except (tweepy.TweepError):
		return 0

getMsgs("alexfatyga_")