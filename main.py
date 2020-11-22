import numpy as np
import pygame
import pygame.freetype
import sys
import time

# variables
SLEEP_TIME = 0.1  # the time period for a chip to move
LINE_WIDTH = 1  # line width
# init game variables
cWidth: int = 100
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


def showChipMotion(col):
    CHIP_COLOR = CHIP_RED_COLOR if redRound else CHIP_YELLOW_COLOR

    centerX = col * cWidth + cWidth / 2

    # print(currentRowsOfEachCol)
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


def isEmpty(col, row):
    if not isValidPos(col, row):
        return False
    return board[col][row] == CELL_BLANK


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
"""


def checkWinRule1DiagonalRT2LB(putCol, putRow):
    # diagonal: right top to left bottom
    countAbove = 0
    countBelow = 0
    for i in range(1, max(cols - putCol, rows - putRow) + 1):
        if isTheSameColor(putCol + i, putRow - i):
            countAbove += 1
        else:
            break

    for i in range(1, max(cols, rows) + 1):
        if isTheSameColor(putCol - i, putRow + i):
            countBelow += 1
        else:
            break

    return countAbove + countBelow + 1 >= numToWin


"""
"""


def checkWinRule1DiagnoalLT2RB(putCol, putRow):
    # diagonal: left top to right bottom
    countAbove = 0
    countBelow = 0

    for i in range(1, max(cols - putCol, rows - putRow) + 1):
        if isTheSameColor(putCol - i, putRow - i):
            countAbove += 1
        else:
            break
    for i in range(1, max(cols, rows) + 1):
        if isTheSameColor(putCol + i, putRow + i):
            countBelow += 1
        else:
            break

    return countAbove + countBelow + 1 >= numToWin


"""
Rule 1: connected under the desired count
"""


def checkWinRule1(putCol, putRow):
    return checkWinRule1Horizon(putCol, putRow) or checkWinRule1Vertical(putCol, putRow) or checkWinRule1DiagonalRT2LB(
        putCol, putRow) or checkWinRule1DiagnoalLT2RB(putCol, putRow)


"""

"""


def isValidDanger(danger, pos):
    return danger[pos[0]][pos[1]] and currentRowsOfEachCol[pos[0]] == pos[1]


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
    return checkWinRule1(putCol, putRow) or checkWinRule2()


def gameWinLose(putCol, putRow):
    # print(board)

    won = checkWin(putCol, putRow)

    if won:
        textsurface = connect4Font.render(('Red' if redRound else 'Yellow') + ' Won!!!', False, (0, 0, 0))
        screen.blit(textsurface, (0, 0))
        pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)

    if blankCount == 0:
        textsurface = connect4Font.render('Nobody Won!!!', False, (0, 0, 0))
        screen.blit(textsurface, (0, 0))
        pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)


"""
"""


def dangerConditionSet(danger, condition, pos):
    if condition:
        for po in pos:
            if isEmpty(po[0], po[1]):
                danger[po[0]][po[1]] = True
                currentTurnDanger.add((po[0], po[1]))


"""
horizon 1:continue in both side
"""


def addOtherSideDangerHorizon1(putCol, putRow):
    #
    leftMostPos = putCol - 1
    while isValidPos(leftMostPos, putRow) and isTheSameColor(leftMostPos, putRow):
        leftMostPos -= 1

    rightMostPos = putCol + 1
    while isValidPos(rightMostPos, putRow) and isTheSameColor(rightMostPos, putRow):
        rightMostPos += 1

    dangerConditionSet(yellowDanger if redRound else redDanger, rightMostPos - leftMostPos >= numToWin,
                       [[leftMostPos, putRow], [rightMostPos, putRow]])


"""
horizon 2: continue at left,but jump at right
"""


def addOtherSideDangerHorizon2(putCol, putRow):
    leftMostPos = putCol - 1
    while isValidPos(leftMostPos, putRow) and isTheSameColor(leftMostPos, putRow):
        leftMostPos -= 1

    rightMostPos = putCol + 1
    if isEmpty(rightMostPos, putRow) and isTheSameColor(rightMostPos + 1, putRow):
        rightMostPos += 1
        while isValidPos(rightMostPos, putRow) and isTheSameColor(rightMostPos, putRow):
            rightMostPos += 1
        dangerConditionSet(yellowDanger if redRound else redDanger, rightMostPos - leftMostPos - 1 >= numToWin,
                           [[putCol + 1, putRow]])


"""
horizon 3: continue at right, but jump at left
"""


def addOtherSideDangerHorizon3(putCol, putRow):
    rightMostPos = putCol + 1
    while isValidPos(rightMostPos, putRow) and isTheSameColor(rightMostPos, putRow):
        rightMostPos += 1

    leftMostPos = putCol - 1
    if isEmpty(leftMostPos, putRow) and isTheSameColor(leftMostPos - 1, putRow):
        leftMostPos -= 1
        while isValidPos(leftMostPos, putRow) and isTheSameColor(leftMostPos, putRow):
            leftMostPos -= 1

        dangerConditionSet(yellowDanger if redRound else redDanger, rightMostPos - leftMostPos - 1 >= numToWin,
                           [[putCol - 1, putRow]])


"""
add danger in horizon direction
"""


def addOtherSideDangerHorizon(putCol, putRow):
    addOtherSideDangerHorizon1(putCol, putRow)
    addOtherSideDangerHorizon2(putCol, putRow)
    addOtherSideDangerHorizon3(putCol, putRow)


"""
add danger in vertical direction
"""


def addOtherSideDangerVertical(putCol, putRow):
    topMostPos = putRow - 1
    bottomMostPos = putRow + 1
    while isValidPos(putCol, bottomMostPos) and isTheSameColor(putCol, bottomMostPos):
        bottomMostPos += 1

    dangerConditionSet(yellowDanger if redRound else redDanger, bottomMostPos - topMostPos >= numToWin,
                       [[putCol, topMostPos]])


"""
When a new chip is put and it may become a danger to the other side, we need add it in 4 directions: 
horizon, 
vertical, 
right top to left bottom, and 
left top to right bottom 
"""


def addOtherSideDanger(putCol, putRow):
    currentTurnDanger.clear()
    # check danger on horizon level
    addOtherSideDangerHorizon(putCol, putRow)
    # check danger on vertical level
    addOtherSideDangerVertical(putCol, putRow)
    # check danger on diagonal right top to left bottom level
    # addDangerDiagonalRT2LB(putCol, putRow, isRedTurn);
    # check danger on diagonal left top to right bottom level;
    # addDangerDiagonalLT2RB(putCol, putRow, isRedTurn);

    print(yellowDanger)


"""
"""


def clearOwnSideDanger(col, row):
    position = [int(col * rows + row)]
    np.put(redDanger if redRound else yellowDanger, position, False)
    print(yellowDanger)


"""
put a chip
"""


def putChip(pos):
    global redRound
    global blankCount

    col = getMouseClickPos(pos)[0]
    row = currentRowsOfEachCol[col]

    # show chip's motion
    showChipMotion(col)

    # the put command below flattens the 2D array
    position = [int(col * rows + row)]
    np.put(board, position, CELL_RED if redRound else CELL_YELLOW)

    blankCount -= 1

    # add other side's danger and clear own side danger
    addOtherSideDanger(col, row)
    clearOwnSideDanger(col, row)

    gameWinLose(col, row)

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
