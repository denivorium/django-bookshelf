from decimal import Decimal

from django.db import models
from lxml import etree

from amazonecs import lookup

class Book(models.Model):

    #IDs
    asin = models.CharField("ASIN", max_length=20, unique=True)
    isbn = models.CharField('ISBN', max_length=10, unique=True)
    ean  = models.CharField('EAN', max_length=13, unique=True)

    title = models.CharField(max_length=255)

    list_price = models.DecimalField(max_digits=6,decimal_places=2,editable=False)
    used_price = models.DecimalField(max_digits=6,decimal_places=2,editable=False)
    new_price = models.DecimalField(max_digits=6,decimal_places=2,editable=False)
    amazon_price = models.DecimalField(max_digits=6,decimal_places=2,editable=False)

    detail_page = models.URLField(editable = False)

    image = models.URLField(editable = False)
    image_height = models.PositiveIntegerField(editable = False)
    image_width = models.PositiveIntegerField(editable = False)

    _content = models.TextField(editable = False)

    created = models.DateTimeField(auto_now_add = True,editable=False)
    modified = models.DateTimeField(auto_now = True,editable=False)

    _xmlcontent = None

    def fromxml(self, tree):
        self._xmlcontent = tree

        self.asin = self._xpath("//ecs:ASIN")[0].text
        self.isbn = self._xpath("//ecs:ItemAttributes/ecs:ISBN")[0].text
        self.ean = self._xpath("//ecs:ItemAttributes/ecs:EAN")[0].text

        self.title = self._xpath("//ecs:ItemAttributes/ecs:Title")[0].text
        self.detail_page = self._xpath("//ecs:DetailPageURL")[0].text

        if self._xpath("//ecs:SmallImage/ecs:URL"):
            self.image = self._xpath("//ecs:SmallImage/ecs:URL")[0].text
            self.image_height = int(self._xpath("//ecs:SmallImage/ecs:Height")[0].text)
            self.image_width = int(self._xpath("//ecs:SmallImage/ecs:Width")[0].text)
        else:
            self.image = "http://g-ecx.images-amazon.com/images/G/01/x-site/icons/no-img-sm._V47056216_.gif"
            self.image_height = 40
            self.image_width = 60


        self.list_price = self._price_from_path("//ecs:ItemAttributes/ecs:ListPrice/ecs:FormattedPrice")
        self.used_price = self._price_from_path("//ecs:OfferSummary/ecs:LowestUsedPrice/ecs:FormattedPrice")
        self.new_price = self._price_from_path("//ecs:OfferSummary/ecs:LowestNewPrice/ecs:FormattedPrice")
        self.amazon_price = self._price_from_path("//ecs:Offers/ecs:Offer/ecs:OfferListing/ecs:Price/ecs:FormattedPrice")

        self._content = etree.tostring(tree)


    def _price_from_path(self, path):
        p = self._xpath(path)
        if not p:
            return Decimal(0)
        else:
            price = p[0].text
            if price.startswith("$"):
                return Decimal(price[1:])
            return None

    def _xpath(self, path):
        NSMAP = {'ecs' : self.content.nsmap[None]}
        return self.content.xpath(path, namespaces = NSMAP)

    @property
    def worthless(self):
        return self.used_price > Decimal(0) and self.used_price < Decimal(10)

    @property
    def content(self):
        if self._xmlcontent is None:
            self._xmlcontent = etree.fromstring(self._content)
        return self._xmlcontent

    @property
    def author_list(self):
        return [e.text for e in self._xpath("//ecs:ItemAttributes/ecs:Author")]

    @property
    def authors(self):
        lst = self.author_list
        if not lst:
            return ""
        if len(lst) == 1:
            return lst[0]
        else:
            end = lst[-1]
            other = lst[:-1]
            return ', '.join(other) + " and " + end


def lookup_book(book_id, id_type):
    try:
        e = lookup(book_id, id_type)
        if e:
            b = Book()
            b.fromxml(e)
            return b
        else:
            return None
    except ValueError:
        return None
