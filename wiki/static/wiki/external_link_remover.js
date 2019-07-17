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
