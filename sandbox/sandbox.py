# mike11860@gmail.com:audrey12ben => nordvpnpass

# digital ocean token: 30481e4713012f917ea4f36b95a5528da83493b396e44142336d992aa6e5bc8a
import logging
import threading
import time
import concurrent.futures


def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    case = 2
    if case == 1:
        logging.info("Main    : before creating thread")
        x = threading.Thread(target=thread_function, args=(1,), daemon=True)
        logging.info("Main    : before running thread")
        x.start()
        logging.info("Main    : wait for the thread to finish")
        x.join()
        logging.info("Main    : all done")
    elif case == 2:
        print('second')

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(thread_function, range(3))


#  find ip and location

import geoip # pip install python-geoip
import pygeoip # pip install 
from geoip import geolite2
import urllib.request
from requests import get

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
print(external_ip)

ip = get('https://api.ipify.org').text

match = geolite2.lookup(ip)
print('Country: '+ match.country)
print('timezone: '+ match.timezone)


from ip2geotools.databases.noncommercial import DbIpCity
response = DbIpCity.get('147.229.2.90', api_key='free')
response.ip_address
response.country
