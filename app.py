from datetime import datetime
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import plotly.graph_objs as go
import pytz
from datetime import timezone

app = dash.Dash(__name__)
server = app.server # the Flask app
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(server)
migrate = Migrate(server, db)
local_tz = pytz.timezone('Israel')


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    samples = db.relationship('Sample', backref='Feed', lazy='dynamic'
                           , cascade='delete')

class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    value = db.Column(db.Float)
    time = db.Column(db.DateTime)

@server.route('/update', methods=['GET', 'POST'])
def update():
    content = request.get_json(silent=False)
    all_feeds = content['all_feeds']
    for feed in all_feeds:
        feed_name = feed['feed_name']
        samples = feed['samples']
        feed = Feed.query.filter_by(name=feed_name).first()
        if feed is None:
            feed = Feed(name=feed_name)
            db.session.add(feed)
            db.session.commit()
        for sample in samples:
            new_sample = Sample(feed_id=feed.id,
                                 value=sample['value'],
                                 time=datetime.fromtimestamp(sample['time']).replace(tzinfo=timezone.utc).astimezone(tz=local_tz))
            db.session.add(new_sample)
        db.session.commit()
            
        
    return 'update success'
    

app.layout = html.Div(children=[
    html.H1(children='Iliso Home Dashboard'),

    html.Div(children='''

    '''),

    dcc.Graph(
        id='coverage-graph'
    ),
     dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0
        )
])

@app.callback(Output('coverage-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    
    motion_feed = Feed.query.filter_by(name='motion').first()
    if motion_feed is None:
        return

    motion_x = []
    motion_y = []
    for sample in motion_feed.samples:
        motion_x.append(sample.time)
        motion_y.append(sample.value)
    data = go.Scatter(
        x = motion_x,
        y = motion_y,
        name = 'motion',
        mode = 'line'
    )

    temp_feed = Feed.query.filter_by(name='temperature').first()
    if temp_feed is None:
        return
    temp_x = []
    temp_y = []
    for sample in temp_feed.samples:
        temp_x.append(sample.time)
        temp_y.append(sample.value)
        
    temp_data = go.Scatter(
        x = temp_x,
        y = temp_y,
        name = 'temperature',
        mode = 'line',
        yaxis='y2'
    )

    audio_feed = Feed.query.filter_by(name='audio').first()
    if audio_feed is None:
        return
    audio_x = []
    audio_y = []
    for sample in audio_feed.samples:
        audio_x.append(sample.time)
        audio_y.append(sample.value)
        
    audio_data = go.Scatter(
        x = audio_x,
        y = audio_y,
        name = 'Noise',
        mode = 'line',
        yaxis='y3'
    )

    layout = dict(title = 'Home Metrics',

                  xaxis=dict(
                      # domain=[0.3, 0.7],
                      title = 'Date'
                  ),
                  yaxis=dict(
                      title='Motion',
                      titlefont=dict(
                          color='#1f77b4'
                      ),
                      tickfont=dict(
                          color='#1f77b4'
                      )
                  ),
                  yaxis2=dict(
                      titlefont=dict(
                          color='#ff7f0e'
                      ),
                      tickfont=dict(
                          color='#ff7f0e'
                      ),
                      anchor='free',
                      overlaying='y',
                      side='left',
                      position=0.1,
                      title='Temperature'
                  ),
                  yaxis3=dict(
                      title='Noise',
                      titlefont=dict(
                          color='#d62728'
                      ),
                      tickfont=dict(
                          color='#d62728'
                      ),
                      anchor='x',
                      overlaying='y',
                      side='right'
                  ),
              )
        
    figure={
        'data': [data,temp_data,audio_data],
        'layout': layout
    }
    return figure



if __name__ == '__main__':
    app.run_server(debug=True)
