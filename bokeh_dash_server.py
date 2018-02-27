#Libraries for Bokeh Server with SQL interface
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, CustomJS, GMapPlot, GMapOptions, Circle, Range1d, VBar
from bokeh.layouts import gridplot, row
from bokeh.io import curdoc

#Setup database
host = 'localhost'
user = 'postgres'
password = 'postgres'
dbname = 'postgres'
tableIn = 'tx_bcn'

#Setup dataframe
engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s'%(user,password,host,dbname))
query = "select * from %s"%(tableIn)
df = pd.read_sql(query,con=engine)
df['tx_date'] = pd.to_datetime(df['tx_date'])
hist, edges = np.histogram(df['tx_date'].dt.month, density=True, bins=len(df['tx_date'].dt.month.unique()))
source = ColumnDataSource(data=dict(
    lat=df['geom_lat'],
    lng=df['geom_lng'],
    date=df['tx_date'],
    barri=df['tx_c_barri']
    )
)
sourceHist = ColumnDataSource(data=dict(
    top=hist,
    bottom=hist*0,
    x=df['tx_date'].dt.month.unique()
    )
)

#Setup map
int_tools = "tap,box_select,lasso_select,pan,wheel_zoom,box_zoom,reset"
map_ApiKey = "AIzaSyBU8DsaCRbO31Z1ohiHOVlKJIQvnbrtanc"
map_options = GMapOptions(lat=41.3922005879675, lng=2.16525977252032, map_type="roadmap", zoom=11)

#Plots
pltSct = figure(tools = int_tools, plot_width=400, plot_height=400, x_axis_type="datetime")
pltSctMarker = Circle(x="date", y="barri", size=3, fill_color="navy", fill_alpha=0.8, line_color=None)
pltSct.add_glyph(source, pltSctMarker)

pltMap = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options, plot_width=400, plot_height=400, api_key=map_ApiKey)
pltMapMarker = Circle(x="lng", y="lat", size=3, fill_color="navy", fill_alpha=0.8, line_color=None)
pltMap.add_glyph(source, pltMapMarker)

pltHist = figure(x_range=Range1d(start=1, end=12),tools = int_tools, plot_width=800, plot_height=200)
pltHist.xaxis.ticker = df['tx_date'].dt.month.unique()
pltHistMarker = VBar(x="x", top="top", bottom="bottom", fill_color="navy", width=1, fill_alpha=0.8, line_color=None)
pltHist.add_glyph(sourceHist, pltHistMarker)

#Set up layouts and add to document
p = gridplot(pltSct, pltMap, pltHist, ncols=2)
curdoc().add_root(p)