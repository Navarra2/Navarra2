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


    #create people
    patientZero = person.Person(random.randint(spawnBuffer,WIDTH - spawnBuffer),random.randint(spawnBuffer,HEIGHT - spawnBuffer), "sick", False)


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #clicked "X" top right 
                running = False
    
        #update people
        patientZero.update()

        #update graphics
        screen.fill(pygame.Color("gray")) #this is needed to erase the trace of the people before
        patientZero.draw(screen)

        pygame.display.flip() #check this line....

        #pause for frames
        clock.tick(MAX_FPS)
    pygame.quit()



main()