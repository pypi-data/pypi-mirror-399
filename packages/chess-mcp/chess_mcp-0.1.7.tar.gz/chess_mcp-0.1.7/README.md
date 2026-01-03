# Chess MCP Server

A Model Context Protocol (MCP) server that provides a chess-playing environment backed by the Stockfish engine. Designed for use with LLM clients (like Claude Desktop) to ensure all chess moves are legal and engine-calculated.

## Features

- **Legal Move Validation**: All moves are validated against chess rules
- **Stockfish Integration**: Uses the Stockfish chess engine for AI moves
- **MCP Protocol**: Communicates via JSON-RPC over stdio
- **In-Memory Game State**: Maintains multiple concurrent games

## Installation

```bash
pip install chess-mcp
```

You'll also need to install Stockfish:

- **Windows**: Download from [Stockfish website](https://stockfishchess.org/download/)
- **macOS**: `brew install stockfish`
- **Linux**: `sudo apt install stockfish` (or equivalent)

## Usage

1. Set the `STOCKFISH_PATH` environment variable to the path of your Stockfish executable:

   ```bash
   export STOCKFISH_PATH=/path/to/stockfish
   ```

2. Run the server:

   ```bash
   python -m chess_mcp
   ```

## MCP Tools

### `new_game()`
Starts a new chess game from the standard initial position.

**Returns:**
- `game_id`: Unique identifier for the game
- `fen`: Current position in FEN notation
- `legal_moves`: List of all legal moves in UCI format

### `make_move(game_id, move_uci)`
Applies a human move to the game. The move must be in UCI format (e.g., "e2e4").

**Parameters:**
- `game_id`: Identifier of the active game
- `move_uci`: Move in UCI format

**Returns:**
- `ok`: Whether the move was legal and applied
- `fen`: Updated board position (if move was legal)
- `legal_moves`: Updated list of legal moves

### `engine_move(game_id, depth=14)`
Asks Stockfish to calculate and play one move for the side to move.

**Parameters:**
- `game_id`: Identifier of the active game
- `depth`: Search depth for Stockfish (higher = stronger but slower)

**Returns:**
- `engine_move`: The move played by Stockfish in UCI format
- `fen`: Updated board position after the move
- `legal_moves`: Updated list of legal moves

## Development

To set up for development:

```bash
git clone https://github.com/yourusername/chess-mcp.git
cd chess-mcp
pip install -e .
```

## License

MIT License