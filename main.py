import pygame 
import neat
import time 
import os 
import random
pygame.font.init()

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

GEN = 0

# loding the images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bird1.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bird2.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bird3.png')))] # the function written is used to make the images bigger thats it
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'pipe.png')))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bg.png')))

STAT_FONT = pygame.font.SysFont('comicsans', 50)

#Bird class 
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 
    ROTATION_VELOCITY = 20 
    ANIMATION_TIME = 5 

    def __init__(self, x, y):
        self.x = x 
        self.y = y
        self.tilt = 0
        self.tick_count = 0 
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        
        
        self.velocity = -10.5 
        self.tick_count = 0
        self.height = self.y 

    def move(self):
        self.tick_count += 1
        
        displacement = self.velocity*self.tick_count + 1.5*self.tick_count**2 
        if displacement >= 16:
            displacement = 16 
        if displacement < 0: 
            displacement -= 2 
        
        self.y = self.y + displacement 
        
        if displacement < 0 or self.y < self.height + 50: 
            if self.tilt < self.MAX_ROTATION: 
                self.tilt = self.MAX_ROTATION
        else: 
            if self.tilt > -90: 
                self.tilt -= self.ROTATION_VELOCITY #
    
    def draw(self, window):
        self.img_count += 1 
        
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0] 
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1] 
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2] 
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1] 
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0] 
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[0] 
            self.img_count = self.ANIMATION_TIME*2 

        
        rotated_image = pygame.transform.rotate(self.img, self.tilt) 
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

#pipe class
class Pipe:
    GAP = 200
    VELOCITY = 5
    def __init__(self, x):
        self.x = x
        self.heigh = 0
        self.top = 0 
        self.bottom = 0 
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # Getting top pipe
        self.PIPE_BOTTOM = PIPE_IMG 
        
        self.passed = False
        self.set_height() 

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height() 
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY
    
    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        
        bird_mask = bird.get_mask()
        top = pygame.mask.from_surface(self.PIPE_TOP)
        bottom = pygame.mask.from_surface(self.PIPE_BOTTOM)

        
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        
        bottom_c_point = bird_mask.overlap(bottom, bottom_offset) 
        top_c_point = bird_mask.overlap(top, top_offset) 

        if top_c_point or bottom_c_point:
            return True
        return False

# base class
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


# the below are the functions are to run the game
def draw_window(window, birds, pipes, base, score, gen):
    window.blit(BG_IMG, (0,0)) 

    for pipe in pipes:
        pipe.draw(window)

    text = STAT_FONT.render('Score: ' + str(score), 1, (255,255,255))
    window.blit(text, (WINDOW_WIDTH  - 15 - text.get_width(), 10))

    text = STAT_FONT.render('Gen: ' + str(gen), 1, (255,255,255))
    window.blit(text, (10, 10))

    base.draw(window)
    for bird in birds:
        bird.draw(window)
    pygame.display.update()

def main(genomes, config): 
    global GEN
    GEN += 1
    network_for_bird = []
    ge = []
    birds = []

    #below is the nerual network
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        network_for_bird.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)


    base = Base(730)
    pipes = [Pipe(600)]
    run = True 
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    while run:
        
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = network_for_bird[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        remove = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    network_for_bird.pop(x)
                    ge.pop(x)
                    
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)
            
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700))

        for r in remove:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                ge[x].fitness -= 1
                birds.pop(x)
                network_for_bird.pop(x)
                ge.pop(x)

        #bird
        base.move()
        draw_window(window, birds, pipes, base, score, GEN)

def run(config_path):
    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 50) 


if __name__ == "__main__":
    
    local_dir = os.path.dirname(__file__) 
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)