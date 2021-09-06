import requests

def shorten_url(long_url):
    url = 'https://api-ssl.bitly.com/v3/shorten'
    access_token = ''
    query = {
            'access_token': access_token,
            'longurl':long_url
            }
    r = requests.get(url,params=query).json()['data']['url']
    return r
