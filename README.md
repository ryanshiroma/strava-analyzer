# Strava Mapper
*This is a project I worked on in March 2019 to learn the basic ideas of using APIs, AWS Lambda, AWS DynamoDB, and Flask in one combined project. It's still a work in progress.*

Strava Mapper is a web app deployed on AWS Lambda that maps out all of your previously run Strava workout routes on a single Google map. 

Try it out here: https://pwjwuiuj6i.execute-api.us-east-1.amazonaws.com/dev/


## Installation/Deployment Instructions
**1) Setup the virtual environment**
```
virtualenv --python=python3.7 env
pip install -r requirements.txt
```
**2) Clone the repo**
```
git clone https://github.com/ryanshiroma/strava-mapper
```
**3) Setup API access accounts**

You'll need to setup accounts with both Google and Strava to access their APIs.
Strava's API is free for use under 600 requests every 15 minutes with a maximum of 30,000 per day.
Google's Maps API is free for the first 28,000 calls per month and $7/1000 calls thereafter. 

Get the Google API key here:
https://developers.google.com/maps/documentation/javascript/get-api-key

and the Strava key here: 
http://developers.strava.com/

**4) Update the config.py file**

Plug in the required Strava and Google Maps API keys into the config.py file
```
client_id = '' # strava client id
client_secret = '' # strava client secret
google_api_key = '' # google maps api key
```

**5) Update the zappa_settings.json file**

Change the `s3_bucket` to to your own unique s3 bucket name. No need to create this bucket, Zappa will automatically create it for you in the next step.

**6) Deploy app with Zappa**

Deploy the app to AWS with a name(in this case `dev` but feel free to use whatever name you like):
```
zappa deploy dev
```
Copy down the deployed app link once the process finishes running.

**7) Update the Strava callback URL**

In order for the Strava authentication to work, you'll need to add the app link to the callback URL on the Strava API site.
https://www.strava.com/settings/api
Under `Authorization Callback Domain`, paste in the deployed app link **domain name only**.
`https://pwjwuiuj6i.execute-api.us-east-1.amazonaws.com/dev/` -> `pwjwuiuj6i.execute-api.us-east-1.amazonaws.com`

**8) Redeploy Updates**
If you make any changes to the code or settings, you can redeploy the app using the existing AWS resources with:
```
zappa update dev
```





