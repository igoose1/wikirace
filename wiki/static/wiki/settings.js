$(window).on("load",function () {
	diff = $("#difficulty").val();
	
	function clicked(){
		$('.settings_window').toggleClass('display');
	}
	
	$('.settings_block').click(clicked);

	function changeState()
	{
		$("#submit_waiting").toggleClass('display')
		$("#submit_settings").toggleClass('display')
	}

	$('#submit_settings').click(function() {
		changeState();
		new_diff = $("#difficulty").val();
		CSRF = $('input[name=csrfmiddlewaretoken]').val()
		$.ajax({
			url: '/set_settings',
			type: 'POST',
			data: {
				difficulty: new_diff,
				csrfmiddlewaretoken: CSRF
			},
			success: function(msg) {
				changeState();
				diff = new_diff;
				clicked();
			},               
			error: function(msg) {
				changeState();
				$("#difficulty").val(diff);
			}
		});
	});
});