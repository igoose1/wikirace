let current_state = true;

$(document).ready(() => {
    function setCookie(cname, cvalue, exdays) {
        var d = new Date();
        d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
        var expires = "expires="+ d.toUTCString();
        document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    }
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2)
            return parts.pop().split(";").shift();
    }
    function change_state() {
        $(".expand_icon").toggleClass('expand_icon_down');
        $(".expand_icon").toggleClass('expand_icon_up');
        $(".box_id").toggleClass("big_box");
        $(".box_id").toggleClass("small_box");

        current_state = !current_state;
        setCookie('saved_state', current_state ? 'opened' : 'closed', 1);
    }

    $(".info_card")
        .click(() => {
            change_state()
        });

    if (getCookie('saved_state') == 'closed' && current_state == true) {
        change_state();
    }
});