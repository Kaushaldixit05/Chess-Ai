class GameState():
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.moveFunction = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                             "Q": self.getQueenMoves, "B": self.getBishopMoves, "K": self.getKingMoves}

        self.whitetomove = True
        self.moveblog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enPassauntPossible = ()

        self.currentCastleRight = CastleRights(True, True, True, True)
        self.castleRightBlog = [
            CastleRights(self.currentCastleRight.wks, self.currentCastleRight.wqs, self.currentCastleRight.bks,
                         self.currentCastleRight.bqs)]

        self.stalemate = False
        self.checkmate = False

    '''
    Takes a move as a parameter and perform it 
    '''

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveblog.append(move)

        self.whitetomove = not self.whitetomove
        # uodate the kings location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            promotedPiece = input("Promote to Q,R,B, or N :")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece


        if move.pieceMoved[1] == 'p' and ((move.endRow - move.startRow) == 2 or (move.endRow - move.startRow) == -2):
            self.enPassauntPossible = ((move.endRow + move.startRow) // 2, move.endCol)

        else:
            self.enPassauntPossible = ()

        if move.isenpassauntMove:
            self.board[move.startRow][move.endCol] = "--"
        self.updateCasteRights(move)
        self.castleRightBlog.append(
            CastleRights(self.currentCastleRight.wks, self.currentCastleRight.wqs, self.currentCastleRight.bks,
                         self.currentCastleRight.bqs))

        if move.castle:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"


    def undoMove(self):
        if len(self.moveblog) != 0:
            move = self.moveblog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whitetomove = not self.whitetomove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isenpassauntMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassauntPossible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassauntPossible = ()

            self.castleRightBlog.pop()
            self.currentCastleRight = self.castleRightBlog[-1]

            if move.castle:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"

                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

    def updateCasteRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastleRight.wks = False
            self.currentCastleRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastleRight.bks = False
            self.currentCastleRight.bqs= False
        elif move.pieceMoved == 'wR':

            if move.startCol == 7:
                self.currentCastleRight.wks = False
            if move.startCol == 0:
                self.currentCastleRight.wqs = False
        elif move.pieceMoved == 'bR':

            if move.startCol == 7:
                self.currentCastleRight.bks = False
            if move.startCol == 0:
                self.currentCastleRight.bqs= False

    def getValidMoves(self):

        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whitetomove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]

        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)

                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)

            if len(moves) == 0:
                self.checkmate = True


        else:
            moves = self.getAllPossibleMoves()
            if self.whitetomove:
                kingRow = self.whiteKingLocation[0]
                kingCol = self.whiteKingLocation[1]
                self.getCastleMoves(kingRow, kingCol, moves)
            else:
                kingRow = self.blackKingLocation[0]
                kingCol = self.blackKingLocation[1]
                self.getCastleMoves(kingRow, kingCol, moves)
            if len(moves) == 0:
                self.stalemate = True

        return moves

    def inCheck(self):

        if self.whitetomove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whitetomove = not self.whitetomove
        opponentMoves = self.getAllPossibleMoves()
        self.whitetomove = not self.whitetomove
        for move in opponentMoves:
            if move.endRow == r and move.endCol == c:
                return True

        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whitetomove) or (turn == 'b' and not self.whitetomove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        pawnPromotion = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whitetomove:
            if self.board[r - 1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    if r - 1 == 0:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r - 1, c), self.board, pawnPromotion=pawnPromotion))
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, -1):
                        if r - 1 == 0:
                            pawnPromotion = True
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, pawnPromotion=pawnPromotion))
                elif (r - 1, c - 1) == self.enPassauntPossible:
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, enpassantMove=True))

            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        if r - 1 == 0:
                            pawnPromotion = True
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, pawnPromotion=pawnPromotion))
                elif (r - 1, c + 1) == self.enPassauntPossible:
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, enpassantMove=True))

        else:
            if self.board[r + 1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    if r + 1 == 7:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + 1, c), self.board, pawnPromotion=pawnPromotion))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        if r + 1 == 7:
                            pawnPromotion = True
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, pawnPromotion=pawnPromotion))
                elif (r + 1, c - 1) == self.enPassauntPossible:
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, enpassantMove=True))

            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        if r + 1 == 7:
                            pawnPromotion = True
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, pawnPromotion=pawnPromotion))

                elif (r + 1, c + 1) == self.enPassauntPossible:
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, enpassantMove=True))

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whitetomove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endpiece = self.board[endRow][endCol]
                        if endpiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endpiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break

                else:
                    break

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whitetomove else "b"
        for m in knightMoves:
            endRows = r + m[0]
            endCols = c + m[1]
            if 0 <= endRows < 8 and 0 <= endCols < 8:
                if not piecePinned:
                    endpiece = self.board[endRows][endCols]
                    if endpiece[0] != allyColor:
                        moves.append(Move((r, c), (endRows, endCols), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whitetomove else "b"

        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if allyColor == 'w':
                    self.whiteKingLocation = (endRow, endCol)
                else:
                    self.blackKingLocation = (endRow, endCol)
                inCheck, pins, check = self.checkForPinsAndChecks()
                if not inCheck:
                    if endPiece == '--' or endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

                if allyColor == 'w':
                    self.whiteKingLocation = (r, c)
                else:
                    self.blackKingLocation = (r, c)

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whitetomove and self.currentCastleRight.wks) or (not self.whitetomove and self.currentCastleRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whitetomove and self.currentCastleRight.wqs) or (not self.whitetomove and self.currentCastleRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastle=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r,c - 2) and not self.squareUnderAttack(r, c - 3):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastle=True))

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins)
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whitetomove else "w"

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):

                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break

                    else:
                        break
                else:
                    break

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whitetomove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]

        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endpiece = self.board[endRow][endCol]
                    if endpiece[0] == allyColor and endpiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endpiece[0] == enemyColor:
                        type = endpiece[1]

                        if (0 <= j < 3 and type == 'R') or \
                                (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endpiece = self.board[endRow][endCol]
                if endpiece[0] == enemyColor and endpiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks


class CastleRights():
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRank = {v: k for k, v in ranksToRows.items()}
    filestoCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filestoCols.items()}

    def __init__(self, startSq, endSq, board, pawnPromotion=False, enpassantMove=False, isCastle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.isPawnPromotion = pawnPromotion

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        self.isenpassauntMove = enpassantMove

        self.castle = isCastle

        if self.isenpassauntMove:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRank[r]
