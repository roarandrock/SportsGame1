import sqlite3

# I assume the DB is existing and pull the info when I initialize the class
# then I need to keep the instance until it's time to update the database and make a new instance

# TODO replace sql with mongodb connection

# Player class
class Player():
    def __init__(self, player_id):
        try:
            db = sqlite3.connect('data/db1')
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            player_x = cursor.execute("select * from players where id= ?", (player_id,)).fetchone()
            # should be a way to automate this
            self.id = player_x["id"] # need a unique player id
            self.player_name = player_x["player_name"]
            self.title = player_x["title"]
            self.current_tile = player_x["current_tile"]
            self.team_name = player_x["team_name"]
            db.close()
        except Exception as e:
            print("Player sql connection failed", player_id, e)

    def update_db(self):
        try:
            db = sqlite3.connect('data/db1')
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            # player_0 = cursor.execute("select * from player where id=?", (self.id,)).fetchone()
            new_tile = self.current_tile
            cursor.execute("update players set current_tile = ? where id = ?", (new_tile, self.id,))
            db.commit()
            db.close()
        except Exception as e:
            print("Player sql connection failed", self.id, e)


class Team:
    def __init__(self, team_name):
        try:
            db = sqlite3.connect('data/db1')
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            entry_x = cursor.execute("select * from teams where team_name= ?", (team_name,)).fetchone()
            self.team_id = entry_x["team_id"] # need a unique player id
            self.team_name = entry_x["team_name"]
            self.team_color = entry_x["team_color"]
            db.close()
        except Exception as e:
            print("Sql connection failed", team_name, e)
        try:
            db = sqlite3.connect('data/db1')
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            player_rows = cursor.execute("select id from players where team_name= ?", (self.team_name,))
            self.player_list = []
            for entry in player_rows:
                self.player_list.append(entry["id"])
            db.close()
        except Exception as e:
            print("Sql connection failed", team_name, e)

    def players_field_hexes(self):
        hexes_with_players = []
        for player_x in self.player_list:
            hexes_with_players.append(Player(player_x).current_tile)
        return hexes_with_players

class Field:

    def __init__(self):
        starting_field = {1: "empty", 2: "empty", 3: "empty", 4: "empty", 5: "empty",
                          6: "empty", 7: "field", 8: "field", 9: "field", 10: "empty",
                          11: "empty", 12: "field", 13: "field", 14: "field", 15: "field",
                          16: "field", 17: "field", 18: "field", 19: "field", 20: "field",
                          21: "empty", 22: "field", 23: "field", 24: "field", 25: "field",
                          26: "empty", 27: "field", 28: "field", 29: "field", 30: "empty",
                          31: "empty", 32: "empty", 33: "empty", 34: "empty", 35: "empty"}
        self.current_field = {} # dictionary of hexes
        self.field_layout = starting_field
        self.ball_hex = None

    def adjacent_hexes(self,hex_id):
        hex_0 = self.current_field[hex_id]
        adj_hexes = []
        speed_player = 1
        # need two checks, one for even and one for odd
        if hex_0.hex_coord_x % 2 ==0:
            flow_1 = True
        else:
            flow_1 = False
        if flow_1 is True:
            check_1 = [[hex_0.hex_coord_x - speed_player, hex_0.hex_coord_y + speed_player],
                       [hex_0.hex_coord_x - 0, hex_0.hex_coord_y + speed_player],
                       [hex_0.hex_coord_x + speed_player, hex_0.hex_coord_y + speed_player],
                       [hex_0.hex_coord_x - speed_player, hex_0.hex_coord_y + 0],
                       [hex_0.hex_coord_x - 0, hex_0.hex_coord_y - speed_player],
                       [hex_0.hex_coord_x + speed_player, hex_0.hex_coord_y + 0]]
        else:
            check_1 = [[hex_0.hex_coord_x - speed_player, hex_0.hex_coord_y - speed_player],
                       [hex_0.hex_coord_x - 0, hex_0.hex_coord_y - speed_player],
                       [hex_0.hex_coord_x + speed_player, hex_0.hex_coord_y - speed_player],
                       [hex_0.hex_coord_x + speed_player, hex_0.hex_coord_y + 0],
                       [hex_0.hex_coord_x + 0, hex_0.hex_coord_y + speed_player],
                       [hex_0.hex_coord_x - speed_player, hex_0.hex_coord_y + 0]]
        for hex_id, hex_x in self.current_field.items():
            if [hex_x.hex_coord_x, hex_x.hex_coord_y] in check_1:
                if self.field_layout[hex_id] == "field":
                    adj_hexes.append(hex_id)
        return adj_hexes

# keep in instance or store in DB?
class Hex:
    def __init__(self):
        self.hex_coord_x = 0
        self.hex_coord_y = 0
        self.pix_box_x = 0
        self.pix_box_y = 0
        self.center_pix_x = 0
        self.center_pix_y = 0
        self.hex_state = "empty"
        self.hex_id = 0


# should only be a single instance
class Gui:
    def __init__(self):
        self.action_menu = False
        self.player_highlight = False
        self.match_menu = False
        self.player_id_selected = None
        self.button_dict = {}
        self.possible_hexes = []
        self.action_selection = False
        self.action_to_do = None
        self.top_message = "Welcome to the Game!"


class Match:
    def __init__(self):
        self.match_number = 0
        self.match_teams = []
        self.human_team = None
        # self.match_players_on_field = []
        # self.match_field = Field


class Move:
    def __init__(self):
        self.hex_start = None
        self.hex_end = None
        self.player_action = None
        self.action_type = None
        self.action_priority = None


# # for experiments
# p1 = Player(5000)
# print("current team ", p1.team_name)
# t1 = Team("Rage")
# print(t1.team_name)
# print(t1.player_list)
# t1.players_on_team("Rage")
# print(t1.player_list)
