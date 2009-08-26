import unittest

from django.conf import settings

import amazonecs

class AmazonECSTestCase(unittest.TestCase):

    def test_hmac(self):
        tosign = """GET
webservices.amazon.com
/onca/xml
AWSAccessKeyId=00000000000000000000&ItemId=0679722769&Operation=ItemLookup&ResponseGroup=ItemAttributes%2COffers%2CImages%2CReviews&Service=AWSECommerceService&Timestamp=2009-01-01T12%3A00%3A00Z&Version=2009-01-06"""

        hmac = amazonecs.hmac_sha(tosign, key="1234567890")
        assert hmac == "Nace+U3Az4OhN7tISqgs1vdLBHBEijWcBeCqL5xN9xg="

    def test_sorted_params(self):
        queryparams = {"Service" : "AWSECommerceService",
                       "Version" : "2008-04-07",
                       "Operation" : "ItemLookup",
                       "AWSAccessKeyId" : "01D05S5Y39RQSCJ36YG2",
                       "SearchIndex" : "Books",
                       "ItemId" : "9781934356319",
                       "IdType" : "ISBN",
                       "ResponseGroup" : "Images,ItemAttributes,ItemIds,OfferSummary,Offers,Small",
                       'Timestamp' : "2009-08-26T17:46:57.000Z"}
        querystring = amazonecs.encode_query(queryparams)

        assert querystring == "AWSAccessKeyId=01D05S5Y39RQSCJ36YG2&IdType=ISBN&ItemId=9781934356319&Operation=ItemLookup&ResponseGroup=Images%2CItemAttributes%2CItemIds%2COfferSummary%2COffers%2CSmall&SearchIndex=Books&Service=AWSECommerceService&Timestamp=2009-08-26T17%3A46%3A57.000Z&Version=2008-04-07"

    def test_to_sign(self):
        queryparams = {"Service" : "AWSECommerceService",
                       "Version" : "2008-04-07",
                       "Operation" : "ItemLookup",
                       "AWSAccessKeyId" : "01D05S5Y39RQSCJ36YG2",
                       "SearchIndex" : "Books",
                       "ItemId" : "9781934356319",
                       "IdType" : "ISBN",
                       "ResponseGroup" : "Images,ItemAttributes,ItemIds,OfferSummary,Offers,Small",
                       'Timestamp' : "2009-08-26T17:46:57.000Z"}

        tosign = amazonecs.get_string_to_sign('GET', 'ecs.amazonaws.com', '/onca/xml', queryparams)
        assert tosign == """GET
ecs.amazonaws.com
/onca/xml
AWSAccessKeyId=01D05S5Y39RQSCJ36YG2&IdType=ISBN&ItemId=9781934356319&Operation=ItemLookup&ResponseGroup=Images%2CItemAttributes%2CItemIds%2COfferSummary%2COffers%2CSmall&SearchIndex=Books&Service=AWSECommerceService&Timestamp=2009-08-26T17%3A46%3A57.000Z&Version=2008-04-07"""

    def test_signature(self):
        tosign = """GET
ecs.amazonaws.com
/onca/xml
AWSAccessKeyId=01D05S5Y39RQSCJ36YG2&IdType=ISBN&ItemId=9781934356319&Operation=ItemLookup&ResponseGroup=Images%2CItemAttributes%2CItemIds%2COfferSummary%2COffers%2CSmall&SearchIndex=Books&Service=AWSECommerceService&Timestamp=2009-08-26T17%3A46%3A57.000Z&Version=2008-04-07"""

        hmac = amazonecs.hmac_sha(tosign, key="1234567890")
        assert hmac == "MjM8H8IFqSGj+lKko7+dAeTyAmKfkBVYZCgAlU3cTA0="

