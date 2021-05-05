from __future__ import absolute_import

import logging


def setup_logger(account, log_file, level=logging.INFO):
    logger_name = f'{account}Log'
    log = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    log.setLevel(level)
    log.addHandler(fileHandler)
    log.addHandler(streamHandler)

    return log


def logger(text='', method='', successful=False, log=''):

    if successful:
        log.info('%s method ran successfully.', method)
    else:
        log.error('Error in %s method: %s', method, text)


def logThis(log, function, positional_arguments, keyword_arguments):
    try:
        value = function(*positional_arguments, **keyword_arguments)
        logger(method=function, successful=True, log=log)

        return value

    except Exception as e:
        logger(text=str(e), method=function, log=log)

        return None
        pass
