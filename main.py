import pygame as pg
import sys
import math
import numpy
import pandas as pd

def random_color():
    return pg.Color(numpy.random.randint(100,200),
                        numpy.random.randint(100,200),
                        0)
    
def clamp (val,minv,maxv):
    return (max(min(val,maxv),minv))

pg.init()

SCREEN_SIZE = 1000
GRID_SIZE = 100
MUTATION_CHANCE = 0.05
MEDICINE_DELAY = 5

WHITE = pg.Color(255,255,255)
BLACK = pg.Color(0,0,0)
CYAN = pg.Color(0, 255, 255)

screen = pg.display.set_mode((SCREEN_SIZE,SCREEN_SIZE),0)
FPS = pg.time.Clock()

diseases = []

diseased_population = [0]
cured_population = [0]

class CellSprite(pg.sprite.Sprite):
    BORDER_WIDTH = 1
    CELL_WIDTH = 800//GRID_SIZE
    
    def __init__(self,pos,group=None):
        super().__init__()
        
        self.image = pg.Surface((self.CELL_WIDTH,self.CELL_WIDTH))
        self.image.fill(BLACK)
        self.cell = pg.Surface((self.CELL_WIDTH - 2*self.BORDER_WIDTH,self.CELL_WIDTH - 2*self.BORDER_WIDTH))
        self.cell.fill(WHITE)
        self.image.blit(self.cell,(self.BORDER_WIDTH,self.BORDER_WIDTH)) 
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.add(group)
        
        # self.font = pg.font.SysFont("Arial", 10)
    
    def change_color(self,new_color):
        self.cell = pg.Surface((self.CELL_WIDTH - 2*self.BORDER_WIDTH,self.CELL_WIDTH - 2*self.BORDER_WIDTH))
        self.cell.fill(new_color)
        self.image.blit(self.cell,(self.BORDER_WIDTH,self.BORDER_WIDTH)) 
    def update(self):
        pass
    def draw_text(self,disease,cure):
        text = self.font.render(f'd = {disease}' + '\n' +  f'c={cure}',False,(0,0,0))
        self.image.blit(text, (0,0))
        
    
class Cell():
    def __init__(self, pos,group):
        self.sprite = CellSprite(pos,group)
        
        self.state = {'cure': 0, 'disease': 0}
        
    def update(self, new_state):
        self.state = new_state
        
        
        
        #print(self.state['disease'])
        
        if self.state['disease'] != 0:
            self.sprite.change_color(pg.Color(clamp(int(self.state['disease'] * 255),0,255),0,0))
            diseased_population[-1] = diseased_population[-1] + 1
        elif self.state['cure'] != 0:
            self.sprite.change_color(CYAN)
            cured_population[-1] = cured_population[-1] + 1
        else:
            self.sprite.change_color(WHITE)
            
        # self.sprite.draw_text(self.state['disease'], self.state['cure'])
            
        


class Grid():
    def __init__(self):
        self.sprite_grp = pg.sprite.Group()
        self.cells = [Cell((x,y),self.sprite_grp) for x in range(0,SCREEN_SIZE-CellSprite.CELL_WIDTH+1,CellSprite.CELL_WIDTH) for y in range(0,SCREEN_SIZE-CellSprite.CELL_WIDTH+1,CellSprite.CELL_WIDTH)]
        self.cell_cnt = len(self.cells)
        self.grid_size = int(math.sqrt(self.cell_cnt))
        
        self.hood = [
            0,1,0,
            1,0,1,
            0,1,0
        ]
        self.hood_size = 3
        
        
        
        
    def update(self):
        new_states = []
        for i,cell in enumerate(self.cells):
            cured = 0
            X,Y = self.__get_cell_index_xy(i)
            # print(X,Y,self.__get_cell_xy_index(X,Y))
            hood_diseases = []
            hood_cures = []
            for j,n in enumerate(self.hood):
                if n == 1:
                    x,y = j%self.hood_size - self.hood_size//2 , j//self.hood_size - self.hood_size//2
                    x,y = X+x, Y+y
                    if x >-1 and x < self.grid_size and y > -1 and y < self.grid_size:
                        # print(x,y)
                        # odtad x,y to beda po kolei wszystkie komorki z sasiedztwa
                        # wiec ponizej mozna zrobic z nimi jakies obliczenie
                        
                        # jezeli X,Y nie jest chora (0) to dostaje chorobe o najwiekszej liczbie z x,y, X,Y zostaje wyleczona jesli w x,y jest odpowiednie lekarstwo
                        # X,Y dostaje wtedy to lekarstwo dostaje tez jakies lekarstwo jesli jeszcze zadnego nie ma. Jesli wsrod x,y nie ma odpowiadajacej lekarstwu choroby X,Y traci lekarstwo
                        
                        # jakie sa choroby dookola
                        if self.cells[self.__get_cell_xy_index(x,y)].state['disease'] != 0:
                            hood_diseases.append(self.cells[self.__get_cell_xy_index(x,y)].state['disease'])
                        # sprawdzamy jakie lekarstwa sa dookola
                        if self.cells[self.__get_cell_xy_index(x,y)].state['cure'] != 0:
                            hood_cures.append(self.cells[self.__get_cell_xy_index(x,y)].state['cure'])
                    
            state = cell.state.copy()
            # if cell.state['disease'] == 0:
            #     state['disease'] = max_disease
            #     # i jeszcze szansa na zmutowanie choroby
                # roll = numpy.random.rand()
                # if roll < MUTATION_CHANCE and max_disease != 0:
                #     print(roll,MUTATION_CHANCE)
                #     state['disease'] = clamp(state['disease'] + 5/255*numpy.random.randn(),0.1,1)
                #     diseases.append(Disease(self,(X,Y),state['disease']))
            # elif cell.state['disease'] in cures:
            #     state['cure'] = state['disease']
            #     state['disease'] = 0
            
            
            # if cell.state['cure'] == 0:
            #     if cures:
            #         state['cure'] = cures[0]
            # elif cured == 0:
            #     state['cure'] = 0
                
            # if state['disease'] == state['cure']:
            #     state['disease'] = 0
            
            # jesli komorka nie jest chora to zaraza sie jakas choroba z sasiedztwa
            # jesli komorka juz jest chora to jest odporna na inne choroby
            if state['disease'] == 0:
                if hood_diseases:
                    state['disease'] = numpy.random.choice(hood_diseases)
                    # za kazdym razem kiedy przenosi sie choroba jest szansa na mutacje
                    roll = numpy.random.rand()
                    if roll < MUTATION_CHANCE:
                        # print(roll,MUTATION_CHANCE)
                        state['disease'] = clamp(state['disease'] + 5/255*numpy.random.randn(),0.1,1)
                        diseases.append(Disease(self,(X,Y),state['disease']))
            # komorka moze sie wyleczyc z choroby jesli w sasiedztwie jest odpowiednie lekarstwo
            # bierze wtedy to lekarstwo
            if state['disease'] in hood_cures:
                state['cure'] = state['disease']
                state['disease'] = 0
                    
            
            
            
            new_states.append(state)
        
        for cell,state in zip(self.cells,new_states):
            cell.update(state)
    
    def __get_cell_xy_index(self,x,y):
        return x * self.grid_size + y
    
    def __get_cell_index_xy(self,ind):
        return (ind//self.grid_size,ind%self.grid_size)
        
        
    def draw(self):
        self.sprite_grp.draw(screen)
        
class Disease():
    def __init__(self,grid : Grid,start,init_val):
        self.grid = grid
        self.disease_val = init_val
        self.start = start
        state = self.grid.cells[self.__get_cell_xy_index(*start)].state.copy()
        state['disease'] = init_val
        self.grid.cells[self.__get_cell_xy_index(*start)].update(state)
        
        #cure timer
        self.cure_timer = MEDICINE_DELAY
    def update(self):
        if self.cure_timer >= 0:
            self.cure_timer = self.cure_timer - 1
        if self.cure_timer == 0:
            state = self.grid.cells[self.__get_cell_xy_index(*self.start)].state.copy()
            state['cure'] = self.disease_val
            state['disease'] = 0
            self.grid.cells[self.__get_cell_xy_index(*self.start)].update(state)
            
    def __get_cell_xy_index(self,x,y):
        return x * self.grid.grid_size + y
    
    def __get_cell_index_xy(self,ind):
        return (ind//self.grid.grid_size,ind%self.grid.grid_size)
    

grid = Grid()


diseases.append(Disease(grid,(3,3),0.5))

while True:
    diseased_population.append(0)
    cured_population.append(0)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            data = pd.DataFrame({
                'count' : diseased_population
                })
            data.to_csv("data.csv")
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            print(diseased_population[-2])
            
    grid.update()
    for d in diseases:
        d.update()
    screen.fill(pg.Color(100,0,0))
    grid.draw()
    pg.display.update()
    FPS.tick(60)