import sqlite3
import models


# self.id = player_x["id"] # need a unique player id
#             self.title = player_x["title"]
#             self.current_tile = player_x["current_tile"]
#             self.team = player_x["team"]

# for creation of the databse
def new_db_empty():
    db = sqlite3.connect('data/db1')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.execute('''
                   CREATE TABLE teams 
                   (team_name TEXT PRIMARY KEY,
                   team_id integer,
                   team_color TEXT)
                   ''')

    cursor.execute('''
                   CREATE TABLE players 
                   (id INTEGER PRIMARY KEY,
                   player_name TEXT,
                   title TEXT,
                   current_tile INTEGER,
                   team_name TEXT NOT NULL, 
                   FOREIGN KEY (team_name) REFERENCES teams (team_name))''')
    db.commit()
    db.close()


def clean_db():
    db = sqlite3.connect('data/db1')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    try:
        cursor.execute('DROP TABLE teams')
    except Exception as e:
        print("Drop failed", e)
    try:
        cursor.execute('DROP TABLE players')
    except Exception as e:
        print("Drop failed", e)
    db.commit()
    db.close()


def fill_db():
    db = sqlite3.connect('data/db1')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    try:
        teams_tuple = [("Rage", "100", "red"),
                       ("Peace", "200", "white")]
        cursor.executemany('''INSERT INTO teams (team_name, team_id, team_color) VALUES (?,?,?)''', teams_tuple)
    except Exception as e:
        print("Fill failed", e)
    try:
        # technically a list of tuples, replace later with an excel or back db?
        players_tuple = [(5000, "Bloodbeard", "Captain", 17, "Rage"),
                         (5001, "Meatwall", "Tank", 18, "Rage"),
                         (5002, "Love Dragon", "Captain", 20, "Peace"),
                         (5003, "Flower", "Tank", 14, "Peace")]
        cursor.executemany(
            '''INSERT INTO players (id, player_name, title, current_tile,team_name) VALUES (?,?,?,?,?)''',
            players_tuple)
    except Exception as e:
        print("Fill failed", e)
    db.commit()
    db.close()

# TODO connect to mongoDB at startup
# TODO make Flask site that connects to mongoDB and lets user modify playernames

# # run functions
# clean_db()
# new_db_empty()
# fill_db()
# p1 = models.Player(5000)
# print(p1.player_name, p1.current_tile)
team1 = models.Team("Peace")
print(team1.player_list, team1.team_color)
team1 = models.Team("Rage")
print(team1.player_list, team1.team_color)
