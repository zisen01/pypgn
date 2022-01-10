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
    for i in range(len(moves)):
        # print(int(moves[i][0][:-1]))
        state = np.zeros((8 ,8 , 6, 2))
        for color, move in zip(['W', 'B'], moves[i][1:]):
            if 'x' in move:

            print(color, move)

def _get_init_state() -> np.ndarray:
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
