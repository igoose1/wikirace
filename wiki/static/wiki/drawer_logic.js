function move_left_bar() {
    let checkbox = document.getElementById("checkbox");
    let transform_block = document.getElementById("menu");
    let background = document.getElementById("menu-background");
    if (checkbox.checked) {
        transform_block.style.transform = "translate(0, 0)";
        background.style.opacity = "0.6";
    } else {
        transform_block.style.transform = "translate(-100%, 0)";
        background.style.opacity = "0";
    }
}

$(document).ready(function set_height_for_wiki_container() {
    let head_height = document.getElementsByClassName("toolbar")[0].offsetHeight + document.getElementsByClassName("target")[0].offsetHeight;
    console.log(head_height);
    document.getElementsByClassName("container")[0].style.height = "calc(100vh - " + head_height + "px)";
});

$(window).on("load", function () {
    if (!!window.performance && window.performance.navigation.type === 2) {
        window.location.reload();
    }
    const anchors = $('a');
    const comp = new RegExp(location.host);
    for (let i = 0; i < anchors.length; i++) {
        if (!comp.test(anchors[i].href)) {

            const span = $('<span>', {class: 'text'}).get(0);
            if (anchors[i].id) {
                span.id = anchors[i].id;
            }
            span.innerHTML = anchors[i].innerHTML;
            anchors[i].parentNode.replaceChild(span, anchors[i]);
        }
    }
});
