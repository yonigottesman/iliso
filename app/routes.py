from datetime import datetime
import time

import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
from flask import Flask,request

import plotly.graph_objs as go
import pytz
from datetime import timezone
from app import db,server,app
from app.models import Feed,Sample

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
        value=['motion', 'temperature','audio'],
        multi=True
    ),

    
    dcc.Graph(
        id='coverage-graph'
    ),
    dcc.Interval(
        id='interval-component',
        interval=60*1000, # in milliseconds
        n_intervals=0
    )
])


    
    
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
                                time=datetime.fromtimestamp(sample['time']).replace(tzinfo=timezone.utc).astimezone(tz=local_tz).replace(tzinfo=None))
            db.session.add(new_sample)
        db.session.commit()
            
        
    return 'update success'
    

common_yaxis_dict_list = [('y','yaxis',dict(titlefont=dict(color='#1f77b4'),
                               tickfont=dict(color='#1f77b4'))),
                          ('y2','yaxis2',dict(titlefont=dict(color='#ff7f0e'),
                               tickfont=dict(color='#ff7f0e'),
                               overlaying='y',
                               side='left',
                               position=0.1)),
                          ('y3','yaxis3',dict(titlefont=dict(color='#2ca02c'),
                               tickfont=dict(color='#2ca02c'),
                               anchor='x',
                               overlaying='y',
                               side='right'))]

@app.callback(Output('coverage-graph', 'figure'),
              [Input('sensor-input', 'value')])
def update_graph(inputs):

    #plotly data and layout for fugure
    data = []
    layout = dict(# title='Home Metrics',
                  xaxis=dict(
                      title = 'Date',
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
                      type='date'
                  )                 
    )
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
            x = x,
            y = y,
            name = feed_name,
            mode = 'line',
            yaxis = common_yaxis_dict_list[i][0]
        )
        data.append(feed_data)
        yaxis = common_yaxis_dict_list[i][2]
        yaxis['title'] = feed_name
        layout[common_yaxis_dict_list[i][1]] = yaxis

        
    figure={
        'data': data,
        'layout': layout
    }
    return figure
        
# @app.callback(Output('coverage-graph', 'figure'),
#               [Input('interval-component', 'n_intervals')])
# def update_graph_live(n):
    
#     motion_feed = Feed.query.filter_by(name='motion').first()
#     if motion_feed is None:
#         return

#     motion_x = []
#     motion_y = []
#     for sample in motion_feed.samples.order_by(Sample.time):
#         motion_x.append(sample.time)
#         motion_y.append(sample.value)
#     data = go.Scatter(
#         x = motion_x,
#         y = motion_y,
#         name = 'motion',
#         mode = 'line'
#     )

#     temp_feed = Feed.query.filter_by(name='temperature').first()
#     if temp_feed is None:
#         return
#     temp_x = []
#     temp_y = []
#     for sample in temp_feed.samples.order_by(Sample.time):
#         temp_x.append(sample.time)
#         temp_y.append(sample.value)
        
#     temp_data = go.Scatter(
#         x = temp_x,
#         y = temp_y,
#         name = 'temperature',
#         mode = 'line',
#         yaxis='y2'
#     )

#     audio_feed = Feed.query.filter_by(name='audio').first()
#     if audio_feed is None:
#         return
#     audio_x = []
#     audio_y = []
#     for sample in audio_feed.samples.order_by(Sample.time):
#         audio_x.append(sample.time)
#         audio_y.append(sample.value)
        
#     audio_data = go.Scatter(
#         x = audio_x,
#         y = audio_y,
#         name = 'Noise',
#         mode = 'line',
#         yaxis='y3'
#     )

#     layout = dict(title = 'Home Metrics',

#                   xaxis=dict(
#                       # domain=[0.3, 0.7],
#                       title = 'Date',
#                       rangeselector=dict(
#                           buttons=list([
#                               dict(count=1,
#                                    label='1day',
#                                    step='day',
#                                    stepmode='backward'),
#                               dict(count=7,
#                                    label='1week',
#                                    step='day',
#                                    stepmode='backward'),
#                               dict(step='all')
#                           ])
#                       ),
#                       rangeslider=dict(),
#                       type='date'
#                   ),
#                   yaxis=dict(
#                       title='Motion',
#                       titlefont=dict(
#                           color='#1f77b4'
#                       ),
#                       tickfont=dict(
#                           color='#1f77b4'
#                       )
#                   ),
#                   yaxis2=dict(
#                       titlefont=dict(
#                           color='#ff7f0e'
#                       ),
#                       tickfont=dict(
#                           color='#ff7f0e'
#                       ),
#                       anchor='free',
#                       overlaying='y',
#                       side='left',
#                       position=0.1,
#                       title='Temperature'
#                   ),
#                   yaxis3=dict(
#                       title='Noise',
#                       titlefont=dict(
#                           color='#d62728'
#                       ),
#                       tickfont=dict(
#                           color='#d62728'
#                       ),
#                       anchor='x',
#                       overlaying='y',
#                       side='right'
#                   ),
#               )
        
#     figure={
#         'data': [data,temp_data,audio_data],
#         'layout': layout
#     }
#     return figure



if __name__ == '__main__':
    app.run_server(debug=True)
