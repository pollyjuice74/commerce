from django.contrib import admin

from .models import User, AuctionListing, Bid, Comments, Watchlist
# Register your models here.

admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(Comments)
admin.site.register(Watchlist)