from flask import Flask, jsonify, request
import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pandas as pd
from ibm_watson import ApiException
from elasticsearch import Elasticsearch 
import pprint


df = pd.read_csv('wuzzf.csv')
df = df[df.categories == 'Hotels']
apikey = 'zTX1zlvOnIQfwCQ_HQHA9zF8iQxCg25DDqudKdG3HlGd'
url = 'https://api.eu-gb.tone-analyzer.watson.cloud.ibm.com/instances/e6a5b86b-3f53-4e37-b6e3-1943c084a331'
authenticator = IAMAuthenticator(apikey)
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)

tone_analyzer.set_service_url(url)

app = Flask(__name__)

@app.route('/<string:name>', methods=['GET'])
def Hotel_ToneAnalyzer(name):
    normal, counts = {}, {}
    tone_analysis = []
    text = ''
    text += ' '.join([ i for i in df[df.name == name]['reviews.text'].values
    if i != ''])

    try:
        # Invoke a Tone Analyzer method
        tone_analysis = tone_analyzer.tone(
            {'text': text},
            content_type='application/json'
        ).get_result()

        for d in tone_analysis['sentences_tone']:
            if d['tones'] == []:
                pass
            else:
                for tone in d['tones']:
                    tone_id = tone['tone_id']
                    score = tone['score']
                    if tone['tone_id'] in normal.keys():
                        counts[tone_id] += 1
                        normal[tone_id] += score
                        normal[tone_id] = round(normal[tone_id]/counts[tone_id],3)
                    else:
                        normal[tone_id] = tone['score']
                        counts[tone_id] = 1
    except ApiException as ex:
        print ("Method failed with status code " + str(ex.code) + ": " + ex.message)

    #return (json.dumps(tone_analysis, indent=2))
    return (json.dumps(normal, indent=2))

def prettyprint(lista):
    pp = pprint.PrettyPrinter(indent=4)
    lista = pp.pprint(lista)
    return lista

@app.route('/ES', methods=['GET'])
def Hotel_indexer():
    with open('tones.json') as json_file:
        to_j = json.load(json_file)
    es=Elasticsearch([{'host':'localhost','port':9200}])
    gh = df.groupby('name')
    hotel_data = {}
    d = {}
    res = []
    for name, group in gh:
        for i in group.columns:
            if i.startswith('review'):
                d[i] = str(group[i])
            else:
                d[i] = str(group[i].unique())
        d['tones_scores'] = to_j[name]
        es.index(index='megacorp',doc_type='hotel',id=name,body=d)
    hotel_names = df['name'].unique()
    
    for i in hotel_names:
        res.append(es.get(index='megacorp',doc_type='hotel',id=i))
    
    #result = ' '.join(map(str, res))
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True, port=8082) #run app on port 8080 in debug mode
