# An eBay-like e-commerce auction site

This project is based on CS50’s Web Programming open-course Project 2 - Commerce.

The specifications can be found on [CS50W's website](https://cs50.harvard.edu/web/2020/projects/2/commerce/).

I learned a lot of Django and Python and it was a lot of fun!

In the end, I got a little bit too excited and decided to add some other features:

- Bidding:
	- I thought that having to open the Listing page every time, just to place a bid, could get a little tedious.
	So, I implemented the bid feature on 3 different pages, Listing page, Active Listings page, and Watchlist page.

- Dashboard:
	- On the dashboard, users can see, edit, close and delete their Listings. 
	Users can also look at the listings that they’ve already placed a bid on to see if it is open, if they won, and what was their last bid.
 
 - Filters:
	 - On the Active Listings page, users can filter their results by categories and keywords.
	 - On the Watchlist page, users can filter to see only the active listings or all of them.

 - Listings:
	 - All Listings need a “closing date”, which the users may edit later. 
	 - If the listing is still open, users can see a timer for the closing date.
	 - There is a table called “Bid Wars”, which shows every bid that has been given to that specific listing and who is winning/won.

A demo of my take on this project is available at [BidWars](https://bidwars.whoismari.dev/)