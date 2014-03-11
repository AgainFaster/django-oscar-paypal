import requests
import time
import urlparse

from paypal import exceptions
from raven.contrib.django.models import client
import logging


def post(url, params):
    """
    Make a POST request to the URL using the key-value pairs.  Return
    a set of key-value pairs.

    :url: URL to post to
    :params: Dict of parameters to include in post payload
    """

    for k in params.keys():
        if type(params[k]) == unicode:
            params[k] = params[k].encode('utf-8')

    # paylfow is not expecting urlencoding (e.g. %, +), therefore don't use urllib.urlencode().
    payload = '&'.join(['%s=%s' % (key, val) for (key, val) in params.items()])

    start_time = time.time()

    num_tries = 3
    logger = logging.getLogger(name="Cart")

    while num_tries:
        try:
            response = requests.post(url, payload, headers={'content-type': 'text/namevalue; charset=utf-8'})
            num_tries = 0
        except Exception as e:
            client.captureException()
            logger.error('Exception Type: %s, Exception: %s' % (type(e), e,))
            num_tries -= 1
            if not num_tries:
                raise exceptions.PayPalError("Unable to communicate with PayPal. Please try again.")
            logger.info('Retrying PayPal request.')

    if response.status_code != requests.codes.ok:
        logger = logging.getLogger(name="Cart")
        logger.error('Unable to communicate with PayPal. HTTP status: %s' % response.status_code)
        raise exceptions.PayPalError("Unable to communicate with PayPal. Please try again.")

    # Convert response into a simple key-value format
    pairs = {}
    for key, values in urlparse.parse_qs(response.content).items():
        pairs[key] = values[0]

    # Add audit information
    pairs['_raw_request'] = payload
    pairs['_raw_response'] = response.content
    pairs['_response_time'] = (time.time() - start_time) * 1000.0

    return pairs
