from sense_hat import SenseHat
from evdev import InputDevice,ecodes,list_devices
from select import select
import random
import time
import sys
sh = SenseHat()
# File to store high score
highscorefile = open('/home/pi/.2048score','r')
global highscore
highscore = int(highscorefile.readline())
highscorefile.close()

# Check that we can see the SenseHat Joystick
devices = [InputDevice(fn) for fn in list_devices()]
for dev in devices:
    print(dev.name)
    if dev.name == "Raspberry Pi Sense HAT Joystick":
        js=dev
        print('found')

sh.clear() # Clear LEDs
#Define the colours for each 'number' square
global colour2
colour2 = [255,0,0]
global colour4
colour4 = [255,128,0]
global colour8
colour8 = [0,255,0]
global colour16
colour16 =  [255,255,0]
global colour32
colour32 = [0,255,128]
global colour64
colour64 = [255,0,128]
global colour128
colour128 = [128,0,255]
global colour256
colour256 = [225,128,55]
global colour512
colour512 = [0,0,255]
global colour1024
colour1024 = [134,55,10]
global colour2048
colour2048 = [255,255,255]

# Dictionary of colours and their corresponding number
colours = {'2':colour2, '4':colour4,'8':colour8,'16':colour16,
           '32':colour32,'64':colour64,'128':colour128,'256':colour256,
           '512':colour512,'1024':colour1024,'2048':colour2048}
# Print each colour with its number
for c in sorted(colours,key=lambda k: int(k) if k.isdigit()else float('-inf')):
    sh.show_message(c,text_colour=[0,0,0],back_colour=colours[c],scroll_speed=0.03)

global score
score = 0
r = [255,0,0]
g = [0,255,0]
b = [0,0,255]
# define each 4x4 square and the pixels that comprise it
global sq00
sq00 = [(0,0),(0,1),(1,0),(1,1)]
global sq01
sq01 = [(0,2),(0,3),(1,2),(1,3)]
global sq02
sq02 = [(0,4),(0,5),(1,4),(1,5)]
global sq03
sq03 = [(0,6),(0,7),(1,6),(1,7)]
global sq10
sq10 = [(2,0),(2,1),(3,0),(3,1)]
global sq11
sq11 = [(2,2),(2,3),(3,2),(3,3)]
global sq12
sq12 = [(2,4),(2,5),(3,4),(3,5)]
global sq13
sq13 = [(2,6),(2,7),(3,6),(3,7)]
global sq20
sq20 = [(4,0),(4,1),(5,0),(5,1)]
global sq21
sq21 = [(4,2),(4,3),(5,2),(5,3)]
global sq22
sq22 = [(4,4),(4,5),(5,4),(5,5)]
global sq23
sq23 = [(4,6),(4,7),(5,6),(5,7)]
global sq30
sq30 = [(6,0),(6,1),(7,0),(7,1)]
global sq31
sq31 = [(6,2),(6,3),(7,2),(7,3)]
global sq32
sq32 = [(6,4),(6,5),(7,4),(7,5)]
global sq33
sq33 = [(6,6),(6,7),(7,6),(7,7)]

# Define columns and rows to make lookups easier when moving
col0 = ['sq03', 'sq02', 'sq01', 'sq00']
col1 = ['sq13', 'sq12', 'sq11', 'sq10']
col2 = ['sq23', 'sq22', 'sq21', 'sq20']
col3 = ['sq33', 'sq32', 'sq31', 'sq30']
row0 = ['sq00', 'sq10', 'sq20', 'sq30']
row1 = ['sq01', 'sq11', 'sq21', 'sq31']
row2 = ['sq02', 'sq12', 'sq22', 'sq32']
row3 = ['sq03' ,'sq13', 'sq23', 'sq33']

# Main dictionary
# First & second values: x and y of 4x4 squares
# Third value: colour to be light
# Fourth value: whether sq has already been merged/ added this movement round
global grid
grid = {'sq00':[0,0,'off',False],'sq10':[1,0,'off',False], 'sq20':[2,0,'off',False],'sq30':[3,0,'off',False],
        'sq01':[0,1,'off',False],'sq11':[1,1,'off',False], 'sq21':[2,1,'off',False],'sq31':[3,1,'off',False],
        'sq02':[0,2,'off',False],'sq12':[1,2,'off',False], 'sq22':[2,2,'off',False],'sq32':[3,2,'off',False],
        'sq03':[0,3,'off',False],'sq13':[1,3,'off',False], 'sq23':[2,3,'off',False],'sq33':[3,3,'off',False]
        }

# Rules for merging squares -> next colour
def add_colours(col1):
    if col1 == colour2:
        return(colour4,4)
    if col1 == colour4:
        return(colour8,8)
    if col1 == colour8:
        return(colour16,16)
    if col1 == colour16:
        return(colour32,32)
    if col1 == colour32:
        return(colour64,64)
    if col1 == colour64:
        return(colour128,128)
    if col1 == colour128:
        return(colour256,256)
    if col1 == colour256:
        return(colour512,512)
    if col1 == colour512:
        return(colour1024,1024)
    if col1 == colour1024:
        return(colour2048,2048)

# maps the string (used as key in grid dictionary) to the variable
# of the same name
def map_sqs(sqstr):
    if sqstr == 'sq00' :
        return(sq00)
    if sqstr == 'sq01' :
        return(sq01)
    if sqstr == 'sq02' :
        return(sq02)
    if sqstr == 'sq03' :
        return(sq03)
    if sqstr == 'sq10' :
        return(sq10)
    if sqstr == 'sq11' :
        return(sq11)
    if sqstr == 'sq12' :
        return(sq12)
    if sqstr == 'sq13' :
        return(sq13)
    if sqstr == 'sq20' :
        return(sq20)
    if sqstr == 'sq21' :
        return(sq21)
    if sqstr == 'sq22' :
        return(sq22)
    if sqstr == 'sq23' :
        return(sq23)
    if sqstr == 'sq30' :
        return(sq30)
    if sqstr == 'sq31' :
        return(sq31)
    if sqstr == 'sq32' :
        return(sq32)
    if sqstr == 'sq33' :
        return(sq33)

# Redraw grid by looping through grid dictionary
def refresh_grid():
    for sq in grid:
        colour = grid[sq][2]
        if colour == 'off':
            load_sq(map_sqs(sq), [0,0,0])
        else:
            load_sq(map_sqs(sq),colour)

# Load and light up an indiviual 4x4 square with colour
def load_sq(sqxy,colour):
    for p in range(4):
        #print(sqxy)
        sh.set_pixel(sqxy[p][0],sqxy[p][1],colour)

# Change the value of the colour value of grid dictionary element
def update_sq(sq, colour):
    grid[sq][2] = colour

# Move everything in grid down
# We start at the 2nd from bottom row and then work up
# Do it three times so that a square at the top with no
# coloured sqs below it will end up at the bottom
def shift_down():
    global grid
    for g in grid:
        grid[g][3] = False
    for r in range(3):
        UDshift(row2,row3)
        UDshift(row1,row2)
        UDshift(row0,row1)
    refresh_grid()

# Move everything up
# Same principle as down but in reverse
def shift_up():
    global grid
    for g in grid:
        grid[g][3] = False
    for r in range(3):
        UDshift(row1,row0)
        UDshift(row2,row1)
        UDshift(row3,row2)
    refresh_grid()

# Move everything left
def shift_left():
    global grid
    for g in grid:
        grid[g][3] = False
    for r in range(3):
        LRshift(col1,col0)
        LRshift(col2,col1)
        LRshift(col3,col2)
    refresh_grid()

# Move everything right
def shift_right():
    global grid
    for g in grid:
        grid[g][3] = False
    for r in range(3):
        LRshift(col2,col3)
        LRshift(col1,col2)
        LRshift(col0,col1)
    refresh_grid()

# Rules for moving left/right. Work through all the elements
# in a given column, comparing to the next left/right column. Rules:
def LRshift(firstcol,secondcol):
    global score
    for block in firstcol:
        x = grid[block][0]
        y = grid[block][1]
        colour = grid[block][2]
        if colour != 'off':
            for lblock in secondcol:
                if grid[lblock][1] == y:
                    # if colour of sq to the left is same and no merge already this round, then merge/add_sq
                    if grid[lblock][2] == colour and grid[lblock][3] == False and grid[block][3] == False:
                        result = add_colours(colour)
                        new_colour = result[0]
                        score= score + result[1]
                        load_sq(map_sqs(lblock),new_colour)
                        grid[block][2] = 'off'
                        grid[lblock][2] = new_colour
                        grid[lblock][3] = True
                    # if sq to left is empty (off) then light that sq the same colour
                    # and set the original sq to off
                    if grid[lblock][2] == 'off':
                        #print(rblock)
                        load_sq(map_sqs(lblock),colour)
                        grid[block][2] = 'off'
                        grid[lblock][2] = colour

# Rules for moving up/down. Work through all the elements
# in a given column, comparing to the next column above/below.
def UDshift(firstrow,secondrow):
    global score
    for block in firstrow:
        x = grid[block][0]
        y = grid[block][1]
        colour = grid[block][2]
        if colour != 'off':
            for lblock in secondrow:
                if grid[lblock][0] == x:
                    if grid[lblock][2] == colour and grid[lblock][3] == False and grid[block][3] == False:
                        result = add_colours(colour)
                        new_colour = result[0]
                        score= score + result[1]
                        #print(rblock)
                        load_sq(map_sqs(lblock),new_colour)
                        grid[block][2] = 'off'
                        grid[lblock][2] = new_colour
                        grid[lblock][3] = True
                    if grid[lblock][2] == 'off':
                        #print(rblock)
                        load_sq(map_sqs(lblock),colour)
                        grid[block][2] = 'off'
                        grid[lblock][2] = colour

# Pick a new  free square
def random_sq():
    empty_sqs = []
    # Find all the empty squares
    for sq in grid:
        if grid[sq][2] == 'off':
            empty_sqs.append(sq)
    # If no empty squares, then game over
    if len(empty_sqs) == 0:
        sh.clear()
        for r in range(2):
            sh.show_message("Game Over: score =",text_colour=[255,255,0], back_colour=[0,128,255],scroll_speed=0.05)
            sh.show_message(str(score),back_colour=[0,255,0],scroll_speed=0.07)
        check_highscore(score)
        sh.clear()
        sys.exit()
    # Pick a random free square
    chosen_sq = random.choice(empty_sqs)
    return(chosen_sq)

# Add a new '2' sq to a free space and refresh grid
def add_sq(col):
    new = random_sq()
    update_sq(new,col)
    load_sq(map_sqs(new),col)
    refresh_grid()

# check for new highscore and write to file if necessary
def check_highscore(score):
    if score > highscore:
        sh.show_message("NEW HIGH SCORE!", text_colour=[255,0,0], back_colour=[255,255,0])
        highscorefile = open('/home/pi/.2048score','r+')
        highscorefile.write(str(score))

# Allow weighted choices for new colours
weighted_cols = [(colour2,100),(colour4,20), (colour8,1)]
pop = [val for val, cnt in weighted_cols for i in range(cnt)]
# START GAME
# Add two '2' squares at the start of the game
add_sq(colour2)
add_sq(colour2)
while True:
    # Monitor joystick and capture events
    r,w,x=select([js.fd],[],[],0.01)
    for fd in r:
         for event in js.read():
             # If it's a 'key' event
              if event.type == ecodes.EV_KEY and event.value==1:
                  if event.code == ecodes.KEY_UP:
                      print("up")
                      shift_up()
                      add_sq(random.choice(pop))
                  elif event.code == ecodes.KEY_LEFT:
                      print("left")
                      shift_left()
                      add_sq(random.choice(pop))
                  elif event.code == ecodes.KEY_RIGHT:
                      print("right")
                      shift_right()
                      add_sq(random.choice(pop))
                  elif event.code == ecodes.KEY_DOWN:
                      print("down")
                      shift_down()
                      add_sq(random.choice(pop))
                  else:
                      print("enter")
