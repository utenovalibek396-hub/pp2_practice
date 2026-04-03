from pygame import *
from pygame.sprite import *

init()
screen = display.set_mode((1000,500))
display.set_caption("New agem window")
class Square(Sprite):
    def __init__(self):
        self.image = Surface((100,100))
        self.rect = self.image.get_rect().move(10,10)
        
class Run(Sprite):
    def __init__(self):
        self.image = image.load("PYGAME/cat.jpg").convert_alpha()
        self.rect = Rect(150,100,50,100)
s1 = Square()
r1 = Run()
while True:
    e = event.wait()
    if e.type == QUIT:
        quit()
        break
    screen.fill((255,255,255))
    s1.image.fill((255,0,255))
    screen.blit(s1.image, s1.rect)
    screen.blit(r1.image,r1.rect)
    display.update()