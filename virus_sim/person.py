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
    def update(self, screen):
        self.move()

        #change from sick to recovered
        if self.status == "sick":
            self.turnsSick +=1
        
            if self.turnsSick == self.recoveryTime:
                self.status = "recovered"
        
        #check for collisions
        self.checkCollidingWithWall(screen)

    def move(self):
        if not self.socialDistancing:
            self.x += self.vx
            self.y += self.vy


    #check for collisions with walls and update the velocity
    def checkCollidingWithWall(self, screen):

        if self.x + self.radius >= screen.get_width() and self.vx > 0: #self.vx > 0 is to prevent it from getting stuck to the wall
            self.vx *= -1
        elif self.x - self.radius < 0 and self.vx < 0:
            self.vx *= -1

        if self.y + self.radius >= screen.get_height() and self.vy > 0: 
            self.vy *= -1
        elif self.y - self.radius < 0 and self.vy < 0:
            self.vy *= -1
