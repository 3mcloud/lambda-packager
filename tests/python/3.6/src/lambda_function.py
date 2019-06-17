import requests


def lamda_handler(event, context):
    r = requests.get('https://google.com')
    return "hello world, " + r.status_code
