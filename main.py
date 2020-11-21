import numpy as np
import pygame
import pygame.freetype
import sys
import time

# variables
SLEEP_TIME = 0.1  # the time period for a chip to move
LINE_WIDTH = 1  # line width
# init game variables
cWidth = 100
cHeight = 100
rows = 6
cols = 7
numToWin = 4
blankCount = rows * cols  # how many blank cells left

radius = cWidth / 2 - 1  # radius of the chips

BKG_COLOR = pygame.Color('blue')
LINE_COLOR = pygame.Color('black')
CHIP_RED_COLOR = pygame.Color('red')
CHIP_YELLOW_COLOR = pygame.Color('yellow')

CELL_BLANK = 0
CELL_RED = 1
CELL_YELLOW = -1

redRound = True  # True:Red; False: Yellow

currentRowsOfEachCol = [rows - 1] * cols  # the current rows of each col

board = np.full((cols, rows), CELL_BLANK)  # board status

yellowDanger = np.full((cols, rows), False)  # yellow player's danger status
redDanger = np.full((cols, rows), False)  # red player's danger status
currentTurnDanger = set()
toBePut = np.full(cols, 0)

size = cWidth * cols, cHeight * rows
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Connect 4')

"""
draw the board, including background and horizen and vertical lines
"""


def drawBoard():
    # draw board background
    pygame.draw.rect(screen, BKG_COLOR, [0, 0, cWidth * cols, cHeight * rows])

    # draw horizon lines
    lLeft = 0
    lWidth = lLeft + cWidth * cols
    for r in range(rows):
        lTop = r * cHeight
        pygame.draw.line(screen, LINE_COLOR, (lLeft, lTop), (lWidth, lTop), LINE_WIDTH)

    # draw vertical lines
    lTop = 0
    lHeight = lTop + cHeight * rows
    for c in range(cols):
        lLeft = c * cWidth
        pygame.draw.line(screen, LINE_COLOR, (lLeft, lTop), (lLeft, lHeight), LINE_WIDTH)


"""get mouse click position"""


def getMouseClickPos(pos):
    col = int(pos[0] / cWidth)
    row = int(pos[1] / cHeight)
    return col, row


"""Simulate chips motion"""


def showChip(col):
    CHIP_COLOR = CHIP_RED_COLOR if redRound else CHIP_YELLOW_COLOR

    centerX = col * cWidth + cWidth / 2

    print(currentRowsOfEachCol)
    for i in range(currentRowsOfEachCol[col]):
        centerY = i * cHeight + cHeight / 2
        # draw chip in motion
        pygame.draw.circle(screen, CHIP_COLOR, (centerX, centerY), radius)
        pygame.display.update()
        pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
        # sleep
        time.sleep(SLEEP_TIME)
        # clear chip in motion
        pygame.draw.circle(screen, BKG_COLOR, (centerX, centerY), radius)
        pygame.display.update()

    # draw chip in the final position
    centerY = (currentRowsOfEachCol[col]) * cHeight + cHeight / 2
    pygame.draw.circle(screen, CHIP_COLOR, (centerX, centerY), radius)
    pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
    pygame.display.update()


"""
if the position is in the board scope
"""


def isValidPos(col, row):
    return 0 <= col < cols and 0 <= row < rows


"""
if the position has the same color chip as the current round's color
"""


def isTheSameColor(col, row):
    if not isValidPos(col, row):
        return False
    if board[col][row] == CELL_BLANK:
        return False

    return board[col][row] == (CELL_RED if redRound else CELL_YELLOW)


"""
check if the player won in horizon direction
"""


def checkWinRule1Horizon(putCol, putRow):
    # horizon
    countLeft = 0
    countRight = 0
    # leftwards
    for i in range(putCol - 1, -1, -1):
        if isTheSameColor(i, putRow):
            countLeft += 1
        else:
            break
    # rightwards
    for i in range(putCol + 1, cols):
        if isTheSameColor(i, putRow):
            countRight += 1
        else:
            break
    return countLeft + countRight + 1 >= numToWin


"""
"""


def checkWinRule1Vertical(putCol, putRow):
    # vertical: top to bottom
    countAbove = 0
    countBelow = 0
    for i in range(1, rows):
        if isTheSameColor(putCol, putRow + i):
            countBelow += 1
        else:
            break

    return countAbove + countBelow + 1 >= numToWin


"""
Rule 1: connected under the desired count
"""


def checkWinRule1(putCol, putRow):
    if checkWinRule1Horizon(putCol, putRow):
        return True

    if checkWinRule1Vertical(putCol, putRow):
        return True

    # if (checkWinRule1DiagonalRT2LB(putCol, putRow)):
    #   return True

    # return checkWinRule1DiagnoalLT2RB(putCol, putRow)
    return False


"""

"""


def isValidDanger(danger, pos):
    return danger[pos[0]][pos[1]] and toBePut[pos[0]] == pos[1]


"""
"""


def getCurrentRoundValidDanger(danger):
    count = 0
    for pos in currentTurnDanger:
        if isValidDanger(danger, pos):
            count += 1

    return count


"""
Rule 2: Although no desired number of chips connected, but another player can not stop curent player's win
"""


def checkWinRule2():
    # if there are more than 2 danger positions in this turn, it is also a win
    count = getCurrentRoundValidDanger(yellowDanger if redRound else redDanger)
    return count >= 2


def checkWin(putCol, putRow):
    if checkWinRule1(putCol, putRow):
        return True
    return checkWinRule2()


def gameWinLose(putCol, putRow):
    print(board)
    print(putCol, putRow)
    won = checkWin(putCol, putRow)

    if won:
        textsurface = connect4Font.render(('Red' if redRound else 'Yellow') + ' Won!!!', False, (0, 0, 0))
        screen.blit(textsurface, (0, 0))
        pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)

    print(blankCount)
    if blankCount == 0:
        textsurface = connect4Font.render('Nobody Won!!!', False, (0, 0, 0))
        screen.blit(textsurface, (0, 0))
        pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)


""""""


def putChip(pos):
    global redRound
    global blankCount

    col, row = getMouseClickPos(pos)
    print(col, row)
    showChip(col)

    # the put command below flattens the 2D array
    position = [int(col * rows + currentRowsOfEachCol[col])]
    np.put(board, position, CELL_RED if redRound else CELL_YELLOW)

    blankCount -= 1
    gameWinLose(col, currentRowsOfEachCol[col])

    currentRowsOfEachCol[col] -= 1
    redRound = not redRound


pygame.init()
pygame.font.init()
connect4Font = pygame.font.SysFont('Comic Sans MS', 30)

drawBoard()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            putChip(event.pos)

    pygame.display.update()
