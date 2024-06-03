""" Define the person class in the simulation"""

import random, pygame, math


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
    def update(self, screen, people):
        self.move()

        #change from sick to recovered
        if self.status == "sick":
            self.turnsSick +=1
        
            if self.turnsSick == self.recoveryTime:
                self.status = "recovered"
        
        #check for collisions
        self.checkCollidingWithWall(screen)
        for other in people:
            if self != other:
                if self.checkCollidingWithOther(other):
                    self.updateCollisionVelocities(other)
                    #update status
                    if self.status == "sick" and other.status == "healthy":
                        other.status = "sick"
                    elif other.status == "sick" and self.status == "healthy":
                        self.status =  "sick"


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

    
    #return True if the self is colliding with other, False otherwise
    def checkCollidingWithOther(self, other): #we are assuming other is a person so it has .x and .y coordinates
        
        distance = math.sqrt(math.pow(self.x - other.x,2)+ math.pow(self.y - other.y,2))
        if distance <= self.radius + other.radius:
            return True
        return False
    
    #update velocities on collision

    def updateCollisionVelocities(self, other):
        
        #type 1 collision - both objects are moving (neither are social distancing) - switch their velocities
        if not self.socialDistancing and not other.socialDistancing:
            tempVX = self.vx 
            tempVY = self.vy

            self.vx = other.vx
            self.vy = other.vy
            other.vx = tempVX
            other.vy = tempVY

        
        #type 2 collision - one object that is social distancing and one that is not
        elif other.socialDistancing:

            magV = math.sqrt(math.pow(self.vx,2), math.pow(self.vy,2))
            tempVector = (self.vx + (self.x - other.x), self.vy + (self.y - other.y))
            magTempVector = math.sqrt(math.pow(tempVector[0],2), math.pow(tempVector[1],2))

            normTempVector = (tempVector[0]/magTempVector , tempVector[1]/magTempVector)
            self.vx = normTempVector[0]*magV
            self.vy = normTempVector[1]*magV
