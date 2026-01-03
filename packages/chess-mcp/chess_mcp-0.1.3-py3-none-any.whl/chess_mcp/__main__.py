"""
Chess MCP Server

This MCP server exposes a chess-playing environment backed by the Stockfish
engine. It is designed to be used by LLM clients (e.g. Claude Desktop) so that:

- All chess moves are strictly legal
- The engine (Stockfish) selects moves for the AI side
- The LLM never hallucinates moves or evaluations

The server maintains in-memory game state and exposes tools to:
- start a new game
- make a human move
- request an engine move

IMPORTANT:
This server runs over stdio using JSON-RPC. Do NOT use print().
Use logging instead.
"""

from __future__ import annotations

import os
import logging
import uuid
from typing import Dict, Any

import chess
import chess.engine
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------
# Logging (stderr only; stdout is reserved for MCP JSON-RPC)
# ---------------------------------------------------------------------
logging.basicConfig(level=logging.WARNING)

log = logging.getLogger("chess-mcp")

# ---------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------
mcp = FastMCP("chess-mcp")

# Path to Stockfish executable (must be set in environment)

STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH")
if not STOCKFISH_PATH or not os.path.exists(STOCKFISH_PATH):
    log.warning("STOCKFISH_PATH is missing or invalid")

# In-memory storage for active games and engines
games: Dict[str, chess.Board] = {}
engines: Dict[str, chess.engine.SimpleEngine] = {}


def get_engine(game_id: str) -> chess.engine.SimpleEngine:
    """
    Get or create a Stockfish engine instance for a given game.

    Each game gets its own engine process to keep state clean.

    Args:
        game_id: Unique identifier of the chess game.

    Returns:
        A running SimpleEngine instance connected to Stockfish.

    Raises:
        RuntimeError: If STOCKFISH_PATH is not set.
    """
    if game_id not in engines:
        if not STOCKFISH_PATH:
            raise RuntimeError("STOCKFISH_PATH not set")
        engines[game_id] = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    return engines[game_id]


@mcp.tool()
async def new_game() -> Dict[str, Any]:
    """
    Start a new chess game from the standard initial position.

    This tool should be called before any moves are made.

    Returns:
        game_id: Unique identifier for the game.
        fen: Current position in FEN notation.
        legal_moves: List of all legal moves in UCI format.
    """
    board = chess.Board()
    game_id = str(uuid.uuid4())
    games[game_id] = board

    return {
        "game_id": game_id,
        "fen": board.fen(),
        "legal_moves": [m.uci() for m in board.legal_moves],
    }


@mcp.tool()
async def make_move(game_id: str, move_uci: str) -> Dict[str, Any]:
    """
    Apply a human move to the game.

    The move is validated against the current board state. Illegal moves
    are rejected and do not modify the game.

    Args:
        game_id: Identifier of the active game.
        move_uci: Move in UCI format (e.g. "e2e4", "g1f3").

    Returns:
        ok: Whether the move was legal and applied.
        fen: Updated board position (if move was legal).
        legal_moves: Updated list of legal moves.
    """
    board = games[game_id]
    move = chess.Move.from_uci(move_uci)

    if move not in board.legal_moves:
        return {"ok": False, "error": "Illegal move"}

    board.push(move)
    return {
        "ok": True,
        "fen": board.fen(),
        "legal_moves": [m.uci() for m in board.legal_moves],
    }


@mcp.tool()
async def engine_move(game_id: str, depth: int = 14) -> Dict[str, Any]:
    """
    Ask Stockfish to calculate and play one move for the side to move.

    This tool is used for the AI opponent. The engine guarantees:
    - legal move selection
    - tactical correctness within the given depth

    Args:
        game_id: Identifier of the active game.
        depth: Search depth for Stockfish (higher = stronger but slower).

    Returns:
        engine_move: The move played by Stockfish in UCI format.
        fen: Updated board position after the move.
        legal_moves: Updated list of legal moves.
    """
    board = games[game_id]
    engine = get_engine(game_id)

    result = engine.play(board, chess.engine.Limit(depth=depth))
    board.push(result.move)

    return {
        "engine_move": result.move.uci(),
        "fen": board.fen(),
        "legal_moves": [m.uci() for m in board.legal_moves],
    }


def main():
    """
    Entry point for the MCP server.

    Starts the FastMCP server using stdio transport so that
    LLM clients (e.g. Claude Desktop) can communicate via JSON-RPC.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()