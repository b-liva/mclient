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
        i = 0
        print('now pinging: %s' % ip)
        status = self.ping(ip)
        if status:
            print('********************************** ', ip, ' is up ************************************')
            # print(status)
            i += 1
            print('#: ', i)
            time.sleep(60)
            return ip
        else:
            print('********************************** ', ip, ' is down **********************************')
            i += 1
            print('#: ', i)
            old_ip = ip
            new_ip = self.change_server_with_ip(old_ip)
            print('new ip: ', new_ip)
            # self.ips.append(new_ip)
            # index = self.ips.index(old_ip)
            # print('deleting: ', index)
            # del(self.ips[index])
            print('ip counts: ', len(self.ips), self.ips)
            # print('new ips: ', self.ips)
            # return {
            #     'old_ip': old_ip,
            #     'new_ip': new_ip,
            # }
            return [old_ip, new_ip]

    def make_threads(self):
        """make threads for each of ips"""
        print('making %s threads' % len(self.ips))
        threads_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.check_ip, self.ips)
            print('results: *************************************************', results)
            # results = [executor.submit(self.check_ip, ip) for ip in self.ips]
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

            futures_list = []
            for ip in self.ips:
                print('thread created for: ', ip)
                index = self.ips.index(ip)
                print('index: ', index)
                f = executor.submit(self.check_ip, self.ips[index])
                futures_list.append(f)

            for f in futures_list:
                index = futures_list.index(f)
                print('this is future: ', f)
                result = f.result()
                print('future results: ', result)
                if result:
                    print(result)
                    old_ip = result[0]
                    new_ip = result[1]
                    index = self.ips.index(old_ip)
                    self.ips[index] = new_ip
                    print(self.ips)

                    self.new_thread(executor, index)

            # for f in concurrent.futures.as_completed(results):
            # for f in results:
            #     index = results.index(f)
            #     result = f.result()
            #     if result:
            #         old_ip = result[0]
            #         new_ip = result[1]
            #         index = self.ips.index(old_ip)
            #         self.ips[index] = new_ip
            #         print(self.ips)
            #
            #     while True:
            #         f = executor.submit(self.check_ip, self.ips[index])
            #         result = f.result()
            #         print('++++++++++++++++++++++++********', result)
            #         # old_ip = result['old_ip']
            #         # new_ip = result['new_ip']
            #         if result:
            #             old_ip = result[0]
            #             new_ip = result[1]
            #             index = self.ips.index(old_ip)
            #             self.ips[index] = new_ip
            #             print(self.ips)
            #             executor.submit(self.check_ip, self.ips[index])

    def make_one_thread(self):
        import functools
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            index = 2
            t0 = executor.submit(self.check_ip, self.ips[index])
            t0.add_done_callback(functools.partial(self._future_completed, index=index))

            index = 1
            t1 = executor.submit(self.check_ip, self.ips[index])
            t1.add_done_callback(functools.partial(self._future_completed, index=index))

            # index = 5
            # t5 = executor.submit(self.check_ip, self.ips[index])
            # t5.add_done_callback(functools.partial(self._future_completed, index=index))

            # result = t0.result()
            # print(result)

            # if result:
            #     print(result)
            #     old_ip = result[0]
            #     new_ip = result[1]
            #     index = self.ips.index(old_ip)
            #     self.ips[index] = new_ip
            #     print(self.ips)
            # while True:
            #     t0 = executor.submit(self.check_ip, self.ips[index])
            #     t0.add_done_callback(self._future_completed())
            #     result = t0.result()
            #     if result:
            #         print(result)
            #         old_ip = result[0]
            #         new_ip = result[1]
            #         index = self.ips.index(old_ip)
            #         self.ips[index] = new_ip
            #         print(self.ips)

            # t0.add_done_callback(self._future_completed())
            # t2 = executor.submit(self.check_ip, self.ips[2])
            # t3 = executor.submit(self.check_ip, self.ips[3])
            # t4 = executor.submit(self.check_ip, self.ips[4])
            # if t0.result():
            #     t0 = executor.submit(self.check_ip, t0.result())
            #     if t0.result():
            #         t0 = executor.submit(self.check_ip, t0.result())
            #         if t0.result():
            #             t0 = executor.submit(self.check_ip, t0.result())
            # if t1.result():
            #     t1 = executor.submit(self.check_ip, t1.result())
            #     if t1.result():
            #         t1 = executor.submit(self.check_ip, t1.result())
            #         if t1.result():
            #             t1 = executor.submit(self.check_ip, '172.217.250.164')

            # self.thread_generator(executor, t0)
            # self.thread_generator(executor, t1)
            # self.make_t_hand()

    def _future_completed(self, future, **kwargs):
        import functools
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            index = 'no index'
            if 'index' in kwargs:
                index = kwargs['index']
            result = future.result()
            if len(result) == 2:
                print('call back finished ==> ', result, ' with index: ', index)
                print(result)
                old_ip = result[0]
                new_ip = result[1]
                index = self.ips.index(old_ip)
                self.ips[index] = new_ip
                print(self.ips)
                fu = executor.submit(self.check_ip, self.ips[index])
                fu.add_done_callback(functools.partial(self._future_completed, index=index))
                return fu
            else:
                ip = result

                # Test for failure
                # if ip == '5.144.130.116':
                #     self.ips[self.ips.index(ip)] = '34.5.4.6'
                #     ip = '34.5.4.6'

                index = self.ips.index(ip)
                fu = executor.submit(self.check_ip, self.ips[index])
                fu.add_done_callback(functools.partial(self._future_completed, index=index))
                return fu

    def thread_generator(self, executor, response):
        if response.result():
            th = executor.submit(self.check_ip, response.result())
            # th.add_done_callback(lambda f: self._future_completed())
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

    def new_thread(self, executor, index):
        while True:
            f = executor.submit(self.check_ip, self.ips[index])
            result = f.result()
            if result:
                print(result)
                old_ip = result[0]
                new_ip = result[1]
                index = self.ips.index(old_ip)
                self.ips[index] = new_ip
                print(self.ips)

    def wait_for_ever(self):
        index = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            fu = executor.submit(self.check_ip, self.ips[index])
            print('inside: ', fu.result())
            return fu


def main():
    """running part of the script"""
    ip_handler = IpHandler()
    ip_handler.get_ips()
    # ip_handler.make_threads()
    # ip_handler.make_t_hand()
    ip_handler.make_one_thread()
    # ping_ips()


if __name__ == '__main__':
    main()
