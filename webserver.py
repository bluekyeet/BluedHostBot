import datetime
import os
import random
import string
import base64
import databasehandler
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('PANELKEY')

lvcodes = {}

link = "https://linkvertise.bluedhost.org"

def makeid(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def linkvertise(userid, urllink):
    encoded_link = base64.b64encode(urllink.encode()).decode()
    base_url = f"https://link-to.net/{userid}/{random.randint(1, 1000)}/dynamic"
    href = f"{base_url}?r={encoded_link}"
    return href


def msToHoursAndMinutes(ms):
    msInHour = 3600000
    msInMinute = 60000
    hours = ms // msInHour
    minutes = round((ms - (hours * msInHour)) / msInMinute * 100) / 100
    return f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"


def check_if_user_maxed(user_id):
    if not user_id.isdigit():
        return render_template("error.html", message="Invalid user ID provided."), 400

    if not databasehandler.check_user_exists(user_id):
        return render_template("error.html", message="User ID not found."), 404

    linkvertise_data = databasehandler.get_linkvertise_info(user_id)
    if linkvertise_data == 400:
        return render_template("error.html", message="Something went wrong. Please contact support."), 500

    linkvertise_count = int(linkvertise_data[0])
    linkvertise_date = linkvertise_data[1]

    if linkvertise_count >= int(os.getenv("LINKVERTISE")):
        if datetime.date.fromisoformat(linkvertise_date) < datetime.date.today():
            databasehandler.update_linkvertise_count(user_id, 0)
        else:
            return render_template("error.html",
                                   message="You have reached the maximum amount of Linkvertise attempts today."), 403

    databasehandler.update_linkvertise_date(user_id, datetime.date.today().isoformat())

    return None


@app.route('/generate', methods=['GET'])
def generate_link():
    user_id = request.args.get('user_id', '')
    success = request.args.get('success', False)

    check_result = check_if_user_maxed(user_id)
    if check_result:
        return check_result

    return render_template("generate.html", link=f"{link}/gen?user_id={user_id}", success=success)


@app.route('/gen', methods=['GET'])
def gen_link():

    user_id = request.args.get('user_id', '')
    check_result = check_if_user_maxed(user_id)
    if check_result:
        return check_result

    referer = request.headers.get("Referer", "")
    if not referer or "/generate" not in referer.lower():
        return render_template("error.html", message="Something went wrong. Please contact support."), 500


    code = makeid(12)
    lv_url = linkvertise("1275759", f"{link}/redeem/{code}?user_id={user_id}")
    lvcodes[user_id] = {"code": code, "generated": datetime.datetime.now().timestamp()}

    return redirect(lv_url)


@app.route('/redeem/<code>', methods=['GET'])
def redeem_link(code):

    user_id = request.args.get('user_id', '')
    if user_id not in lvcodes or lvcodes[user_id]["code"] != code:
        return redirect(url_for('generate_link'))

    referer = request.headers.get('Referer', '')

    if not referer or 'linkvertise.com' not in referer or referer is None:
        return render_template("error.html",
                               message=f"Please make sure you are not using an ad blocker (or linkvertise bypasser)."), 403

    time_elapsed = datetime.datetime.now().timestamp() - lvcodes[user_id]["generated"]
    min_time = int(os.getenv("LINKVERTISE_MIN_TIME"))
    del lvcodes[user_id]
    if time_elapsed < min_time:
        return render_template("error.html",
                               message=f"Please make sure you are not using an ad blocker (or linkvertise bypasser)."), 403

    linkvertise_info = databasehandler.get_linkvertise_info(user_id)

    daily_total = linkvertise_info[0]
    if daily_total >= int(os.getenv("LINKVERTISE")):
        return render_template("error.html",
                               message="You have reached the maximum amount of Linkvertise attempts today."), 403

    databasehandler.update_linkvertise_count(user_id, daily_total + 1)
    databasehandler.update_coin_count(user_id, int(os.getenv("LINKVERTISE_COINS")))



    return redirect(url_for('generate_link', user_id=user_id, success=True))


def run_webserver():
    app.run(host='0.0.0.0', port=25002)
