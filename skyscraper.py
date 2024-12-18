import pygame
import copy
import time
import math
import itertools
counter = 0

# Brute Force Algorithm
def is_valid_view(row, view):
    max_height = 0
    visible = 0
    for height in row:
        if height > max_height:
            visible += 1
            max_height = height
    return visible == view

def is_valid_solution(grid, top, bottom, left, right):
    n = len(grid)
    for i in range(n):
        if top[i] > 0 and not is_valid_view(grid[i], top[i]):
            return False
        if bottom[i] > 0 and not is_valid_view(grid[i][::-1], bottom[i]):
            return False
        column = [grid[j][i] for j in range(n)]
        if left[i] > 0 and not is_valid_view(column, left[i]):
            return False
        if right[i] > 0 and not is_valid_view(column[::-1], right[i]):
            return False
    return True

def solve_skyscraper(n, top, bottom, left, right):
    all_permutations = list(itertools.permutations(range(1, n+1)))
    global counter
    counter = 0
    for grid in itertools.product(all_permutations, repeat=n):
        counter += 1
        if counter > 100000:
           backtrack_states.text = "BF: 100,000+"
           break
        # print(f"\r{counter}", end="", flush=True)
        # time.sleep(0.0002)  # Uncommenting will add a small delay for visibility
        if is_valid_solution(grid, top, bottom, left, right):
            return grid
    
    return None

def print_solution(solution):
    if solution:
        # Transpose the grid
        transposed = list(zip(*solution))
        # for row in transposed:
            # print(' '.join(map(str, row)))
    else:
        print("No solution found")


# Constraint Propagation Algorithm
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

  if possible_value in grid[cell] and len(grid[cell]) == 1:
    for val in grid[cell]:
      for neighbor in neighbors[cell]:
        if not remove_value(grid, neighbor, val):
          return None
    return grid

  if possible_value in grid[cell]:

      for value in grid[cell].copy():
        if value != possible_value:
          if not remove_value(grid, cell, value):
            return None

      return grid
  return None

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

def search(grid, states):

  if grid is None:
    return None, False, states

  states += 1
  cell = min((c for c in cells if len(grid[c]) > 1), default = None, key= lambda c: len(grid[c]))
  if cell is None:
    return grid, clues_check(grid), states

  for possible_value in grid[cell].copy():

    grid_copy = copy.deepcopy(grid)
    # Inference rules are applied in the assign function to narrow down possible cell values
    assigned_grid = assign(grid_copy, cell, possible_value)
    temp_grid, valid_clues_check, states = search(assigned_grid, states)

    # If the grid is not None and passed clue check, then a solution is found
    if temp_grid is not None and valid_clues_check:
      return temp_grid, valid_clues_check, states

  return None, False, states

def verify_solution(grid, left_clues, right_clues, top_clues, bottom_clues):

  grid_length = int(math.sqrt(len(grid)))

  rows = [chr(ord('@')+number) for number in range(1, grid_length + 1)]
  columns = [str(number) for number in range(1, grid_length + 1)]

  row_ordered_cells = tuple(letter + digit for letter in rows for digit in columns)
  column_ordered_cells = tuple(letter + digit for digit in columns for letter in rows)

  for cell in row_ordered_cells:
    if len(grid[cell]) != 1:
      return False

  if clues_check(grid):

    for i in range(grid_length):
      row = row_ordered_cells[i*grid_length: (i*grid_length) + grid_length]
      s = set()
      for cell in row:
        if str(grid[cell]) in s:
          return False
        s.add(str(grid[cell]))

      column = column_ordered_cells[i*grid_length: (i*grid_length) + grid_length]
      s = set()
      for cell in column:
        if str(grid[cell]) in s:
          return False
        s.add(str(grid[cell]))

    return True

  return False

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
    def __init__(self, x, y, width, height, text, max_value=9, increment_on_click=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color('blue')
        self.text = text
        self.max_value = max_value
        self.increment_on_click = increment_on_click

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        txt_surface = font.render(self.text, True, pygame.Color('white'))
        screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
          if self.increment_on_click:
                current_value = int(self.text)
                current_value = (current_value + 1) % (self.max_value + 1)
                self.text = str(current_value)
          else:
                if self.text == "Solve":
                    global state_counter

                    valid.text = ""
    
                    for box in grid2.input_boxes:
                        box.text = ""
                    grid2.clues = []
                    holder = []
                    grid2.answer = []

                    i = 0
                    
                    for box in grid2.clue_boxes:
                        if i != grid2.size - 1:
                            holder.append(int('0' if box.text == '' else box.text))
                            i += 1
                        else:
                            holder.append(int('0' if box.text == '' else box.text))
                            i = 0
                            grid2.clues.append(holder)
                            holder = []

                    try:
                        state_counter = 0
                        grid2.solution()
                        valid.text = "Possible"
                        grid2.fill_in()
                    except Exception as e:
                        valid.text = "Not Possible"
                    
                      
                    try:
                      solution = solve_skyscraper(grid2.size, top_clues, bottom_clues, left_clues, right_clues)

                      if counter < 100000:
                         backtrack_states.text = f"BF: {counter}"
                      
                    except Exception as e:
                       print(e)

                elif self.text == "Clear Board":
                    valid.text = ""
                    for box in grid2.clue_boxes:
                        box.text = "0"
                    for box in grid2.input_boxes:
                        box.text = ""
                    runtime.text = "Runtime: "
                    backtrack_states.text = "BF: "
                    num_states.text = "CP: "
                
                elif  self.text == "Create":
                    runtime.text = "Runtime: "
                    valid.text = ""
                    backtrack_states.text = "BF: "
                    num_states.text = "CP: "
                    
                    new_size = int(new_grid_size.text) if new_grid_size.text.isdigit() else 4  
                    grid2.__init__(new_size, start_x, start_y, [[0] * new_size] * 4)  
                    grid2.setup_board(grid2.clues)  
                    # print(f"Grid resized to: {new_size}x{new_size}")

                    new_width = grid2.width + 200
                    new_height = grid2.y + 200

                    global screen  
                    screen = pygame.display.set_mode((new_width, new_height))

                    # print(f"Screen resized to: {new_width}x{new_height}")
                    clear_button.rect.topleft = (50, new_height - 50)
                    valid.rect.topleft = (225, new_height - 50)
                    
                    solve_button.rect.topleft = (400, new_height - 50)

                    num_states.rect.topleft = (new_width - 150, (new_height/2) - 100)

                    backtrack_states.rect.topleft = (new_width - 150, (new_height/2) - 150)

                    runtime.rect.topleft = (new_width - 220, (new_height/2) - 200)

                    decrease_btn.rect.topleft = (new_width - 150, (new_height/2) - 50)
                    new_grid_size.rect.topleft = (new_width - 100, (new_height/2) - 50)
                    increase_btn.rect.topleft = (new_width - 50, (new_height/2) - 50)

                    size_button.rect.topleft = (new_width - 150, new_height/2)

                elif self.text == "+":
                  current_value = int(new_grid_size.text)
                  current_value = (current_value + 1)
                  new_grid_size.text = str(current_value)
                
                elif self.text == "-":
                  current_value = int(new_grid_size.text)
                  current_value = (current_value - 1)
                  new_grid_size.text = str(current_value)
 
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
            self.clue_boxes.append(Button(left_clues_x, self.start, 30, 32, "0", grid2.size, True))
            self.start += 50

        # top
        # top_clues_y = self.y - 280
        top_clues_y = holder - 75
        bottom_clues_y = self.y + 20
        x_offset = 125
        for col in range(self.size):
            self.clue_boxes.append(Button(x_offset, top_clues_y, 30, 32, "0", grid2.size, True))
            x_offset += 100

        # right
        left_clues_x = 40
        right_clues_x = self.width - 100
        self.start = holder
        for row in range(self.size):
            self.clue_boxes.append(Button(right_clues_x, self.start, 30, 32, "0",grid2.size, True))
            self.start += 50

        # bottom
        top_clues_y = self.y - 280
        # top_clues_y = holder - 280
        bottom_clues_y = self.y + 20
        x_offset = 125

        for col in range(self.size):
            self.clue_boxes.append(Button(x_offset, bottom_clues_y, 30, 32, "0", grid2.size, True))
            x_offset += 100
    
    def solution(self):
        global left_clues
        global right_clues
        global top_clues
        global bottom_clues
        global grid_length
        global left_clues
        global right_clues
        global top_clues
        global bottom_clues
        global grid_length
        global cells, groupings, neighbors
        global grid
        global cells
        global grid_seq
        global sol
        global states
        global rows
        global columns
        global start
        global end
        global valid_clues_check

        # left 0
        # top 1
        # right 2
        # bottom 3

        grid_length = self.size

        left_clues = self.clues[0]
        top_clues = self.clues[1]
        right_clues = self.clues[2]
        bottom_clues = self.clues[3]

        rows = [chr(ord('@')+number) for number in range(1, grid_length + 1)]

        columns = [str(number) for number in range(1, grid_length+1)]

        cells = tuple(letter + digit for letter in rows for digit in columns)

        groupings = {c: tuple([[c[0] + digit for digit in columns],[letter + c[1] for letter in rows]])  for c in cells}

        neighbors = {c: set(tuple([c[0] + digit for digit in columns] + [letter + c[1] for letter in rows])) for c in cells}

        for cell in cells:
          neighbors[cell].remove(cell)

        grid = initialize_grid(grid_length, cells, left_clues, right_clues, top_clues, bottom_clues)
        states = 0
        start = time.time()
        sol, valid_clues_check, states = search(grid, states)
        end = time.time()
        print(f"Time(seconds): {end - start}")
        runtime.text = f"Runtime: {(end-start):.4f} sec"
        # print(verify_solution(sol, left_clues, right_clues, top_clues, bottom_clues))
        print("States explored:", states)
        # print(sol)

        num_states.text = f"CP: {states}"

        i = 1
        holder = []
        for key in sol.keys():
            if i != self.size:
                holder.append(list(sol[key])[0])
                i+=1
            else:

                holder.append(list(sol[key])[0])
                self.answer.append(holder)
                holder = []
                i = 1  

    def fill_in(self):
        i = 0
        j = 0
        for box in self.input_boxes:
            if j != grid2.size - 1:
                box.text = str(self.answer[i][j])
                j += 1
            else:
                box.text = str(self.answer[i][j])
                j = 0
                i += 1

left_clues = [2,2,1,4,4]
right_clues = [4,3,3,2,1]
top_clues = [3,1,2,3,5]
bottom_clues = [2,3,3,2,1]

grid_length = len(left_clues)


rows = [chr(ord('@')+number) for number in range(1, grid_length + 1)]

columns = [str(number) for number in range(1, grid_length+1)]

cells = tuple(letter + digit for letter in rows for digit in columns)

groupings = {c: tuple([[c[0] + digit for digit in columns],[letter + c[1] for letter in rows]])  for c in cells}

neighbors = {c: set(tuple([c[0] + digit for digit in columns] + [letter + c[1] for letter in rows])) for c in cells}

for cell in cells:
  neighbors[cell].remove(cell)

grid = initialize_grid(grid_length, cells, left_clues, right_clues, top_clues, bottom_clues)
states = 0
start = time.time()
sol, valid_clues_check, states = search(grid, states)
end = time.time()

start_x = 125
start_y = 100
grid_size = 5
state_counter = 0

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


grid2 = board(grid_size, start_x, start_y, clues)
grid2.setup_board(clues)

pygame.init()

# Screen dimensions
screen = pygame.display.set_mode((grid2.width + 150, grid2.y + 150))

font = pygame.font.Font(None, 32)

clear_button = Button(50, grid2.y + 100, 150, 40, "Clear Board", False)

valid = TextBox(225, grid2.y + 100, 150, 40,"")

backtrack_states = TextBox(grid2.width, grid2.y - 240, 150, 40, "BF: ")

num_states = TextBox(grid2.width, grid2.y - 180, 150, 40, "CP: ")

runtime = TextBox(grid2.width - 80, grid2.y - 300, 220, 40, "Runtime: ")

solve_button = Button(415, grid2.y + 100, 150, 40, "Solve", False)

decrease_btn = Button(grid2.width, grid2.y - 125, 50, 40, "-", False)

new_grid_size = InputBox(grid2.width + 50, grid2.y - 125, 150, 40, f"{grid_length}")

increase_btn = Button(grid2.width + 150 - 50, grid2.y - 125, 50, 40, "+", False)

size_button = Button(grid2.width, grid2.y - 50, 150, 40, "Create", False)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for box in grid2.clue_boxes:
            box.handle_event(event)
        new_grid_size.handle_event(event)
        clear_button.handle_event(event)
        solve_button.handle_event(event)
        size_button.handle_event(event)
        decrease_btn.handle_event(event)
        increase_btn.handle_event(event)

    screen.fill((255, 255, 255))

    for box in grid2.input_boxes:
        box.draw(screen)

    for clue in grid2.clue_boxes:
        clue.draw(screen)

    runtime.draw(screen)
    num_states.draw(screen)
    valid.draw(screen)
    clear_button.draw(screen)
    solve_button.draw(screen)
    size_button.draw(screen)
    new_grid_size.draw(screen)
    decrease_btn.draw(screen)
    increase_btn.draw(screen)
    backtrack_states.draw(screen)

    pygame.display.flip()

pygame.quit()