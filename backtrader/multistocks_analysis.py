import plotly.express as px
import os
import pandas as pd
import csv
import matplotlib.pyplot as plt
import plotly.graph_objects as go

dfs = []

path = "csv_multistocks/"
filepaths = os.listdir(path)

for file in filepaths:
    #print(file)
    if "csv" not in file:
        continue

    with open(path+file, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        rows = []
        reader.__next__()  # Skip first line
        for row in reader:
            if "======" in row[0]:
                break
            rows.append(row[:13] + row[14:])

        df = pd.DataFrame(rows[1:], columns=rows[0])  # [start:stop:step]
        df = df.set_index("datetime")
        df.name = os.path.splitext(os.path.basename(file))[0]
        dfs.append(df)
        
        #print(df)

def final_value_to_csv():
    totalvalue= []
    for value in dfs:
        totalval = pd.DataFrame(columns=["Data akcie", "Konečná hodnota"])
        totalval["Konečná hodnota"] = value["value"].tail(1)
        totalval["Data akcie"] = value.name
        totalval = totalval.reset_index()
        totalval = totalval.drop("datetime", 1)
        totalval = totalval.set_index("Data akcie")
        totalvalue.append(totalval)
    totalvalue = pd.concat(totalvalue)

    dch= []
    for ch in dfs:
        dchf = pd.DataFrame()
        dchf["Počáteční cena akcie"] = ch["close"].head(1)
        dchf["Data akcie"] = ch.name
        dchf = dchf.reset_index()
        dchf = dchf.drop("datetime", 1)
        dchf = dchf.set_index("Data akcie")
        dch.append(dchf)
    dch = pd.concat(dch)

    dct= []
    for ch in dfs:
        dctf = pd.DataFrame()
        dctf["Konečná cena akcie"] = ch["close"].tail(1)
        dctf["Data akcie"] = ch.name
        dctf = dctf.reset_index()
        dctf = dctf.drop("datetime", 1)
        dctf = dctf.set_index("Data akcie")
        dct.append(dctf)
    dct = pd.concat(dct)

    totalvalue["Počáteční cena akcie"] = dch["Počáteční cena akcie"].astype("float").round(decimals=6)
    totalvalue["Konečná cena akcie"] = dct["Konečná cena akcie"].astype("float").round(decimals=6)

    vstupní_poplatek = totalvalue["Konečná cena akcie"].astype("float").sum() * 0.002
    poplatek_za_ukončení = totalvalue["Počáteční cena akcie"].astype("float").sum() * 0.002
    poplatky = vstupní_poplatek + poplatek_za_ukončení

    khu_s = (totalvalue["Konečná hodnota"].astype("float").sum() - 11000).round(decimals=6)
    khu_bah = (totalvalue["Konečná cena akcie"].astype("float").sum() - totalvalue["Počáteční cena akcie"].astype("float").sum()).round(decimals=6)
    print("-"*100)
    print(totalvalue.sort_values(by="Konečná hodnota", ascending=False))
    print("-"*100)
    print("Součet konečných hodnot= ", khu_s)
    print("Konečná hodnota portfolia při použití strategie Buy and Hold= ", khu_bah - poplatky)
    print("-"*100)

    #totalvalue.to_csv("backtrader/totalvalue.csv")
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
    fig.update_xaxes(
    rangebreaks=[
        {'pattern': 'day of week', 'bounds': [6, 1]},
        {'pattern': 'hour', 'bounds':[21,13]}
    ])
    fig.show()
    plotly.io.write_json(fig, "backtrader/figures/twitterAIR1mm.json")
    #fig.write_image("backtrader/figures/test.png", scale=3)
    #fig.write_html("backtrader/figures/newsF2_multistocsk.html")
    return

final_value_to_csv()
mustistocks_value_chart()