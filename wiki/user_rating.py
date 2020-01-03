from .models import GameTypes, GameStats
from django.conf import settings


def get_average_move_count(class_type):
    n_avg = GameStats.get_average_hops_count()
    if n_avg is None:
        n_avg = settings.DEFAULT_MIN_MOVES[class_type] * settings.AVG_MULT
    return n_avg


def get_min_move_count(game_stats):
    n_min = GameStats.get_min_hops_count()
    if game_stats.class_type == GameTypes.trial:
        n_min = game_stats.trial_id.min_hops
    if n_min is None:
        n_min = settings.DEFAULT_MIN_MOVES[game_stats.class_type.value]
    return n_min


def get_difficult_coefficient(game_stats):
    if game_stats.class_type == GameTypes.trial:
        return game_stats.trial_id.difficulty
    return settings.K_DIFF[game_stats.class_type.value]


def calculate_rating_coefficient():
    # TODO: Create dynamic coefficient
    return settings.K_DEFAULT_RATE


def calculate_rate_change(game_stats):
    """
        f(n) = k_diff * (a * n + b) / k_att
        f(n_min) = k_diff
        f(n_avg) = k_avg
        f(n) - change of rate, -k_diff <= f(n) <= k_diff
        k_diff - difficulty coefficient, k_diff >= 0
        k_avg - rating coefficient, k_avg < 1
        k_att - attempt coefficient, k_att >= 1
        a, b - some parameters
    """
    class_type = game_stats.class_type.value

    k_avg = calculate_rating_coefficient()
    k_diff = get_difficult_coefficient(game_stats)
    k_att = GameStats.get_attemps_count(game_stats.user_id, game_stats.game_pair)
    n_avg = get_average_move_count(class_type)
    n_min = get_min_move_count(game_stats)
    n = game_stats.hops

    if n_avg == n_min:
        return k_diff / k_att

    b = -n_avg * (1 - k_avg) / (n_min - n_avg) + k_avg
    a = (1 - k_avg) / (n_min - n_avg)

    delta = a * n + b
    if abs(delta) > 1:
        delta = delta / abs(delta)
    if delta < 0:
        delta /= settings.NEGATIVE_DELTA_DEVIDER
    print(delta, k_avg, k_diff, k_att, n_avg, n_min)
    return k_diff * delta / k_att
