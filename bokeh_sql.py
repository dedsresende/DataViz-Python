import random
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, CustomJS, GMapPlot, GMapOptions, Circle, Range1d
from bokeh.layouts import gridplot
from sqlalchemy import create_engine


host = 'localhost'
user = 'postgres'
password = 'postgres'
dbname = 'postgres'
tableIn = 'tx_bcn'


engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s'%(user,password,host,dbname))
query = "select * from %s"%(tableIn)
df = pd.read_sql(query,con=engine)
df['tx_date'] = pd.to_datetime(df['tx_date'])
df['year'] = df['tx_date'].dt.year
df['month'] = df['tx_date'].dt.month
df['day'] = df['tx_date'].dt.date
df['hour'] = df['tx_date'].dt.hour


dfMonth = df.groupby(df['month'], as_index=False).size().reset_index()
dfMonth.columns = ['month','n']

map_options = GMapOptions(lat=41.3922005879675, lng=2.16525977252032, map_type="roadmap", zoom=11)
plotMapBase = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options, plot_width=400, plot_height=400)
plotMapBase.api_key = "AIzaSyBU8DsaCRbO31Z1ohiHOVlKJIQvnbrtanc"


source = ColumnDataSource(data=dict(
    x0=df['tx_date'], y0=df['tx_c_barri'],
    x1=df['geom_lng'], y1=df['geom_lat'],
    dateReset=df['tx_date'], barriReset=df['tx_c_barri'],
    xReset=df['geom_lng'], yReset=df['geom_lat'],
    month=df['month']
    )
)
sourceHist = ColumnDataSource(dfMonth)

TOOLS = "tap,box_select,lasso_select,pan,wheel_zoom,box_zoom,reset"


pltSct = figure(tools = TOOLS, plot_width=400, plot_height=400, x_axis_type="datetime")
pltSct.scatter(x='x0', y='y0', size=3, alpha=0.5, source=source, color='navy', selection_color='orange')
mapMarker = Circle(x="x1", y="y1", size=5, fill_color="navy", fill_alpha=0.8, line_color=None)
plotMapBase.add_glyph(source, mapMarker)
pltHist = figure(tools = TOOLS, plot_width=800, plot_height=200)
pltHist.vbar(x='month', top='n', width=0.5, source=sourceHist, color='navy', selection_color='orange')
pltHist.xaxis.ticker = dfMonth['month']


source.callback = CustomJS(args=dict(source=source, sourceHist=sourceHist), code="""
    var selIds = source.selected['1d'].indices;
    var selData = source.data;
    var sourceOutData = sourceHist.data;


    console.log(selData['x0'][0]);
    """)

sourceHist.callback = CustomJS(args=dict(source=source, sourceHist=sourceHist), code="""
    var selIds = sourceHist.selected['1d'].indices[0];
    var selData = sourceHist.data;
    var sourceData = source.data;

    sourceData['x0'] = source.data['dateReset'];
    sourceData['x1'] = source.data['xReset'];
    sourceData['y0'] = source.data['barriReset'];
    sourceData['y1'] = source.data['yReset'];

    var x0 = [];
    var x1 = [];
    var y0 = [];
    var y1 = [];


    for (i in sourceData['month']){
        if (sourceData['month'][i]==selIds){
            x0.push(sourceData['x0'][i]);
            x1.push(sourceData['x1'][i]);
            y0.push(sourceData['y0'][i]);
            y1.push(sourceData['y1'][i])
        }
    };

    sourceData['x0'] = x0;
    sourceData['x1'] = x1;
    sourceData['y0'] = y0;
    sourceData['y1'] = y1;

    source.change.emit();
    """)


p = gridplot(pltSct, plotMapBase, pltHist, ncols=2)
show(p)