from flask import Flask, render_template, request
import requests
import json
from time import sleep
import random
from datetime import datetime, timedelta
from config import CLASSROOM_ID, COOKIES

app = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-CSRFToken': COOKIES['csrftoken'],
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://play.picoctf.org/classrooms/' + str(CLASSROOM_ID),
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}


@app.route("/")
def scoreboard():
    try:
        refresh = int(request.args.get("refresh"))
    except BaseException:
        refresh = False

    if "demo" in request.args:
        scoreboard = {}
        challenges = {
            i: {"gym_points": 50 * random.randint(1, 9)} for i in range(20)
        }
        for i in range(20):
            user_id = str(i)
            scoreboard[user_id] = {
                "username": f"user_{i}",
                "solves": {},
                "points": 0
            }

            num_solves = random.randint(0, 15)
            user_submissions = random.sample(
                list(challenges.keys()), num_solves)

            user_submissions = {
                chall_id: {
                    "timestamp": datetime.now() - timedelta(minutes=random.randint(0, 60))
                }
                for chall_id in user_submissions
            }

            # sort the solved challenges by timestamp
            user_submissions = dict(sorted(
                user_submissions.items(),
                key=lambda item: item[1]["timestamp"]
            ))

            for chall_id in user_submissions:
                timestamp = user_submissions[chall_id]["timestamp"]
                scoreboard[user_id]['points'] += \
                    challenges[chall_id]['gym_points']
                scoreboard[user_id]["solves"][chall_id] = {
                    "points_gained": challenges[chall_id]['gym_points'],
                    "total_points": scoreboard[user_id]['points'],
                    "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                }

        # sort the scoreboard by points
        scoreboard = dict(sorted(
            scoreboard.items(),
            key=lambda item: item[1]['points'],
            reverse=True))

        return render_template(
            'scoreboard.html',
            scoreboard=scoreboard,
            refresh=refresh)

    try:
        with open('challenges.json', 'r') as f:
            data = json.load(f)
            challenges = data['challenges']
    except Exception as e:
        next_page = 'https://play.picoctf.org/api/challenges/'
        params = {'order_by': 'gym_points'}
        challenges = []
        while next_page:
            response = requests.get(
                next_page,
                params=params,
                cookies=COOKIES,
                headers=headers)

            if response.status_code != 200:
                print("Failed to retrieve challenges:", response.status_code)
                print("Response:", response.text)
                return

            data = response.json()
            next_page = data['next']
            challenges += data['results']

            sleep(5)

        challenges = {
            challenge['id']: challenge for challenge in challenges
        }

        with open('challenges.json', 'w') as f:
            json.dump({'challenges': challenges}, f)

    params = {
        'classroom': str(CLASSROOM_ID),
        'page': '1',
        'pending': 'false',
        'leader': 'false',
        'page_size': '100',
        'event': 'gym',
    }

    response = requests.get(
        'https://play.picoctf.org/api/classroom_members/',
        params=params,
        cookies=COOKIES,
        headers=headers)

    if response.status_code != 200:
        print("Failed to retrieve data:", response.status_code)
        print("Response:", response.text)
        exit(1)

    data = response.json()
    # Extract usernames
    users = [(str(member['user_id']), member['username'])
             for member in data['results']]

    try:
        with open('scoreboard.json', 'r') as f:
            data = json.load(f)
            scoreboard = data['scoreboard']
    except Exception as e:
        scoreboard = {}

    for user_id, username in users:
        if user_id not in scoreboard:
            scoreboard[user_id] = {
                "username": username,
                "solves": {},
                "points": 0
            }

        params = {
            'user': user_id,
            'page_size': 100
        }

        response = requests.get(
            'https://play.picoctf.org/api/submissions/',
            params=params,
            cookies=COOKIES,
            headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve submissions for {username}:",
                  response.status_code)
            continue

        data = response.json()
        user_submissions = data['results']
        user_submissions = {
            str(challenge['challenge']['id']): {"timestamp": challenge['timestamp']}
            for challenge in user_submissions
            if challenge['correct']
        }
        user_submissions = dict(sorted(
            user_submissions.items(),
            key=lambda item: item[1]["timestamp"]))

        for chall_id in user_submissions:
            if chall_id not in scoreboard[user_id]["solves"]:
                scoreboard[user_id]['points'] += \
                    challenges[chall_id]['gym_points']
                scoreboard[user_id]["solves"][chall_id] = {
                    "points_gained": challenges[chall_id]['gym_points'],
                    "total_points": scoreboard[user_id]['points'],
                    "timestamp": user_submissions[chall_id]["timestamp"]
                }

        sleep(0.5)

    # sort the scoreboard by points
    scoreboard = dict(sorted(
        scoreboard.items(),
        key=lambda item: item[1]['points'],
        reverse=True))

    with open('scoreboard.json', 'w') as f:
        json.dump({'scoreboard': scoreboard}, f)

    return render_template(
        'scoreboard.html',
        scoreboard=scoreboard,
        refresh=refresh)
