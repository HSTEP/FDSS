import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

df = pd.read_csv("optimalization_results/TEST_OPTs.csv")
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
fig.write_html("figures/test.html")



#fig = go.Figure(data=[go.Scatter3d(x=df["Period_long"], y=df["Period_short"], z=df["PnL"], color=df["Stop_loss%"], marker=dict(color=df["dd"]))])
#fig.show()

#fig = go.Figure(data=[go.Mesh3d(x=df["Period_long"],
#                y=df["Period_short"],
#                z=df["PnL"]
#                )])
#
#fig.show()