import sqlite3

def upsertStats(dbconn, schoolname, date, testnum, positivenum):
    dbconn.cursor().execute("INSERT OR REPLACE INTO university_covid_stats values (?, ?, ?, ?)", (schoolname, date, testnum, positivenum))
    dbconn.commit()

def main():
    con = sqlite3.connect('covid_stats.db')
    cur = con.cursor()

    #upsertStats(con, "a", "2021/11/28", 200, 22)

    for row in cur.execute('SELECT * FROM university_covid_stats ORDER BY university_name, date'):
            print(row)

    con.close()

main()

