

$(document).ready(() => {

	$('#full_rating').on('click', (object) => {
		var full_rating = $('#full_rating');
		full_rating.toggleClass("rating-full");
	});



	class Postfix {
		constructor(postfix, count, color)
		{
			this.postfix = postfix;
			this.count = count;
			this.color = color;
		}
	}

	var postfixes = [
		new Postfix("", 1),
		new Postfix("K", 1000),
		new Postfix("M", 1000000),
		new Postfix("B", 1000000000),
	]

	var elements = $(".rating");

	for (var i=0; i < elements.length; i++) 
	{
		element = elements[i];
		var rating_string = element.innerText;
		element.classList.remove("content-loading")
		var rating = Number(rating_string);
		var current_postfix_id = 0;
		for (var j = 1; j < postfixes.length; j++)
		{
			if (rating >= postfixes[j].count)
				current_postfix_id = j;
			else
				break;
		}
		var postfix = postfixes[current_postfix_id];
		var original = Math.floor(rating).toString();
		original = original.split("").reverse().join("");
		original = original.match(/.{1,3}/g);
		original = original.join('.');
		original = original.split("").reverse().join("");
		var content = Math.floor(
			rating / postfix.count
			).toString() + postfix.postfix
		while (content.length < 4) {
			content = " " + content;
		}
		
		var html = `<div class="original">${original}</div><div class="edited">${content}</div>`
		element.innerHTML = html;
		element.classList.add(`rating-group-0${postfix.postfix}`);

	}

})

