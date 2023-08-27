import random
pieceScores = {"K":0,"Q":9,"R":5,"B":3,"N":3,"p":1}
CHECKMAKE = 1000
STALEMATE = 0


def findRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]

def findBestMoves(gs,validMoves):

    turnMultiplier = 1 if gs.whitetomove else -1
    maxScore =-CHECKMAKE
    bestMove = None
    for playermove in validMoves:
        gs.makeMove(playermove)
        if gs.checkmate:
            score = CHECKMAKE
        elif gs.stalemate:
            score = STALEMATE
        else :
            score = scoreMaterial(gs.board)
        if score>maxScore:
            score  = maxScore
            bestMove = playermove

        gs.undoMove()
    return bestMove




#Score board based on material

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScores[square[1]]
            elif square[0] == 'b':
                score -= pieceScores[square[1]]

    return score

