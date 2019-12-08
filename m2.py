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
