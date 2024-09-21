
class LabyrinthError(Exception):
    def __init__(self, message):
        self.message = message


class Labyrinth:
    def __init__(self, filename):
        
        # get the labyrinth content as an matrix
        labyrinth = []
        with open(filename, 'r') as file:
            file_content = file.read()
        rows = file_content.strip().split('\n')
        for row in rows:
            row_data = [ele for ele in row if ele != " "]
            if row_data != []:
                labyrinth.append(row_data)
        
        # check incorrect input
        x, y = len(labyrinth), len(labyrinth[0])
        for i in range(x):              # two lines do not contain same number of digits
            if y == len(labyrinth[i]):
                continue
            else:
                raise LabyrinthError('Incorrect input.')
        if x < 2 or y < 2 or x > 41 or y > 31:       # too big or too small
            raise LabyrinthError('Incorrect input.')
        for i in range(x):                 # contain other digits
            for j in range(y):
                if labyrinth[i][j] not in {'0', '1', '2', '3'}:
                    raise LabyrinthError('Incorrect input.')
        
        # check valid labyrinth representation
        for i in range(x):
            if labyrinth[i][-1] in {'1', '3'}:
                raise LabyrinthError('Input does not represent a labyrinth.')
        for j in range(y):
            if labyrinth[-1][j] in {'2', '3'}:
                raise LabyrinthError('Input does not represent a labyrinth.')
           
        # extend the labyrinth
        self.ext_labyrinth = [[0]*(2*y) for _ in range(2*x)]
        for i in range(x):
            for j in range(y):
                self.ext_labyrinth[2*i][2*j] = 1
                match labyrinth[i][j]:
                    case '1':
                        self.ext_labyrinth[2*i][2*j + 1] = 1
                    case '2':
                        self.ext_labyrinth[2*i + 1][2*j] = 1
                    case '3':
                        self.ext_labyrinth[2*i][2*j + 1] = 1
                        self.ext_labyrinth[2*i + 1][2*j] = 1
        self.ext_labyrinth = self.ext_labyrinth[:-1]          # delete the last row
        self.ext_labyrinth = [row[:-1] for row in self.ext_labyrinth]   # delete the last column 
        x, y = len(self.ext_labyrinth), len(self.ext_labyrinth[0]) # reassign x and y to be the size of extended labyrinth
        
        # count the gates
        self.number_of_gates = 0
        self.position_of_gates = []
        for i in range(y):
            if self.ext_labyrinth[0][i] == 0:
                self.number_of_gates += 1
                self.position_of_gates.append((0,i))
            if self.ext_labyrinth[-1][i] == 0:
                self.number_of_gates += 1
                self.position_of_gates.append((x-1,i))
        for i in range(1, x-1):
            if self.ext_labyrinth[i][0] == 0:
                self.number_of_gates += 1
                self.position_of_gates.append((i,0))
            if self.ext_labyrinth[i][-1] == 0:
                self.number_of_gates += 1
                self.position_of_gates.append((i,y-1))
        
        # the dfs search function for components
        def dfsComponents(matrix, i, j, id):
            matrix[i][j] = id
            if 0 <= i-1 <len(matrix):
                if matrix[i-1][j] == -1:
                    dfsComponents(matrix, i-1, j, id)
            if 0 <= i+1 <len(matrix):
                if matrix[i+1][j] == -1:
                    dfsComponents(matrix, i+1, j, id)
            if 0 <= j-1 <len(matrix[0]):
                if matrix[i][j-1] == -1:
                    dfsComponents(matrix, i, j-1, id)
            if 0 <= j+1 <len(matrix[0]):
                if matrix[i][j+1] == -1:
                    dfsComponents(matrix, i, j+1, id)
        
        #count the sets of walls
        sow_matrix = [[0 for _ in range(y)] for _ in range(x)]   #sow_matrix: sets of walls matrix
        for i in range(x):
            for j in range(y):
                if self.ext_labyrinth[i][j] == 0:
                    sow_matrix[i][j] = -2
                else:
                    sow_matrix[i][j] = -1
        self.number_of_sets_of_walls = 0
        for i in range(x):
            for j in range(y):
                if sow_matrix[i][j] == -1:
                    dfsComponents(sow_matrix, i, j, self.number_of_sets_of_walls)
                    self.number_of_sets_of_walls += 1
        #self.number_of_sets_of_walls also contains pillars
        
        #compute the number and position of pillars
        self.pillars = 0
        for i in range(x):
            for j in range(y):
                dead_end_conut = 0
                if self.ext_labyrinth[i][j] == 1:
                    if 0 <= i-1:
                        if self.ext_labyrinth[i-1][j] == 0:
                            dead_end_conut += 1
                    else: dead_end_conut += 1
                    if i+1 < x:
                        if self.ext_labyrinth[i+1][j] == 0:
                            dead_end_conut += 1
                    else: dead_end_conut += 1
                    if 0 <= j-1:
                        if self.ext_labyrinth[i][j-1] == 0:
                            dead_end_conut += 1
                    else: dead_end_conut += 1
                    if j+1 < y:
                        if self.ext_labyrinth[i][j+1] == 0:
                            dead_end_conut += 1
                    else: dead_end_conut += 1
                    if dead_end_conut == 4:
                        self.pillars +=1
        
        #get the correct result for self.number_of_sets_of_walls
        self.number_of_sets_of_walls = self.number_of_sets_of_walls - self.pillars
        
        #compute accessible areas
        access_matrix = [row[:] for row in self.ext_labyrinth]
        for i in range(x):
            for j in range(y):
                if self.ext_labyrinth[i][j] == 0:
                    access_matrix[i][j] = -1
                else:
                    access_matrix[i][j] = -2
        self.accessible_areas = 0
        for (i, j) in self.position_of_gates:
            if access_matrix[i][j] == -1:
                    dfsComponents(access_matrix, i, j, self.accessible_areas)
                    self.accessible_areas += 1
        #and inaccessible inner point
        self.inaccessible_points = 0
        for i in range(x):
            for j in range(y):
                if access_matrix[i][j] == -1:
                    self.ext_labyrinth[i][j] = -9   #to prevent further mistakes
                    if i%2 == 1 and j%2 == 1:
                        self.inaccessible_points += 1
        
        #the function to check dead ends(three walls)
        def dead_end(matrix, i, j, id):
            if matrix[i][j] != id:
                return False
            dead_end_conut = 0
            if 0 <= i-1 and matrix[i-1][j] != id:
                dead_end_conut += 1
            if i+1 < x and matrix[i+1][j] != id:
                dead_end_conut += 1
            if 0 <= j-1 and matrix[i][j-1] != id:
                dead_end_conut += 1
            if j+1 < y and matrix[i][j+1] != id:
                dead_end_conut += 1
            if dead_end_conut == 3:
                return True
            else: return False
             
        #for cul-de-sacs
        cds_matrix = [row[:] for row in self.ext_labyrinth]
        deadends = []
        for i in range(x):
            for j in range(y):
                if dead_end(cds_matrix, i, j, 0): #if the point is a dead end
                    deadends.append((i,j))
        
        for (i,j) in deadends:
            while dead_end(cds_matrix, i, j, 0):
                cds_matrix[i][j] = -1
                if 0 <= i-1 and cds_matrix[i-1][j] == 0:
                    i = i-1
                    continue
                if i+1 < x and cds_matrix[i+1][j] == 0:
                    i = i+1
                    continue
                if 0 <= j-1 and cds_matrix[i][j-1] == 0:
                    j = j-1
                    continue
                if j+1 < y and cds_matrix[i][j+1] == 0:
                    j = j+1
                    continue              
        
        self.number_of_cds = 2
        for i in range(x):
            for j in range(y):
                if cds_matrix[i][j] == -1:
                    dfsComponents(cds_matrix, i, j, self.number_of_cds)
                    self.number_of_cds += 1
        self.number_of_cds -= 2
        
        #the function to check path
        def have_path(matrix, i, j):
            if matrix[i][j] != 0:
                return False
            dead_end_conut = 0
            if i-1 >= 0:
                if matrix[i-1][j] != 0:
                    dead_end_conut += 1
            else: dead_end_conut += 1
            if i+1 < x:
                if matrix[i+1][j] != 0:
                    dead_end_conut += 1
            else: dead_end_conut += 1
            if j-1 >= 0:
                if matrix[i][j-1] != 0:
                    dead_end_conut += 1
            else: dead_end_conut += 1
            if j+1 < y:
                if matrix[i][j+1] != 0:
                    dead_end_conut += 1
            else: dead_end_conut += 1
            if dead_end_conut == 3:
                return True
            else: return False
        
        #finally for entry-exit paths
        path_matrix =  [[0 for _ in range(y)] for _ in range(x)]
        for i in range(x):
            for j in range(y):
                if cds_matrix[i][j] != 0:
                    path_matrix[i][j] = 1   
        #find gates for labyrinth without cul-de-sacs
        new_gates = 0
        entry = []
        for i in range(y):
            if path_matrix[0][i] == 0:
                new_gates += 1
                entry.append((0,i))
            if path_matrix[-1][i] == 0:
                new_gates += 1
                entry.append((x-1,i))
        for i in range(1, x-1):
            if path_matrix[i][0] == 0:
                new_gates += 1
                entry.append((i,0))
            if path_matrix[i][-1] == 0:
                new_gates += 1
                entry.append((i,y-1))
        #begin search for path
        self.number_of_paths = 0
        visited = []
        path_id = 2
        for (i, j) in entry:
            if (i,j) in visited:
                continue
            visited.append((i,j))
            curr_path = []
            while(have_path(path_matrix, i, j)):
                path_matrix[i][j] = path_id
                curr_path.append((i, j))
                if 0 <= i-1 and path_matrix[i-1][j] == 0:
                    i = i-1
                    continue
                if i+1 < x and path_matrix[i+1][j] == 0:
                    i = i+1
                    continue
                if 0 <= j-1 and path_matrix[i][j-1] == 0:
                    j = j-1
                    continue
                if j+1 < y and path_matrix[i][j+1] == 0:
                    j = j+1
                    continue
            #the search ends
            if (i, j) in self.position_of_gates:
                path_matrix[i][j] = path_id
                self.number_of_paths += 1
                visited.append((i,j))
            else:
                for (i, j) in curr_path:
                    path_matrix[i][j] = 0
            path_id += 1
             
            
    def display_features(self):
        if self.number_of_gates == 0:
            print("The labyrinth has no gate.")
        elif self.number_of_gates == 1:
            print("The labyrinth has a single gate.")
        else:
            print("The labyrinth has", self.number_of_gates, "gates.")
        
        if self.number_of_sets_of_walls == 0:
            print("The labyrinth has no wall.")
        elif self.number_of_sets_of_walls == 1:
            print("The labyrinth has walls that are all connected.")
        else:
            print("The labyrinth has", self.number_of_sets_of_walls, "sets of walls that are all connected.")
        
        if self.inaccessible_points == 0:
            print('The labyrinth has no inaccessible inner point.')
        elif self.inaccessible_points == 1:
            print('The labyrinth has a unique inaccessible inner point.')
        else:
            print('The labyrinth has', self.inaccessible_points, 'inaccessible inner points.')
            
        if self.accessible_areas == 0:
            print('The labyrinth has no accessible area.')
        elif self.accessible_areas == 1:
            print('The labyrinth has a unique accessible area.')
        else:
            print('The labyrinth has', self.accessible_areas, 'accessible areas.')
            
        if self.number_of_cds == 0:
            print('The labyrinth has no accessible cul-de-sac.')
        elif self.number_of_cds == 1:
            print('The labyrinth has accessible cul-de-sacs that are all connected.')
        else:
            print('The labyrinth has', self.number_of_cds, 'sets of accessible cul-de-sacs that are all connected.')
        
        if self.number_of_paths == 0:
            print('The labyrinth has no entry-exit path with no intersection not to cul-de-sacs.')
        elif self.number_of_paths == 1:
            print('The labyrinth has a unique entry-exit path with no intersection not to cul-de-sacs.')
        else:
            print('The labyrinth has', self.number_of_paths, 'entry-exit paths with no intersections not to cul-de-sacs.')
    
