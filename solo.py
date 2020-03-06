import subprocess
import concurrent.futures
import time
from config import anti_ips


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CheckIP:
    antis_list = anti_ips.ipds

    def make_threads(self):
        """make threads for each of ips"""
        import threading
        print('making %s threads' % len(self.antis_list))
        antis = anti_ips.ipds
        print(antis)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            for anti in self.antis_list:
                fu = executor.submit(self.check_ip, anti)

    def check_ip(self, anti):
        status = self.ping(anti['ip'])
        if status:
            print(f"{Colors.OKGREEN}***************************{anti['acc']}: {anti['ip']} is up *****************************{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}*************************** {anti['acc']}: {anti['ip']} is down *****************************{Colors.ENDC}")

    def ping(self, ip, check_net=True):
        if check_net:
            self.check_net_connectivity()
        output = subprocess.Popen(["ping.exe", ip], stdout=subprocess.PIPE).communicate()[0]
        if str(output).count('Request timed out') > 1:
            return False
        return True

    def check_net_connectivity(self):
        net_status = self.ping('www.google.com', check_net=False)
        while not net_status:
            print('internet connection problem')
            net_status = self.ping('www.google.com')
            time.sleep(5)
        return net_status


if __name__ == '__main__':
    ip_checker = CheckIP()
    ip_checker.make_threads()
