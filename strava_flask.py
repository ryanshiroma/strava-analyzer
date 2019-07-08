from flask import Flask, render_template, redirect, request, session, make_response
from stravalib.client import Client
import sys
import config
import base64
import json
import requests
from gmplot import gmplot
from statistics import mean
import polyline
import os 
import boto3
import time
import decimal

app = Flask(__name__,template_folder='templates')


client_id = config.client_id
app.secret_key = config.client_secret
app.config['SESSION_TYPE'] = 'filesystem'
@app.route('/')
@app.route('/index')
def index():
    if request.args.get('code'):
        #take code and convert to token
        code = request.args.get('code')
        token = token_exchange(code)

        #put athlete_id in cookie and upload  rest to dynamodb
        client=Client(token['access_token'])
        athlete_id=client.get_athlete().id
        session['athlete_id'] = athlete_id
        session['expires_at'] = token['expires_at']

        # put athlete/token information in dynamodb
        dynamodb = boto3.resource('dynamodb')
        db = dynamodb.Table('strava_table')
        try:
            entry = db.put_item(Item={
                    'athlete_id':athlete_id,
                    'code':code,
                    'access_token':token['access_token'],
                    'refresh_token':token['refresh_token'],
                    'expires_at':decimal.Decimal(token['expires_at'])})
        except: 
            render_template('index.html',auth_link=request.url_root+'authenticate')      
        return redirect(request.url_root+'map', code=302)  

    #if user is already authenticated and not expired
    if ('athlete_id' in session) and (time.time() < session['expires_at']):
        return render_template('index.html',auth_link=request.url_root+'map')   
    
    # load page for authentication
    return render_template('index.html',auth_link=request.url_root+'authenticate')

        

    
@app.route('/map')
def map():
    #return to index if user has no athlete_id cookie
    if 'athlete_id' not in session:
        return redirect(request.url_root)

    #get info from dynamodb with athlete_id
    athlete_id = session['athlete_id']
    dynamodb = boto3.resource('dynamodb')
    db = dynamodb.Table('strava_table')
    try:
        data = db.get_item(Key={'athlete_id':athlete_id})['Item']
    except:
        # return to index for authentication
        return redirect(request.url_root+'authenticate', code=302)
    
    #redirect to reauthenticate if token has expired
    if time.time() > data['expires_at']:
        return redirect(request.url_root+'authenticate', code=302)

    # create strava client and pull activities
    client = Client(data['access_token'])
    activities=list(client.get_activities())

    # add polylines
    gmap = gmplot.GoogleMapPlotter(0,0, 12,config.google_api_key)
    for i in reversed(range(len(activities))):
        try:
            pl=polyline.decode(activities[i].to_dict()['map']['summary_polyline'])
            lats,longs=zip(*pl)
            gmap.plot(lats,longs, 'cornflowerblue', edge_width=4)#,edge_alpha=0.3)
        except:
            print('no polyline for '+activities[i].to_dict()['name'])
    gmap.center = (mean(lats),mean(longs))

    #output maps html file and load back in as string form(kinda hacky since the draw() function only outputs files)
    file_name=str(athlete_id)+'.html'
    os.chdir('/tmp')
    gmap.draw(file_name)
    with open(file_name, 'r') as map_file:
        html_string = map_file.read()
    os.remove(file_name)
    return html_string


@app.route('/authenticate', methods=['GET', 'POST'])
def auth():
    base_url = config.auth_url + '?client_id=' + config.client_id + \
        '&response_type=code&redirect_uri=' + request.url_root + \
        '&scope='+config.scope +\
        '&approval_prompt='+config.approval_prompt
    response = make_response(redirect(base_url, 302))
    return response

def token_exchange(code):
    client = Client()
    token = client.exchange_code_for_token(client_id=config.client_id, client_secret=config.client_secret, code=code)
    return token

def refresh_token(refresh_token):
    client = Client()
    token = client.refresh_access_token(client_id=config.client_id, client_secret=config.client_secret, refresh_token=refresh_token)
    return token
