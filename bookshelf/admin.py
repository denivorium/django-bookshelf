from django.contrib import admin
from bookshelf import models

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'list_price', 'amazon_price',
                    'new_price', 'used_price', 'image', 'detail_page')

    search_fields = ('title')

admin.site.register(models.Book, BookAdmin)
