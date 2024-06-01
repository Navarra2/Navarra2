"""This class is responsible for storing all the information of the current state of the chess game. 
It will also be responsible to determine the valid moves at the current state. It will have a move log."""


class GameState:
    def __init__(self) -> None:
        # board is 8x8 2dim list, each element of the list has 2 characters
        # the 1st represent color ("b"or "w") and the 2nd represents the type of piece
        # the string "--" represents the empty space
        # numpy arrays can make it more efficient
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "B": self.getBishopMoves,
            "N": self.getKnightMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
        }
        self.WhitetoMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()  # coordinates for the square where en passant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [
            CastleRights(
                self.currentCastlingRight.wks,
                self.currentCastlingRight.wqs,
                self.currentCastlingRight.bks,
                self.currentCastlingRight.bqs,
            )
        ]

    """Takes a move as a parameter and executes it (this will not work for castling, en-passant and pawn promotion)"""

    def makeMove(self, move, bot_promoting_piece = None):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.WhitetoMove = not self.WhitetoMove  # swap players
        # update king's location
        if move.pieceMoved == "wK":
            self.whiteKingLocation == (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation == (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            if bot_promoting_piece is not None:
                promotedPiece = bot_promoting_piece
            else:
                promotedPiece = input("Promote to Q,R,B or N:")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        # en passant capture
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # capture the pawn
        # update the enpassant possible variable
        if (
            move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2
        ):  # 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()  # we only have opportunity to do en passant 1 move after the 2 square advance

        # update castling rights -whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(
            CastleRights(
                self.currentCastlingRight.wks,
                self.currentCastlingRight.wqs,
                self.currentCastlingRight.bks,
                self.currentCastlingRight.bqs,
            )
        )
        #print(self.currentCastlingRight.wks,self.currentCastlingRight.wqs,self.currentCastlingRight.bks,self.currentCastlingRight.bqs)

        if move.castle:
            if move.endCol - move.startCol == 2:  # Kingside
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1
                ]  # move rook
                self.board[move.endRow][
                    move.endCol + 1
                ] = "--"  # empty space where rook was
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2
                ]  # move rook
                self.board[move.endRow][
                    move.endCol - 2
                ] = "--"  # empty space where rook was

    """Undo the last move made"""

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.WhitetoMove = not self.WhitetoMove  # switch turns back
            # update king's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation == (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation == (move.startRow, move.startCol)
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][
                    move.endCol
                ] = "--"  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undo castling rights
            self.castleRightsLog.pop()  # get rid of the new castle rights from the move we are undoing
            castleRights = self.castleRightsLog[
                -1
            ]  # set the current castle rights to the last in the list

            self.currentCastlingRight.wks = castleRights.wks
            self.currentCastlingRight.wqs = castleRights.wqs
            self.currentCastlingRight.bks = castleRights.bks
            self.currentCastlingRight.bqs = castleRights.bqs

            if move.castle:
                if move.endCol - move.startCol == 2:  # kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                        move.endCol - 1
                    ]  # move rook
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][
                        move.endCol + 1
                    ]  # move rook
                    self.board[move.endRow][move.endCol + 1] = "--"

            self.checkMate = False
            self.staleMate = False

    """Update the castle rights given a move"""

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False

        # if rook is captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    """ All moves considering checks"""

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.WhitetoMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # one check -> block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of the squares between the enemy piece and the king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][
                    checkCol
                ]  # enemy piece causing the check
                validSquares = []  # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (
                            kingRow + check[2] * i,
                            kingCol + check[3] * i,
                        )  # check[2] and check[3] are check directions
                        validSquares.append(validSquare)
                        if (
                            validSquare[0] == checkRow and validSquare[1] == checkCol
                        ):  # once you get to piece end checks
                            break
                # get rid of any moves that don't block the checks or move king
                for i in range(
                    len(moves) - 1, -1, -1
                ):  # go through backwards when you are removing from a list as iterating
                    if (
                        moves[i].pieceMoved[1] != "K"
                    ):  # move doesn't move king so it must block or capture
                        if (
                            not (moves[i].endRow, moves[i].endCol) in validSquares
                        ):  # move doesn't block check or capture piece
                            moves.remove(moves[i])

            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        if self.WhitetoMove and (self.currentCastlingRight.wks or self.currentCastlingRight.wqs):
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves, "w"
            )
        elif not self.WhitetoMove and (self.currentCastlingRight.bks or self.currentCastlingRight.bqs):
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves, "b"
            )

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        return moves

    """
    def getValidMoves(self):
        
        #naive solution
        #1) generate all the possible moves
        moves = self.getAllPossibleMoves()
        
        #2) for each move, make the move
        for i in range(len(moves)-1,-1,-1): #when removing from a list, go backwards through that list
            self.makeMove(moves[i])
            #3) generate all opponents moves
            #4) for each of these moves, see if they attack the king
            self.WhitetoMove = not self.WhitetoMove
            if self.inCheck():
                moves.remove(moves[i]) #5) if they attack the king, it's not a valid move
            self.WhitetoMove = not self.WhitetoMove
            self.undoMove()
        
        if len(moves) == 0 : #either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves  # for now we will not worry about checks


    def inCheck(self): #determine if the current player is in check
        if self.WhitetoMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
    
    def squareUnderAttack(self,r,c): #determine if the enemy can attack the square (r,c)
        self.WhitetoMove = not self.WhitetoMove #switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.WhitetoMove = not self.WhitetoMove

        for move in oppMoves:
            if move.endRow == r  and move.endCol == c: #square is underattack
                return True
        return False
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of cols in given row
                turn = self.board[r][c][0]
                if (turn == "w" and self.WhitetoMove) or (
                    turn == "b" and not self.WhitetoMove
                ):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](
                        r, c, moves
                    )  # apply the function associated to the piece type
        return moves

    """Get all the pawn moves for the pawn located at row, col and add these moves to the list"""

    def getPawnMoves(self, r, c, moves):

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.WhitetoMove:  # white pawns to move
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                        moves.append(Move((r, c), (r - 2, c), self.board))

            # captures
            if c - 1 >= 0:  # capture on the left
                if self.board[r - 1][c - 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(
                            Move(
                                (r, c), (r - 1, c - 1), self.board, isEnpassantMove=True
                            )
                        )
            if c + 1 <= 7:  # capture on the right
                if self.board[r - 1][c + 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(
                            Move(
                                (r, c), (r - 1, c + 1), self.board, isEnpassantMove=True
                            )
                        )

        else:  # black pawns to move
            if self.board[r + 1][c] == "--":  # 1 square pawn advance
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # captures
            if c - 1 >= 0:  # capture on the right
                if self.board[r + 1][c - 1][0] == "w":
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(
                            Move(
                                (r, c), (r + 1, c - 1), self.board, isEnpassantMove=True
                            )
                        )

            if c + 1 <= 7:  # capture on the left
                if self.board[r + 1][c + 1][0] == "w":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(
                            Move(
                                (r, c), (r + 1, c + 1), self.board, isEnpassantMove=True
                            )
                        )

        # add pawn promotions later

    def getRookMoves(self, r, c, moves):

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if (
                    self.board[r][c][1] != "Q"
                ):  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1))
        enemyColor = "b" if self.WhitetoMove else "w"

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if (
                        not piecePinned
                        or pinDirection == d
                        or pinDirection == (-d[0], -d[1])
                    ):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getBishopMoves(self, r, c, moves):

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (1, 1), (-1, 1), (1, -1))  # 4 diagonals
        enemyColor = "b" if self.WhitetoMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if (
                        not piecePinned
                        or pinDirection == d
                        or pinDirection == (-d[0], -d[1])
                    ):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getKnightMoves(self, r, c, moves):

        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = (
            (-2, 1),
            (-2, -1),
            (2, -1),
            (2, 1),
            (1, -2),
            (1, 2),
            (-1, -2),
            (-1, 2),
        )
        allyColor = "w" if self.WhitetoMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # not ally piece (empty of enemy)
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.WhitetoMove else "b"

        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not ally piece
                    # place king on end square and check for checks
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on original  location
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        # self.getCastleMoves(r,c,moves,allyColor)

    """Generate all valid castle moves for the king at (r,c) and add them to the list"""

    def getCastleMoves(self, r, c, moves, allyColor):
        if self.squareUnderAttack(r, c):
            return  # can't castle while we are in check

        if (self.WhitetoMove and self.currentCastlingRight.wks) or (
            not self.WhitetoMove and self.currentCastlingRight.bks
        ):
            self.getKingSideCastleMoves(r, c, moves, allyColor)

        if (self.WhitetoMove and self.currentCastlingRight.wqs) or (
            not self.WhitetoMove and self.currentCastlingRight.bqs
        ):
            self.getQueenSideCastleMoves(r, c, moves, allyColor)

    def getKingSideCastleMoves(self, r, c, moves, allyColor):
        if (
            self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--"
        ):  # this will not be an error since the king is on the center of the board
            # check if the empty are not being attacked
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(
                r, c + 2
            ):
                moves.append(Move((r, c), (r, c + 2), self.board, castle=True))

    def getQueenSideCastleMoves(self, r, c, moves, allyColor):
        if (
            self.board[r][c - 1] == "--"
            and self.board[r][c - 2] == "--"
            and self.board[r][c - 3] == "--"
        ):  # this will not be an error since the king is on the center of the board
            # check if the empty are not being attacked
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(
                r, c - 2
            ):
                moves.append(Move((r, c), (r, c - 2), self.board, castle=True))

    def squareUnderAttack(
        self, r, c
    ):  # determine if the enemy can attack the square (r,c)
        self.WhitetoMove = not self.WhitetoMove  # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.WhitetoMove = not self.WhitetoMove

        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is underattack
                return True
        return False

    def getQueenMoves(self, r, c, moves):  # a queen is a bishop + a rook
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def checkForPinsAndChecks(self):
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False

        if self.WhitetoMove:
            enemycolor = "b"
            allycolor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemycolor = "w"
            allycolor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # check outward from king for pins and checks, keep track of pins
        directions = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )

        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible Pins

            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allycolor and endPiece[1] != "K":
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemycolor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1) orthogonally away from the king and piece is a rook
                        # 2)diagonally away from king and piece is a bishop
                        # 3) 1 square away diagonally from king and piece is a pawn
                        # 4) any direction and piece is a queen
                        # 5) any direction in 1 square away  and piece is a king (this is necessary to prevent a king move to a square controlled by another king)

                        if (
                            (0 <= j <= 3 and type == "R")
                            or (4 <= j <= 7 and type == "B")
                            or (
                                i == 1
                                and type == "p"
                                and (
                                    (enemycolor == "w" and 6 <= j <= 7)
                                    or (enemycolor == "b" and 4 <= j <= 5)
                                )
                            )
                            or (type == "Q")
                            or (i == 1 and type == "K")
                        ):

                            if possiblePin == ():  # nopiece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                        else:  # enemy piece not applying check
                            break
                else:
                    break  # off board
        knightMoves = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if (
                    endPiece[0] == enemycolor and endPiece[1] == "N"
                ):  # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


"""
    def getKingMoves(self,r,c,moves):
        kingMoves = ((0,1),(0,-1),(1,-1),(1,1),(-1,1),(-1,-1),(1,0),(-1,0))
        allyColor = "w" if self.WhitetoMove else "b"
        for m in kingMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and  0 <= endCol <8: # on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not ally piece (empty of enemy)
                    moves.append(Move((r,c),(endRow,endCol),self.board))
"""


"""
    def getRookMoves(
        self, r, c, moves
    ):  # check in the 4 directions until you hit a piece or the end of the board

        counter = 1
        turn = self.board[r][c][0]  # color of the piece
        while r + counter <= 7:  # down
            if self.board[r + counter][c] == "--":  # rook can go to the empty square
                moves.append(Move((r, c), (r + counter, c), self.board))
                counter += 1
            else:  # hit a piece
                if (
                    self.board[r + counter][c][0] != turn
                ):  # if you a hit a piece with opposite color you can do the move
                    moves.append(Move((r, c), (r + counter, c), self.board))
                break
        counter = 1
        while r - counter >= 0:  # up
            if self.board[r - counter][c] == "--":  # rook can go to the empty square
                moves.append(Move((r, c), (r - counter, c), self.board))
                counter += 1
            else:  # hit a piece
                if (
                    self.board[r - counter][c][0] != turn
                ):  # if you a hit a piece with opposite color you can do the move
                    moves.append(Move((r, c), (r - counter, c), self.board))
                break
        counter = 1
        while c + counter <= 7:  # right
            if self.board[r][c + counter] == "--":  # rook can go to the empty square
                moves.append(Move((r, c), (r, c + counter), self.board))
                counter += 1
            else:  # hit a piece
                if (
                    self.board[r][c + counter][0] != turn
                ):  # if you a hit a piece with opposite color you can do the move
                    moves.append(Move((r, c), (r, c + counter), self.board))
                break
        counter = 1
        while c - counter >= 0:  # left
            if self.board[r][c - counter] == "--":  # rook can go to the empty square
                moves.append(Move((r, c), (r, c - counter), self.board))
                counter += 1
            else:  # hit a piece
                if (
                    self.board[r][c - counter][0] != turn
                ):  # if you a hit a piece with opposite color you can do the move
                    moves.append(Move((r, c), (r, c - counter), self.board))
                counter = 1
                break

    def getBishopMoves(self, r, c, moves):
        counter = 1
        turn = self.board[r][c][0]  # color of the piece
        while r + counter <= 7 and c + counter <= 7:  # down right
            if (
                self.board[r + counter][c + counter] == "--"
            ):  # bishop can go to the empty square
                moves.append(Move((r, c), (r + counter, c + counter), self.board))
                counter += 1
            else:  # hit a piece
                if (
                    self.board[r + counter][c + counter][0] != turn
                ):  # if you a hit a piece with opposite color you can do the move
                    moves.append(Move((r, c), (r + counter, c + counter), self.board))
                break
        counter = 1
        while r - counter >= 0 and c + counter <= 7:  # up right
            if (
                self.board[r - counter][c + counter] == "--"
            ):  # bishop can go to the empty square
                moves.append(Move((r, c), (r - counter, c + counter), self.board))
                counter += 1
            else:  # hit a piece
                if (
                    self.board[r - counter][c + counter][0] != turn
                ):  # if you a hit a piece with opposite color you can do the move
                    moves.append(Move((r, c), (r - counter, c + counter), self.board))
                break
        counter = 1
        while r + counter <= 7 and c - counter >= 0:  # down left
            if (
                self.board[r + counter][c - counter] == "--"
            ):  # bishop can go to the empty square
                moves.append(Move((r, c), (r + counter, c - counter), self.board))
                counter += 1
            else:  # hit a piece
                if (
                    self.board[r + counter][c - counter][0] != turn
                ):  # if you a hit a piece with opposite color you can do the move
                    moves.append(Move((r, c), (r + counter, c - counter), self.board))
                break
        counter = 1
        while r - counter >= 0 and c - counter >= 0:  # up left
            if (
                self.board[r - counter][c - counter] == "--"
            ):  # bishop can go to the empty square
                moves.append(Move((r, c), (r - counter, c - counter), self.board))
                counter += 1
            else:  # hit a piece
                if (
                    self.board[r - counter][c - counter][0] != turn
                ):  # if you a hit a piece with opposite color you can do the move
                    moves.append(Move((r, c), (r - counter, c - counter), self.board))
                counter = 1
                break

    def getKnightMoves(
        self, r, c, moves
    ):  # iterate over the 8 possible positions and check if they are valid
        turn = self.board[r][c][0]  # color of the piece
        possible_knight_moves = [
            [r + 1, c + 2],
            [r - 1, c + 2],
            [r + 1, c - 2],
            [r - 1, c - 2],
            [r + 2, c + 1],
            [r + 2, c - 1],
            [r - 2, c + 1],
            [r - 2, c - 1],
        ]
        for m in possible_knight_moves:
            [mr, mc] = m
            if mr >= 0 and mr <= 7 and mc >= 0 and mc <= 7:
                if self.board[mr][mc] == "--":
                    moves.append(Move((r, c), (mr, mc), self.board))
                else:
                    if (
                        self.board[mr][mc][0] != turn
                    ):  # if you a hit a piece with opposite color you can do the move
                        moves.append(Move((r, c), (mr, mc), self.board))

    def getQueenMoves(self, r, c, moves):  # a queen is a bishop + a rook
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(
        self, r, c, moves
    ):  # iterate over the 8 possible positions and check if they are valid
        turn = self.board[r][c][0]  # color of the piece
        counters = [-1, 0, 1]
        possible_moves = []
        for c1 in counters:
            for c2 in counters:
                possible_moves.append([r + c1, c + c2])
        for m in possible_moves:
            [mr, mc] = m
            if mr >= 0 and mr <= 7 and mc >= 0 and mc <= 7:
                if self.board[mr][mc] == "--":
                    moves.append(Move((r, c), (mr, mc), self.board))
                else:
                    if (
                        self.board[mr][mc][0] != turn
                    ):  # if you a hit a piece with opposite color you can do the move
                        moves.append(Move((r, c), (mr, mc), self.board))
"""


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:

    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(
        self, startSq, endSq, board, isEnpassantMove=False, castle=False
    ) -> None:
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.castle = castle

        # pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (
            self.pieceMoved == "bp" and self.endRow == 7
        ):
            self.isPawnPromotion = True
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

        self.moveID = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )  # gives us an unique ID
        # print(self.moveID)
        self.isCapture = self.pieceCaptured != "--"

    """Overwriting the equals method"""

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    def getChessNotation(self):
        # you can add to make this real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    # overriding the str() function
    def __str__(self):
        # castle move
        if self.castle:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow, self.endRow)
        # pawn moves
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
            # pawn promotions
        # two of the same type of piece moving to a square

        # also "+" adding check move and checkmate "#"

        # piece moves

        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare
