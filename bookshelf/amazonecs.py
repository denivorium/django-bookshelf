import base64
from datetime import datetime
import hashlib, hmac
import urllib2, urllib
from lxml import etree

from django.conf import settings

ECS_URL = "http://ecs.amazonaws.com/onca/xml"

def encode_query(querydict):
    params = [(k,v) for k,v in querydict.items()]
    params.sort()
    return urllib.urlencode(params).replace('+', '%20').replace('%7E', '~')

def hmac_sha(tosign, key=settings.AWS_SECRET_KEY):
    return base64.encodestring(hmac.new(key, tosign, hashlib.sha256).digest())[:-1]

def get_string_to_sign(httpverb, hostname, requesturi, queryparams):
    return '\n'.join((httpverb, hostname, requesturi, encode_query(queryparams)))

def sign_request(httpverb, hostname, requesturi, queryparams):
    return hmac_sha(get_string_to_sign(httpverb, hostname, requesturi, queryparams))

def lookup(item_id, id_type):
    httpverb = 'GET'
    hostname = 'ecs.amazonaws.com'
    requesturi = '/onca/xml'
    params = {"Service" : "AWSECommerceService",
              "Version" : settings.AWS_ECS_VERSION,
              "Operation" : "ItemLookup",
              "AWSAccessKeyId" : settings.AWS_ACCESS_KEY,
              "SearchIndex" : "Books",
              "ItemId" : item_id,
              "IdType" : id_type,
              "ResponseGroup" : "Images,ItemAttributes,ItemIds,OfferSummary,Offers,Small",
              'Timestamp' : datetime.utcnow().isoformat().split('.')[0] + ".000Z"}

    signature = sign_request(httpverb, hostname, requesturi, params)
    params.update({'Signature': signature})
    querystring = encode_query(params)

    url = 'http://' + hostname + requesturi + '?' + querystring
    print 'Signed URL is ', url

    r = etree.fromstring(urllib2.urlopen(url).read())

    nsmap = {'ecs' : r.nsmap[None]}
    if r.xpath('//ecs:IsValid', namespaces = nsmap)[0].text == 'True':
        items = r.xpath('//ecs:Item', namespaces = nsmap)
        if len(items):
            return items[0]
        else:
            return None
    else:
        raise ValueError('Request is not valid, full response %s' % etree.tostring(r))

