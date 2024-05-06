import logging
log = logging.getLogger('bot')
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', datefmt='%Y-%m-%d %H:%M:%S', style='{',))
log.addHandler(ch)
# log.propagate = False

def get_logger(name):
    return log.getChild(name)