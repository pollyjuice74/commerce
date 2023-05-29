from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"


class AuctionListing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    auctioneer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions", null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.auctioneer.username} at ${self.price}"


class Bid(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} bidded {self.amount} for {self.listing.title}"


class Comments(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=200, blank=False, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter.username} commented on {self.listing.title}"
    
class Watchlist(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.user.username} added {self.listing.title} to his watchlist"