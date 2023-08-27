import pygame as p
from Chess import ChessEngine,SmartMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 60
IMAGES = {}


def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'wp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("IMAGES/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()


    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClick = []
    gameOver = False
    playerOne = False
    playerTeo = True


    while running:
        validMoves = gs.getValidMoves()

        humanTurn = (gs.whitetomove and playerOne) or (not gs.whitetomove and playerTeo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #MOuse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClick = []
                    else:
                        sqSelected = (row, col)
                        playerClick.append(sqSelected)
                    if len(playerClick) == 2:
                        move = ChessEngine.Move(playerClick[0], playerClick[1], gs.board)
                        print(move.getChessNotation())


                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade =True
                                animate = True
                                sqSelected = ()
                                playerClick = []

                        if not moveMade:
                            playerClick = [sqSelected]



            #Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z :
                    gs.undoMove()
                    moveMade=True
                    animate = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClick = []
                    moveMade = False
                    animate = False




        #AI move finder logic
        if not gameOver and not humanTurn:
            AImove = SmartMoveFinder.findBestMoves(gs,validMoves)
            if AImove is None:
                AImove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AImove)

            moveMade = True
            animate = True




        if moveMade:
            if animate:
                animateMoves(gs.moveblog[-1],screen,gs.board,clock)
            validMoves =gs.getValidMoves
            moveMade=False
            animate = False


        if gs.checkmate:
            gameOver = True
            if gs.whitetomove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White  wins by checkmate")

        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate")


        drawGameState(screen, gs,validMoves,sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()
def highlightSquare(screen, gs , validMoves , sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0]== ('w' if gs.whitetomove else 'b'):
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c :
                    screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))



def drawGameState(screen, gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquare(screen,gs,validMoves,sqSelected)
    drawPeices(screen, gs.board)



def drawBoard(screen):
    global colours
    colours = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colours[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPeices(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMoves(move,screen,board,clock):
    global colours

    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    FPS = 10
    FrameCount =  (abs(dR) + abs(dC))*FPS
    for frame in range(FrameCount+1):
       r,c = move.startRow+dR*frame/FrameCount,move.startCol+dC*frame/FrameCount
       drawBoard(screen)
       drawPeices(screen,board)
       color = colours[(move.endRow+move.endCol)%2]
       endSquare = p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
       p.draw.rect(screen,color,endSquare)
       if move.pieceCaptured != "--":
           screen.blit(IMAGES[move.pieceMoved],endSquare)
       screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
       p.display.flip()
       clock.tick(60)



def drawText(screen , text):
    font = p.font.SysFont("Helyitca",32,True,False)
    textObject =  font.render(text,0,p.Color('Black'))
    textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2 - textObject.get_width()/2,HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)

if __name__ == "__main__":
    main()
