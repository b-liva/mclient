''' The config file for the project. All of the configs go here.
'''
import os

PRODUCTION = os.environ['ENVIRONMENT']
print(PRODUCTION)
if PRODUCTION == "production_aws":
    # BASE_URL = 'http://3.84.206.7:8000/'
    # BASE_URL = 'http://3.84.206.7:8004/'
    BASE_URL = 'http://52.90.251.144:8004/'
else:
    BASE_URL = 'http://localhost:8002/'
URLS = {
    'get-all-servers': BASE_URL + "cloud/get-all-servers",
    'change-server': BASE_URL + 'cloud/change-server',
    'change-dns': BASE_URL + 'cloud/change-dns',
    'find-new-drop': BASE_URL + 'cloud/find-new-drop',
    # 'get-all-servers': BASE_URL + "mtph/get-all-servers",
    # 'change-server': BASE_URL + 'mtph/change-server',
}
print(URLS)
