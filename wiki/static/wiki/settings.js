function clicked(){
	$('.settings_window').toggleClass('display');
}


state = 0
function changeState()
{
	state ^= 2;
	$("#submit_waiting").toggleClass('display')
}

function changeState_save()
{
	state ^= 1;
	$("#submit_settings").toggleClass('display')
	$("#close_settings").toggleClass('display')
}

function checkState()
{
	new_diff = $("#difficulty_field").val();
	new_name = $("#name_field").val();
	if ((state & 2) == 0)
	{
		if ((new_diff == diff) && (new_name == name))
		{
			if ((state & 1) != 0)
				changeState_save();
			
		}
		else
		{
			if ((state & 1) == 0)
				changeState_save();
		}
	}
}


$(window).on("load",function () {
	diff = $("#difficulty_field").val();
	name = $("#name_field").val();
	
	
	$('.settings_block').click(clicked);
	$('#close_settings').click(clicked);
	
	$('#submit_settings').click(function() {
		changeState();
		new_diff = $("#difficulty_field").val();
		new_name = $("#name_field").val();
		CSRF = $('input[name=csrfmiddlewaretoken]').val();
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
				checkState()
			},               
			error: function(msg) {
				changeState();
				$("#difficulty").val(diff);
				$("#difficulty").val(name);
				checkState()
			}
		});
	});
});