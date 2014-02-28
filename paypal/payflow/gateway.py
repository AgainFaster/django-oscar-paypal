"""
Gateway module - this module should be ignorant of Oscar and could be used in a
non-Oscar project.  All Oscar-related functionality should be in the facade.
"""
import logging

from django.conf import settings
from django.core import exceptions

from paypal import gateway
from paypal.payflow import models
from paypal.payflow import codes

logger = logging.getLogger('paypal.payflow')


def authorize(order_number, card_number, cvv, expiry_date, amt, **kwargs):
    """
    Make an AUTHORIZE request.

    This holds the money within the customer's bankcard but doesn't
    actually settle - that comes from a later step.

    * The hold lasts for around a week.
    * The hold cannot be cancelled through the PayPal API.
    """
    return _submit_payment_details(codes.AUTHORIZATION, order_number, card_number, cvv, expiry_date,
                                   amt, **kwargs)


def sale(order_number, card_number, cvv, expiry_date, amt, **kwargs):
    """
    Make a SALE request.

    This authorises money within the customer's bank and marks it for settlement
    immediately.
    """
    return _submit_payment_details(codes.SALE, order_number, card_number, cvv, expiry_date,
                                   amt, **kwargs)


def _submit_payment_details(trxtype, order_number, card_number, cvv, expiry_date, amt, **kwargs):
    """
    Submit payment details to PayPal.
    """
    params = {
        'TRXTYPE': trxtype,
        'TENDER': codes.BANKCARD,
        'AMT': amt,
        # Bankcard
        'ACCT': card_number,
        'CVV2': cvv,
        'EXPDATE': expiry_date,
        # Audit information (eg order number)
        'COMMENT1': order_number,
        'COMMENT2': kwargs.get('comment2', ''),
        # Billing address (only required if using address verification service)
        'FIRSTNAME': kwargs.get('first_name', kwargs.get('firstname', '')),
        'LASTNAME': kwargs.get('last_name', kwargs.get('lastname', '')),
        'STREET': kwargs.get('street', ''),
        'CITY': kwargs.get('city', ''),
        'STATE': kwargs.get('state', ''),
        'ZIP': kwargs.get('zip', ''),
        'BILLTOCOUNTRY': kwargs.get('countrycode', ''),
        'EMAIL': kwargs.get('user_email', ''),
        'PHONENUM': kwargs.get('billing_phone_number', ''),
    }
    return _transaction(params, _settings_params(**kwargs))


def delayed_capture(order_number, pnref, amt=None, **kwargs):
    """
    Perform a DELAYED CAPTURE transaction.

    This captures money that was previously authorised.
    """
    params = {
        'COMMENT1': order_number,
        'TRXTYPE': codes.DELAYED_CAPTURE,
        'ORIGID': pnref
    }
    if amt:
        params['AMT'] = amt
    return _transaction(params, _settings_params(**kwargs))


def reference_transaction(order_number, pnref, amt, **kwargs):
    """
    Capture money using the card/address details of a previous transaction

    * The PNREF of the original txn is valid for 12 months
    """
    params = {
        'COMMENT1': order_number,
        # Use SALE as we are effectively authorising and settling a new
        # transaction
        'TRXTYPE': codes.SALE,
        'TENDER': codes.BANKCARD,
        'ORIGID': pnref,
        'AMT': amt,
    }
    return _transaction(params, _settings_params(**kwargs))


def credit(order_number, pnref, amt=None, **kwargs):
    """
    Refund money back to a bankcard.
    """
    params = {
        'COMMENT1': order_number,
        'TRXTYPE': codes.CREDIT,
        'ORIGID': pnref
    }
    if amt:
        params['AMT'] = amt
    return _transaction(params, _settings_params(**kwargs))


def void(order_number, pnref, **kwargs):
    """
    Prevent a transaction from being settled
    """
    params = {
        'COMMENT1': order_number,
        'TRXTYPE': codes.VOID,
        'ORIGID': pnref
    }
    return _transaction(params, _settings_params(**kwargs))


def _get_setting(setting_dict, name, default=None):
    """
    If name is not it kwargs, try to get it from settings
    """
    return setting_dict.get(name.lower(), getattr(settings, name.upper(), default))


def _settings_params(**kwargs):
    settings_params = {
        'PAYPAL_PAYFLOW_VENDOR_ID': _get_setting(kwargs, 'PAYPAL_PAYFLOW_VENDOR_ID'),
        'PAYPAL_PAYFLOW_PASSWORD': _get_setting(kwargs, 'PAYPAL_PAYFLOW_PASSWORD'),
        'PAYPAL_PAYFLOW_USER': _get_setting(kwargs, 'PAYPAL_PAYFLOW_USER',
                                            _get_setting(kwargs, 'PAYPAL_PAYFLOW_VENDOR_ID')),
        'PAYPAL_PAYFLOW_PARTNER': _get_setting(kwargs, 'PAYPAL_PAYFLOW_PARTNER', 'PayPal'),
        'PAYPAL_PAYFLOW_CURRENCY': _get_setting(kwargs, 'PAYPAL_PAYFLOW_CURRENCY', 'USD'),
        'PAYPAL_PAYFLOW_PRODUCTION_MODE': _get_setting(kwargs, 'PAYPAL_PAYFLOW_PRODUCTION_MODE', False),
    }

    for setting in ('PAYPAL_PAYFLOW_VENDOR_ID', 'PAYPAL_PAYFLOW_PASSWORD'):
        if not settings_params.get(setting):
            raise exceptions.ImproperlyConfigured("You must define a %s setting" % setting)

    return settings_params


def _transaction(extra_params, settings_params):
    """
    Perform a transaction with PayPal.

    :extra_params: Additional parameters to include in the payload other than
    the user credentials.
    """
    if 'TRXTYPE' not in extra_params:
        raise RuntimeError("All transactions must specify a 'TRXTYPE' paramter")

    # Validate constraints on parameters
    constraints = {
        codes.AUTHORIZATION: ('ACCT', 'AMT', 'EXPDATE'),
        codes.SALE: ('AMT',),
        codes.DELAYED_CAPTURE: ('ORIGID',),
        codes.CREDIT: ('ORIGID',),
        codes.VOID: ('ORIGID',),
    }
    trxtype = extra_params['TRXTYPE']
    for key in constraints[trxtype]:
        if key not in extra_params:
            raise RuntimeError(
                "A %s parameter must be supplied for a %s transaction" % (
                    key, trxtype))

    # Set credentials
    params = {
        'VENDOR': settings_params.get('PAYPAL_PAYFLOW_VENDOR_ID'),
        'PWD': settings_params.get('PAYPAL_PAYFLOW_PASSWORD'),
        'USER': settings_params.get('PAYPAL_PAYFLOW_USER'),
        'PARTNER': settings_params.get('PAYPAL_PAYFLOW_PARTNER'),
        'CURRENCY': settings_params.get('PAYPAL_PAYFLOW_CURRENCY'),
    }
    params.update(extra_params)

    # Ensure that any amounts have a currency and are formatted correctly
    if 'AMT' in params:
        params['AMT'] = "%.2f" % params['AMT']

    if settings_params.get('PAYPAL_PAYFLOW_PRODUCTION_MODE'):
        url = 'https://payflowpro.paypal.com'
    else:
        url = 'https://pilot-payflowpro.paypal.com'

    logger.info("Performing %s transaction (trxtype=%s)",
                codes.trxtype_map[trxtype], trxtype)
    pairs = gateway.post(url, params)

    # Beware - this log information will contain the Payflow credentials
    # only use it in development, not production.
    if not settings_params.get('PAYPAL_PAYFLOW_PRODUCTION_MODE'):
        logger.debug("Raw request: %s", pairs['_raw_request'])
        logger.debug("Raw response: %s", pairs['_raw_response'])

    return models.PayflowTransaction.objects.create(
        comment1=params['COMMENT1'],
        trxtype=params['TRXTYPE'],
        tender=params.get('TENDER', None),
        amount=params.get('AMT', None),
        pnref=pairs.get('PNREF', None),
        ppref=pairs.get('PPREF', None),
        cvv2match=pairs.get('CVV2MATCH', None),
        avsaddr=pairs.get('AVSADDR', None),
        avszip=pairs.get('AVSZIP', None),
        result=pairs.get('RESULT', None),
        respmsg=pairs.get('RESPMSG', None),
        authcode=pairs.get('AUTHCODE', None),
        raw_request=pairs['_raw_request'],
        raw_response=pairs['_raw_response'],
        response_time=pairs['_response_time']
    )
