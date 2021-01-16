Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 26 2018, 23:26:24) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "copyright", "credits" or "license()" for more information.
>>> import os
import random

import cherrypy

def convert(dic):
  return [dic["x"],dic["y"]]

near_food = []
my_id = []
def nextmoves(head_pos):
  directions = {"up": [0,1],
                      "down": [0,-1],
                      "left": [-1,0],
                      "right": [1,0],
                      "center": [0,0]}
  moves = ["up", "down", "left", "right"]
  outlist = []
  for mov in moves:
    next_move = [directions[mov][0]+head_pos[0],directions[mov][1]+head_pos[1]]
    outlist.append([mov,next_move])
  return outlist

def get_weighted_moves(head_pos, danger_squares):
    possible_moves = nextmoves(head_pos)
    #worklist = []
    outlist = []
    holding = []
    #Take out unsafe moves
    for mov in possible_moves:
        if mov[1] in danger_squares:
            holding.append(mov)
    for hol in holding:
        possible_moves.remove(hol)
    
    for mov in possible_moves:
        can_reach = []
        have_checked = []
        will_check = nextmoves(mov[1])
        to_check = []
        for pair in will_check:
            to_check.append(pair[1])
        print("moves to check")
        print(to_check)
        print(mov[0])
        where = mov[0]
        while to_check != []:
            check = to_check.pop()
            #print("Check\n")
            #print(check)
            #check = checkit[1]
            if (check in have_checked) or (check in can_reach):
                pass
            elif check in danger_squares:
                have_checked.append(check)
            else:
                new_moves = nextmoves(check)
                for mov in new_moves:
                    to_check.append(mov[1])
                can_reach.append(check)
        outlist.append([where,len(can_reach)])
    return outlist

def choose_move(w_list):
    my_min = -1
    outlist = []
    for n in w_list:
        if n[1] > my_min:
            my_min = n[1]
            outlist = [n[0]]
        elif n[1] == my_min:
            outlist.append(n[0])
        else:
            pass
    return outlist            
        


def manhatten(p1, p2):
  return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

max_len = 0 

border = []

class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "Benj",  # TODO: Your Battlesnake Username
            "color": "#006eff",  # TODO: Personalize
            "head": "fang",  # TODO: Personalize
            "tail": "block-bum"  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json
        
        me = data["you"]
        my_id.append(me["id"])

        board = data["board"]
        width = board["width"]
        height = board["height"]
        for x in range(width):
          border.append([x,-1])
          border.append([x,height])
        for y in range(height):
          border.append([-1,y])
          border.append([width,y])

        #max_len = manhatten([-1,-1],[width,height])
       # print(max_len)
        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json


        my_snake = data["you"]
        my_head = convert(my_snake["head"])  
        
        
        board = data["board"]
        # Choose a random direction to move in
        food = []
        foodboard = board["food"]
        for coord in foodboard:
          food.append(convert(coord))
       
          

        #print(width+height)
        snakes = board["snakes"]
        
        #cur_turn = board["turn"]

        danger_squares = []

        for snake in snakes:
          their_pos = snake["body"]
          their_head = snake["head"]
          their_id = snake["id"]
          if not (their_id in my_id):
            nexts = nextmoves(convert(their_head))
            for n in nexts:
              danger_squares.append(n[1])
          for pos in their_pos:
            danger_squares.append(convert(pos))
          
        #for pos in my_pos:
        #  danger_squares.append(convert(pos))
        
       # print("Danger Squares:\n")
       # print(danger_squares)
       # print("\n \nMy Head:\n")
       # print(my_head)
       # print("\n")

        possible_moves = ["up", "left", "right", "down"]
        directions = {"up": [0,1],
                      "down": [0,-1],
                      "left": [-1,0],
                      "right": [1,0],
                      "center": [0,0]}
        holding = []
        #FIND DEATH SQUARES AND REMOVE THEM
        n_moves = nextmoves(my_head)
        #print(possible_moves)
        for move in n_moves:
          if (move[1] in danger_squares) or (move[1] in border):
            holding.append(move[0])
        for move in holding:
          possible_moves.remove(move)
        print("Danger Squares")
        #print(my_head)
        print(danger_squares)

        #print(possible_moves)
        ptr = []
        near_food_dist = 10000
        danger = danger_squares + border
        #FIND closest source of food.
        #print("All food")
        #print(food)
        for fd in food:
          #print("I'm in loop")
          #print(manhatten(my_head,fd))
          #print(near_food_dist)
          if manhatten(my_head,fd) <= near_food_dist:
            ptr = fd
            near_food_dist = manhatten(my_head,fd)
            #print(fd)
            #print(manhatten(my_head,fd))
            

        #print("Nearest Food")
        #print(ptr)
        new_pts = []
        for move in possible_moves:
          new_pts.append([move,[directions[move][0]+my_head[0],directions[move][1]+my_head[1]]])
        dists = []
        for nwpt in new_pts:
          dists.append([nwpt[0],manhatten(ptr,nwpt[1])])
        next_move = ""
        min_dist = 100000
        for n in dists:
          if n[1] < min_dist:
            next_move = n[0]
        move = next_move
        #from the remaining see how far the food it.
        red = get_weighted_moves(my_head,  danger)
        print("Weighted Moves\n")
        print(red)
        blue = choose_move(red)

        

        move = random.choice(blue)
        #print("Head")
        #print(my_head)
        print(f"MOVE: {move}")
        return {"move": move, "shout": "Stay Safe!"}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
