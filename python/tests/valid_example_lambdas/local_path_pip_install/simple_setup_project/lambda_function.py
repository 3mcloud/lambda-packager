import requests


def lamda_handler(event, context):
    r = requests.get('https://www.3m.com')
    return "hello world, " + r.status_code
