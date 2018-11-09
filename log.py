# -*- coding: utf-8 -*-
import time
import logging
import os

def create_directory(directory):
    """Creates the directory if not exists and returns it path.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.realpath("%s/" % directory)

# Setting up the logger
log = logging.getLogger('chatbot')
hdlr = logging.FileHandler(os.path.realpath('%s/chatbot%s.log' % (
    create_directory('log'), time.strftime("%Y-%m-%d %H:%M"))))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)