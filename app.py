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


app = dash.Dash(__name__)
server = app.server # the Flask app
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(server)
migrate = Migrate(server, db)

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
                                 time=datetime.fromtimestamp(sample['time']))
            db.session.add(new_sample)
        db.session.commit()
            
        
    return 'update success'
    

app.layout = html.Div(children=[
    html.H1(children='Iliso Home Dashboard'),

    html.Div(children='''
        Feed coverage
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
    if motion_feed is not None:
        x = []
        y = []
        for sample in motion_feed.samples:
            x.append(sample.time)
            y.append(sample.value)
    
        figure={
            'data': [
                {'x': x, 'y': y, 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Coverage'
            }
        }
        return figure



if __name__ == '__main__':
    app.run_server(debug=True)
