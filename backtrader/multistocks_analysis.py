import plotly.express as px
import os
import pandas as pd
import csv
import matplotlib.pyplot as plt
import plotly.graph_objects as go

dfs = []

#filepaths = ["/Users/stepan/OneDrive/Diplomka/python/backtrader/csv_multistocks/" + path for path in os.listdir(path)]

path = "csv_multistocks/"
filepaths = os.listdir(path)

for file in filepaths:
    with open("csv_multistocks/"+file) as f:
        reader = csv.reader(f, delimiter=",")
        rows = []
        reader.__next__()  # Skip first line
        for row in reader:
            if "======" in row[0]:
                break
            rows.append(row[:13] + row[14:])

        df = pd.DataFrame(rows[1:], columns=rows[0])  # [start:stop:step]
        df = df.set_index("datetime")
        df.name = file[4:-4]
        dfs.append(df)
        #print(df)

def final_value_to_csv():
    totalvalue= []
    for value in dfs:
        totalval = value["value"].tail(1)
        totalvalue.append(totalval)
    totalvalue = pd.concat(totalvalue)
    #totalvalue.to_csv("totalvalue.csv")
    totalvalue_ok = pd.read_csv("totalvalue.csv")
    return

def mustistocks_value_chart():
    fig = go.Figure()
    for df in dfs:
        fig.add_trace(go.Scatter(x=df.index, y=df["value"].astype(float), mode="lines", name=df.name))
    
    #fig.update_traces(marker=dict(size=9))
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', showgrid=True, gridwidth=0.5, gridcolor='grey', zeroline=True, zerolinewidth=2, zerolinecolor='black' )
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', showgrid=True, gridwidth=0.5, gridcolor='grey', zeroline=True, zerolinewidth=2, zerolinecolor='black')
    fig.update_layout(
        title_text = "Hodnota účtu", title_x = 0.5,
        xaxis_title="Datum",
        yaxis_title="Hodnota účtu",
        plot_bgcolor = "white",
        legend_font_color = "black",
        title_font_color= "black",
        margin=dict(
            #l=0,
            #r=0,
            #b=0,
            #t=0
        ),
    paper_bgcolor="white",
    )
    fig.write_image("figures/test.png", scale=3)
    fig.write_html("figures/test.html")
    return

mustistocks_value_chart()

# print(totalvalue_ok.index)
# fig = go.Figure()
# fig.add_trace(go.Scatter(y=totalvalue_ok["value"],mode="lines"))
# fig.show()
