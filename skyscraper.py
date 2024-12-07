import copy


def create_groupings_and_neighbors(left_clues, right_clues, top_clues, bottom_clues,grid_length):

  rows = [chr(ord('@')+number) for number in range(1, grid_length + 1)]

  columns = [str(number) for number in range(1, grid_length+1)]

  cells = tuple(letter + digit for letter in rows for digit in columns)

  groupings = {c: tuple([[c[0] + digit for digit in columns],[letter + c[1] for letter in rows]])  for c in cells}

  neighbors = {c: set(tuple([c[0] + digit for digit in columns] + [letter + c[1] for letter in rows])) for c in cells}

  for cell in cells:
    neighbors[cell].remove(cell)

  return cells, groupings, neighbors

def process_clues(grid, grid_length, clues, direction):

  for i in range(len(clues)):

    if clues[i] == 0:
      continue

    c = None
    if direction == 'L':
      c = tuple([chr(ord('@') + i+1) + str(digit) for digit in range(1, grid_length+1)])
    elif direction =='R':
      c = tuple([chr(ord('@') + i+1) + str(digit) for digit in range(grid_length, 0, -1)])
    elif direction == 'T':
      c = tuple([chr(ord('@') + j+1) + str(i+1) for j in range(len(clues))])
    elif direction == 'B':
      c = tuple([chr(ord('@') + j+1) + str(i+1) for j in range(len(clues)-1, -1, -1)])

    # Alter the existing set of possible values instead of creating new set
    # This make sure after processing clues from all directions to check for a valid puzzle
    # If any cell with 0 possible value then the puzzle is invalid

    if 1 < clues[i] and clues[i] < grid_length:
      # If clues is between 1 & grid_length, then update the possible range of values
      # with maximum value for each cell being, max_val = grid_length - clue[i] + 1 + distance
      for distance in range(len(c)):
        cell = c[distance]
        max_val = grid_length - clues[i] + 1 + distance

        if max_val > grid_length:
          max_val = grid_length

        for j in range(max_val+1, grid_length+1):
          if j in grid[cell]:
            grid[cell].remove(j)

    elif clues[i] == 1:
      # If clue is 1 then the first cell of that row/column is resolved
      i = grid_length

      for i in range(len(c)):
        cell = c[i]
        if i == 0:
          grid[cell] = set([grid_length]) if grid_length in grid[cell] else set()
        else:
          if grid_length in grid[cell]:
            grid[cell].remove(grid_length)

    elif clues[i] == grid_length:
      # If clue is = grid length then the entire row/column of clue is resolved
      i = 1
      for cell in c:
        grid[cell] = set([i]) if i in grid[cell] else set()
        i += 1

def initialize_grid(grid_length, cells, left_clues, right_clues, top_clues, bottom_clues):

  grid = {cell: set([number for number in range(1, grid_length+1)]) for cell in cells}
  process_clues(grid, grid_length, left_clues, 'L')
  process_clues(grid, grid_length, right_clues, 'R')
  process_clues(grid, grid_length, top_clues, 'T')
  process_clues(grid, grid_length, bottom_clues, 'B')

  # If constraints of the puzzle are invalid, return None
  for cell in cells:
    if len(grid[cell]) == 0:
      return None

  return grid

def remove_value(grid, cell, possible_value):

  # If the value is not a possibility for this cell, return True
  if possible_value not in grid[cell]:
    return True

  # If this value is the only possibility for this cell, then removing it makes the grid invalid, return None
  if len(grid[cell]) == 1:
    return None

  grid[cell].remove(possible_value) # Remove the value from possibility

  # If after removing and there is only one possible value left for the cell, then remove that possibility from the neighboring cells
  if len(grid[cell]) == 1:
    # Outer for loop only has 1 iteration
    for val in grid[cell]:
      for neighbor in neighbors[cell]:
        if not remove_value(grid, neighbor, val):
          return None

  # After recursively removing possibilities from neighboring cells, check constraints of grouping to see if there is only one cell that has the recently removed value
  # as its possibility
  for grouping in groupings[cell]:
    count = 0
    t = None
    for c in grouping:
      if possible_value in grid[c]:
        t = c
        count += 1

    if count == 0:
      return None
    if count == 1 and not assign(grid, t, possible_value):
      return None

  return True

def assign(grid, cell, possible_value):

  # Two possiblities when invoking this function
  # If the assigned cell only has one possible value, then remove that possible value from all neighbors
  if possible_value in grid[cell] and len(grid[cell]) == 1:
    for val in grid[cell]:
      for neighbor in neighbors[cell]:
        if not remove_value(grid, neighbor, val):
          return None
    return grid

  # If the assigned cell has other possible values, call remove_value() to remove all the other values from possibility for this cell
  if possible_value in grid[cell]:

      for value in grid[cell].copy():
        if value != possible_value:
          if not remove_value(grid, cell, value):
            return None

      return grid

  return None

def sequence_filtration(grid):

  temp_grid = {}
  for i in range(grid_length):
    if left_clues[i] != 0:
      valid_sequences = get_valid_sequences('L', left_clues[i], i)
      cells = tuple([chr(ord('@') + i+1) + str(digit) for digit in range(1, grid_length+1)])
      for sequence in valid_sequences:
        for j in range(len(sequence)):
          if cells[j] not in temp_grid:
            temp_grid[cells[j]] = set()

          temp_grid[cells[j]].add(sequence[j])

    if right_clues[i] != 0:
      valid_sequences = get_valid_sequences('R', right_clues[i], i)
      cells = tuple([chr(ord('@') + i+1) + str(digit) for digit in range(grid_length, 0, -1)])
      for sequence in valid_sequences:
        for j in range(len(sequence)):
          if cells[j] not in temp_grid:
            temp_grid[cells[j]] = set()

          temp_grid[cells[j]].add(sequence[j])

    if top_clues[i] != 0:
      valid_sequences = get_valid_sequences('T', top_clues[i], i)
      cells = tuple([chr(ord('@') + j+1) + str(i+1) for j in range(grid_length)])
      for sequence in valid_sequences:
        for j in range(len(sequence)):
          if cells[j] not in temp_grid:
            temp_grid[cells[j]] = set()

          temp_grid[cells[j]].add(sequence[j])

    if bottom_clues[i] != 0:
      valid_sequences = get_valid_sequences('B', bottom_clues[i], i)
      cells = tuple([chr(ord('@') + j+1) + str(i+1) for j in range(grid_length-1, -1, -1)])
      for sequence in valid_sequences:
        for j in range(len(sequence)):
          if cells[j] not in temp_grid:
            temp_grid[cells[j]] = set()

          temp_grid[cells[j]].add(sequence[j])

  return temp_grid

def get_valid_sequences(direction, clue, i):
  constraints = get_constraints_list(direction, i)
  sequences = unique_sequences(constraints)
  valid_sequences = []

  for sequence in sequences:
    visible = 0
    max_value = 0
    for value in sequence:
      if value > max_value:
        visible += 1
        max_value = value

    if clue == visible:
      valid_sequences.append(sequence)

  return valid_sequences

def get_constraints_list(direction, i):
  constraints = []

  if direction == 'L':
    for j in range(1, grid_length + 1):
      cell = chr(ord('@') + i+1) + str(j)
      constraints.append(grid[cell])

  elif direction == 'R':
    for j in range(grid_length, 0, -1):
      cell = chr(ord('@') + i+1) + str(j)
      constraints.append(grid[cell])

  elif direction == 'T':
    for j in range(grid_length):
      cell = chr(ord('@') + j+1) + str(i+1)
      constraints.append(grid[cell])

  elif direction == 'B':
    for j in range(grid_length - 1, -1, -1):
      cell = chr(ord('@') + j+1) + str(i+1)
      constraints.append(grid[cell])

  return constraints

def unique_sequences(constraints):
  sequences = []

  def helper(sequence_list, index):
    for constraint in constraints[index]:
      temp = sequence_list.copy()
      if constraint in sequence_list:
        continue

      temp.append(constraint)

      if index == len(constraints) - 1:
        sequences.append(temp)
      else:
        helper(temp, index+1)

  helper([], 0)

  return sequences

def clues_check(grid):
  for i in range(grid_length):

    if left_clues[i] != 0:
      cells = tuple([chr(ord('@') + i+1) + str(digit) for digit in range(1, grid_length+1)])

      visible = 0
      max_val = 0

      for cell in cells:
        (val,) = grid[cell]
        if val > max_val:
          visible += 1
          max_val = val
      if visible != left_clues[i]:
        return False

    if right_clues[i] != 0:
      cells = tuple([chr(ord('@') + i+1) + str(digit) for digit in range(grid_length, 0, -1)])
      visible = 0
      max_val = 0

      for cell in cells:
        (val,) = grid[cell]
        if val > max_val:
          visible += 1
          max_val = val
      if visible != right_clues[i]:
        return False

    if top_clues[i] != 0:
      cells = tuple([chr(ord('@') + j+1) + str(i+1) for j in range(grid_length)])
      visible = 0
      max_val = 0

      for cell in cells:
        (val,) = grid[cell]
        if val > max_val:
          visible += 1
          max_val = val
      if visible != top_clues[i]:
        return False

    if bottom_clues[i] != 0:
      cells = tuple([chr(ord('@') + j+1) + str(i+1) for j in range(grid_length-1, -1, -1)])
      visible = 0
      max_val = 0

      for cell in cells:
        (val,) = grid[cell]
        if val > max_val:
          visible += 1
          max_val = val
      if visible != bottom_clues[i]:
        return False

  return True

def search(grid):
  if grid is None:
    return None

  grid_seq = sequence_filtration(grid)

  for cell in grid_seq:

    for value in grid[cell] - grid_seq[cell]:
      remove_value(grid, cell, value)


  cell = min((c for c in cells if len(grid[c]) > 1), default = None, key= lambda c: len(grid[c]))

  if cell is None:
    return grid

  for possible_value in grid[cell].copy():

    grid_copy = copy.deepcopy(grid)
    assigned_grid = assign(grid_copy, cell, possible_value)
    temp_grid = search(assigned_grid)

    # If the grid is not None, then a solution is found
    if temp_grid is not None and clues_check(temp_grid):
      return temp_grid

  return None


left_clues = [3,1,2,3]
right_clues = [2,3,3,1]
top_clues = [2,3,1,2]
bottom_clues = [3,2,2,1]

grid_length = len(left_clues)


cells, groupings, neighbors = create_groupings_and_neighbors(left_clues, right_clues, top_clues, bottom_clues)

grid = initialize_grid(grid_length, cells, left_clues, right_clues, top_clues, bottom_clues)


for cell in cells:
  if len(grid[cell]) == 1:
    for val in grid[cell]:
      grid = assign(grid, cell, val)

grid_seq = sequence_filtration(grid)

for cell in grid_seq:

  for value in grid[cell] - grid_seq[cell]:
    remove_value(grid, cell, value)

sol = search(grid)
print(sol)