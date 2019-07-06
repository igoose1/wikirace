$(window).on("load",function () {
	diff = $("#difficulty_field").val();
	name = $("#name_field").val();
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
		new_diff = $("#difficulty_field").val();
		new_name = $("#name_field").val();
		CSRF = $('input[name=csrfmiddlewaretoken]').val()
		$.ajax({
			url: '/set_settings',
			type: 'POST',
			data: {
				difficulty: new_diff,
				name: new_name,
				csrfmiddlewaretoken: CSRF
			},
			success: function(msg) {
				changeState();
				diff = new_diff;
				name = new_name;
				clicked();
			},               
			error: function(msg) {
				changeState();
				$("#difficulty").val(diff);
				$("#difficulty").val(name);
			}
		});
	});
});