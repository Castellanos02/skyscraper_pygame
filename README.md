# Skyscraper Puzzle GUI

This project provides a **user-friendly GUI** where you can:
- Input custom puzzles.
- Solve the puzzle automatically.
- Clear the board for a fresh start.
- Generate new grid size puzzle.
- View how many states are created for the Brute Force (BF) apporach and Constraint Propagation (CP)
- View the runtime of the Constraint Porpagation algorithm

---

## Dependencies

- **Pygame**
- **Pip**

Install dependencies using:

'''
pip install pygame
pip install pip
'''
---

## How to Use

1. **Launch the Program**.
2. Use the **grid** to interact with the puzzle:
   - Edge clues indicate visibility constraints (Blue boxes)
   - Assign values to cells (Black boxes)
3. Utilize the buttons to control the puzzle:
   - **Clear Board**: Reset the puzzle grid.
   - **Solve**: Automatically solve the puzzle.
   - **Create**: Generate a new puzzle with a different grid size.
   - **+**: Increase the grid size number
   - **-**: Decreases the grid size number
---

## Rules of the Puzzle

The Skyscraper Puzzle follows these rules:

1. The grid size is typically **NxN** (e.g., 4x4, 5x5).
2. Each row and column must contain the numbers **1 to N** without repeats.
3. Edge clues indicate how many skyscrapers are visible:
   - A taller skyscraper blocks shorter ones behind it.
   - Example: Clue `3` means 3 skyscrapers are visible in that row or column.
4. The goal is to fill the grid so all visibility clues are satisfied.
