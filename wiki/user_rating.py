from .models import GameTypes, GameStats


def get_average_move_count():
    return GameStats.get_average_hops_count()


def get_min_move_count():
    return GameStats.get_min_hops_count()


def get_difficult_coefficient(game_stats):
    # There are random difficulty coefficients
    # TODO: Find normal values
    k_diff = {
        GameTypes.easy: 1.0,
        GameTypes.medium: 2.0,
        GameTypes.hard: 3.0,
        GameTypes.random: 2.0,
        GameTypes.by_id: 0.0
    }
    if game_stats.class_type == GameTypes.trial:
        return game_stats.trial_id.difficulty
    return k_diff[game_stats.class_type]


def calculate_rating_coefficient():
    # TODO: Create dynamic coefficient
    return 0.5


def calculate_rate_change(game_stats):
    """
        f(n) = k_diff * (a / (n - b) - c)
        f(n_min) = k_diff
        f(n_avg) = k_avg
        f(inf) = -k_diff
        f(n) - change of rate, -k_diff <= f(n) <= k_diff
        k_diff - difficulty coefficient, k_diff >= 0
        k_avg - rating coefficient, k_avg < 1
        a, b, c - some parameters
    """

    k_avg = calculate_rating_coefficient()
    k_diff = get_difficult_coefficient[game_stats]
    n_avg = get_average_move_count()
    n_min = get_min_move_count()

    n = game_stats.hops

    c = -1
    b = (2 * n_min - n_avg * (k_avg + 1)) / (1 - k_avg)
    a = 2 * (n_min - b)

    delta = k_diff * (a / (n - b) - c)
    if delta < -k_diff:
        delta = -k_diff

    return delta
