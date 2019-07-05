let current_state = true;

$(document).ready(() => {

    function change_state() {
		$(".expand_icon").toggleClass('expand_icon_down');
		$(".expand_icon").toggleClass('expand_icon_up');
		$(".box_id").toggleClass("big_box");
		$(".box_id").toggleClass("small_box");
		
        current_state = !current_state
    }

    $(".info_card")
        .click(() => {
            change_state()
        });
    change_state();
});