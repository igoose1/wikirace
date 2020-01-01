$(document).ready(() => {

    $('#id-play').on('click', () => {
        let input = $('#game-id');
        if (input.hasClass("wrong-input"))
            return;
        let game_id = input.val();
        window.location.href = 'start_by_id/' + game_id;
    });

    $('#diff-play').on('click', () => {
        let difficulty = $("#diff-field").val();
        postSettings(difficulty, () => {
            window.location.href = 'game_start'
        })
    });

    $('#card-random').on('click', () => {
        postSettings('random', () => {
            window.location.href = 'game_start'
        })
    });


    $('#card-global-rating').on('click', () => {
                window.location.href = 'global_rating'
    });

    function postData(where, data, onSuccess) {
        data['csrfmiddlewaretoken'] = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: where,
            type: 'POST',
            data: data,
            success: function (msg) {
                onSuccess()
            },
        });
    }

    function postSettings(difficulty, onSuccess) {
        postData('set_settings',
            {
                difficulty: difficulty,
            },
            onSuccess
        );
    }

    $('#game-id').on('input', () => {
        let input = $('#game-id');
        let game_id = input.val();
        game_id = parseInt(game_id, 10);
        if (((game_id == null) || (game_id < 0)) ^ input.hasClass("wrong-input")) {
            input.toggleClass("wrong-input");
        }
    });

    $('#card-continue').on('click', () => {
        window.location.href = 'continue';
    });


    let closableCardList = ['tutorial', 'user-game', 'trial', 'settings'];
    closableCardList.forEach((value) => {
        addOnClick(value)
    });

    $('#name-button').on('click', (event) => {
        let name = $("#name").val();
        postData('set_name',{name: name}, () => {
            toggleGameCard('settings');
            event.stopPropagation();
        });
    });

    $('#name-first-button').on('click', (event) => {
        let name = $("#name-first").val();
        postData('set_name',{name: name}, () => {
            toggleGameCard('name');
            event.stopPropagation();
            $('#card-name').toggleClass('force-invisible')
        });
    });

    $("#open-settings").on('click', () => {
        toggleGameCard('settings');
    });

    $('.event-box').on('click', (event) => {
        let eventBlock = $(event.target);
        while (!eventBlock[0].classList.contains('event-box'))
            eventBlock = eventBlock.parent();
        eventBlock.find('.event-content').toggleClass('visible').toggleClass('invisible');
        eventBlock.find('.expand-event-img').toggleClass('inverted');
        event.stopPropogation();    
    });
});
