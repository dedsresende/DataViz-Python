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
source = ColumnDataSource(df)
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
pltSctMarker = Circle(x="tx_date", y="tx_c_barri", size=3, fill_color="navy", fill_alpha=0.8, line_color=None)
pltSctMarkerSelected = Circle(x="tx_date", y="tx_c_barri", size=3, fill_color="orange", fill_alpha=0.8, line_color=None)
pltSct.add_glyph(source, pltSctMarker, selection_glyph = pltSctMarkerSelected, nonselection_glyph = pltSctMarker)

pltMap = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options, plot_width=400, plot_height=400, api_key=map_ApiKey)
pltMapMarker = Circle(x="geom_lng", y="geom_lat", size=3, fill_color="navy", fill_alpha=0.8, line_color=None)
pltMapMarkerSelected = Circle(x="geom_lng", y="geom_lat", size=3, fill_color="orange", fill_alpha=0.8, line_color=None)
pltMap.add_glyph(source, pltMapMarker, selection_glyph = pltMapMarkerSelected, nonselection_glyph = pltMapMarker)

pltHist = figure(x_range=Range1d(start=1, end=12),tools = int_tools, plot_width=800, plot_height=200)
pltHist.xaxis.ticker = df['tx_date'].dt.month.unique()
pltHistMarker = VBar(x="x", top="top", bottom="bottom", fill_color="navy", width=1, fill_alpha=0.8, line_color=None)
pltHistMarkerSelected = VBar(x="x", top="top", bottom="bottom", fill_color="orange", width=1, fill_alpha=0.8, line_color=None)
pltHist.add_glyph(sourceHist, pltHistMarker, selection_glyph = pltHistMarkerSelected, nonselection_glyph = pltHistMarker)

#Set up callbacks
def selection_source(attrname, old, new):
    selIndx = source.selected['1d']['indices']
    dfSel = df.ix[selIndx]

    hist, edges = np.histogram(dfSel['tx_date'].dt.month, density=True, bins=len(dfSel['tx_date'].dt.month.unique()))

    sourceHist.data['top'] = hist
    sourceHist.data['bottom'] = hist*0
    x=dfSel['tx_date'].dt.month.unique()


def selection_sourceHist(attrname, old, new):
    selIndx = sourceHist.selected['1d']['indices'][0]
    selIndxVal = sourceHist.data['top'][selIndx]

    dfHist = df
    dfHist['bin'] = pd.qcut(df['tx_date'].dt.month, len(df['tx_date'].dt.month.unique()), duplicates='drop', labels=False)

    source.data['tx_date'] = dfHist[dfHist['bin']==selIndx]['tx_date']
    source.data['tx_c_barri'] = dfHist[dfHist['bin']==selIndx]['tx_c_barri']
    source.data['geom_lng'] = dfHist[dfHist['bin']==selIndx]['geom_lng']
    source.data['geom_lat'] = dfHist[dfHist['bin']==selIndx]['geom_lat']


source.on_change('selected', selection_source)
sourceHist.on_change('selected', selection_sourceHist)

#Set up layouts and add to document
p = gridplot(pltSct, pltMap, pltHist, ncols=2)
curdoc().add_root(p)