import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def scatter3D():
    df = pd.read_csv("optimalization_results/twitterAIR1.csv")
    print(df)
    fig = px.scatter_3d(x=df["Period_long"], y=df["Period_short"], z=df["PnL"], color=df["Stop_loss%"], size=df["dd"], labels={"color": "stop-loss"})
    # fig.marker.opacity = 1
    # fig.marker.line.width=0

    fig.update_traces(marker=dict(#size= 2, 
                                opacity = 1, 
                                line=dict(width = 0)))
    fig.update_layout(
            scene = dict(
                xaxis = dict(title = "Perioda dlouhodobého MA"),
                yaxis = dict(title = "Perioda krátkodobého MA"),
                zaxis = dict(title = "Hodnota účtu"),
                aspectratio = dict( x=3, y=1, z=1 ),
                aspectmode = 'manual',
                )),
    fig.show()
    plotly.io.write_json(fig, "figures/twitterAIR1.json")
    #fig.write_html("figures/newsF2.html")
    return

def scatter03D():
    df = pd.read_csv("optimalization_results/news0G1.csv")
    print(df)
    fig = px.scatter_3d(x=df["Period_short"], y=df["Stop_loss%"], z=df["PnL"], color=df["dd"], size=df["dd"], labels={"color": "Draw Down [%]"})
    # fig.marker.opacity = 1
    # fig.marker.line.width=0

    fig.update_traces(marker=dict(#size= 2, 
                                opacity = 1, 
                                line=dict(width = 0)))
    fig.update_layout(
            scene = dict(
                xaxis = dict(title = "Perioda MA"),
                yaxis = dict(title = "Stop loss [%]"),
                zaxis = dict(title = "Hodnota účtu"),
                aspectratio = dict( x=3, y=1, z=1 ),
                aspectmode = 'manual',
                )),
    fig.show()
    plotly.io.write_json(fig, "figures/news0G1j.json")
    #fig.write_html("figures/newsF2.html")
    return

    scatter3D()












#########################creating dataframe from two resulting in dataframe where values are matching#####################
#creating dataframe-1
df1 = pd.DataFrame({
    "Name": ["Ryan","Rosy","Wills","Tom","Alice","Volter","Jay","John","Ronny"],
    "Age": [25,26,14,19,22,28,30,32,28],
    "Height": [189.0,193.0,200.0,155.0,165.0,170.0,172.0,156.0,165.0]})
#creating dataframe-2
df2 = pd.DataFrame({
    "Name": ["Ryan","Rosy","Wills","Tom","Alice",np.nan,"Jay","John","Ronny"],
    "Age": [25,26,14,0,22,28,30,32,28],
    "Height": [189.0,np.nan,200.0,155.0,np.nan,170.0,172.0,156.0,165.0]})

commondf=pd.merge(df1,df2, on=["Name","Age","Height"])
print(commondf)