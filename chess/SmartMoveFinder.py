""" This is the script where AI can be added to define the computer moves"""

import random

#TODO check pawn promotions with the bot for more than just the queen

# the white wants the score to be positive and black wants negative score
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

"""Picks and returns a random move"""


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


"""Finds the best move based on material alone - Min Max Algorithm"""


def findGreedyMove(gs, validMoves):

    turnMultiplier = 1 if gs.WhitetoMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE

        if gs.staleMate:
            opponentMaxScore = STALEMATE
        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves:
                gs.makeMove(opponentsMove)
                gs.getValidMoves()
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


"""helper method to make the 1st recursive call"""


def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    # findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.WhitetoMove else -1)
    findMoveNegaMaxAlphaBeta(
        gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.WhitetoMove else -1
    )

    # findMoveMinMax(gs, validMoves, DEPTH, gs.WhitetoMove )

    return nextMove


def findMoveMinMax(gs, validMoves, depth, WhiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)

    if WhiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            if move.isPawnPromotion:
                for piece in ["Q", "N"]:
                    print("here1")
                    gs.makeMove(move,bot_promoting_piece = piece)
                    nextMoves = gs.getValidMoves()
                    score = findMoveMinMax(gs, nextMoves, depth - 1, False)
                    if score > maxScore:
                        maxScore = score
                        if depth == DEPTH:
                            nextMove = move
                    gs.undoMove()
            else:
                gs.makeMove(move)
                nextMoves = gs.getValidMoves()
                score = findMoveMinMax(gs, nextMoves, depth - 1, False)
                if score > maxScore:
                    maxScore = score
                    if depth == DEPTH:
                        nextMove = move
                gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move,bot_promoting_piece = "Q")
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)

            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE

    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    # move ordering - implement later
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(
            gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier
        )
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:  # pruning happens
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


"""Score the board based on material"""


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score


"""A positive score  is good for white and a negative score is good for black"""


def scoreBoard(gs):

    if gs.checkMate:
        if gs.WhitetoMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score
