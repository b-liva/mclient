import random
from os import system
import concurrent.futures
import config
import time

from _thread import start_new_thread


class IpHandler:
    ips = []

    def get_ips(self):
        """gets a list of ips related to the servers"""
        print('get the list of ips from each service(Amazon, Digital ocean, ...)')
        self.ips = config.ips
        print(self.ips)

    def check_ip(self, ip):
        """
        pings each ip and return a boolean
        :return: Boolean
        """
        # for i in range(6):
        while True:
            print('now pinging: %s' % ip)
            status = self.ping(ip)
            if status:
                print('********************************** ', ip, ' is up ************************************')
                # print(status)
                time.sleep(60)
            else:
                print('********************************** ', ip, ' is down **********************************')
                old_ip = ip
                new_ip = self.change_server_with_ip(old_ip)
                print('new ip: ', new_ip)
                self.ips.append(new_ip)
                index = self.ips.index(old_ip)
                print('deleting: ', index)
                del(self.ips[index])
                print('ip counts: ', len(self.ips), self.ips)
                # print('new ips: ', self.ips)
                return new_ip

    def make_threads(self):
        """make threads for each of ips"""
        print('making %s threads' % len(self.ips))
        threads_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # results = executor.map(self.check_ip, self.ips)
            results = [executor.submit(self.check_ip, ip) for ip in self.ips]
            for f in concurrent.futures.as_completed(results):
                res = f.result()
                print('++++++++++++++ ', res)

                self.thread_generator(executor, f)
                # if res:
                #     results.append(executor.submit(self.check_ip, res))
                #     for x in concurrent.futures.as_completed(results):
                #         new_res = x.result()
                #         if new_res:
                #             results.append(executor.submit((self.check_ip, new_res)))

    def make_thread(self, ip):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            ex = executor.submit(self.check_ip, ip)
            return ex.result()

    def make_t_hand(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            t0 = executor.submit(self.check_ip, self.ips[0])
            t1 = executor.submit(self.check_ip, self.ips[1])
            # t2 = executor.submit(self.check_ip, self.ips[2])
            # t3 = executor.submit(self.check_ip, self.ips[3])
            # t4 = executor.submit(self.check_ip, self.ips[4])
            if t0.result():
                t0 = executor.submit(self.check_ip, t0.result())
                if t0.result():
                    t0 = executor.submit(self.check_ip, t0.result())
                    if t0.result():
                        t0 = executor.submit(self.check_ip, t0.result())
            if t1.result():
                t1 = executor.submit(self.check_ip, t1.result())
                if t1.result():
                    t1 = executor.submit(self.check_ip, t1.result())
                    if t1.result():
                        t1 = executor.submit(self.check_ip, '172.217.250.164')

            self.thread_generator(executor, t0)
            self.thread_generator(executor, t1)
            # self.make_t_hand()

    def thread_generator(self, executor, response):
        if response.result():
            th = executor.submit(self.check_ip, response.result())
            self.thread_generator(executor, th)

    def ping(self, ip):
        response = system('ping ' + ip)
        if response == 0:
            return True
            # return True
        elif response == 1:
            return False

    def change_server_with_ip(self, ip):
        """if an ip ping shows a failure then a request will be sent to the webapp to change the corresponting server"""
        print('Make a request to change the server with ip: ', ip)
        new_ip = str(int(200 * random.random())) \
                 + '.' + str(int(1000 * random.random())) \
                 + '.' + str(int(1000 * random.random())) \
                 + '.' + str(int(1000 * random.random()))
        return new_ip


def main():
    """running part of the script"""
    ip_handler = IpHandler()
    ip_handler.get_ips()
    # ip_handler.make_threads()
    ip_handler.make_t_hand()
    # ping_ips()


if __name__ == '__main__':
    main()
