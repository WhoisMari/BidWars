$(function() {

	var nav_status = 'hide';

	$('.currency').maskMoney({thousands:',', decimal:'.'});

	$('#menu-toggle').click(function(){
		
		if(nav_status == 'hide'){
			$('.wrap-nav').removeClass("wrap-nav-hide");
			$('.wrap-nav').addClass("wrap-nav-show");
			nav_status = 'show';
		}
		else{
			$('.wrap-nav').removeClass("wrap-nav-show");
			$('.wrap-nav').addClass("wrap-nav-hide");
			nav_status = 'hide';						
		}

	});
	

	let closing_date = document.getElementById("closing-date")
	if(closing_date != null){

		closing_date = closing_date.innerText;
		let is_closed = document.getElementById("is_closed").innerText;

		countDown = new Date(closing_date).getTime();
		console.log(is_closed);
		if(is_closed == 'False')
			timer = setInterval(checkListingStatus, 1);

		checkListingStatus();
	}


	function checkListingStatus(){

		const second = 1000,
		minute = second * 60,
		hour = minute * 60,
		day = hour * 24;

		let now = new Date().getTime();
		let	distance = countDown - now;
	
		document.getElementById("days").innerText = Math.floor(distance / (day)),
		document.getElementById("hours").innerText = Math.floor((distance % (day)) / (hour)),
		document.getElementById("minutes").innerText = Math.floor((distance % (hour)) / (minute)),
		document.getElementById("seconds").innerText = Math.floor((distance % (minute)) / second);

		let is_closed = document.getElementById("is_closed")
		if(is_closed != null && is_closed.innerText == 'True')
			distance = -1;


		if (distance < 0) {

			let countdown = document.getElementById("countdown"),
				content = document.getElementById("countdown-message");

			countdown.style.display = "none";
			content.style.display = "flex";

			if(typeof timer !== 'undefined'){
				clearInterval(timer);
				window.location.reload();	
			}
			
		}
	}

});