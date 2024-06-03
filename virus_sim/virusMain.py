import pygame, random
import person

def main():
    pygame.init()
    
    #screen setup
    WIDTH = HEIGHT = 600
    screen = pygame.display.set_mode([WIDTH,HEIGHT])
    pygame.display.set_caption("Virus Simulation")
    screen.fill(pygame.Color("gray"))

    #clock setup
    clock = pygame.time.Clock()
    MAX_FPS = 20


    #variables
    running = True
    spawnBuffer = 10
    numPeople = 200


    #create people
    patientZero = person.Person(random.randint(spawnBuffer,WIDTH - spawnBuffer),random.randint(spawnBuffer,HEIGHT - spawnBuffer), "sick", False)
    people = [patientZero]
    for i in range(numPeople-1):
        socialDistancing = False

        colliding = True

        #avoiding two people to be colliding initially
        while colliding:
            peeps = person.Person(random.randint(spawnBuffer,WIDTH - spawnBuffer),random.randint(spawnBuffer,HEIGHT - spawnBuffer), "healthy", socialDistancing)
            colliding = False
            for peeps2 in people:
                if peeps.checkCollidingWithOther(peeps2):
                    colliding = True
                    break
            
            
        people.append(peeps)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #clicked "X" top right 
                running = False
    
        #update people
        for p in people:
            p.update(screen, people)

        #update graphics
        screen.fill(pygame.Color("gray")) #this is needed to erase the trace of the people before
        
        for p in people:
            p.draw(screen)

        pygame.display.flip() #check this line....

        #pause for frames
        clock.tick(MAX_FPS)
    pygame.quit()



main()