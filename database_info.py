import kody
import pandas as pd
def database_info(db_name_contains, column_name):

    cursor=kody.cnx.cursor()

    # získání názvu tabulek
    cursor.execute("""SELECT table_name FROM information_schema.tables WHERE TABLE_NAME LIKE '%"""+db_name_contains+"""%'""")
    table = [item[0] for item in cursor.fetchall()]
    table.sort()

    df = pd.DataFrame(columns=["Název tabulky","Počet řádků","Nejstarší příspěvek", "Nejnovější příspěvek", "Velikost [MB]"])

    for table_name in table:
        try:
            cursor.execute("""SELECT COUNT(*) FROM """+ table_name +""";""")
            count = int(cursor.fetchone()[0])
            cursor.execute("""SELECT """+column_name+""" FROM """+ table_name +""" ORDER BY """+column_name+""" DESC LIMIT 1;""")
            time_to = str(cursor.fetchone()[0])
            cursor.execute("""SELECT """+column_name+""" FROM """+ table_name +""" ORDER BY """+column_name+""" ASC LIMIT 1;""")
            time_from = str(cursor.fetchone()[0])
            cursor.execute("SELECT ROUND(((data_length + index_length) / 1024 / 1024), 2) FROM information_schema.TABLES WHERE TABLE_NAME LIKE \""+ table_name +"\" ")
            size = float(cursor.fetchone()[0])

            df = df.append({"Název tabulky" : table_name,"Počet řádků" : count,"Nejstarší příspěvek" : time_from, "Nejnovější příspěvek" : time_to, "Velikost [MB]" : size}, ignore_index=True)

            print('{:<23s}{:>8s}{:>25s}{:>25s}{:>14s}'.format(table_name,str(count),time_from, time_to, str(size)))
        except TypeError:
            continue
    df["Počet řádků"].astype("int")
    df["Velikost [MB]"].astype("float")
    print("-"*100)
    print(df)
    print("Celková velikost= ", df["Velikost [MB]"].sum(), "MB")
    print("Celkový počet řádků= ", df["Počet řádků"].sum())
    print("-"*100)
    #df.to_csv("database_info.csv")


print('{:<23s}{:>8s}{:>25s}{:>25s}{:>14s}'.format("table_name",str("count"),"time_from", "time_to", str("Size [MB]")))
print("-"*100)
#database_info("news", "published")
#database_info("tweetTable_AR", "created_at")
database_info("reddit", "time")
print("-"*100)