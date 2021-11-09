from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class User(AbstractUser):
	pass


class Category(models.Model):
	title = models.CharField(max_length=64)

	def __str__(self):
		return f"{self.title}"


class Listing(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=64)
	description = models.TextField()
	price = models.DecimalField(max_digits=10, decimal_places=2)
	image = models.URLField(max_length=500)
	closing_date = models.DateTimeField(auto_now_add=False)

	created_at = models.DateTimeField(auto_now_add=True)
	closed = models.BooleanField(default=False)
	closed_at = models.DateTimeField(null=True)
	
	categories = models.ManyToManyField(Category)
	watchers = models.ManyToManyField(User, related_name="watchers")


	def __str__(self):
		return f"Listing: {self.title }   posted by: {self.user}"

	def highestBid(self, return_format = 'money'):
		qs_bid = Bid.objects.filter(listing=self).order_by("-price")[:1]
		if return_format == 'bid':
			return qs_bid[0] if qs_bid else False

		if return_format == 'winner':
			return f"The winner was {qs_bid[0].user}." if qs_bid else "There were no bids."
		
		price = qs_bid[0].price if qs_bid else self.price
	
		if return_format == 'money':
			return f"${price:,.2f}"
		
		return float(price)
		
	def minBid(self):
		min_bid = self.highestBid("float")
		return f"{(min_bid + 0.01):.2f}"
	
	def addBid(self, new_bid, user_id):
		result = {}
		highest_bid = self.highestBid("float")
		new_bid = float(new_bid.replace(",", ""))
		if new_bid > highest_bid:

			if new_bid < 1000000000:

				user = User.objects.get(id=user_id)
				new_bid = Bid.objects.create(user = user, listing = self, price = new_bid)
				new_bid.save()
				result = {
					"class" : "success",
					"message" : "Bid completed."
				}
			else:
				result = {
					"class" : "danger",
					"message" : "Your bid shouldn't exceed 10 characters."
				}
		else:
			result = {
				"class" : "danger",
				"message" : "Your bid must be higher than the lastest bid."
			}

		return result

	def close(self):
		self.closed_at = datetime.now()
		self.closed = True
		self.save()

		highest_bid = self.highestBid("bid")
		if highest_bid:
			bid = Bid.objects.get(id=highest_bid.id)
			bid.is_winner = 1
			bid.save()

		return True

	def userBids(self, user_id):
		qs_bids = Bid.objects.filter(user_id=user_id, listing=self).order_by("-bidded_at")
		return qs_bids

	def userLatestBid(self, user_id):
		qs_bid = Bid.objects.filter(user_id=user_id, listing=self).order_by("-bidded_at")[:1]

		return f"${qs_bid[0].price:,.2f}" if qs_bid else "-"

	def getImage(self, format="url"):
		placeholder_url = "https://socialistmodernism.com/wp-content/uploads/2017/07/placeholder-image.png"
		return self.image if self.image else placeholder_url

	def setFlags(self, user_id):
		
		self.is_watched = True if self.watchers.filter(id=user_id) else False
		self.is_owner = True if self.user.id == user_id else False

		return self


class Bid(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
	price = models.DecimalField(max_digits=16, decimal_places=2)
	bidded_at = models.DateTimeField(auto_now_add=True)
	is_winner = models.BooleanField(default=False)
	def __str__(self):
		return f"Bid by user id: {self.user.id} on item id: {self.listing.id} with price: {self.price} "

	def money(self):
		return f"{self.price:,.2f}"

class Comment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Comment: {self.text} by: {self.user}"