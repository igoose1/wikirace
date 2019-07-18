$(document).ready(() => {
    let closableCardList = ['leaderboard', 'share'];
    closableCardList.forEach((value) => {
        addOnClick(value)
    });

    let friendsButton = $('#friends-button');
    let globalButton = $('#global-button');
    let friendsTable = $('#friends-table');
    let globalTable = $('#global-table');

    function toggle() {
        friendsTable.toggleClass('closed');
        globalTable.toggleClass('closed');
        friendsButton.toggleClass('switch-checked');
        globalButton.toggleClass('switch-checked');
    }

    friendsButton.on('click', () => {
        if (friendsTable.hasClass('closed'))
            toggle()
    });

    globalButton.on('click', () => {
        if (globalTable.hasClass('closed'))
            toggle()
    });

    $("#copy_link").on('click', (event) => {
        const copyText = document.getElementById("link");
        copyText.select();
        document.execCommand("copy");
        alert("Copied the text: " + copyText.value);
        event.stopPropagation();
    })
});