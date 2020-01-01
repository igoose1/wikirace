from .models import GameTypes, GameStats
from django.conf import settings


def get_average_move_count(class_type):
    n_avg = GameStats.get_average_hops_count()
    if n_avg is None:
        n_avg = settings.DEFAULT_MIN_MOVES[class_type] * settings.AVG_MULT
    return n_avg


def get_min_move_count(class_type):
    n_min = GameStats.get_min_hops_count()
    if n_min in None:
        n_min = settings.DEFAULT_MIN_MOVES[class_type]
    return n_min


def get_difficult_coefficient(class_type):
    if game_stats.class_type == GameTypes.trial:
        return game_stats.trial_id.difficulty
    return k_diff[game_stats.class_type]


def calculate_rating_coefficient():
    # TODO: Create dynamic coefficient
    return settings.K_DEFAULT_RATE


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
    class_type = game_stats.class_type

    k_avg = calculate_rating_coefficient()
    k_diff = get_difficult_coefficient(class_type)
    n_avg = get_average_move_count(class_type)
    n_min = get_min_move_count(class_type)

    n = game_stats.hops

    c = -1
    b = (2 * n_min - n_avg * (k_avg + 1)) / (1 - k_avg)
    a = 2 * (n_min - b)

    delta = k_diff * (a / (n - b) - c)
    if delta < -k_diff:
        delta = -k_diff

    return delta
