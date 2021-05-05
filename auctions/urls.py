from django.urls import path
from django.http import HttpResponse
from . import views

urlpatterns = [
	path("", views.index, name="index"),
	path("login", views.login_view, name="login"),
	path("logout", views.logout_view, name="logout"),
	path("register", views.register, name="register"),
	path("listing/<int:listing_id>", views.listing, name="listing"),
	path("watchlist", views.watchlist, name="watchlist"),
	path("watchlist/<str:action>/<str:listing_id>/", views.watchlist, name="watchlist-actions"), 
	path("dashboard", views.dashboard, name="dashboard"),
	path("dashboard/<str:action>/<str:listing_id>/", views.dashboard, name="dashboard"),
	path("manage-listings/<str:action>/", views.manage_listings, name="manage-listings"),
	path("manage-listings/<str:action>/<str:listing_id>/", views.manage_listings, name="manage-listings"),
	path("close-listings", views.close_listings, name="close-listings"),
]