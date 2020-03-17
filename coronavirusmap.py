import plotly
from plotly import graph_objs as go
import us
import pandas as pd
from bs4 import BeautifulSoup
import re
import requests

r = requests.get('https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports')
soup = BeautifulSoup(r.content, features="lxml")
dates = str(pd.read_html(str(soup)))

# Finds the .csv files date
find = re.findall('NaN                             (.*).csv',dates)
latest_date = find[-1] # Gets the last item on the list

df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + latest_date + '.csv')

for col in df.columns:
    df[col] = df[col].astype(str)

# Rename a column name
df.rename(columns={'Province/State': 'StateName'}, inplace=True)

# This filters out data so that we only have data for US
df=df[df['Country/Region'].str.contains("US")]

# Create a new column with abbreviated state names so that we can map the values later
states_dic=us.states.mapping('name', 'abbr')
df.StateName.map(states_dic)
df['code'] = df.StateName.map(states_dic)

# Remove rows with NaN
df = df.dropna()

df['text'] = df['StateName'] + '<br>' + \
    'Confirmed: ' + df['Confirmed'] + '<br>' + \
    'Deaths: ' + df['Deaths'] + '<br>' + \
    'Recovered: ' + df['Recovered'] + '<br>' + \
    'Last Update: ' + df['Last Update']



fig = go.Figure(data=go.Choropleth(
    locations=df['code'],
    z=df['Confirmed'].astype(float),
    locationmode='USA-states',
    colorscale='Reds',
    autocolorscale=False,
    text=df['text'], # hover text
    marker_line_color='white', # line markers between states
    colorbar_title="Hundreds"
))

fig.update_layout(
    title_text='Latest Reported Coronavirus Numbers by State <br>Data Source: Systems Science and Engineering at JHU <br>Data gets updated on daily basis <br>(Hover for breakdown)',
    geo = dict(
        scope='usa',
        projection=go.layout.geo.Projection(type = 'albers usa'),
        showlakes=True, # lakes
        lakecolor='rgb(255, 255, 255)'),
)

fig.show()
