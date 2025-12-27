import requests
#this imports the requests library to make HTTP requests to the Microsoft Translator API
from flask_babel import _ , current_app
#this imports the _ function from flask_babel for translations
from app import current_app #importing the app instance from the app package

def translate(text, source_language, dest_language):

    #this function translates text from source_language to dest_language using the Microsoft Translator API
    if 'MS_TRANSLATOR_KEY' not in current_app.config or not \
           current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    #this checks if the MS_TRANSLATOR_KEY is set in the app config

    source_language = source_language.split("_")[0] #en_US -> en
    dest_language = dest_language.split("_")[0]     #es_ES -> es
    
    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': current_app.config['MS_TRANSLATOR_REGION']
    }
    #this sets up the authentication headers for the API request
    #the translatory requires an API key and a region header for authentication
    #the region is set to 'global' for the Microsoft Translator service, but it may vary based on your subscription
    

    #the dictionary from the config file is passed as the headers argument to the requests.post() method
    r = requests.post(
        'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from={}&to={}'.format(
            source_language, dest_language), headers=auth, json=[{'Text': text}])
    #this makes a HTTP POST request to the Microsoft Translator API's translate endpoint(first argument)
    #second argument is the headers(api key and region)
    #the third argument is the JSON payload containing the text to be translated

    if r.status_code != 200:
        return _('Error: the translation service failed.')
    #this checks if the request was successful
    return r.json()[0]['translations'][0]['text']
    #this extracts and returns the translated text from the API response
    #the response is in JSON format, and we navigate through the structure to get the translated text
    #r.json() converts the response to a Python list,
    #[0] accesses the first item in the list
    #'translations'[0] accesses the first translation in the translations array
    #'text' gets the actual translated text string