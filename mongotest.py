# Made a cloud cluster with Mongo DB Atlas
# No IP restriction but there is one admin with these credentials:
# Name: Admin1
# password: ykACiEQFzM8SYBM
# ReadWriter1
# password: MvnmPUNcpElMGKMd

from pymongo import MongoClient
import datetime

client = MongoClient(
    "mongodb+srv://ReadWriter1:MvnmPUNcpElMGKMd@clustertestgame-zbbya.gcp.mongodb.net/test?retryWrites=true&w=majority")
# client = MongoClient("mongodb+srv://Admin1:ykACiEQFzM8SYBM@clustertestgame-zbbya.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.test
db = client.gettingStarted

team = db.team

teamDocument1 = {
    "team_name": "Rage",
    "team_id": 100,
    "team_color": "red",
    "players_on_team": [5000, 5001]
}

teamDocument2 = {
    "team_name": "Peace",
    "team_id": 200,
    "team_color": "white",
    "players_on_team": [5002, 5003]
}

team.insert_many([teamDocument1, teamDocument2])

player = db.player

players_tuple = [(5000, "Bloodbeard", "Captain", 17, "Rage"),
                 (5001, "Meatwall", "Tank", 18, "Rage"),
                 (5002, "Love Dragon", "Captain", 20, "Peace"),
                 (5003, "Flower", "Tank", 14, "Peace")]
player_document_list = []
for player_x in players_tuple:
    player_x_dict = {}
    player_x_dict.setdefault("id", player_x[0])
    player_x_dict.setdefault("player_name", player_x[1])
    player_x_dict.setdefault("title", player_x[2])
    player_x_dict.setdefault("current_tile", player_x[3])
    player_x_dict.setdefault("team_name", player_x[4])
    player_document_list.append(player_x_dict)

player.insert_many(player_document_list)


find1 = team.find({"team_id": 200})
find2 = player.find({"team_name": "Rage"})
for post in find1:
    print(post)

for post in find2:
    print(post)

# how to clean out a db
# team.delete_many({})
# player.delete_many({})


# teams_tuple = [("Rage", "100", "red"),
#                ("Peace", "200", "white")]
# cursor.executemany('''INSERT INTO teams (team_name, team_id, team_color) VALUES (?,?,?)''', teams_tuple)
# except Exception as e:
# print("Fill failed", e)
# try:
#   # technically a list of tuples, replace later with an excel or back db?
#   players_tuple = [(5000, "Bloodbeard", "Captain", 17, "Rage"),
#                    (5001, "Meatwall", "Tank", 18, "Rage"),
#                    (5002, "Love Dragon", "Captain", 20, "Peace"),
#                    (5003, "Flower", "Tank", 14, "Peace")]
#     '''INSERT INTO players (id, player_name, title, current_tile,team_name) VALUES (?,?,?,?,?)''',
