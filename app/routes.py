from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask, request
import plotly.graph_objs as go
from threading import Thread

import pytz
from datetime import timezone
from app import db, server, app
from app.models import Feed, Sample
import time
local_tz = pytz.timezone('Israel')

app.layout = html.Div(children=[
    html.H1(children='Eyal Sleep Analysis'),

    html.Div(children='''

    '''),
    dcc.Dropdown(
        id='sensor-input',
        options=[{'label': 'Motion', 'value': 'motion'},
                 {'label': 'Temperature', 'value': 'temperature'},
                 {'label': 'Noise', 'value': 'audio'}],
        value=['motion', 'temperature', 'audio'],
        multi=True
    ),

    dcc.Graph(
        id='coverage-graph'
    )
])

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


def clean_history():
    for s in Sample.query.order_by(Sample.time).limit(100):
        db.session.delete(s)
    db.session.commit()


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
                                time=datetime.fromtimestamp(sample['time'])
                                .replace(tzinfo=timezone.utc)
                                .astimezone(tz=local_tz).replace(tzinfo=None))
            db.session.add(new_sample)
        db.session.commit()

    if len(Sample.query.all()) >= 9900:
        Thread(target=clean_history).start()

    return 'update success'


common_yaxis_dict_list = [('y', 'yaxis', dict(titlefont=dict(color='#1f77b4'),
                                              tickfont=dict(color='#1f77b4'))),
                          ('y2', 'yaxis2', dict(titlefont=dict(color='#ff7f0e'),
                                                tickfont=dict(color='#ff7f0e'),
                                                overlaying='y',
                                                side='left',
                                                position=0.1)),
                          ('y3', 'yaxis3', dict(titlefont=dict(color='#2ca02c'),
                                                tickfont=dict(color='#2ca02c'),
                                                anchor='x',
                                                overlaying='y',
                                                side='right'))]


@app.callback(Output('coverage-graph', 'figure'),
              [Input('sensor-input', 'value')])
def update_graph(inputs):

    # plotly data and layout for fugure
    data = []
    layout = dict(xaxis=dict(title='Date',
                             rangeselector=dict(
                                 buttons=list([
                                     dict(count=1,
                                          label='1day',
                                          step='day',
                                          stepmode='backward'),
                                     dict(count=7,
                                          label='1week',
                                          step='day',
                                          stepmode='backward'),
                                     dict(step='all')
                                 ])
                             ),
                             rangeslider=dict(),
                             type='date'))
    for i, feed_name in enumerate(inputs):
        feed = Feed.query.filter_by(name=feed_name).first()
        if feed is None:
            continue

        x = []
        y = []
        for sample in feed.samples.order_by(Sample.time):
            x.append(sample.time)
            y.append(sample.value)

        feed_data = go.Scatter(
            x=x,
            y=y,
            name=feed_name,
            mode='line',
            yaxis=common_yaxis_dict_list[i][0]
        )
        data.append(feed_data)
        yaxis = common_yaxis_dict_list[i][2]
        yaxis['title'] = feed_name
        layout[common_yaxis_dict_list[i][1]] = yaxis

    figure = {
        'data': data,
        'layout': layout
    }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
