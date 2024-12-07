import pygame
import copy
# import skyscraper as sk

import copy
grid_length = 0
left_clues = []
right_clues = []
top_clues = []
bottom_clues = []
groupings = {}
neighbors = {}
cells = ()


def create_groupings_and_neighbors(left_clues, right_clues, top_clues, bottom_clues):
  global groupings
  global neighbors
  global cells

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

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color('gray')
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('white') if self.active else pygame.Color('gray')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, screen):
        txt_surface = font.render(self.text, True, pygame.Color('black'))
        width = max(50, txt_surface.get_width() + 10)
        self.rect.w = width
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class TextBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, screen):
        txt_surface = font.render(self.text, True, pygame.Color('black'))
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, pygame.Color('black'), self.rect, 2)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color('blue')
        self.text = text
        

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        txt_surface = font.render(self.text, True, pygame.Color('white'))
        screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.text == "Solve":
                    grid.clues = []
                    holder = []
                    i = 0
                    
                    for box in grid.clue_boxes:
                        # print(box.text)
                        if i != grid.size - 1:
                            holder.append(int(box.text))
                            i += 1
                        else:
                            holder.append(int(box.text))
                            i = 0
                            grid.clues.append(holder)
                            holder = []
                    print(grid.clues)
                    # try:
                    #     grid.solution()
                    #     valid.text = "Possible"
                    #     grid.fill_in()
                    # except Exception as e:
                    #     print(e)
                    #     valid.text = "Not Possible"
                    grid.solution()
                    


                elif self.text == "Clear Board":
                    valid.text = ""
                    for box in grid.clue_boxes:
                        # print(box)
                        box.text = ""
                    for box in grid.input_boxes:
                        # print(box)
                        box.text = ""
 
class board:
    def __init__(self, size, start_x, start_y, clues):
        self.start = start_y
        self.size = size
        self.x = start_x
        self.y = start_y
        self.input_boxes = []
        self.clue_boxes = []
        self.answer = []
        self.clues = clues
        

        # self.solution()

    def setup_board(self, clues):
        holder = []
        i = 0 

        for col in range(self.size):
            self.x = 125
            for row in range(self.size):
                self.input_boxes.append(TextBox(self.x, self.y, 20, 32))
                self.x += 100
                if i == 0:
                    holder.append(self.x)
            self.y += 50
            i += 1
        
        self.width = max(holder) + 100        
        self.setup_clue_boxes(clues)
    
    def setup_clue_boxes(self, clues):


        # left 0
        # top 1
        # right 2
        # bottom 3

        # left
        left_clues_x = 40
        right_clues_x = self.width - 100
        holder = self.start
        for row in range(self.size):
            self.clue_boxes.append(InputBox(left_clues_x, self.start, 30, 32, ""))
            self.start += 50

        # top
        # top_clues_y = self.y - 280
        top_clues_y = holder - 75
        bottom_clues_y = self.y + 20
        x_offset = 125
        for col in range(self.size):
            self.clue_boxes.append(InputBox(x_offset, top_clues_y, 30, 32, ""))
            x_offset += 100

        # right
        left_clues_x = 40
        right_clues_x = self.width - 100
        self.start = holder
        for row in range(self.size):
            self.clue_boxes.append(InputBox(right_clues_x, self.start, 30, 32, ""))
            self.start += 50

        # bottom
        top_clues_y = self.y - 280
        # top_clues_y = holder - 280
        bottom_clues_y = self.y + 20
        x_offset = 125

        for col in range(self.size):
            self.clue_boxes.append(InputBox(x_offset, bottom_clues_y, 30, 32, ""))
            x_offset += 100
    
    def solution(self):
        global left_clues
        global right_clues
        global top_clues
        global bottom_clues
        global grid_length
        # left 0
        # top 1
        # right 2
        # bottom 3

        grid_length = self.size

        left_clues = self.clues[0]
        top_clues = self.clues[1]
        right_clues = self.clues[2]
        bottom_clues = self.clues[3]

        # print()

        cells, groupings, neighbors = create_groupings_and_neighbors(left_clues, right_clues, top_clues, bottom_clues)

        print(cells)

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
        print(sol.keys())

        i = 1
        holder = []
        for key in sol.keys():
            if i != 4:
                holder.append(list(sol[key])[0])
                i+=1
            else:

                holder.append(list(sol[key])[0])
                self.answer.append(holder)
                holder = []
                i = 1
        # self.answer.append(holder)
        print(self.answer)    

    def fill_in(self):
        i = 0
        j = 0
        for box in self.input_boxes:
            if j != 3:
                box.text = str(self.answer[i][j])
                j += 1
            else:
                box.text = str(self.answer[i][j])
                j = 0
                i += 1



start_x = 125
start_y = 100
grid_size = 5

# left 0
# top 1
# right 2
# left 3

clues = [
    [3,1,2,3],
    [2,3,1,2],
    [2,3,3,1],
    [3,2,2,1]
]


grid = board(grid_size, start_x, start_y, clues)
grid.setup_board(clues)

pygame.init()

# Screen dimensions
screen = pygame.display.set_mode((grid.width + 150, grid.y + 150))

font = pygame.font.Font(None, 32)

valid = TextBox(225, grid.y + 100, 150, 40,"")

clear_button = Button(50, grid.y + 100, 150, 40, "Clear Board")

solve_button = Button(400, grid.y + 100, 150, 40, "Solve")

new_grid_size = InputBox(615, grid.y - 125, 150, 40, "")

size_button = Button(615, grid.y - 50, 150, 40, "Create")


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for box in grid.clue_boxes:
            box.handle_event(event)
        # new_grid_size.handle_event(event)
        clear_button.handle_event(event)
        solve_button.handle_event(event)
        # size_button.handle_event(event)

    screen.fill((255, 255, 255))

    for box in grid.input_boxes:
        box.draw(screen)

    for clue in grid.clue_boxes:
        clue.draw(screen)

    valid.draw(screen)
    clear_button.draw(screen)
    solve_button.draw(screen)
    # size_button.draw(screen)
    # new_grid_size.draw(screen)

    pygame.display.flip()

pygame.quit()