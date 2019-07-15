$(document).ready(() => {

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

    let closableCardList = ['tutorial', 'user-game'];
    closableCardList.forEach((value) => {
        $('#close-' + value).on('click', (event) => {
            toggleGameCard(value);
            event.stopPropagation();
        });
        let currentCard = $('#card-' + value);
        currentCard.on('click', () => {
            if (!currentCard.hasClass('card-opened'))
                toggleGameCard(value);
        });
    });

    $('#id-play').on('click', () => {
        let input = $('#game-id');
        if (input.hasClass("wrong-input"))
            return;
        let game_id = input.val();
        window.location.href = '/start_by_id/' + game_id;
    });

    let difficulty = $("#diff-field").val();
    $('#diff-play').on('click', () => {
        let newDifficulty = $("#diff-field").val();
        if (difficulty !== newDifficulty) {
            let CSRF = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: '/set_settings',
                type: 'POST',
                data: {
                    difficulty: newDifficulty,
                    csrfmiddlewaretoken: CSRF
                },
                success: function (msg) {
                    window.location.href = '/game_start'
                },
            });
        } else
            window.location.href = '/game_start'
    });

    $('#game-id').on('input', () => {
        let input = $('#game-id');
        let game_id = input.val();
        game_id = parseInt(game_id, 10);
        if (((game_id == null) || (game_id < 0)) ^ input.hasClass("wrong-input")) {
            input.toggleClass("wrong-input");
        }
    });
});