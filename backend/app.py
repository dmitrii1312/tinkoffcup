from flask import Flask, render_template, request
from datetime import datetime
import time

# Our api
from calendar_zone import CalendarZone

app = Flask(__name__, template_folder='../templates')
mainObj = CalendarZone("http://tsquared.keenetic.pro:5232/", 'admin', 'admin')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        start_time = datetime.strptime(
            str(request.form['startTime']),
            "%Y-%m-%dT%H:%M"
        )

        end_time = datetime.strptime(
            str(request.form['endTime']),
            "%Y-%m-%dT%H:%M"
        )

        #Check entered data
        #.....


        # mainObj.
        # calendar = principal.calendar(name="tinkoffcup")
        # add_event(calendar,
        #           start=start_time,
        #           end=end_time,
        #           summary="FROM BACKEND FLASK")

        return 'Ok'
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)