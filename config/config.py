import os

PRODUCTION = os.environ['ENVIRONMENT']
if PRODUCTION == 'production_do':
    base_url = 'http://165.227.65.164:8001/'
elif PRODUCTION == 'production_aws':
    # base_url = 'http://3.84.206.7:8000/'
    base_url = 'http://3.84.206.7:8004/'
else:
    base_url = 'http://localhost:8002/'
urls = {
    'get-all-servers': base_url + "cloud/get-all-servers",
    'change-server': base_url + 'cloud/change-server',
    'change-dns': base_url + 'cloud/change-dns',
    'find-new-drop': base_url + 'cloud/find-new-drop',
    # 'get-all-servers': base_url + "mtph/get-all-servers",
    # 'change-server': base_url + 'mtph/change-server',
}
print(urls)