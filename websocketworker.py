#!/usr/bin/env python


import logging
import time
import random
logger = logging.getLogger(__name__)

def worker():
    """worker function"""
    print('=========================Worker start==================')
    # name = multiprocessing.current_process().name
    # with s:
    # pool.makeActive(name)

    while 1:
        logger.warning(
            "++++++++++++++I'm a websocket process - Hi! ++++++++++++")
        print('==================Worker random======================')
        time.sleep(random.random()*100)
        # pool.makeInactive(name)

