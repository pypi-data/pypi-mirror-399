import curses as c
import time
import PIL.Image
import math
import sys
import argparse as arg
import os
PAD_HEIGHT = 31
PAD_WIDTH = 88
X_MARGIN = 30
Y_MARGIN = 10
COLORFIX = [1,2,3,4,5,6,7]
INFO_BG = 9
xOffset = 0
yOffset = 0
rect_y = -1 #starting position
rect_x = -1
rectPreviousColor = [0,0,0,0] #type: list
filename = "unnamed.png"
pairs = []
debugPairs = []
fieldChars = [] #list[list[str]]
fieldColors = [] #list[list[int]]
debugPairBool = False
debug16Pair = False
drawBool = True
unsavedContent = False
paintColor = 1
reverseColor = 8
currentColor = 0
statusBarNext = ""
statusBarCurrent = ""
infobarPos = False
colormap = [
        (12, 12, 12),      # Black
        (197, 15, 31),     # Red
        (19, 161, 14),     # Green
        (193, 156, 0),     # Yellow
        (0, 55, 218),      # Blue
        (136, 23, 152),    # Magenta
        (58, 150, 221),    # Cyan
        (204, 204, 204),   # White/Gray
    ]
colorPairDark = True
def pad_ref(pad: c.window):
    pad.noutrefresh(yOffset,xOffset,0,0,min(PAD_HEIGHT-1,lines),min(PAD_WIDTH,c.COLS)-1)
def cursor_move(y,x,stdscr):
    global cursorY,cursorX
    if False:
        if y >= lines:
            y = 0
        elif y < 0:
            y = lines-1 #cursor can not move into the infobar
        if x >= c.COLS:
            x = 0
        elif x < 0:
            x = c.COLS-1
    #protection replaced by the relMove() boundaries
    cursorY = y
    cursorX = x
    stdscr.move(y,x)

def relMove(y,x,stdscr,pad = None,doColor=False,doRefresh=True):
    global xOffset,yOffset
    nextY = y+cursorY
    nextX = x+cursorX
    if (nextX > c.COLS-X_MARGIN) and (xOffset+c.COLS < PAD_WIDTH-1):
        nextX = cursorX
        xOffset += 1
    elif (nextX < X_MARGIN) and (xOffset > 0):
        nextX = cursorX
        xOffset -= 1
    if (nextY > lines-Y_MARGIN) and (yOffset+lines < PAD_HEIGHT-1):
        nextY = cursorY
        yOffset += 1
    if (nextY < Y_MARGIN) and (yOffset > 0):
        nextY = cursorY
        yOffset -= 1
    pass #fix from pad image edges, handle offset moving
    if (nextX >= c.COLS) or (nextX < 0):
        nextX = cursorX
    if (nextY >= lines) or (nextY < 0):
        nextY = cursorY
    pass #block moving past edges of screen
    if (yOffset + nextY >= PAD_HEIGHT):
        nextY = cursorY
    if (yOffset+nextY >= PAD_HEIGHT-1):
        safetyAdj = -1
    else:
        safetyAdj = 0
    if (xOffset + nextX >= PAD_WIDTH+safetyAdj):
        nextX = PAD_WIDTH-xOffset-1+safetyAdj
    cursor_move(nextY,nextX,stdscr)
    stdscr.addstr(nextY,nextX,fieldChars[yOffset+nextY][xOffset+nextX],
                  c.color_pair(fieldColors[yOffset+nextY][xOffset+nextX])) #attempt to show the cursor
    if doColor:
        color_pos(currentColor,pad)
    stdscr.move(nextY,nextX)
    stdscr.refresh()

def round_color(r: int,g: int,b: int,colormap: list) -> int:
    dist_linear = []
    dist_quadratic = []
    for color in colormap:
        dr = abs(color[0]-r)
        dg = abs(color[1]-g)
        db = abs(color[2]-b)
        dist_linear.append(round((dr+dg+db)/3,2))
        dist_quadratic.append(round(math.sqrt((dr**2+dg**2+db**2)/9),2))
        #print(f"rounding {r},{g},{b} against {color}: linear {dist_linear[-1]} quadratic {dist_quadratic[-1]}")
    dist_sorted = sorted(dist_linear)
    res = dist_linear.index(dist_sorted[0])
    if False:
        print(f"linear {dist_linear}")
        print(f"quadratic {dist_quadratic}")
        print(dist_sorted)
    print(f"matched {r},{g},{b} to {colormap[res]}")
    return res

def color_pos(color: int,pad,char: str = " "):
    global unsavedContent
    unsavedContent = True
    fieldChars[yOffset+cursorY][xOffset+cursorX] = char
    fieldColors[yOffset+cursorY][xOffset+cursorX] = color
    pad.addstr(yOffset+cursorY,xOffset+cursorX,char,c.color_pair(color))

def load_file(path: str):
    global fieldColors,fieldChars
    img = PIL.Image.open(path)
    imgPixels = img.load()
    color_cache = {}
    fieldChars = [["" for x in range(img.size[0])] for y in range(img.size[1])]
    fieldColors = [[0 for x in range(img.size[0])] for y in range(img.size[1])]
    if img.mode != "RGB":
        img = img.convert("RGB")
    pad = c.newpad(img.size[1]+1,img.size[0]+1)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            clr = imgPixels[x,y] #type: ignore
            cached = color_cache.get(str(clr),-1)
            if cached < 0:
                cached = round_color(clr[0],clr[1],clr[2],colormap)
                color_cache[str(clr)] = cached
            if cached > 0:
                cached += 7
            fieldColors[y][x] = cached
            pad.addstr(y,x," ",c.color_pair(cached))
    return((img.size[1],img.size[0],pad))


def save_array(colors,chars,doSave=False):
    #colormap = [(0,0,0),(0xff,0,0),(0,0xff,0),(0xff,0xff,0),(0,0,0xff),(0xff,0,0xff),(0,0xFF,0xFF),(0xC0,0xC0,0xC0)]
    img = PIL.Image.new("RGB",(len(chars[0]),len(chars)),"black")
    imgPixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            colorNum = colors[y][x]
            if colorNum > 7:
                colorNum -= 7
            if colorNum >= len(colormap):
                colorNum = -1
            imgPixels[x,y] = colormap[colorNum] #type: ignore
    if doSave:
        img.save(filename)
    else:
        img.show()


def refresh_infobar(stdscr):
    for x in range(c.COLS-1):
        stdscr.addstr(lines,x," ",c.color_pair(INFO_BG))

def delete_rect():
    global rectPreviousColor #rx,ry -> x,ry -> x,y -> rx,y corners
    if rect_y < -1 or (rect_y == cursorY+yOffset and rect_x == cursorX+xOffset):
        return None
    fieldColors[rect_y]


def updateInfo(stdscr: c.window):
    global statusBarCurrent
    stdscr.addstr(lines,c.COLS-21,f"off x {xOffset}, y {yOffset}",c.color_pair(INFO_BG))
    if statusBarCurrent != statusBarNext:
        stdscr.addstr(lines,min(c.COLS-len(statusBarNext)-1,44),statusBarNext,c.color_pair(INFO_BG))
        statusBarCurrent = statusBarNext
    else:
        stdscr.addstr(lines,min(c.COLS-len(statusBarNext)-1,44),statusBarNext,c.color_pair(INFO_BG))
    if unsavedContent:
        a = "*"
    else:
        a = ""
    stdscr.addstr(lines,27,filename+a,c.color_pair(INFO_BG))
    if infobarPos:
        stdscr.addstr(lines,7,f"x {xOffset+cursorX}, y {yOffset+cursorY}",c.color_pair(INFO_BG))
    if drawBool:
        stdscr.addstr(lines,23,"%",c.color_pair(INFO_BG))
    else:
        stdscr.addstr(lines,23,"X",c.color_pair(INFO_BG))

def init(stdscr):
    global fieldChars, fieldColors, COLORFIX, filename, PAD_HEIGHT, PAD_WIDTH
    global statusBarNext, infobarPos, colorPairDark
    parser = arg.ArgumentParser()
    parser.add_argument("-n","--filename",type=str,help="This is the filename your image will be saved as",required=False)
    parser.add_argument("-y","--height",type=int,default=31,help="Height of the image canvas",required=False)
    parser.add_argument("-x","--width",type=int,default=88,help="Width of the image canvas",required=False)
    parser.add_argument("-p","--pos",action="store_true",help="Display cursor position relative to image on the infobar",required=False)
    parser.add_argument("-l","--load",action="store_true",help="Load the image with the specified filename")
    parser.add_argument("-c","--change-color",action="store_true",help="Use a brighter color for rendering")
    args = parser.parse_args()
    if args.pos:
        infobarPos = True
    colorPairDark = not args.change_color
    if (args.filename == None or args.filename == "") and args.load:
        raise ValueError("file to load not provided")
    if (args.filename != None) and args.filename != "":
        if (args.filename in os.listdir()) or (args.filename+".png" in os.listdir()):
            statusBarNext = f"{args.filename} exists, but it wasn't loaded"
            stdscr.addstr(lines,min(c.COLS-len(statusBarNext)-1,38),statusBarNext,c.color_pair(INFO_BG))
        if "." in args.filename or args.load: #ensure the provided filename is loaded
            filename = args.filename
        else:
            filename = args.filename+".png"
    c.curs_set(1)
    c.start_color()
    stdscr.keypad(True)
    if sys.platform == "win32":
        COLORFIX = [4,2,6,1,5,3,7]
    if args.load:
        PAD_HEIGHT,PAD_WIDTH,pad = load_file(filename)
    else:
        pad = c.newpad(PAD_HEIGHT,PAD_WIDTH)
        fieldChars = [["" for x in range(PAD_WIDTH)] for y in range(PAD_HEIGHT)]
        fieldColors = [[0 for x in range(PAD_WIDTH)] for y in range(PAD_HEIGHT)]
    print(f"loading mode {args.load} width {PAD_WIDTH} height {PAD_HEIGHT}")
    return pad

def main(stdscr: c.window):
    global cursorX,cursorY, currentColor, lines, statusBarNext, drawBool
    global unsavedContent
    cursorY = round(c.LINES/2)
    cursorX = round(c.COLS/2)
    lines = c.LINES-1
    cursor_move(cursorY,cursorX,stdscr)
    drawBool = False
    pad = init(stdscr)
    if cursorY >= PAD_HEIGHT:
        cursorY = round(PAD_HEIGHT/2)
    if cursorX >= PAD_WIDTH:
        cursorX = round(PAD_WIDTH/2)
    for i in range(7):
        pairs.append(c.init_pair(i+1,8+COLORFIX[i],0))
        debugPairs.append((i+1,8+COLORFIX[i],0))
    colorReg2 = 1
    for i in range(7):
        if i == 2:
            colorReg2 = 0
        else:
            colorReg2 = 1
        if colorPairDark:
            colorReg2 = 0
        #print(f"bright color {i} has CR2 {colorReg2}")
        pairs.append(c.init_pair(8+i,0,8*colorReg2+COLORFIX[i]))
        debugPairs.append((8+i,0,8*colorReg2+COLORFIX[i]))
    for i in range(min(PAD_WIDTH,c.COLS)-1):
        try:
            pass
            #stdscr.addstr(lines,i,'b',c.color_pair(i%16))
        except Exception:
            pass
    stdscr.refresh()
    time.sleep(0.1)
    pad_ref(pad)
    if debugPairBool:
        for i in range(128-8):
            pairs.append(c.init_pair(i+16,2*i,0))
            debugPairs.append((i+16,2*i,0))
            pairs.append(c.init_pair(i+16+120,0,2*i))
            debugPairs.append((i+16+120,0,2*i))
        for y in range(0, min(c.LINES-2,PAD_HEIGHT-1)):
            for x in range(0, min(c.COLS-1,PAD_WIDTH-1)):
                pad.addstr(y,x, 'a',c.color_pair(16+round((3*x) % 255)))
    pad_ref(pad)
    refresh_infobar(stdscr)
    updateInfo(stdscr)
    cursor_move(cursorY,cursorX,stdscr)
    pad_ref(pad)
    adjColorSet = 1
    lastColor = 0
    colorReg = 1
    debugColorInput = False
    while True:
        lines = c.LINES-1
        k = stdscr.getkey()
        if k != "\n":
            stdscr.addstr(lines,c.COLS-21-7,k,c.color_pair(INFO_BG))
        if k == "q" or k == "Q":
            break
        if (k in "wasd" or k in [c.KEY_UP,c.KEY_DOWN,c.KEY_LEFT,c.KEY_RIGHT]) and drawBool:
            color_pos(currentColor,pad)
        if k == c.KEY_UP or k == "w":
            relMove(-1,0,stdscr,pad,drawBool)
        elif k == c.KEY_DOWN or k == "s":
            relMove(1,0,stdscr,pad,drawBool)
        elif k == c.KEY_LEFT or k == "a":
            relMove(0,-1,stdscr,pad,drawBool)
        elif k == c.KEY_RIGHT or k == "d":
            relMove(0,1,stdscr,pad,drawBool)
        elif k == "e":
            drawBool = (not drawBool)
        elif k == "f" and debugColorInput:
            color_pos(9,pad)
        elif k == "g" and debugColorInput:
            color_pos(12,pad)
        elif k == "h" and debugColorInput:
            color_pos(15,pad)
        elif k == "j" and debugColorInput:
            color_pos(5,pad,"#")
        elif k == "p":
            stdscr.refresh()
        elif k == "l":
            pass
        elif k == "b":
            save_array(fieldColors,fieldChars)
        elif k == "x":
            save_array(fieldColors,fieldChars,doSave=True)
            unsavedContent = False
        elif k == "v":
            colorReg = 0
        elif k == "1":
            currentColor = 0+7*colorReg+adjColorSet #cooked if statement because the smarter way to do this did not work idk
        elif k == "2":
            currentColor = 1+7*colorReg+adjColorSet
        elif k == "3":
            currentColor = 2+7*colorReg+adjColorSet
        elif k == "4":
            currentColor = 3+7*colorReg+adjColorSet
        elif k == "5":
            currentColor = 4+7*colorReg+adjColorSet
        elif k == "6":
            currentColor = 5+7*colorReg+adjColorSet
        elif k == "7":
            currentColor = 6+7*colorReg+adjColorSet
        elif k == "8" and False:
            currentColor = 7+7*colorReg+adjColorSet
        elif k == "9" and False:
            currentColor = 8+7*colorReg+adjColorSet
        elif k == "0":
            currentColor = 0
        elif k == "" or k == None:
            pass
        else:
            pass
        pass
        if lastColor != currentColor:
            lastColor = currentColor
            if drawBool:
                color_pos(currentColor,pad)
            colorReg = 1
        refresh_infobar(stdscr)
        updateInfo(stdscr)
        #stdscr.addstr(lines,0," ",c.color_pair(0))
        stdscr.addstr(lines,1," ",c.color_pair(currentColor))
        stdscr.addstr(lines,2," ",c.color_pair(currentColor))
        stdscr.addstr(lines,0,str(currentColor),c.color_pair(currentColor))
        stdscr.addstr(lines,3," ",c.color_pair(0))
        pad_ref(pad)
        stdscr.move(cursorY,cursorX)
        stdscr.noutrefresh()
        c.doupdate()
    time.sleep(1)

def package():
    c.wrapper(main)

if __name__ == "__main__" or False:
    package()

if debugPairBool or debug16Pair:
    for i in range(math.floor(len(debugPairs)/2)):
        print(f"{debugPairs[2*i]}    {debugPairs[2*i+1]}")
    #print(f"last {debugPairs[-1]}")