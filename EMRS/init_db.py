import pandas as pd
import sqlite3 as sq

# Import CSV
data = pd.read_csv('dataset.csv', encoding_errors='ignore')   
df = pd.DataFrame(data)

# Connect to database
connection = sq.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cursor = connection.cursor()

# Insert dataframe into table
for row in df.itertuples():
    cursor.execute('''
                INSERT INTO songs (artist, track, genre, lyrics)
                VALUES (?,?,?,?)
                ''',
                (row.artist, 
                row.track,
                row.genre,
                row.lyrics)
                )
connection.commit()
connection.close()