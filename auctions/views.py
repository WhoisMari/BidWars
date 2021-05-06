from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Listing, Bid, Category, Comment
import logging
import requests
from datetime import datetime
import pytz
from django.utils.timezone import make_naive, make_aware


def register(request):
	if request.method == "POST":
		username = request.POST["username"]
		email = request.POST["email"]
		password = request.POST["password"]
		confirmation = request.POST["confirmation"]
		if password != confirmation:
			messages.warning(request, "Passwords must match")
			return render(request, "auctions/register.html")

		try:
			user = User.objects.create_user(username, email, password)
			user.save()
		except IntegrityError:
			messages.warning(request, "Username already taken")
			return render(request, "auctions/register.html")

		login(request, user)
		messages.success(request, "Registered succesfully")
		return redirect("index")

	else:
		return render(request, "auctions/register.html")


def login_view(request):
	if request.method == "POST":
		username = request.POST["username"]
		password = request.POST["password"]
		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			messages.info(request, "Welcome back!")
			return redirect("index")
		else:
			messages.warning(request, "Invalid username and/or password.")
			return render(request, "auctions/login.html")
	else:
		return render(request, "auctions/login.html")


@login_required
def logout_view(request):
	logout(request)
	return redirect("index")


@login_required
def dashboard(request, action = "list", listing_id = 0):
	qs_listings = Listing.objects.filter(user_id=request.user.id).order_by("-created_at")
	qs_my_bids = Listing.objects.filter(bid__user_id=request.user.id).distinct().order_by("created_at")
	bids = []
	for bid in qs_my_bids:
		bid.user_latest_bid = bid.userLatestBid(request.user.id)
		bid.winner = False
		winning_bid = bid.highestBid('bid')
		if winning_bid.user == request.user and bid.closed:
			bid.winner = True

		bids.append(bid)

	context = {
		"listings": qs_listings,
		"bids": bids,
	}

	return render(request, "auctions/dashboard.html", context)


def index(request):
	qs_listings = Listing.objects.all()
	categories_filter = request.POST.getlist("category[]", [])
	search_listing = request.POST.get("search_listing", "")
	is_owner = False

	if request.method == "POST":	

		if request.user.is_authenticated:
			new_bid = request.POST.get("bid", "")
			if new_bid:
				listing_id = request.POST.get("listing_id", "")
				listing = Listing.objects.get(id=listing_id)
				result = listing.addBid(new_bid, request.user.id)

				if result["class"]=="success":
	
					return redirect("index")
				else:
					messages.warning(request, result["message"])				
		else:
			messages.warning(request, "User must be logged in.")

		if categories_filter:
			qs_listings = qs_listings.filter(categories__in=categories_filter)

		if search_listing:
			qs_listings = qs_listings.filter(title__icontains=search_listing)
		
	qs_listings = qs_listings.filter(closed=False).order_by("-created_at")
	if not qs_listings:
		messages.info(request, "No active listings yet.")

	listings = []

	for listing in qs_listings:
		listing = listing.setFlags(request.user.id)
		listings.append(listing)

	context = {
		"listings": listings,
		"categories": Category.objects.all(),
		"selected_categories": categories_filter,
		"search": search_listing,
	}
	return render(request, "auctions/index.html", context)


def listing(request, listing_id):
	listing = Listing.objects.get(id=listing_id)
	is_owner = False
	time_now = datetime.now()

	if request.user.id == listing.user.id:
		is_owner = True

	if listing.closing_date < make_aware(time_now) and listing.closed == 0:
		listing.close()
		return HttpResponseRedirect(reverse("listing", args=[listing_id]))	
	
	if listing.closed == 1:
		messages.info(request, f"This listing is closed. {listing.highestBid('winner')}")

	if request.method == "POST":
		if request.user.is_authenticated:

			comment = request.POST.get("comment", "")
			if comment:
				new_comment = Comment.objects.create(user_id = request.user.id, listing_id = listing_id, text = comment)
				new_comment.save()
				return HttpResponseRedirect(reverse("listing", args=[listing_id]))		

			new_bid = request.POST.get("bid", "")
			if new_bid:
				if listing.closed == False:
					result = listing.addBid(new_bid, request.user.id)
					if result["class"]=="success":
						return HttpResponseRedirect(reverse("listing", args=[listing_id]))
					else:		
						messages.warning(request, result["message"])

			close = request.POST.get("close_listing", False)
			if close and is_owner:
				listing.close()			
				return HttpResponseRedirect(reverse("listing", args=[listing_id]))				
		else:
			messages.warning(request, "User must be logged in.")

	qs_bids = Bid.objects.filter(listing_id=listing_id).order_by("-bidded_at")

	context = {
		"listing":  listing,
		"bids": qs_bids,
		"is_owner": is_owner,
		"comments": Comment.objects.filter(listing_id=listing_id).order_by("-created_at")
	}
	return render(request, "auctions/listing-info.html", context)


@login_required
def manage_listings(request, action, listing_id = 0):
	valid_actions = ['create','delete','update','close']
	listing = []
	
	if action in valid_actions:
		if listing_id:
			listing = Listing.objects.get(id=listing_id)

			if request.user.id == listing.user_id:
				if action == "close":
					listing.close()

					messages.success(request, "Listing closed")
					return redirect("dashboard")

				if action == "delete":
					listing.delete()
					messages.success(request, "Listing deleted")
					return redirect("dashboard")

		if request.method == "POST":
			user = request.user
			categories = request.POST.getlist("category[]", [])
			title = request.POST.get("title", "")
			description = request.POST.get("description", "")
			image = request.POST.get("image", "")
			closing_date = request.POST.get("closing_date", "")
			price = request.POST.get("price", "")

			qs_categories = Category.objects.filter(id__in=categories)
			
			if action == "create":
				if title and description and price and closing_date:
					price  = float(price.replace(",", ""))
					if price < 1000000000:
						new_listing = Listing.objects.create(user = user, title = title, description = description, price = price, image = image, closing_date = closing_date)
						new_listing.save()

						for qs_category in qs_categories:
							new_listing.categories.add(qs_category)

						messages.success(request, "Listing created")
						return redirect('index')
					else:
						messages.warning(request, "Your price shouldn't exceed 10 characters.")
				else:
					messages.warning(request, "You must have, at least, a title, a description and a price.")

			if action == "update":
				if request.user.id == listing.user_id:
					listing.title = title
					listing.description = description
					listing.image = image
					listing.closing_date = closing_date
					listing.save()
					listing.categories.clear()
					
					for qs_category in qs_categories:
						listing.categories.add(qs_category)
						
					messages.success(request, "Listing updated!")

					return HttpResponseRedirect(reverse("manage-listings", args=["update", listing_id]))
		
	context = {
		"categories": Category.objects.all(),
		"action": action,
		"listing": listing,
	}
	
	return render(request, "auctions/listings-form.html", context)


@login_required
def watchlist(request, action = "list", listing_id = 0):
	qs_listings = Listing.objects.filter(watchers__in=[request.user.id]).filter(closed=False)
	wl_filter = request.POST.get("wl_filter", "active")
	
	if request.method == "POST":
		if wl_filter == "active":
			qs_listings = Listing.objects.filter(watchers__in=[request.user.id]).filter(closed=False)

		if wl_filter == "all":
			qs_listings =  Listing.objects.filter(watchers__in=[request.user.id])
			
	if listing_id:
		listing = Listing.objects.get(id=listing_id)

		if action == "add":
			listing.watchers.add(request.user)
			return HttpResponseRedirect(reverse("index")+f"#listing-{listing_id}")

		if action == "remove":
			watcher = listing.watchers.get(id=request.user.id)
			listing.watchers.remove(watcher)
			return HttpResponseRedirect(reverse("index")+f"#listing-{listing_id}")

	if request.method == "GET":
		if not qs_listings:
			messages.info(request, "You don't have any listings on your watchlist.")
	

	context = {
		"listings": qs_listings,
		"is_watchlist": True,
		"selected_filter": wl_filter,
	}
	
	return render(request, "auctions/watchlist.html", context)


def close_listings(request):

	qs_listings = Listing.objects.filter(closed=False)

	for listing in qs_listings:
		time_now = datetime.now()
		if listing.closing_date < make_aware(time_now) and listing.closed == 0:
			listing.close()

	return HttpResponse(status=200)