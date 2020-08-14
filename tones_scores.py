from flask import Flask, jsonify, request
import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pandas as pd
from ibm_watson import ApiException
from elasticsearch import Elasticsearch 


df = pd.read_csv('wuzzf.csv')
df = df[df.categories == 'Hotels']
apikey = 'zTX1zlvOnIQfwCQ_HQHA9zF8iQxCg25DDqudKdG3HlGd'
url = 'https://api.eu-gb.tone-analyzer.watson.cloud.ibm.com/instances/e6a5b86b-3f53-4e37-b6e3-1943c084a331'
authenticator = IAMAuthenticator(apikey)
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)

d
tones = {}
errors = []
for hotel in df['name'].unique():
    try:
        tones[hotel] = get_hotel_tones(hotel)
    except ApiException as ex:
        errors.append(hotel)
        print ("Method failed with status code " + str(ex.code) + ": " + ex.message)
with open('tones.json', 'w') as fp:
    json.dump(tones, fp)
