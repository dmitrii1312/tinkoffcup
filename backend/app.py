from flask import Flask, render_template, request
from datetime import datetime
import time

# Our api
from calendar_zone import CalendarZone
from parse_config import *
import os.path as path

# Start app
app = Flask(__name__, template_folder='../templates')

### READ CONFIG JSON ###

# Ищем и проверяем существование конфига в корне проекта
config_path = path.abspath(path.join(__file__ ,"../../config.json"))
if not path.exists(config_path):
    print("Config file doesn't exists")

json_config_data = get_all_config(config_path)

remote_server = json_config_data['caldav_server']
username = json_config_data['username']
password = json_config_data['password']

zones = json_config_data['calForZones']

calendar_zones_objs = {}
for i in zones:
    calendar_zones_objs[i] = \
        CalendarZone(remote_server, username, password, zones[i])

### READ CONFIG JSON ###

@app.route('/', methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':

    #     start_time = datetime.strptime(
    #         str(request.form['startTime']),
    #         "%Y-%m-%dT%H:%M"
    #     )

    #     end_time = datetime.strptime(
    #         str(request.form['endTime']),
    #         "%Y-%m-%dT%H:%M"
    #     )

    data = {
        'zones': list(calendar_zones_objs.keys())
    }

        # mainObj.
        # calendar = principal.calendar(name="tinkoffcup")
        # add_event(calendar,
        #           start=start_time,
        #           end=end_time,
        #           summary="FROM BACKEND FLASK")

        # return render_template('index.html', data=data)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)