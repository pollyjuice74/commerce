from .models import AuctionListing
from django.db.models import Count

def categories(request):
    categories = AuctionListing.objects.filter(is_active=True).values('category').annotate(count=Count('category')).values_list('category', flat=True)
    return {'categories': categories}