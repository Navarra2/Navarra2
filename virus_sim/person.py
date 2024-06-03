""" Define the person class in the simulation"""

import random, pygame


minMovement = 0.5
maxSpeed = 5

class Person():


    colors = {"healthy": "white", "sick":"red", "recovered":"blue"} #match the colors with the status
    
    

    #status = "healthy", "sick", "recovered"
    def __init__(self, x, y, status, socialDistancing):
        
        self.x = x
        self.y = y
        self.status = status
        self.socialDistancing = socialDistancing
        self.recoveryTime = random.randint(150,200) #each person will have their own recovery time
        
        #represent them in circles
        self.radius = 6

        #velocity
        self.vx = self.vy = 0

        #turns sick
        self.turnsSick = 0


        if not self.socialDistancing:
            while -minMovement < self.vx < minMovement and -minMovement < self.vy < minMovement: #preventing 0 velocities
                self.vx = random.uniform(-maxSpeed,maxSpeed)
                self.vy = random.uniform(-maxSpeed,maxSpeed)
    
    #screen - the surface
    def draw(self, screen):
        #pygame takes integers in the drawing
        pygame.draw.circle(screen, pygame.Color(self.colors[self.status]), (int(self.x), int(self.y)), self.radius)

    #execute once per frame
    def update(self):
        self.move()

        #change from sick to recovered
        if self.status == "sick":
            self.turnsSick +=1
        
            if self.turnsSick == self.recoveryTime:
                self.status = "recovered"
            


    def move(self):
        if not self.socialDistancing:
            self.x += self.vx
            self.y += self.vy
