import os

PRODUCTION = os.environ['PRODUCTION']
if PRODUCTION == 'production':
    base_url = '165.227.65.164:8001/'
else:
    base_url = 'http://localhost:8002/'
urls = {
    'get-all-servers': base_url + "mtph/get-all-servers",
    'change-server': base_url + 'mtph/change-server',
}