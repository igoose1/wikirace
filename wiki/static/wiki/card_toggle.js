function changeVisible(sel) {
    sel
        .toggleClass('visible')
        .toggleClass('invisible');
}

function toggleGameCard(name) {
    changeVisible($('.block-' + name));
    changeVisible($('#close-' + name).toggleClass('close-button-visible'));
    changeVisible($('#card-' + name).toggleClass('card-opened'));
    changeVisible($('.card'));
}

function addOnClick(name) {
    $('#close-' + name).on('click', (event) => {
        toggleGameCard(name);
        event.stopPropagation();
    });
    let currentCard = $('#card-' + name);
    currentCard.on('click', () => {
        if (!currentCard.hasClass('card-opened'))
            toggleGameCard(name);
    });
}