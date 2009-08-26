# Create your views here.

from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse

import models

ID_TYPES = ('ISBN', 'EAN', 'UPC')

def books(request):
    if request.method == 'POST':
        book_id = request.POST['book_id'].replace('-', '')
        id_type = request.POST['id_type']

        q = {}
        q[str(id_type.lower())] = id_type
        if list(models.Book.objects.filter(**q)):
            raise ValueError("Book already exists")

        book = models.lookup_book(book_id, id_type)
        if book:
            book.save()
            return HttpResponseRedirect( '/')
        #return render_to_response('book_list.html', {"book" : book})
        else:
            return HttpResponseRedirect( '/?failure=1&book_id=%s&id_type=%s' % (book_id, id_type))
    else:
        books = models.Book.objects.all().order_by('-created')

        user_can_add = request.user.is_staff

        if request.GET.get('failure'):
            message = "Not found"
            previous_book_id = request.GET.get('book_id', "")
            previous_id_type = request.GET.get('id_type', "")

        total_list_price = sum(b.list_price for b in books)
        total_amazon_price = sum(b.amazon_price for b in books)
        total_new_price = sum(b.new_price for b in books)
        total_used_price = sum(b.used_price for b in books)

        good_list_price = sum(b.list_price for b in books if not b.worthless)
        good_amazon_price = sum(b.amazon_price for b in books if not b.worthless)
        good_new_price = sum(b.new_price for b in books if not b.worthless)
        good_used_price = sum(b.used_price for b in books if not b.worthless)

        MEDIA_URL = settings.MEDIA_URL

        return render_to_response('books.html', locals())
