import sqlite3
import os

# Change working directory to where your CSV and SQLite database are located
os.chdir('C:/Users/asus/Documents/flask help/engine')

# Connect to SQLite database
con = sqlite3.connect("voiceAssistant.db")
cursor = con.cursor()

# Check if 'contacts' table exists, create it if not
#cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
 #                   id INTEGER PRIMARY KEY,
  #                  name VARCHAR(200),
   #                 mobile_no VARCHAR(255)
    #            )''')

# Specify the column indices you want to import (0-based index)
#desired_columns_indices = [0, 1]  # Adjust these indices based on your CSV structure

# Read data from CSV and insert into SQLite table for the desired columns
#with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
   # csvreader = csv.reader(csvfile)
    
  #  for row in csvreader:
  #      selected_data = [row[i] for i in desired_columns_indices]
 #       cursor.execute('''INSERT INTO contacts (id, name, mobile_no) VALUES (null, ?, ?);''', tuple(selected_data))

# Commit changes and close connection
#con.commit()
#con.close()

#query ="INSERT INTO contacts VALUES(null, 'papa', '6393663648')"
#cursor.execute(query)
#con.commit()


query = 'mahi'
query = query.strip().lower()

cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
results = cursor.fetchall()
print(results[0][0])


