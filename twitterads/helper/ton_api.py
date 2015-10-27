import ConfigParser
import urllib
import random
import base64
import hmac
import binascii
import time
import collections
import hashlib
import requests
import json
from twython import Twython
import urllib
from wsgiref.handlers import format_date_time
import datetime
import sys, json 
from time import mktime

def escape(s):
    """Percent Encode the passed in string"""
    return urllib.quote(s, safe='~')


def get_nonce():
    """Unique token generated for each request"""
    n = base64.b64encode(
        ''.join([str(random.randint(0, 9)) for i in range(24)]))
    print(len(n))
    return n


def generate_signature(method, url, url_parameters, oauth_parameters,
                       oauth_consumer_key, oauth_consumer_secret,
                       oauth_token_secret=None, status=None):
    """Create the signature base string"""

    #Combine parameters into one hash
    temp = collect_parameters(oauth_parameters, status, url_parameters)

    #Create string of combined url and oauth parameters
    parameter_string = stringify_parameters(temp)

    #Create your Signature Base String
    signature_base_string = (
        method.upper() + '&' +
        escape(str(url)) + '&' +
        escape(parameter_string)
    )
    #Get the signing key
    signing_key = create_signing_key(oauth_consumer_secret, oauth_token_secret)

    return calculate_signature(signing_key, signature_base_string)

def collect_parameters(oauth_parameters, status, url_parameters):
    """Combines oauth, url and status parameters"""
    #Add the oauth_parameters to temp hash
    temp = oauth_parameters.copy()

    #Add the status, if passed in.  Used for posting a new tweet
    if status is not None:
        temp['status'] = status

    #Add the url_parameters to the temp hash
    for k, v in url_parameters.iteritems():
        temp[k] = v

    return temp


def calculate_signature(signing_key, signature_base_string):
    """Calculate the signature using SHA1"""
    hashed = hmac.new(signing_key, signature_base_string, hashlib.sha1)

    sig = binascii.b2a_base64(hashed.digest())[:-1]

    return escape(sig)


def create_signing_key(oauth_consumer_secret, oauth_token_secret=None):
    """Create key to sign request with"""
    signing_key = escape(oauth_consumer_secret) + '&'

    if oauth_token_secret is not None:
        signing_key += escape(oauth_token_secret)

    return signing_key


def create_auth_header(parameters):
    """For all collected parameters, order them and create auth header"""
    ordered_parameters = {}
    ordered_parameters = collections.OrderedDict(sorted(parameters.items()))
    auth_header = (
        '%s="%s"' % (k, v) for k, v in ordered_parameters.iteritems())
    val = "OAuth " + ', '.join(auth_header)
    return val


def stringify_parameters(parameters):
    """Orders parameters, and generates string representation of parameters"""
    output = ''
    ordered_parameters = {}
    ordered_parameters = collections.OrderedDict(sorted(parameters.items()))

    counter = 1
    for k, v in ordered_parameters.iteritems():
        output += escape(str(k)) + '=' + escape(str(v))
        if counter < len(ordered_parameters):
            output += '&'
            counter += 1

    return output


def get_oauth_parameters(consumer_key, access_token):
    """Returns OAuth parameters needed for making request"""
    oauth_parameters = {
        'oauth_timestamp': str(int(time.time())),
        'oauth_signature_method': "HMAC-SHA1",
        'oauth_version': "1.0",
        'oauth_token': access_token,
        'oauth_nonce': get_nonce(),
        'oauth_consumer_key': consumer_key
    }

    return oauth_parameters



class TwitterTon():

    def __init__(self, twitter_consumer_key, twitter_consumer_secret,
                       access_token, access_token_secret):
        self.method = "post"
        self.ton_url = "https://ton.twitter.com/1.1/ton/bucket/ta_partner"
        self.url_parameters = {}
        self.keys = {
                    "twitter_consumer_key": twitter_consumer_key,
                    "twitter_consumer_secret": twitter_consumer_secret,
                    "access_token": access_token,
                    "access_token_secret": access_token_secret
                    }
        self.oauth_parameters = get_oauth_parameters(
                                self.keys['twitter_consumer_key'],
                                self.keys['access_token'])

        self.oauth_parameters['oauth_signature'] = generate_signature(self.method,
                                                                      self.ton_url,
                                                                      self.url_parameters, self.oauth_parameters,
                                                                      self.keys['twitter_consumer_key'],
                                                                      self.keys['twitter_consumer_secret'],
                                                                      self.keys['access_token_secret'])

        

    def upload_data(self, file_path):   
        now = datetime.datetime.now() + datetime.timedelta(days=10)
        stamp = format_date_time(mktime(now.timetuple()))
        file_upload = open(file_path,'rU').read()
        headers = {'Authorization':create_auth_header(self.oauth_parameters), 'X-TON-Expires':stamp}
        self.ton_url += '?' + urllib.urlencode(self.url_parameters)
        r = requests.post(self.ton_url, headers=headers, data=file_upload)
        return r.headers
   