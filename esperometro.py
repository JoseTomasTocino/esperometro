#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from datetime import datetime
import os
import locale
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

app = Flask(__name__)
app.config.from_pyfile("settings.py")

client = MongoClient(app.config['MONGO_HOST'], app.config['MONGO_PORT'])
db = client[app.config['MONGO_DB']]
db.authenticate(app.config['MONGO_USER'], os.environ['MONGO_PASS'])

@app.route('/')
def show_list():
    delays = db.delays.find()

    accumulated_delay = db.stats.find_one({'key': 'accumulated_delay'})
    average_delay = db.stats.find_one({'key': 'average_delay'})

    accumulated_delay = accumulated_delay['value'] if accumulated_delay else 0
    average_delay = average_delay['value'] if average_delay else 0.0

    stats = {
        'num_delays': db.delays.count(),
        'accumulated_delay': accumulated_delay,
        'average_delay': average_delay
    }

    return render_template("list.html", delays=delays, stats=stats)


@app.route('/add', methods=['GET', 'POST'])
def show_add_form():
    error = None

    if request.method == 'POST':

        if request.form['password'] != os.environ['PASSWORD']:
            error = u'Contraseña incorrecta'

        elif not request.form['original_time'] or \
             not request.form['arrival_time'] or \
             not request.form['date']:
            error = u'Faltan campos'

        else:
            form_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            original_time = datetime.strptime(request.form['original_time'], '%H:%M').time()
            arrival_time = datetime.strptime(request.form['arrival_time'], '%H:%M').time()

            original_datetime = datetime.combine(form_date, original_time)
            arrival_datetime = datetime.combine(form_date, arrival_time)

            delay_in_minutes = (arrival_datetime - original_datetime).seconds / 60

            obj = {
                'original_time': original_datetime,
                'arrival_time': arrival_datetime,
                'delay': delay_in_minutes
            }

            db.delays.insert_one(obj)

            update_stats()

            return redirect(url_for('show_list'))

    return render_template('form.html', error=error)

def update_stats():
    # Compute total waited time
    accumulated_delay = sum(x['delay'] for x in db.delays.find())

    # Compute average delay
    average_delay = float(accumulated_delay) / db.delays.count()

    # Delete old stats
    db.stats.delete_many({'key': { '$in': ['accumulated_delay', 'average_delay']}})

    # Write new stats
    db.stats.insert_many([
        {'key': 'accumulated_delay', 'value': accumulated_delay},
        {'key': 'average_delay', 'value': average_delay}
    ])


if __name__ == '__main__':
    app.run(host='0.0.0.0')