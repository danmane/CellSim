from pdb import set_trace as debug
from random import random

# Warning: Nothing is done atm to ensure that the children are valid children, i.e. they haven't died...

"""Entry Point"""
def dna_grass(cell):
    """Entry point for the program. Automates cell behavior."""
    if getMem(cell, 'initialized') == 0:
        initialize(cell)
    clean_mem(cell)
    role = getMem(cell, 'role')
    if role == 0:
        print "Error: Cell has no role!"
        debug()
    elif role == 'stem':
        automate_stem(cell)
    elif role == 'root':
        automate_root(cell)
    elif role == 'leaf':
        automate_leaf(cell)
    elif role == 'store':
        automate_store(cell)
    elif role == 'origin':
        automate_origin(cell)
    elif role == 'bud':
        automate_bud(cell)
    manage_resource_flow(cell)
        
def initialize(cell):
    if 'growth_sugar' not in cell.memory:
        cell.memory['growth_sugar'] = cell.sugar_consumption * 20
    if 'growth_water' not in cell.memory:
        cell.memory['growth_water'] = cell.water_consumption * 20
    if 'sugar_children' not in cell.memory:
        cell.memory['sugar_children'] = []
    if 'water_children' not in cell.memory:
        cell.memory['water_children'] = []
    cell.memory['initialized'] = 1
    if 'demand' not in cell.memory:
        cell.memory['demand'] = ((0, 0), (0, 0))
        
def clean_mem(cell):
    for child in cell.memory['sugar_children']:
        if not child.alive:
            cell.memory['sugar_children'].remove(child)
    for child in cell.memory['water_children']:
        if not child.alive:
            cell.memory['water_children'].remove(child)

def automate_origin(cell):
    stem_mem = {'role': 'stem', 'unestablished': 1, 'growth_til_leaf': 2}
    root_mem = {'role': 'root', 'water_children': [cell], 'growth_dir': 'S', 'root_growth_limit': 1}
    cell.memory['root_growth_limit'] = 2
    new_stem = cell.divide('N', 300, 300, stem_mem)
    new_root = cell.divide('S', 250, 60, root_mem)
    cell.memory['growth_sugar'] = 0
    cell.memory['growth_water'] = 0
    add_sugar_child(cell, new_stem)
    add_water_child(cell, new_stem)
    add_sugar_child(cell, new_root)
    cell.memory['role'] = 'store'
    cell.memory['unestablished'] = 1
    initialize(new_stem)
    initialize(new_root)

def automate_stem(cell):
    if getMem(cell, 'unestablished') == 1:
        establish_stem(cell)
    else:
        if getMem(cell, 'growth_to_bud') == 0 and isEmpty(cell, 'N'):
            if cell.sugar > 40 and cell.water > 40:
                new_cell = cell.divide('N', cell.sugar - 30, cell.water - 30, {'role': 'bud'})
                initialize(new_cell)
                add_water_child(cell, new_cell)
                add_sugar_child(cell, new_cell)
                # Get rid of this sugar child once the bud has established itself
            else:
                cell.memory['growth_sugar'] = 40
                cell.memory['growth_water'] = 40
    
def automate_bud(cell):
    if getMem(cell.adjacent['S'], 'role') == 'stem':
        # Bud to the NW, NE, and revert to stem with budcounter
        if   isEmpty(cell, 'NW'): dir = 'NW'
        elif isEmpty(cell, 'NE'): dir = 'NE'
        elif isEmpty(cell, 'N' ): dir = 'N'
        else: 
            dir = 'X'
            debug()
        if dir in ('NW', 'NE'):
            if cell.sugar > 40 and cell.water > 40:
                new_mem = {'role': 'bud', 'growth_dir': dir, 'bud_growth_limit': 5}
                new_cell = cell.divide(dir, 10, 10, new_mem)
                initialize(new_cell)
                add_sugar_child(new_cell, cell)
                add_water_child(cell, new_cell)
            else:
                cell.memory['growth_sugar'] = 40
                cell.memory['growth_water'] = 40
        if dir == 'N':
            cell.memory['role'] = 'stem'
            cell.memory['growth_to_bud'] = 3
    else:
        growth_limit = getMem(cell, 'bud_growth_limit')
        growth_dir = getMem(cell, 'growth_dir')
        leafdir = 'X'
        for dir in outsideDirs(growth_dir):
            if isEmpty(cell, dir):
                leafdir = dir
        if leafdir != 'X':
            grow_leaf(cell, leafdir)
        elif isEmpty(cell, growth_dir) and growth_limit > 0 and can_grow(cell, 40, 40):
            new_mem = {'role': 'bud', 'growth_dir': growth_dir, 'bud_growth_limit': growth_limit - 1, 'sugar_children': [cell]}
            new_bud = cell.divide(growth_dir, 10, 10, new_mem)
            initialize(new_bud)
            add_water_child(cell, new_bud)
                
def can_grow(cell, sugar_req, water_req):
    if cell.sugar > sugar_req and cell.water>water_req:
        cell.memory['growth_sugar'] = 0
        cell.memory['growth_water'] = 0
        return True
    else:
        cell.memory['growth_sugar'] = sugar_req
        cell.memory['growth_water'] = water_req
        return False
                
def outsideDirs(dir):
    if dir in ('NW', 'SW'):
        return ['N', 'W', 'S']
    elif dir in ('NE', 'SE'):
        return ['N', 'E', 'S']
                
def grow_leaf(cell, dir):
    if cell.sugar >= 150 and cell.water >= 80:
        new_mem = {'role': 'leaf', 'growth_sugar': 110, 'growth_water': 50, 'sugar_children': [cell]}
        new_cell = cell.divide(dir, 120, 50, new_mem)
        add_water_child(cell, new_cell)
        initialize(new_cell)
        cell.memory['growth_sugar'] = 0
        cell.memory['growth_water'] = 0
    else:
        cell.memory['growth_sugar'] = 150
        cell.memory['growth_water'] = 80

def establish_stem(cell):
    if 'N' in cell.adjacent and getMem(cell.adjacent['N'], 'unestablished') == 0:
        cell.memory['unestablished'] = 0
        cell.memory['sugar_children'] = [cell.adjacent['S']]
        
    growth_til_leaf = getMem(cell, 'growth_til_leaf')
    if growth_til_leaf != 0:
        if isEmpty(cell, 'N'):
            if cell.sugar > 40 and cell.water > 40:
                new_mem = {'role': 'stem', 'unestablished': 1, 'growth_sugar': 200, 'growth_water': 200, 'growth_til_leaf': growth_til_leaf -1}
                new_cell = cell.divide('N', cell.sugar-30, cell.water-30, new_mem)
                add_sugar_child(cell, new_cell)
                add_water_child(cell, new_cell)
                initialize(new_cell)
                report(cell, 'Growing up!')
            else:
                report(cell, 'Not enough resources to grow up!')
            cell.memory['growth_sugar'] = 200
            cell.memory['growth_water'] = 200
        else:
            report(cell, 'Waiting for establishment.')
            cell.memory['growth_sugar'] = 0
            cell.memory['growth_water'] = 0
    else:
        if isEmpty(cell, 'NE'):
            if cell.sugar > 150 and cell.water > 80:
                new_mem = {'role': 'leaf', 'growth_sugar': 110, 'growth_water': 50, 'sugar_children': [cell]}
                new_cell = cell.divide('NE', 120, 50, new_mem)
                add_water_child(cell, new_cell)
                initialize(new_cell)
        else:
            if cell.sugar > 150 and cell.water > 80:
                new_mem = {'role': 'leaf', 'growth_sugar': 110, 'growth_water': 50, 'sugar_children': [cell]}
                new_cell = cell.divide('NW', 120, 50, new_mem)
                add_water_child(cell, new_cell)
                initialize(new_cell)
                cell.memory['unestablished'] = 0
                cell.memory['sugar_children'] = [cell.adjacent['S']]
                cell.memory['growth_to_bud'] = 0

def automate_store(cell):
    if getMem(cell, 'already_established') == 0 and not isEmpty(cell, 'N') and getMem(cell.adjacent['N'], 'unestablished') == 0:
        cell.memory['unestablished'] = 0
        cell.memory['sugar_children'] = [cell.adjacent['S']]
        cell.memory['root_growth_limit'] = 3
        cell.memory['already_established'] = 1
    
    if getMem(cell, 'unestablished') == 0:
        if isEmpty(cell, 'SE'): dir = 'SE'
        elif isEmpty(cell, 'SW'): dir = 'SW'
        else: dir = 'X'
        if dir != 'X':
            if cell.sugar > 150 and cell.water > 100:
                root_mem = {'role': 'root', 'water_children': [cell], 'growth_dir': dir, 'root_growth_limit': 5}
                new_root = cell.divide(dir, 110, 60, root_mem)
                add_sugar_child(cell, new_root)
                initialize(new_root)
            else:
                cell.memory['growth_sugar'] = 150
                cell.memory['growth_water'] = 100
        else:
            cell.memory['growth_sugar'] = 0
            cell.memory['growth_water'] = 0
        if random() < .02:
            cell.memory['root_growth_limit'] += 1
        
        
def automate_root(cell):
    if cell.type == 'GENERIC':
        if cell.sugar > 110:
            cell.specialize('ROOT')
        else:
            cell.memory['growth_sugar'] = 110
    else:
        dir = cell.memory['growth_dir']
        if oppDir(dir) in cell.adjacent:
            parent_root = cell.adjacent[oppDir(dir)]
            growth_remaining = parent_root.memory['root_growth_limit'] - 1
        else:
            growth_remaining = 0
        cell.memory['root_growth_limit'] = growth_remaining
        if isEmpty(cell, dir) and growth_remaining > 0:
            if cell.sugar > 140 and cell.water >= 30:
                new_mem = {'role': 'root', 'water_children': [cell], 'root_growth_limit': growth_remaining - 1, 'growth_dir': dir}
                new_cell = cell.divide(dir, 110, 10, new_mem)
                initialize(new_cell)
                add_sugar_child(cell, new_cell)
            else:
                cell.memory['growth_sugar'] = 140
                cell.memory['growth_water'] = 30
        else:
            cell.memory['growth_sugar'] = 0
            cell.memory['growth_water'] = 0

    
def automate_leaf(cell):
    if cell.type != 'PHOTO' and cell.sugar > 110 and cell.water > 40:
        cell.specialize('PHOTO')
    
    if cell.type == 'PHOTO':
        cell.memory['growth_sugar'] = 0
        cell.memory['growth_water'] = 100
        # Good to keep a substantial reserve of water, if you are a leaf.

"""Resource flow functions"""

def manage_resource_flow(cell):
    """Manages resource flow from a cell. If sugar children or water children need resources, they will be sent; high priority first, low priority after. If no resources are needed, but the cell has more than it needs, it evenly distributes its excess resources to neighboring cells.
    
    Presently no adjustment is made for a situation where one cell has multiple parents (i.e. violation of tree structure)
    """

    min_sugar = cell.sugar_consumption * 10
    free_sugar = cell.sugar - min_sugar
    
    min_water = cell.water_consumption * 10
    free_water = cell.water - min_water
    
    if cell.type == 'PHOTO':
        photo_water = cell.light * cell.free_spaces * cell.photo_factor
        if free_water >= photo_water:
            cell.photosynthesize()
        free_water -= 2 * photo_water
    
    children_sugar_demand, children_water_demand = get_children_demand(cell)

    growth_sugar = getMem(cell, 'growth_sugar') + 1 
    growth_water = getMem(cell, 'growth_water') + 1 
    # +1 deals with some issue (related to floats I think) that caused cell.sugar or water to approach growth_sugar but not reach it, preventing conditions from triggering

    if free_sugar < children_sugar_demand[0]:
    # Triggers if free sugar is less than the net high_sugar_demand
        report(cell, 'Insufficient free sugar for high demand')
        if free_sugar > 0:
            distribute(cell, free_sugar, 'sugar', 'high')
        high_sugar_demand = children_sugar_demand[0] - free_sugar
        # Reports a higher demand than sum of adj demands if free sugar is less than zero, a lower one if free sugar is greater than zero
        free_sugar = 0
        
    elif free_sugar >= children_sugar_demand[0]:
    # Triggers if there's enough free sugar to satisfy everyone's pressing needs
        report(cell, 'Sufficient sugar for high demand')
        distribute(cell, children_sugar_demand[0], 'sugar', 'high')
        high_sugar_demand = 0
        free_sugar -= children_sugar_demand[0]
    
    free_sugar -= growth_sugar
    # Now that we are switching to low demand, the cell's free sugar has to take into account its own growth requirements.
    
    low_sugar_demand = max(children_sugar_demand[1] - free_sugar, 0)
    # As before, free sugar might be negative (in which case low_sugar_demand goes higher than children's demand) or positive (vice versa)
    
    if free_sugar > 0:
        amt_to_send = min(children_sugar_demand[1], free_sugar)
        distribute(cell, amt_to_send, 'sugar', 'low')
        free_sugar -= amt_to_send
    
        if free_sugar > 0: #There is free sugar leftover after satisfying low and high demand!
            distribute(cell, free_sugar, 'sugar', 'even')

    if free_water < children_water_demand[0]:
    # Triggers if free water is less than the net high_water_demand
        if free_water > 0:
            distribute(cell, free_water, 'water', 'high')
        high_water_demand = children_water_demand[0] - free_water
        # Reports a higher demand than sum of adj demands if free water is less than zero, a lower one if free water is greater than zero
        free_water = 0
        
    elif free_water >= children_water_demand[0]:
    # Triggers if there's enough free water to satisfy everyone's pressing needs
        distribute(cell, children_water_demand[0], 'water', 'high')
        high_water_demand = 0
        free_water -= children_water_demand[0]
      
    free_water -= growth_water
    
    low_water_demand = max(children_water_demand[1] - free_water, 0)
    
    if free_water > 0:
        amt_to_send = min(children_water_demand[1], free_water)
        distribute(cell, amt_to_send, 'water', 'low')
        free_water -= amt_to_send
    
        if free_water > 0: #There is free water leftover after satisfying low and high demand!
            distribute(cell, free_water, 'water', 'even')
        
    cell.memory['demand'] = ( (high_sugar_demand, low_sugar_demand), (high_water_demand, low_water_demand) )
        

def get_children_demand(cell):
    """Returns how much resources are demanded by the cell's children"""
    high_sugar_demand = 0
    low_sugar_demand  = 0
    high_water_demand = 0
    low_water_demand  = 0
    
    if getMem(cell, 'sugar_children') != 0:
        # getMem returns 0 if the cell has no such record in memory. Since cell initialization adds an empty list for children if none is found, this should never happen
        for sugar_child in getMem(cell, 'sugar_children'):
            child_demand = getMem(sugar_child, 'demand')
            high_sugar_demand += child_demand[0][0]
            low_sugar_demand  += child_demand[0][1]
            
    if getMem(cell, 'water_children') != 0:
        for water_child in getMem(cell, 'water_children'):
            child_demand = getMem(water_child, 'demand')
            high_water_demand += child_demand[1][0]
            low_water_demand  += child_demand[1][1]             
    
    return ((high_sugar_demand, low_sugar_demand), 
            (high_water_demand, low_water_demand))

def distribute(cell, amount, resource, pattern):
    """Automates distribution of resource (given amount) to adjacent cells according to pattern
    
    cell: A cell
    amount: A float
    resource: 'sugar' or 'water'
    pattern: 'high' distributes according to high demand profile for given resource, 'low' according to the low demand profile, 'even' gives equally to each adjacent cell
    """

    report(cell, 'Distributing {0} {1} in pattern {2}'.format(amount, resource, pattern))
    
    index1 = int(resource == 'water')
    if pattern in ('high', 'low'):
        index2 = int(pattern == 'low')
        demand = get_children_demand(cell)[index1][index2]
        if demand == 0:
            distribution_factor = 1
        else:
            distribution_factor = float(amount) / demand
        # The proportion of amount demanded to give to each adjacent cell
        
        if resource == 'sugar' and getMem(cell, 'sugar_children') != 0:
            for sugar_child in getMem(cell, 'sugar_children'):
                amt_to_send = getMem(sugar_child, 'demand')[index1][index2] * distribution_factor
                xferToTarget(cell, sugar_child, amt_to_send, resource)
        elif resource == 'water' and getMem(cell, 'water_children') != 0:
                for water_child in getMem(cell, 'water_children'):
                    amt_to_send = getMem(water_child, 'demand')[index1][index2] * distribution_factor
                    xferToTarget(cell, water_child, amt_to_send, resource)
    else:
        if pattern != 'even':
            debug()
        num_adjacent_cells = 9 - cell.free_spaces
        # Used 9 as starting number so that the cell will always keep a portion for itself!
        amt_to_send = float(amount) / num_adjacent_cells
        
        for dir in cell.adjacent.iterkeys():
            xferResource(cell, dir, amt_to_send, resource)
                
def xferToTarget(cell, target, amount, resource):
    target_dir = 'X'
    for dir, child in cell.adjacent.iteritems():
        if child == target:
            target_dir = dir
            break
    if target_dir == 'X':
    # Tried to transfer to a non-adjacent target
        debug()
    else:
        xferResource(cell, target_dir, amount, resource)

def xferResource(cell, dir, amount, resource):
    if resource == 'sugar':
        cell.transfer(dir, amount, 0)
    else:
        cell.transfer(dir, 0, amount)
        
def add_sugar_child(cell, child):
    """Note: Takes the direction the child is in, not the direction the parent is in"""
    if 'sugar_children' not in cell.memory:
        cell.memory['sugar_children'] = []
    cell.memory['sugar_children'].append(child)
    
def add_water_child(cell, child):
    """Note: Takes the direction the child is in, not the direction the parent is in"""
    if 'water_children' not in cell.memory:
        cell.memory['water_children'] = []  
    cell.memory['water_children'].append(child)


"""General functions"""

def isEmpty(cell, dir):
    """Reports if cell's adjacent space is empty (True) or filled (false)"""
    if dir in cell.adjacent:
        return False
    else:
        return True

def getMem(cell, arg):
    if arg in cell.memory:
        return cell.memory[arg]
    else:
        print "Cell " + str(cell) + " attempted to access non-existant memory " + arg
        return 0
        
def adjAttr(cell, dir, attr):
    if dir in cell.adjacent:
        return cell.adjacent[dir].__dict__(attr)
    else:
        return 0

def oppDir(dir):
    directions     = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    opp_directions = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
    return opp_directions[directions.index(dir)]

def report(cell, message):
    """Put a message in the debug message list"""
    cell.debug.append(message)