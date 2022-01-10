import re
import numpy as np
from typing import List, NewType, Union
from http.client import HTTPException, HTTPSConnection

Move = NewType('Move', Union[str, List])
State = NewType('State', np.ndarray)

PGN_REGEX = r'(?i)(\.pgn)$'
URL_REGEX = r'(\/\/)|(http)'


def _get_pgn_list(path: str) -> list:
    if re.search(PGN_REGEX, path):
        with open(file=path, mode='r') as f:
            lines = f.read().splitlines()
            return lines
    else:
        return _get_lichess_pgn_lines(path)


def _get_tags(pgn: list) -> dict:
    tag_list = [tag for tag in pgn if re.search(r'^\[', tag)]
    tag_dict: dict = {}
    for tag in tag_list:
        key = tag.split(" ", 1)[0][1:]
        val = tag.split(" ", 1)[1][1:-2]
        tag_dict[key] = val

    return tag_dict


def _get_moves(pgn: list) -> List[Move]:
    movetext = ''
    for i in range(len(pgn)):
        if re.search(r'^1\.', pgn[i]):
            movetext: str = " ".join([pgn[i] for i in range(i, len(pgn))])

    # some formats of pgn does not have space after period
    if not re.search(r'^1\. ', movetext):
        movetext = movetext.replace('.', '. ')
    movetext_items = movetext.split(" ")

    moves = []
    for i, item in enumerate(movetext_items):
        if re.search(r'\d\.', item):
            move = [movetext_items[i],
                    movetext_items[i + 1],
                    movetext_items[i + 2]]
            moves.append(move)
    return moves

def _get_states(moves: list) -> List[State]:
    states = []
    start = _get_init_state()
    states.append(start)
    visualize(start)
    print()
    for color, move in zip(['W', 'B'], moves[0][1:]):
        state = _play_move(color, move, states[-1])
        visualize(state)
        print()
    # for i in range(len(moves)):
    #     state = states[-1]
    #     for color, move in zip(['W', 'B'], moves[i][1:]):
    #
    #         print(color, move)

def _play_move(color, move, state) -> State:
    def text2coord(text):
        char_dict = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":8}
        return (char_dict[text[0]], int(text[1])-1)

    print(color, move)
    color_dict = {"W":0, "B":1}
    piece_dict = {"P":0, "R":1, "N":2, "B":3, "Q":4, "K":5}

    color = color_dict[color]

    if len(move) == 2:
        piece = piece_dict["P"]
        # This must be a move of pawn
        (x,y) = text2coord(move)

        #back trace the pawn in this y axis, and change it to 0
        for i in range(state.shape[1]):
            if state[x][i][piece][color] == 1:
                state[x][i][piece][color] = 0
        state[x][y][piece][color] = 1
    else:
        piece = piece_dict[move[0]]
        (x,y) = text2coord(move[-2:])




    return state

def _find_from_coord(piece, now_coord):
    candidate = []
    #pawn
    if piece == 0:
        if now_coord[1] in (4,5):
            candidate.append((now_coord[0], ))
    #rook
    #knight
    #bishop
    #queen
    #king

def visualize(state):
    piece_dict = {0:"P", 1:"R", 2:"N", 3:"B", 4:"Q", 5:"K"}
    color_dict = {0:"W", 1:"B"}
    WCOLOR =    '\033[31m' # color for white, but is actually red
    BCOLOR =    '\033[30m'
    GCOLOR =    '\033[33m'
    ENDC =      '\033[0m'
    visual_string = ""
    for y in range(state.shape[1]):
        line = ""
        for x in range(state.shape[0]):
            NoPiece = True
            for piece in range(state.shape[2]):
                for color in range(state.shape[3]):
                    if state[x][y][piece][color] == 1:
                        NoPiece = False
                        if color_dict[color] == "W":
                            line += WCOLOR + piece_dict[piece] + ENDC
                        if color_dict[color] == "B":
                            line += BCOLOR + piece_dict[piece] + ENDC
            if NoPiece:
                line += GCOLOR + "_" + ENDC
        visual_string += line
        if y < state.shape[1]-1:
            visual_string += "\n"
    print(visual_string)


def _get_init_state() -> State:
    # Assuming black is on the opponent(up) side, and white is on the player(down) side
    state = np.zeros((8 ,8 , 6, 2))
    # pawns
    for i in range(8):
        state[i][1][0][0] = 1 # white pawns
        state[i][6][0][1] = 1 # black pawns

    # rooks
        #white
    state[0][0][1][0] = 1
    state[7][0][1][0] = 1
        #black
    state[0][7][1][1] = 1
    state[7][7][1][1] = 1
    # knights
        #white
    state[1][0][2][0] = 1
    state[6][0][2][0] = 1
        #black
    state[1][7][2][1] = 1
    state[6][7][2][1] = 1
    # bishops
        #white
    state[2][0][3][0] = 1
    state[5][0][3][0] = 1
        #black
    state[2][7][3][1] = 1
    state[5][7][3][1] = 1
    # queens
        #white
    state[3][0][4][0] = 1
        #black
    state[3][7][4][1] = 1
    # kings
        #white
    state[4][0][5][0] = 1
        #black
    state[4][7][5][1] = 1

    return state

def _get_lichess_pgn_lines(src: str) -> list:
    conn = HTTPSConnection("lichess.org")

    payload = ""
    endpoint = "/game/export/"
    params = "?evals=0&clocks=0&opening=0&literate=0"

    if re.search(URL_REGEX, src):
        tmp = re.split(r'org/', src)
        game_id = tmp[-1]
    else:
        game_id = src

    conn.request("GET", endpoint + game_id + params, payload)
    res = conn.getresponse()

    if res.status == 200:
        data = res.read()
        conn.close()
        return data.decode("utf-8").splitlines()
    else:
        conn.close()
        raise HTTPException(f'Unexpected status code! Expected: 200 Actual: {res.status}')
