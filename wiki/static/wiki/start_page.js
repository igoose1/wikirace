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

    $('#diff-play').on('click', () => {
        let difficulty = $("#diff-field").val();
        postSettings(difficulty, difficulty, () => {
            window.location.href = '/game_start'
        })

    });

    $('#card-random').on('click', () => {
        postSettings('none', 'random', () => {
            window.location.href = '/game_start'
        })
    });

    function postSettings(difficulty, current_difficulty, onSuccess) {
        let CSRF = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: '/set_settings',
            type: 'POST',
            data: {
                difficulty: difficulty,
                current_difficulty: current_difficulty,
                csrfmiddlewaretoken: CSRF
            },
            success: function (msg) {
                onSuccess()
            },
        });
    }

    $('#game-id').on('input', () => {
        let input = $('#game-id');
        let game_id = input.val();
        game_id = parseInt(game_id, 10);
        if (((game_id == null) || (game_id < 0)) ^ input.hasClass("wrong-input")) {
            input.toggleClass("wrong-input");
        }
    });
});
