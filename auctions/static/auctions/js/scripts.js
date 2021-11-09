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

		let start_timer = checkListingStatus();
		if(start_timer)
			timer = setInterval(checkListingStatus, 800);

	}


	function checkListingStatus(){

		let is_closed = document.getElementById("is_closed").innerText;
		console.log(is_closed);
		if( is_closed == 'True')
			return false;

		countDown = new Date(closing_date.innerText).getTime();
		const second = 1000,
		minute = second * 60,
		hour = minute * 60,
		day = hour * 24;

		let now = new Date().getTime();
		let	distance = countDown - now;
		let countdown = document.getElementById("countdown");
		let content = document.getElementById("countdown-message");
	
		if (distance < 0){

			countdown.style.display = "none";
			content.style.display = "flex";
			document.getElementById("is_closed").innerText = 'True';

			if(typeof timer !== 'undefined'){
				clearInterval(timer);
				window.location.reload();	
			}
			
			return false;
		}

		countdown.style.display = "flex";
		content.style.display = "none";

		document.getElementById("days").innerText = Math.floor(distance / (day)),
		document.getElementById("hours").innerText = Math.floor((distance % (day)) / (hour)),
		document.getElementById("minutes").innerText = Math.floor((distance % (hour)) / (minute)),
		document.getElementById("seconds").innerText = Math.floor((distance % (minute)) / second);

		return true;

	}

});