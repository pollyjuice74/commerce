from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.urls import reverse
from django import forms


from .models import User, AuctionListing, Bid, Comments, Watchlist


def index(request):
    # Filter active listings
    active_listings = AuctionListing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": active_listings,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ["title", "description", "price", "image_url", "category"]

def create_listing(request):
    if request.method == 'POST':

        # Create form with post data and redirect to home/
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.auctioneer = request.user  # Set the auctioneer field to the current user
            listing.save()
            return redirect("index")
    else: 
        # Create empty form
        form = CreateListingForm()

        return render(request, "auctions/create_listing.html", {
            "form": form
        })
    

@login_required
def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    comments = Comments.objects.filter(listing=listing)

    if request.method == 'POST':
        # Adding and removing from watchlist
        if "add_watchlist" in request.POST:
            Watchlist.objects.create(user=request.user, listing=listing)
        elif "remove_watchlist" in request.POST:
            Watchlist.objects.filter(user=request.user, listing=listing).delete()

        # Placing bid
        elif "place_bid" in request.POST:
            amount = request.POST["amount"]
            if float(amount) > listing.price:
                Bid.objects.create(listing=listing, bidder=request.user, amount=amount)
                listing.price = float(amount) # Update listing price
                listing.save()
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "message": "Invalid bid amount."
                })
            
        # Check if auction is closed
        elif "closed_auction" in request.POST:
            if request.user == listing.auctioneer:
                if not listing.is_active:
                    return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "message": "Auction already closed."
                })

                highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

                if highest_bid:
                    listing.winner = highest_bid.bidder
                    listing.is_active = False
                    listing.save()

        elif "add_comment" in request.POST:
            comment = request.POST.get('comment')
            Comments.objects.create(listing=listing, commenter=request.user, content=comment)
            return redirect("listing", listing_id=listing_id)
            
    watchlist_exists = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    
    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "watchlist_exists": watchlist_exists,
        "comments": comments,
    })


def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items,
    })


def category_listings(request, category):
    listings = AuctionListing.objects.filter(category=category, is_active=True)
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings,
    })