import pygame
import numpy as np
import random
import os
import neat
pygame.init()

class player():
    def __init__(self,w,h):
        self.w = w
        self.h = h
        self.size = (self.w,self.h)
        self.x = win_w//10
        self.y = win_h-win_h//10-h
        self.isJump = False
        self.jumpCount = 10
        self.score = 0
        self.img_count = 0
    
    def draw(self,win):#,img):
        pygame.draw.rect(win,(255,0,0),(self.x,self.y,self.w,self.h))
        #win.blit(img,(self.x,self.y))
        
    def Duck(self):
        if not(self.isJump):
            self.w = self.size[1]
            self.h = self.size[0]
            self.y = win_h-win_h//10-self.h
        else:
            self.w = self.size[0]
            self.h = self.size[1]
            self.y = win_h-win_h//10-self.h
                
    def Jump(self):
        if self.isJump == True:
            if self.jumpCount >= -10:
                neg = 1
                if self.jumpCount < 0:
                    neg = -1
                # Jumps to 296 max (154 delta)
                self.y -= self.jumpCount**2 * neg * 0.4
                self.jumpCount -= 1
            else:
                self.isJump = False
                self.jumpCount = 10
                
class obstacle():
    obstacle_count = 0
    def __init__(self,x,y,w,h,vel = 10,obs_type=(1,1)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vel = int(vel * (1+self.obstacle_count/100))
        self.points = 1
        self.obs_type = obs_type
        self.img_count = 0
        
        obstacle.obstacle_count += 1
        
    def move(self):
        self.x -= self.vel
        
    def draw(self,win):
        pygame.draw.rect(win,(0,255,0),(self.x,self.y,self.w,self.h))     
                

def drawBackground(win):
    win.fill((255,255,255))
    pygame.draw.line(win,(0,0,0),(0,win_h-win_h//10),(win_w,win_h-win_h//10))
    
    if len(dinos) > 0:
        font = pygame.font.SysFont('comicsans', 30,1)
        
        text_score = font.render('Score: '+str(np.round(max([g.fitness for g in ge]),2)),1,(0,0,0))
        win.blit(text_score,(10,10))
        
        text_gen = font.render('Gen: '+str(gen),1,(0,0,0))
        win.blit(text_gen,(win_w-win_w//10,10))
        
        text_alive = font.render('Alive: '+str(len(dinos)),1,(0,0,0))
        win.blit(text_alive,(10,35))
        
    #pygame.draw.line(win,(0,0,255),(0,500-50-154),(win_w,500-50-154))

def drawWindow(win,dino_imgs,cactus_imgs,birds_imgs):
    drawBackground(win)
    for dino in dinos:
        #dino.draw(win)
        if dino.isJump:
            win.blit(dino_imgs[0],(dino.x,dino.y))
        else:
            dino.img_count += 1
            win.blit(dino_imgs[dino.img_count // 2],(dino.x,dino.y))
            if dino.img_count == 5:
                dino.img_count = 0
    for obs in obstacles:
        #obs.draw(win)
        if obs.obs_type[0] == 1:
            win.blit(cactus_imgs[obs.obs_type[1]-1],(obs.x,obs.y))
        else:
            obs.img_count += 1
            win.blit(birds_imgs[obs.img_count//10],(obs.x,obs.y))
            if obs.img_count == 19:
                obs.img_count = 0
    
    
def makeRandomObstacle():
    if obstacle.obstacle_count >= 5:
        obs_nr = random.choices([1,2],[0.6,0.4])[0]
        if obs_nr == 1:
            cactus_nr = random.choices([1,2],[0.7,0.3])[0]
            if cactus_nr == 1:
                return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-100,45,100,20,(1,1))
            else:
                return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-50,45,50,20,(1,2))
        else:
            bird_nr = random.choices([1,2,3],[0.3,0.4,0.3])[0]
            if bird_nr == 1:
                return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-45-15,45,30,20,(2,1))
            elif bird_nr == 2:
                return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-90-15,45,30,20,(2,2))
            else:
                return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-154-15,45,30,20,(2,3))
    elif obstacle.obstacle_count == 0:
        return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-154-15,45,30,20,(2,3))
    elif obstacle.obstacle_count == 1:
        return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-50,45,50,20,(1,2))
    elif obstacle.obstacle_count == 2:
        return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-45-15,45,30,20,(2,1))
    elif obstacle.obstacle_count == 3:
        return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-90-15,45,30,20,(2,2))        
    elif obstacle.obstacle_count == 4:
        return obstacle(int(np.random.normal(win_w,win_w//10)),
                              win_h-win_h//10-100,45,100,20,(1,1))

def CheckPoints(player,obstacle):
    points = [(player.x,player.y),
              (player.x+player.w,player.y),
              (player.x+player.w,player.y+player.h),
              (player.x,player.y+player.h)]
    for point in points:
        x = point[0]
        y = point[1]
        if (x>=obstacle.x and x<=obstacle.x+obstacle.w) and (y>=obstacle.y and y <= obstacle.y+obstacle.h):
                return True

#def reset():
#    print("Well done.\nScore: "+ str(dino.score))
    #obstacles[:] = []              

def main(genomes, config):
    global win_w,win_h,dinos,obstacles,gen,ge
    pygame.init()
    gen += 1
    win_w = 1000
    win_h = 500
    
    win = pygame.display.set_mode((win_w,win_h))
    dino_imgs = [pygame.image.load("./images/DinoRun1.png"),
                 pygame.image.load("./images/DinoRun2.png"),
                 pygame.image.load("./images/DinoRun3.png")]
    cactus_imgs = [pygame.image.load("./images/Cactus1.png"),
                   pygame.image.load("./images/Cactus2.png")]
    birds_imgs = [pygame.image.load("./images/Bird1.png"),
                  pygame.image.load("./images/Bird2.png")] 
    
    nets = []
    ge = []
    dinos = []
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        dinos.append(player(45,90))
        g.fitness = 0
        ge.append(g)
        
    # player(45,90)
    
    # Initialise objects
    obstacles = []
    for i in range(2):
        if i == 0:
            obs = makeRandomObstacle()
        else:
            obs = makeRandomObstacle()
            obs.x += obstacles[-1].x
        
        obstacles.append(obs)
    
    # Draw start
    drawWindow(win,dino_imgs,cactus_imgs,birds_imgs)
    pygame.display.update()
    
    run = True
    while run:
        pygame.time.delay(1000//30)
        
        drawWindow(win,dino_imgs,cactus_imgs,birds_imgs)
        pygame.display.update()
        
        obs_ind = 0
        if len(dinos) > 0:
            if len(obstacles) > 1 and (dinos[0].x > obstacles[0].x +
                  obstacles[0].w):
                obs_ind = 1
        else:
            pygame.quit()
            run = False
            obstacle.obstacle_count = 0
            break
        
        for x, dino in enumerate(dinos):
            #dino.move()
            # Appreciate distance
            ge[x].fitness += .01
            
            output = nets[x].activate((dino.y,abs(obstacles[obs_ind].x - dino.x),
                         obstacles[obs_ind].y-dino.y,obstacles[obs_ind].obs_type[0]))
            
            if output[0] > 0.5:
                dino.isJump=True
                ge[x].fitness -= 3
            dino.Jump()
            
        for obs in obstacles:
            obs.move()
           
            # Removing block
            if obs.x <= -obs.w:
                obstacles.pop(obstacles.index(obs))
                
                obs = makeRandomObstacle()
                obs.x += obstacles[-1].x
                obstacles.append(obs)
            
            for x, dino in enumerate(dinos):
                # Counting points
                if obs.x + obs.w//2 <= dino.x + dino.w//2:
                    dino.score += obs.points
                    for g in ge:
                        g.fitness += 5
                    
                # Killing dino
                if CheckPoints(dino,obs):
                    ge[x].fitness -= 1
                    dinos.pop(x)
                    nets.pop(x)
                    ge.pop(x)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

#print("\033[H\033[J")

gen = 0

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    
    winner = p.run(main,50)
    
    print('\nBest genome:\n{!s}'.format(winner))
    
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config.txt")
    run(config_path)
    