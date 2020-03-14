import subprocess
import json
from os import system
import requests
import concurrent.futures
import functools
import time
import platform
import logging
from config import config, fake_ips


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('debug.log')
# file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
# logger.addHandler(stream_handler)


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    ResetAll = "\033[0m"

    Bold = "\033[1m"
    Dim = "\033[2m"
    Underlined = "\033[4m"
    Blink = "\033[5m"
    Reverse = "\033[7m"
    Hidden = "\033[8m"

    ResetBold = "\033[21m"
    ResetDim = "\033[22m"
    ResetUnderlined = "\033[24m"
    ResetBlink = "\033[25m"
    ResetReverse = "\033[27m"
    ResetHidden = "\033[28m"

    Default = "\033[39m"
    Black = "\033[30m"
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Magenta = "\033[35m"
    Cyan = "\033[36m"
    LightGray = "\033[37m"
    DarkGray = "\033[90m"
    LightRed = "\033[91m"
    LightGreen = "\033[92m"
    LightYellow = "\033[93m"
    LightBlue = "\033[94m"
    LightMagenta = "\033[95m"
    LightCyan = "\033[96m"
    White = "\033[97m"

    BackgroundDefault = "\033[49m"
    BackgroundBlack = "\033[40m"
    BackgroundRed = "\033[41m"
    BackgroundGreen = "\033[42m"
    BackgroundYellow = "\033[43m"
    BackgroundBlue = "\033[44m"
    BackgroundMagenta = "\033[45m"
    BackgroundCyan = "\033[46m"
    BackgroundLightGray = "\033[47m"
    BackgroundDarkGray = "\033[100m"
    BackgroundLightRed = "\033[101m"
    BackgroundLightGreen = "\033[102m"
    BackgroundLightYellow = "\033[103m"
    BackgroundLightBlue = "\033[104m"
    BackgroundLightMagenta = "\033[105m"
    BackgroundLightCyan = "\033[106m"
    BackgroundWhite = "\033[107m"


class IpHandler:
    ips = []
    conf_id = []
    my_ip = ''
    ips_not_in_dns = list()
    number_of_threads = 0
    up_list = []
    checking_list = []
    down_list = []

    def get_ips(self):
        self.check_net_connectivity()
        """gets a list of ips related to the servers"""
        url = config.URLS['get-all-servers']
        # url = "http://ff18da60.ngrok.io/mtph/get-all-servers"
        response = requests.get(url)

        self.conf_id = response.json()
        self.ips = [item['ip'] for item in self.conf_id]
        logger.info(f'ips fetched: {self.ips}')

    def get_id_by_ip(self, ip):
        self.check_net_connectivity()
        for item in self.conf_id:
            if item['ip'] == ip:
                id = item['id']
                return id

    def check_ip(self, server, lock):
        """
        pings each ip and return a boolean
        :return: Boolean
        """

        ip = server['ip']

        status = self.fping(ip)
        if status:
            if ip not in self.up_list:
                self.up_list.append(ip)
            up_count = len(self.up_list)
            not_count = len(self.ips_not_in_dns)
            failure_stage_count = len(self.checking_list)
            total = up_count + not_count + failure_stage_count
            print(f'{Colors.OKGREEN}U:{up_count}, Fs:{failure_stage_count} N:{not_count}, T:{total} '
                  f'*************************{ip} is up ***************************** {Colors.ENDC}')
            if ip in self.ips_not_in_dns:
                print(f"{Colors.OKBLUE}Adding {ip} to dns was failed before. Now trying to add again.{Colors.ENDC}")
                res = self.change_dns(action='add', lock=lock, new_ip=ip)
                if ip not in self.up_list:
                    self.up_list.append(ip)
                self.ips_not_in_dns.remove(ip)
                logger.info(f'ips not in dns: {self.ips_not_in_dns}')
                print(f'# of ips not in dns: {len(self.ips_not_in_dns)}')
            time.sleep(30)
            return server
        else:
            ip_timing_status = ip in self.ips_not_in_dns
            if ip not in self.checking_list and not ip_timing_status:
                self.checking_list.append(ip)
            timing = {
                'count': 1 if ip_timing_status else 2,
                'delay': 1 if ip_timing_status else 2
            }

            ip_is_up = self.certainty_check(server, ip, count=timing['count'], delay=timing['delay'])
            if ip_is_up:
                self.checking_list.remove(ip)
                return server
            old_server = server
            # TODO: (3): What if this is the only ip?
            # TODO: Adding error log here.
            if ip_timing_status:
                print(f'{Colors.LightRed}*************************** {ip} is down *****************************{Colors.ENDC}')
                self.ips_not_in_dns.remove(ip)
            else:
                if ip in self.up_list:
                    self.up_list.remove(ip)

                print(f'{Colors.FAIL}*************************** {ip} is down *****************************{Colors.ENDC}')
                logger.info(f"Removing {old_server['ip']} from dns")
                self.change_dns('remove', lock, old_ip=old_server['ip'])
            # todo (5): Handling failure.
            new_server = self.change_server_by_id(old_server['id'])
            logger.info(f"New Server Created with ip: {new_server['ip']}")
            if ip in self.checking_list:
                self.checking_list.remove(ip)
            # new_server = self.find_new_drop_by_ip(ip)
            if not new_server:
                logger.info('No server created before. So continue running with old server.')
                # todo (8): Should we add dns again?
                return server

            # todo (6): what if first checks fails and other passes.
            self.fping(new_server['ip'])
            time.sleep(5)
            status = self.fping(new_server['ip'])
            if status:
                logger.info(f"{Colors.OKBLUE}{new_server['ip']} is checked and working. prepare to add to dns{Colors.ENDC}")
                # else only pass the ip to check and change without changing dns

                res = self.change_dns(action='add', lock=lock, new_ip=new_server['ip'])
                time.sleep(30)
            else:
                if new_server['ip'] not in self.ips_not_in_dns:
                    logger.info(f"{new_server['ip']} just created but has failed.")
                    self.ips_not_in_dns.append(new_server['ip'])
                    logger.info(f'ips not in dns: {self.ips_not_in_dns}')
                    print(f'# of ips not in dns: {len(self.ips_not_in_dns)}')

            return [old_server, new_server]

    def certainty_check(self, server, ip, count=3, delay=3):
        self.check_net_connectivity()
        additional_check = False
        while count > 0:
            print(f'{Colors.WARNING}checking again for certainty: {count} remaining for ip: {ip}{Colors.ENDC}')
            additional_check = self.fping(ip)
            count -= 1
            time.sleep(delay)
            # if additional_check:
            #     return server
        return additional_check

    def make_threads(self):
        """make threads for each of ips"""
        import threading
        self.number_of_threads = len(self.ips)
        print('making %s threads' % self.number_of_threads)
        lock = threading.Lock()
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:

            for server in self.conf_id:
                fu = executor.submit(self.check_ip, server, lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=self.conf_id.index(server), lock=lock))

    def _future_completed(self, future, **kwargs):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            index = 'no index'
            if 'index' in kwargs:
                index = kwargs['index']
            lock = kwargs['lock']
            result = future.result()
            if result.__class__.__name__ == 'list':
                # server failed and a new one is created.
                old_server = result[0]
                new_server = result[1]
                logger.info(f'new server is created:{new_server}')
                index = self.conf_id.index(old_server)
                self.conf_id[index] = new_server

                fu = executor.submit(self.check_ip, self.conf_id[index], lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=index, lock=lock))
                return fu
            else:
                # server is up
                server = result

                index = self.conf_id.index(server)
                fu = executor.submit(self.check_ip, self.conf_id[index], lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=index, lock=lock))
                return fu

    def ping(self, ip, check_net=True):
        if check_net:
            self.check_net_connectivity()
        output = subprocess.Popen(["ping.exe", ip], stdout=subprocess.PIPE).communicate()[0]
        if str(output).count('Request timed out') > 1:
            return False
        return True

    def fping(self, ip, packet_count=15, check_net=True):
        if check_net:
            self.check_net_connectivity()
        cmd = ['fping', '-c', str(packet_count)]
        cmd.append(str(ip))
        ping = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = ping.communicate()
        out = str(output[-1])
        if '%,' in out:
            res = out.split('%,')[0]
            res = res.split("/")[-1]
        else:
            res = out.split('=')
            res = res[-1].split('%')[0]
            res = res.split("/")[-1]
        status = True
        if int(res) >= 50:
            status = False
            return status
        return status

    def check_net_connectivity(self):
        net_status = self.ping('www.google.com', check_net=False)
        while not net_status:
            print('internet connection problem')
            net_status = self.ping('www.google.com')
            time.sleep(5)
        return net_status

    def change_server_by_id(self, id):
        self.check_net_connectivity()
        url = config.URLS['change-server']
        _data = {
            'id': id,
        }
        data = json.dumps(_data)
        response = requests.post(url, data)
        new_serve = response.json()
        logger.info('New server: ', new_serve)
        return new_serve

    def change_dns(self, action, lock, **kwargs):
        self.check_net_connectivity()
        lock.acquire()
        url = config.URLS['change-dns']
        _data = dict()
        if 'old_ip' in kwargs:
            _data['old_ip'] = kwargs['old_ip']
        if 'new_ip' in kwargs:
            _data['new_ip'] = kwargs['new_ip']
        _data['action'] = action
        data = json.dumps(_data)
        response = requests.post(url, data)
        lock.release()
        return response

    def find_new_drop_by_ip(self, ip):
        self.check_net_connectivity()
        url = config.URLS['find-new-drop']
        _data = {
            'old_ip': ip
        }
        data = json.dumps(_data)
        response = requests.post(url, data)
        new_server = response.json()
        return new_server

    def api_request(self, url):
        response = requests.get(url)
        return response


def main():
    """running part of the script"""
    ip_handler = IpHandler()
    ip_handler.get_ips()

    ip_handler.make_threads()


if __name__ == '__main__':
    main()
