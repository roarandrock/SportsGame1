
import random, sys, pygame, time, copy, math, sqlite3
import models, db_creation
from pygame.locals import *


FPS = 20 # frames per second to update the screen
WINDOWWIDTH = 1000 # width of the program's window, in pixels
WINDOWHEIGHT = 800 # height in pixels
SPACESIZE =  110 # width & height of each space on the board, in pixels
PLAYERSIZE = int(SPACESIZE/2)-15
BOARDWIDTH = 6 # how many columns of spaces on the game board
BOARDHEIGHT = 6 # how many rows of spaces on the game board
ANIMATIONSPEED = 25 # integer from 1 to 100, higher is faster animation

# Amount of space on the left & right side (XMARGIN) or above and below
# (YMARGIN) the game board, in pixels.
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

#              R    G    B
# https://www.rapidtables.com/web/color/blue-color.html
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  0, 255)
LIGHTERBLUE = (176, 196, 222)
BROWN      = (174,  94,   0)
BLUE       = (0, 0, 155)
RED        = (155, 0, 0)
YELLOW     = (155, 155, 0)
DARKGRAY    = (40, 40, 40)
LIGHTGRAY = (100, 100, 100)
BRIGHTRED   = (255, 0, 0)
BRIGHTYELLOW = (255, 255, 0)
BRIGHTGREEN = (0, 255, 0)

def main():
    global MAINCLOCK, DISPLAYSURF, BGIMAGE

    pygame.init()

    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Sports!')

    # Set up the background image.
    boardImage = pygame.image.load('flippyboard.png')
    # Use smoothscale() to stretch the board image to fit the entire board:
    boardImage = pygame.transform.smoothscale(boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
    boardImageRect = boardImage.get_rect()
    boardImageRect.topleft = (XMARGIN, YMARGIN)
    BGIMAGE = pygame.image.load('flippybackground.png')
    # Use smoothscale() to stretch the background image to fit the entire window:
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    BGIMAGE.blit(boardImage, boardImageRect)

    # Run the main game.
    while True:
        if runGame() == False:
            break

def runGame():

    # get the right database for the starting players
    db_creation.clean_db()
    db_creation.new_db_empty()
    db_creation.fill_db()

    # set the stage
    turn = 'player'
    current_match = models.Match()
    current_match.match_number = 1
    current_match.match_teams = ["Rage", "Peace"]
    current_match.human_team = "Rage"
    starting_field = models.Field()
    starting_gui = models.Gui()

    current_field, current_gui = drawBoard(starting_field, starting_gui)

    while True: # main game loop
        # Keep looping for player and computer's turns.
        player_move_commit_list = []
        computer_move_commit_list = []
        if turn == 'player':
            # Player's turn:
            moves_committed = False
            moves_commit_list = []
            while moves_committed is False:
                # Keep looping until the player submits three moves
                checkForQuit()
                for event in pygame.event.get(): # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        # Handle mouse click events
                        mousex, mousey = event.pos
                        hex_id, button_name = getSpaceClicked(mousex, mousey, current_field, current_gui)
                        player_selected = check_click(hex_id)

                        if current_gui.action_selection is False and player_selected is not None:
                            # print(hex_id,models.Player(player_selected).player_name)
                            current_gui.player_highlight = True
                            current_gui.player_id_selected = player_selected
                            if player_selected in models.Team(current_match.human_team).player_list:
                                current_gui.action_menu = True
                                current_gui.top_message = "Choose an action for " + models.Player(player_selected).player_name
                        elif button_name is not None:
                            # draw possible hexes for an action
                            current_gui.possible_hexes = action_possible_hexes(button_name, current_gui, current_field)
                            if len(current_gui.possible_hexes) > 0:
                                current_gui.action_selection = True
                                current_gui.action_to_do = button_name
                                current_gui.top_message = "Choose a hex for " + button_name
                            # TODO add back button or someway to cancel selection
                        elif hex_id in current_gui.possible_hexes and current_gui.action_selection is True:
                            # after hex selected
                            move_commit_x = action_commit(hex_id, current_gui)
                            moves_commit_list.append(move_commit_x)
                            current_gui.action_selection = False
                            current_gui.action_to_do = None
                            current_gui.possible_hexes = []
                            current_gui.player_id_selected = None
                            current_gui.player_highlight = False
                            m2 = len(models.Team(current_match.human_team).player_list)
                            m1 = len(moves_commit_list)
                            current_gui.top_message = str(m1) + " out of " + str(m2) + " moves committed"

                # update drawing of game board
                current_field, current_gui = drawBoard(current_field, current_gui)

                # update display
                MAINCLOCK.tick(FPS)
                pygame.display.update()

                # checks if all moves_committed
                if len(moves_commit_list) >= len(models.Team(current_match.human_team).player_list):
                    moves_committed = True
                    current_gui.top_message = "Player's turn complete. Computer's turn."
                    player_move_commit_list = moves_commit_list

            # End the turn
        else:
            # Computer's turn:

            current_field, current_gui = drawBoard(current_field, current_gui)

            # Make it look like the computer is thinking by pausing a bit.
            pauseUntil = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pauseUntil:
                pygame.display.update()

            current_gui.top_message = "Computer turn complete. Human's turn"

        current_field = implement_moves(current_field, player_move_commit_list)

        # update board
        current_field, current_gui = drawBoard(current_field, current_gui)

        # update display
        MAINCLOCK.tick(FPS)
        pygame.display.update()

        # Only set for the player's turn if they can make a move.
        turn = 'player'


def implement_moves(current_field, move_list):
    # TODO implement results display
    for move_x in move_list:
        if move_x.action_type == "Move":
            # check if player is still there
            if models.Player(move_x.player_action).current_tile == move_x.hex_start:
                # check if end space is free
                # TODO replace with match class
                teams_in_play = ["Rage", "Peace"]
                all_player_hexes = []
                for team_x in teams_in_play:
                    all_player_hexes = all_player_hexes + models.Team(team_x).players_field_hexes()
                if move_x.hex_end not in all_player_hexes:
                    # move player
                    player_0 = models.Player(move_x.player_action)
                    player_0.current_tile = move_x.hex_end
                    player_0.update_db()
        elif move_x.action_type == "Throw":
            print("Throw")
        elif move_x.action_type == "Tackle":
            # check if player is still there
            if models.Player(move_x.player_action).current_tile == move_x.hex_start:
                # check if end space has an opponent
                teams_in_play = ["Rage", "Peace"]
                all_player_hexes = []
                for team_x in teams_in_play:
                    all_player_hexes = all_player_hexes + models.Team(team_x).players_field_hexes()
                if move_x.hex_end in all_player_hexes and \
                        move_x.hex_end != models.Player(move_x.player_action).current_tile:
                    # move player
                    player_0 = models.Player(move_x.player_action)
                    player_0.current_tile = move_x.hex_end
                    player_0.update_db()
                    # move tackled player
                    player_1 = models.Player(check_click(move_x.hex_end))
                    tackle_complete = False
                    hex_3_x = None
                    hex_3_y = None
                    while tackle_complete is False:
                        hex_0 = current_field.current_field[move_x.hex_start]
                        hex_1 = current_field.current_field[player_1.current_tile]
                        delta_x = 0
                        delta_y = 0
                        if hex_0.hex_coord_x == hex_1.hex_coord_x:
                            delta_x = 0
                            if hex_0.hex_coord_y > hex_1.hex_coord_y:
                                delta_y = -1
                            else:
                                delta_y = 1
                        elif hex_0.hex_coord_x > hex_1.hex_coord_x:
                            delta_x = -1
                            if hex_0.hex_coord_y == hex_1.hex_coord_y:
                                delta_y = -1
                        else:
                            delta_x = 1
                            if hex_0.hex_coord_y == hex_1.hex_coord_y:
                                delta_y = -1
                        hex_3_x = hex_1.hex_coord_x + delta_x
                        hex_3_y = hex_1.hex_coord_y + delta_y
                        # TODO check for player already in place and resolve
                        tackle_complete = True
                    for hex_id, hex_x in current_field.current_field.items():
                        if hex_x.hex_coord_x == hex_3_x and hex_x.hex_coord_y == hex_3_y:
                            player_1.current_tile = hex_id
                            player_1.update_db()
                elif move_x.hex_end == models.Player(move_x.player_action).current_tile:
                    print("Self-tackle")
                else:
                    print("No one to tackle", move_x.hex_end, all_player_hexes)
            # move both players
        else:
            print("action not found ", move_x.action_type)
    return current_field


def action_commit(hex_id, current_gui):
    move_to_commit = models.Move()
    move_to_commit.hex_start = models.Player(current_gui.player_id_selected).current_tile
    move_to_commit.hex_end = hex_id
    move_to_commit.action_type = current_gui.action_to_do
    move_to_commit.player_action = current_gui.player_id_selected
    return move_to_commit


def drawBoard(field_current, gui_current):
    # Draw background of board.
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    board_width_hexes = 7
    board_height_hexes = 5
    unique_id = 0
    hex_x = 0

    # draw hexagon field
    for x in range(board_width_hexes):
        hex_x += 1
        hex_y = 0

        for y in range(board_height_hexes):
            hex_y += 1
            hex_details = models.Hex()
            hex_side = SPACESIZE / math.sqrt(3)
            hex_height_tip = abs(math.sin(math.degrees(30))*hex_side)
            hex_radius = abs(math.cos(math.degrees(30))*hex_side)

            # even row
            if x % 2 == 0:
                starty = (y * 2 * hex_radius) + YMARGIN
                startx = (x * (hex_side + hex_height_tip)) + XMARGIN
            # odd row
            else:
                starty = (y * 2 * hex_radius + hex_radius) + YMARGIN
                startx = (x * (hex_side + hex_height_tip)) + XMARGIN

            polygon_points = [[hex_height_tip + startx, starty],
                              [hex_height_tip + hex_side + startx, starty],
                              [hex_height_tip*2 + hex_side + startx, hex_radius + starty],
                              [hex_height_tip + hex_side + startx, hex_radius*2 + starty],
                              [hex_height_tip + startx, hex_radius*2 + starty],
                              [startx, hex_radius + starty]]

            unique_id += 1
            center_x = int(startx + hex_height_tip + (hex_side / 2))
            center_y = int(starty + hex_radius)

            if field_current.field_layout[unique_id] == "field":
                pygame.draw.polygon(DISPLAYSURF, DARKGRAY, polygon_points, 5)

            # Label tiles, can hide
            font_obj = pygame.font.Font('freesansbold.ttf', 15)
            coord_to_write = "(" + str(hex_x) + ", " + str(hex_y) + ") " + str(unique_id)
            text_surface_object = font_obj.render(coord_to_write, True, BLACK)
            text_rect_object = text_surface_object.get_rect()
            text_rect_object.center = (center_x, center_y)
            DISPLAYSURF.blit(text_surface_object, text_rect_object)

            # assign tiles values and then make the field dict of hex class
            hex_details.hex_id = unique_id
            hex_details.hex_coord_x = hex_x
            hex_details.hex_coord_y = hex_y
            hex_details.pix_box_x = startx
            hex_details.pix_box_y = starty
            hex_details.center_pix_x = center_x
            hex_details.center_pix_y = center_y
            field_current.current_field.setdefault(unique_id,hex_details)

    # Draw the players
    # TODO replace with either Match class or store this in the field?
    teams_in_match = ["Peace", "Rage"]
    human_team_name = "Rage"
    all_player_list = []
    human_team_list = []
    for team_name in teams_in_match:
        team_x = models.Team(team_name)
        all_player_list = team_x.player_list+all_player_list
        if team_name is human_team_name:
            human_team_list = team_x.player_list
    for player_id in all_player_list:
        player_x = models.Player(player_id)
        hex_x = field_current.current_field[player_x.current_tile]
        team_x = models.Team(player_x.team_name)
        if team_x.team_color == "blue":
            tile_color = BLUE
        elif team_x.team_color == "red":
            tile_color = RED
        elif team_x.team_color == "white":
            tile_color = WHITE
        else:
            tile_color = BLACK
        pygame.draw.circle(DISPLAYSURF,tile_color,(hex_x.center_pix_x,hex_x.center_pix_y),
                           PLAYERSIZE)
        font_obj = pygame.font.SysFont('couriernew.ttf', 25)
        if "Captain" in player_x.title:
            player_title = "C"
        elif "Tank" in player_x.title:
            player_title = "T"
        else:
            player_title = "WTF"
        text_surface_object = font_obj.render(player_title, True, BLACK, tile_color)
        text_rect_object = text_surface_object.get_rect()
        text_rect_object.center = (hex_x.center_pix_x, hex_x.center_pix_y)
        DISPLAYSURF.blit(text_surface_object, text_rect_object)

    topbar_surface = pygame.Surface((BOARDWIDTH * SPACESIZE,YMARGIN - 10))
    topbar_surface.fill(LIGHTERBLUE)
    details_font = pygame.font.SysFont('couriernew.ttf', 40)
    to_blit_list = [[topbar_surface, (5 + XMARGIN, 5)]]
    text_color = BLACK
    text_row = gui_current.top_message
    text_surf = details_font.render(text_row, True, text_color, LIGHTERBLUE)
    y_pos = int(YMARGIN/2)
    x_pos = XMARGIN + int(BOARDWIDTH * SPACESIZE/2)
    text_rect = text_surf.get_rect(center=(x_pos, y_pos))
    to_blit_list.append([text_surf, text_rect])
    DISPLAYSURF.blits(to_blit_list)

    # Draw the player menu and selected player
    if gui_current.player_id_selected is not None and gui_current.player_highlight is True:
        current_field_dict = field_current.current_field

        # circle around selected player
        hex_to_highlight = models.Player(gui_current.player_id_selected).current_tile
        player_x = current_field_dict[hex_to_highlight].center_pix_x
        player_y = current_field_dict[hex_to_highlight].center_pix_y
        pygame.draw.circle(DISPLAYSURF, YELLOW, (player_x, player_y), PLAYERSIZE, 2)

        # player details on left side
        sidebar_surface = pygame.Surface((XMARGIN - 10, int(BOARDWIDTH * SPACESIZE/2)))
        sidebar_surface.fill(DARKGRAY)
        details_font = pygame.font.SysFont('couriernew.ttf', 25)
        text_row_list = ["Player Details"]
        row_i = 1
        to_blit_list = [[sidebar_surface, (5,YMARGIN)]]
        text_row_list.append("Name: " + models.Player(gui_current.player_id_selected).player_name)
        text_row_list.append("Team: " + models.Player(gui_current.player_id_selected).team_name)
        text_row_list.append("Title: " + models.Player(gui_current.player_id_selected).title)
        for row in text_row_list:
            text_surf = details_font.render(row, True, GREEN, DARKGRAY)
            y_pos = YMARGIN+int((SPACESIZE*row_i)/2)
            row_i += 1
            text_rect = text_surf.get_rect(center=(int((XMARGIN-5)/2), y_pos))
            to_blit_list.append([text_surf,text_rect])
        DISPLAYSURF.blits(to_blit_list)

        # if player character, the show action menu
        # can store menu as a dict with positions in gui_current, actions come from player class
        action_list = ["Move", "Throw", "Tackle"]
        action_button_dict = {}
        if gui_current.player_id_selected in human_team_list:
            sidebar_surface = pygame.Surface((XMARGIN - 10, BOARDWIDTH * SPACESIZE))
            sidebar_surface.fill(LIGHTGRAY)
            details_font = pygame.font.SysFont('couriernew.ttf', 25)
            text_row_list = ["Action Menu"]
            row_i = 1
            to_blit_list = [[sidebar_surface, (5+XMARGIN+BOARDWIDTH*SPACESIZE, YMARGIN)]]
            for action_x in action_list:
                text_row_list.append(action_x)
            for row in text_row_list:
                # cheat for not showing options when not possible 
                text_color = WHITE
                if field_current.ball_hex == models.Player(gui_current.player_id_selected).current_tile and \
                        row == "Tackle":
                    text_color = LIGHTGRAY
                elif field_current.ball_hex != models.Player(gui_current.player_id_selected).current_tile and \
                        row == "Throw":
                    text_color = LIGHTGRAY
                text_surf = details_font.render(row, True, text_color, LIGHTGRAY)
                y_pos = YMARGIN + int((SPACESIZE * row_i) / 2)
                x_pos = XMARGIN + BOARDWIDTH * SPACESIZE + int(XMARGIN/2)
                text_rect = text_surf.get_rect(center=(x_pos, y_pos))
                if row_i > 1: # not box around the menu title
                    button_rect_shape = pygame.Rect(text_rect.top,text_rect.left,XMARGIN-30,int(SPACESIZE/2))
                    button_rect_shape.centerx = int(XMARGIN/2)
                    button_rect_shape.centery = int(row_i*SPACESIZE/2)
                    button_rect = pygame.draw.rect(sidebar_surface, DARKGRAY, button_rect_shape, 2)
                    action_button_dict.setdefault(row,button_rect_shape)
                row_i += 1
                to_blit_list.append([text_surf, text_rect])
            DISPLAYSURF.blits(to_blit_list)
            gui_current.button_dict = action_button_dict

    # reset ball if not in play
    if field_current.ball_hex is None:
        field_current.ball_hex = 16
    ball_x = field_current.current_field[field_current.ball_hex].center_pix_x - int(SPACESIZE/5)
    ball_y = field_current.current_field[field_current.ball_hex].center_pix_y + int(SPACESIZE/3)
    pygame.draw.circle(DISPLAYSURF, BRIGHTBLUE, (ball_x, ball_y), int(SPACESIZE/5))

    # draw highlighted hexes for actions
    if len(gui_current.possible_hexes) > 0:
        for hex_id in gui_current.possible_hexes:
            highlight_x = field_current.current_field[hex_id].center_pix_x
            highlight_y = field_current.current_field[hex_id].center_pix_y
            pygame.draw.circle(DISPLAYSURF, YELLOW, (highlight_x, highlight_y), PLAYERSIZE-5, 2)

    return field_current, gui_current

    # for pointy side up
    # # even row
    # if y % 2 == 0
    #     startx = (x * 2 * hex_radius) + XMARGIN
    #     starty = (y * (hex_side+hex_height_tip)) + YMARGIN
    # # odd row
    # else:
    #     startx = (x * 2 * hex_radius + hex_radius) + XMARGIN
    #     starty = (y * (hex_side + hex_height_tip)) + YMARGIN
    #
    # polygon_points = [[startx, hex_height_tip + starty],
    #                   [hex_radius + startx, starty],
    #                   [hex_radius * 2 + startx, hex_height_tip + starty],
    #                   [hex_radius * 2 + startx, hex_height_tip + hex_side + starty],
    #                   [hex_radius + startx, hex_height_tip * 2 + hex_side + starty],
    #                   [startx, hex_height_tip + hex_side + starty]]


def getSpaceClicked(mousex, mousey, current_field,current_gui):
    # Determine which hex was clicked (Or returns None not in any space.)
    potential_button = None
    potential_hex = None
    # First filters if clicked off the board, need to change when adding buttons
    if mousex < XMARGIN:
        return None
    if mousey < YMARGIN or mousey > (YMARGIN + BOARDHEIGHT*SPACESIZE):
        return None
    if mousex > (XMARGIN+BOARDWIDTH*SPACESIZE):
        check_distance = XMARGIN
        for button_name, button_rect in current_gui.button_dict.items():
            sidebar_x_delta = XMARGIN+SPACESIZE*BOARDWIDTH
            sidebar_y_delta = YMARGIN
            offset_x = mousex - sidebar_x_delta
            offset_y = mousey - sidebar_y_delta
            x_delta = abs(offset_x - button_rect.centerx)
            y_delta = abs(offset_y - button_rect.centery)
            if x_delta < button_rect.width and y_delta < button_rect.height:
                total_distance = x_delta + y_delta
                if total_distance < check_distance:
                    check_distance = total_distance
                    potential_button = button_name
    check_distance = SPACESIZE*2
    dict_of_field = current_field.current_field
    # print(current_field,dict_of_field)
    for hex_id, hex_x in dict_of_field.items():
        x_delta = abs(mousex-hex_x.center_pix_x)
        y_delta = abs(mousey-hex_x.center_pix_y)
        if x_delta < SPACESIZE and y_delta < SPACESIZE:
            total_distance = x_delta + y_delta
            if total_distance < check_distance:
                check_distance = total_distance
                potential_hex = hex_id
    return potential_hex, potential_button


def checkForQuit():
    for event in pygame.event.get((QUIT, KEYUP)): # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

def check_click(hex_id):
    player_selected = None
    # TODO replace with match class
    current_teams = ["Rage", "Peace"]
    players_on_field = []
    for team_name in current_teams:
        players_on_field = players_on_field + models.Team(team_name).player_list
    for player_x in players_on_field:
        if models.Player(player_x).current_tile == hex_id:
            player_selected = player_x
    return player_selected


def action_possible_hexes(action_selected, current_gui, current_field):
    possible_hexes = []
    if action_selected == "Move":
        # find options to move
        current_hex_id = models.Player(current_gui.player_id_selected).current_tile
        adj_hexes = current_field.adjacent_hexes(current_hex_id)
        for hex_id in adj_hexes:
            player_occupied = check_click(hex_id)
            if player_occupied is None:
                possible_hexes.append(hex_id)
    elif action_selected == "Throw":
        # find options to throw
        current_hex_id = models.Player(current_gui.player_id_selected).current_tile
        current_teams = ["Rage", "Peace"]
        players_on_field = []
        player_hexes = []
        for team_name in current_teams:
            players_on_field = players_on_field + models.Team(team_name).player_list
        # check validity of throw, only sideways and back passes
        check_y = current_field.current_field[current_hex_id].hex_coord_y
        for player_x in players_on_field:
            hex_x = current_field.current_field[models.Player(player_x).current_tile]
            if hex_x.hex_coord_y <= check_y:
                possible_hexes.append(hex_x.hex_id)
    elif action_selected == "Tackle":
        # find options to tackle
        current_hex_id = models.Player(current_gui.player_id_selected).current_tile
        adj_hexes = current_field.adjacent_hexes(current_hex_id)
        for hex_id in adj_hexes:
            player_occupied = check_click(hex_id)
            if player_occupied is not None:
                possible_hexes.append(hex_id)
    else:
        print("Error, action not possible: ", action_selected)
    return possible_hexes
    #
    # # old code from flippy
    # # Draw the additional tile that was just laid down. (Otherwise we'd
    # # have to completely redraw the board & the board info.)
    # if tileColor == WHITE_TILE:
    #     additionalTileColor = WHITE
    # else:
    #     additionalTileColor = BLACK
    # additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    # pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2) - 4)
    # pygame.display.update()
    #
    # for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2.55)):
    #     if rgbValues > 255:
    #         rgbValues = 255
    #     elif rgbValues < 0:
    #         rgbValues = 0
    #
    #     if tileColor == WHITE_TILE:
    #         color = tuple([rgbValues] * 3) # rgbValues goes from 0 to 255
    #     elif tileColor == BLACK_TILE:
    #         color = tuple([255 - rgbValues] * 3) # rgbValues goes from 255 to 0
    #
    #     for x, y in tilesToFlip:
    #         centerx, centery = translateBoardToPixelCoord(x, y)
    #         pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(SPACESIZE / 2) - 4)
    #     pygame.display.update()


if __name__ == '__main__':
    main()
