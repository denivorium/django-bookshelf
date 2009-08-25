import urllib2, urllib
from lxml import etree

from django.conf import settings

ECS_URL = "http://ecs.amazonaws.com/onca/xml"

def lookup(item_id, id_type):
    params = {"Service" : "AWSECommerceService",
              "Version" : settings.AWS_ECS_VERSION,
              "Operation" : "ItemLookup",
              "SubscriptionId" : settings.AWS_ACCESS_KEY,
              "SearchIndex" : "Books",
              "ItemId" : item_id,
              "IdType" : id_type,
              "ResponseGroup" : "Images,ItemAttributes,ItemIds,OfferSummary,Offers,Small"}

    url  = ECS_URL + "?" + urllib.urlencode(params)
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


