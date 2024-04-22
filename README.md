# Aduhuli Game Rulebook

Welcome to the traditional game of Aduhuli, also known as Goat and Tigers. This is a strategic two-player game from South India where one player controls three tigers and the other up to fifteen goats. The game is played on a unique board with the tigers attempting to 'hunt' the goats, while the goats aim to immobilize the tigers.

## Equipment
- **Game Board**: The Aduhuli game board is composed of intersecting lines with designated spots for placing game pieces.
- **Game Pieces**: Includes 18 pieces - 3 tigers and 15 goats.

## Setup
- **Initial Position**: Place all three tigers on the apex and two inner positions closest to the apex at the start of the game.
- **Goats**: Begin the game off the board. They are introduced onto the board one by one during play.

## Rules of Play

### Goat Rules
1. **Introduction of Goats**: All 15 goats must be placed onto the board before any goat can move.
2. **Movement**: Goats can only move to adjacent intersections along the lines of the board; they cannot jump over tigers or other goats.
3. **Capture**: Goats are removed from the board when captured by a tiger. Goats must leave the board when captured and cannot jump over tigers or other goats.

### Tiger Rules
1. **Movement and Capture**: Tigers can move to any adjacent intersection along the lines of the board and can capture goats by jumping over them to an adjacent free position. Tigers can capture goats during any move, and do not need to wait until all goats are placed.
2. **Restrictions**: Tigers cannot jump over other tigers. They can capture only one goat at a time and must jump over a goat in any direction, as long as there is an open space to complete their turn.

## Game Play
1. **Starting the Game**: The player controlling the goats goes first, placing one goat onto a free intersection on the board. Play then alternates with the tiger player moving one tiger.
2. **Goat Placement**: Goats must be placed on the board until all 15 are on the board. They cannot move until all are placed.
3. **Tiger Movement**: Tigers can begin capturing goats from their first move. Moves alternate between players.

## Winning the Game
1. **Tigers Win**: If the tigers capture at least six goats.
2. **Goats Win**: If the goats immobilize all three tigers so that they cannot move.

## Avoiding Repetition
To prevent repetitive cycles of positions, once all goats are placed, no move may return the board to a situation that has already occurred during the game. This rule helps keep the gameplay dynamic and prevents stalling tactics.


Let's model this game:

Let's say we have a board mxn, where m is the number of rows and n is the number of columns. Each cell represents a position on the board. The cell can be thought of as a node in a graph. The edges of the graph are the possible moves from one cell to another. The game board can be represented as a graph where each cell is a node and the edges represent the possible moves from one cell to another. The game board can be represented as an adjacency list or an adjacency matrix.

Not all cells are valid cells. Some cells are invalid because they are outside the board.
Also not all cells are connected to all other cells. Some cells are connected to only a subset of cells.
Every connected (edge) is a bi-directional connection. If a tiger can move from cell A to cell B, then it can also move from cell B to cell A given that there is no one else in the way.
