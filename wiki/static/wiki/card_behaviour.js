let current_state = true;

$(document).ready(() => {

    function change_state() {
        if (current_state) {
            $(".start_page").hide();
            $(".finish_page").hide();
        } else {
            $(".start_page").show();
            $(".finish_page").show();
        }
        current_state = !current_state
    }

    $(".expand")
        .toggleClass('rotated')
        .click(() => {
            change_state()
        });
    change_state();
});