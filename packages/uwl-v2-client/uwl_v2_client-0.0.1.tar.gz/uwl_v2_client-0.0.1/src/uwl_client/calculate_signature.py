import hashlib
import hmac
from collections import OrderedDict


def hash_parameters(parameters):
    str_hash = ""
    ordered_dict = OrderedDict(parameters)
    for key in ordered_dict.keys():
        str_hash = str_hash + key + str(parameters[key])
    return str_hash


def calculate_signature(api_secret, parameters):
    str_hash = hash_parameters(parameters)
    signature = hmac.new(
        api_secret.encode("utf-8"), str_hash.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return signature
