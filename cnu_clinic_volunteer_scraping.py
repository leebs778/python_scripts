
"""
QuickNDirty script to fetch volunteer availabilities for CNU's Covid-19 Vaccine Clinic via their calendly
whose client-side requests I snooped. When availabilities are found, it prints indicating so and
uses the mac say command. Then jump to the calendly url below

Mac OS Catalina 10.15.7
Python 3.8.3

Usage: either on demand or in conjunction with crontab to run regularly.
• If using with crontab, see example below to run it every minute (that's the most frequently crontab allows)
    */1 * * * * $PYTHON_PATH $PATH_TO_THIS_SCRIPT >> $PATH_TO_OUTPUT_FILE 2>&1

• Then I keep an eye on the output file with a terminal with tail -f <Path_to_output_file>
• Practice good logfile hygiene and clear out your logs fam <3
    $ true > $PATH_TO_OUTPUT_FILE

# Url to book dates
# https://calendly.com/students-cnuclinic/students
"""

import requests
from datetime import datetime, timedelta
import os
import time
import json


# Add to list dates formatted as 'YYYY-MM-DD' if you wanna ignore days
blacklisted_days = []

def print_f(*text):
    print('[{}] '.format(datetime.now().strftime("%m/%d:%X")), *text)

def get_last_day_of_month(any_day):
    # get close to the end of the month for any day, and add 4 days 'over'
    next_month = any_day.replace(day=28) + timedelta(days=4)
    # subtract the number of remaining 'overage' days to get last day of current month, or the previous day of the first of next month
    return next_month - timedelta(days=next_month.day)

def get_formatted_time(timestamp):
    return timestamp.strftime("%Y-%m-%d")

def get_avail(response):
    avail = []
    has_avail = False
    for day in response['days']:
        if day['status'] != 'unavailable' and day['date'] not in blacklisted_days:
            has_avail = True
            avail.append("Date: {}, Spots: {}".format(day['date'], day['spots']))
    return has_avail, avail

# get next 3 months
def get_time_windows():
    time_windows = []
    start_time = datetime.now()
    for i in range(3):
        last_day = get_last_day_of_month(start_time)
        time_windows.append(
            (
                get_formatted_time(start_time),
                get_formatted_time(last_day)
            )
        )
        start_time = last_day + timedelta(days=1)
    return time_windows


def get_availabilities(start, end):
    url = "https://calendly.com/api/booking/event_types/AFA3CLO2TTN3F3N6/calendar/range?timezone=America%2FLos_Angeles&diagnostics=false&range_start={}&range_end={}"

    payload={}
    headers = {
      'authority': 'calendly.com',
      'pragma': 'no-cache',
      'cache-control': 'no-cache',
      'accept': 'application/json, text/plain, */*',
      'x-newrelic-id': 'VwUDWFRaGwECU1dbDgY=',
      'x-csrf-token': 'XK9SOhJn7uJwIxVy3c6DQWz5t+FDNRQI2pU9JMDYSZEdHlWkcuYL9qc/88bbjd0i4AxSzhC10jyDiJSptJE1Ww==',
      'x-requested-with': 'XMLHttpRequest',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
      'sec-fetch-site': 'same-origin',
      'sec-fetch-mode': 'cors',
      'sec-fetch-dest': 'empty',
      'accept-language': 'en-US,en;q=0.9',
      'cookie': '__cfduid=dce69be6d8a7192ba315a22e19d5113631614887542; referrer_user_id=9447792; referred_via=badge; website_language=en; _ga=GA1.2.1011409368.1614888917; _gid=GA1.2.418400259.1614888917; ajs_anonymous_id=%22f65eb639-907e-450c-a334-de66ed2db4d0%22; _fbp=fb.1.1614888917212.1807539883; _omappvp=ax4P6gy0pz3FhUM47eLkwf2G0BFc7GbdpzSkgphhjyHthProEaeRwLplekJsMkzclGwwHlKEH0Sx9td48rbHopHQjVbCHa5Y; _omappvs=1614888917395; _hjid=6827f3f1-9451-4442-a446-3bb2ff62e110; _hjFirstSeen=1; _hp2_id.3509290134=%7B%22userId%22%3A%227239849761114105%22%2C%22pageviewId%22%3A%225376306732314241%22%2C%22sessionId%22%3A%222979337154639959%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _hjAbsoluteSessionInProgress=0; _hp2_ses_props.3509290134=%7B%22r%22%3A%22https%3A%2F%2Fcalendly.com%2Fstudents-cnuclinic%2Fstudents%3Fmonth%3D2021-04%22%2C%22us%22%3A%22invitee%22%2C%22um%22%3A%22badge%22%2C%22ua%22%3A%22sign_up%22%2C%22ts%22%3A1614888917469%2C%22d%22%3A%22calendly.com%22%2C%22h%22%3A%22%2F%22%2C%22q%22%3A%22%3Futm_campaign%3Dsign_up%26utm_medium%3Dbadge%26utm_source%3Dinvitee%22%7D; _calendly_session=5yJtZLATpwRfyhm5I4MdbNrMygCoGsv3zWEz0mYDxsYny1M3TNhp8CNskADWSGoPkfq05VKY2KltL9uon1ZLTUTcAFDOMP%2F1JKfhxwjK%2FmbuTdJKTclWXK2NnUtz1ZmE7OTWIUHaVKOppUb5784g8Wy0hCvFlDRD0bAFEUbEOf6Ibx3qGxGvb5xd0%2B6zq8bd95lX%2F5i5V6mPYA4ypwvVp9ht5WMLadLi9gaemFFR8KUW93qOo%2F2pl9%2FxzbCtgvXpUeAnx99q8OtIOXa%2FfgAuYIxA%2BDMcFw3HL9LHCTd7Jfb3cHsyzOUIrIV%2F0cYHSFIK4Dm5vTNJwyKWdUWeyMNnTk244XfQV4nkVpOW0oqjWYarXpit90F63Br4yaUhJwnkU6bu2ToLe34EebQGO5Q9P3luE7eq3VAT4R%2BAJUpkLz6htXevK7mz7IlaFmPXGebn1QeUklQeH80aoKqE9MWDwRDYMdRC%2FZabMrlik%2BTuiOl4wrO4baPk2Hnas3VCU0SU4ttwI4WYby7XZqEx%2BlVAyf1ZXqYyCs3ur1IIeor%2BlYFOPudLxmB%2FnkEoA6W2DFCnigfvGqQF7U5BDmzNZXFwmdYqwT5o7UGxPHbGDqh9%2B9cLAppRcdTH--nXms4ZeVRxNt7W5t--T2Mx0BGru6swOxxOSpIHQA%3D%3D; _calendly_session=ysnB3DiH6WcqzVrI1Z2ODoBu7Mlp580KLEc4X76qtNU3dIK0EKxFoT%2FqdGZMw%2FJC%2Bx2JRgNAO%2F92%2FRHoiUO1OeNzWZvJyBVhMwEog7QT%2FaKgdYECq4iJvmkRt0vecwd%2BewdHP3cHqT1h0twb5MlzdCEXozKDqb5GDm01r%2Famgu4ceVBJZEWVvafhyniMYm3GAHbUGRRPS94w%2B1hnwf4dH00hevf%2BR%2B6BKC3mTVwxSVPPTcclSSsbTti6xpZ5NNKsRut93qT4knZX6G1EwqzLU9nvxRcvdo5JDUpLFLWZ4DlxGm39jWSV5QCgAH%2FWFheN6vMZNE4tKZQRQPOSR%2BLdkpOosDcbGMiet3tLdg3QSsNa06sDsjftEP2KLTYGbUD064OjdmGswVCl%2F5gxbtKpwOM29vOBfDhD%2BVIPN2H%2BQ5bDypFOpgFbfGtnPP9BtLcqCJ3a2OcMklFHTFjR39p%2Fkq9fS4eJoXtDHctvyX8jJT76B7knEtUWPzE3XFdMSkVh6%2BwFvZfX5FsBYYVRtK06yaScjM9nspozv5ADQ2FbjVpnJeGvWB3d%2Beq%2Bn9KWR1kFDcSNtyjpA74iTMjQvY7S2bZHzVpSN3v4KOyZFhkjfUTsEm40xeVG--HIx9aDseHHISyWEX--6o1H0VbRfqoAtNB4TXRkbQ%3D%3D'
    }
    return requests.request("GET", url.format(start_window, end_window), headers=headers, data=payload)

def output_availabilities(has_avail, avail):
    print_f('{} to {}:'.format(start_window, end_window))
    print_f('\tAvailability? ', has_avail)
    print_f('\tAvailabilities: ', avail)
    for i in range(1):
        # Use mac's voice command, lol, to be loud about it.
        os.system('say -v Fred "VACCINE SPOT AVAILABLE"')

# Add more iterations/pauses to get around crontab's limit around only executing
# every minute. Also don't wanna swarm calendly :)
NUM_ITERATIONS = 8
PAUSE = 5 # seconds
for i in range(NUM_ITERATIONS):
    for start_window, end_window in get_time_windows():
        response = get_availabilities(start_window, end_window)
        response_json = response.json()
        has_avail, avail = get_avail(response_json)
        if has_avail:
            output_availabilities(has_avail, avail)

    # Indicate successful execution
    print_f('.')

    time.sleep(PAUSE)
