""" Works with digital ocean servers """
from requests import get
import digitalocean


class DoHandler(digitalocean.Manager):
    my_ip = ''

    def __init__(self):
        self.my_ip = get('https://api.ipify.org').text
        super(DoHandler).__init__()



