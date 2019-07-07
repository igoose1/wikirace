from django.conf import settings
from django.db.models import  F, ExpressionWrapper, fields
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from wiki.models import GameStat
from datetime import datetime, timedelta
from django.utils import timezone

def get_date_str(date):
    return date.strftime('%d %H:%M')

def get_period_str(period):
    days = ''
    if (period.days != 0):
        days = str(period.days)
    hours  = period.seconds // 3600
    mins = (period.seconds % 3600) // 60
    return days + ' {:02}:{:02}'.format(hours,mins)

def g_activity_in_time(period, now_time):
    activity_in_time = []
    max_total = 1
    for i in range(24):
        sel_time = now_time - period
        all_of = GameStat.objects.filter(steps__gte=1).filter(start_time__gte=sel_time).filter(start_time__lte=now_time).all()
        total = len(all_of)
        max_total = max(max_total, total)
        activity_in_time.append(
                {
                    'total': total,
                    'tip': get_date_str(now_time)
                }
            )

        now_time = sel_time
    activity_in_time = list(reversed(activity_in_time))
    return {
                'title': 'Activity in time',
                'name': 'Games started',
                'tip': 'time',
                'max': max_total,
                'g': activity_in_time
            }

def g_steps_in_time(period, now_time):
    steps_in_time = []
    max_total = 1
    for i in range(24):
        sel_time = now_time - period
        all_of = GameStat.objects.filter(start_time__gte=sel_time).filter(start_time__lte=now_time).all()
        total = sum(map(lambda x: x.steps, all_of))
        max_total = max(max_total, total)
        steps_in_time.append(
                {
                    'total': total,
                    'tip': get_date_str(now_time)
                }
            )

        now_time = sel_time
    steps_in_time = list(reversed(steps_in_time))
    return {
                'title': 'Steps in time',
                'name': 'Steps in started games',
                'tip': 'time',
                'max': max_total,
                'g': steps_in_time
            }

def g_finished_in_time(period, now_time):
    finished_in_time = []
    max_finished = 1
    for i in range(24):
        sel_time = now_time - period
        all_of = GameStat.objects.filter(finished=True).filter(last_action_time__gte=sel_time).filter(last_action_time__lte=now_time).all()
        total = len(all_of)
        max_finished = max(max_finished, total)
        finished_in_time.append(
                {
                    'total': total,
                    'tip': get_date_str(now_time)
                }
            )

        now_time = sel_time    
    finished_in_time = list(reversed(finished_in_time))
    return  {
                'title': 'Finished games in time',
                'name': 'Finished games',
                'tip': 'time',
                'max': max_finished,
                'g': finished_in_time
            }

def g_steps_chart(period, now_time):
    sel_time = now_time - period
    steps = []
    max_steps = 1
    for i in range(1,24):
        all_of = GameStat.objects.filter(steps=i).filter(last_action_time__gte=sel_time).filter(last_action_time__lte=now_time).all()
        total = len(all_of)
        max_steps = max(max_steps, total)
        steps.append(
                {
                    'total': total,
                    'tip': str(i)
                }
            )
    all_of = GameStat.objects.filter(steps__gte=24).filter(last_action_time__gte=sel_time).filter(last_action_time__lte=now_time).all()
    total = len(all_of)
    max_steps = max(max_steps, total)
    steps.append(
                {
                    'total': total,
                    'tip': '>23'
                }
            )
    
    return  {
                'title': 'Steps in last active games in period of ' + get_period_str(period) + ' back of ' + get_date_str(now_time),
                'name': 'Count',
                'tip': 'steps',
                'max': max_steps,
                'g': steps
            }

def g_finished_time_chart(period, period_start):
    duration = ExpressionWrapper(F('last_action_time')-F('start_time'), output_field=fields.DurationField())
    all_of = GameStat.objects.filter(finished=True).annotate(period=duration)
    games = []
    max_games = 1
    for i in range(23):
        sel_time = period_start + period
        of = all_of.filter(period__gte=period_start, period__lte=sel_time).all()
        total = len(of)
        max_games = max(max_games, total)
        games.append(
                {
                    'total': total,
                    'tip': get_period_str(period_start)
                }
            )
        period_start = sel_time
        
    of = all_of.filter(period__gte=period_start).all()
    total = len(of)
    max_games = max(max_games, total)
    games.append(
                {
                    'total': total,
                    'tip': '>= '+get_period_str(period_start)
                }
            )
    
    return  {
                'title': 'Finished games times',
                'name': 'Games',
                'tip': 'total time',
                'max': max_games,
                'g': games
            }

def g_unfinished_time_chart(period, period_start):
    duration = ExpressionWrapper(F('last_action_time')-F('start_time'), output_field=fields.DurationField())
    all_of = GameStat.objects.filter(finished=False,steps__gte=1).annotate(period=duration)
    games = []
    max_games = 1
    for i in range(23):
        sel_time = period_start + period
        of = all_of.filter(period__gte=period_start, period__lte=sel_time).all()
        total = len(of)
        max_games = max(max_games, total)
        games.append(
                {
                    'total': total,
                    'tip': get_period_str(period_start)
                }
            )
        period_start = sel_time
        
    of = all_of.filter(period__gte=period_start).all()
    total = len(of)
    max_games = max(max_games, total)
    games.append(
                {
                    'total': total,
                    'tip': '>= '+get_period_str(period_start)
                }
            )
    
    return  {
                'title': 'Unfinished games times (with more than 0 steps)',
                'name': 'Games',
                'tip': 'total time',
                'max': max_games,
                'g': games
            }

@login_required
def statisticOverview(request):
    if request.user.is_staff:
        template = loader.get_template('admin/stats.html')
        period = timedelta(hours = 1)
        period_start = timedelta(hours = 0)
        try:
            h = int(request.GET.get('h', '0'))
            m = int(request.GET.get('m', '0'))
            H = int(request.GET.get('H', '0'))
            
            h = max(h, 0)
            m = max(m, 0)
            H = max(H, 0)
            if h+m == 0:
                h = 1
            period = timedelta(hours = h, minutes = m)
            period_start = timedelta(hours = H)
        except:
            pass
        
        
        now_time = timezone.now() - period_start
        charts = [
               g_activity_in_time(period,now_time),
               g_finished_in_time(period,now_time),
               g_steps_in_time(period,now_time),
               g_steps_chart(period,now_time),
               g_finished_time_chart(period,period_start),
               g_unfinished_time_chart(period,period_start)
            ]
        data = {
            'charts': charts
            }
        return HttpResponse(template.render(data, request))
    else:
        return Http404()
