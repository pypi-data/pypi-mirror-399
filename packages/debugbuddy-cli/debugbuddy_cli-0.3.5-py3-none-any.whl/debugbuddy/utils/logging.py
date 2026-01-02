import logging

logger = logging.getLogger('debugbuddy')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)