
$(document).ready(() => {

	$("#full_rating").on("click", (object) => {
		var full_rating = $("#full_rating");
		full_rating.toggleClass("rating-full");
	});

	WS = "&nbsp"


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

	function beautify_number(n) {
		var result = Math.floor(n).toString();
		result = result.split("").reverse().join("");
		result = result.match(/.{1,3}/g);
		result = result.join(" ");
		result = result.split("").reverse().join("");
		return result;
	}

	function make_n_len(n, text) {
		if (text.length < n) {
			var count = n - text.length;
			while (count-- > 0)
				text = WS + text;
		}
		return text;	
	}

	var elements = $(".rating");

	for (var i=0; i < elements.length; i++) 
	{
		var element = elements[i];
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
		var original = beautify_number(rating);

		var content = Math.floor(
			rating / postfix.count
			).toString() + postfix.postfix

		var html = `<div class="original">${original}</div><div class="edited">${content}</div>`
		element.innerHTML = html;
		element.classList.add(`rating-group-0${postfix.postfix}`);

	}

})