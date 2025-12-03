import pygame

pygame.init()

window = pygame.display.set_mode((500,500))
clock = pygame.time.Clock()

height = 0
speed = 0
jumpforce = 10
grav = 0.5
dt = 1

while True:
	dt = 60*clock.get_time()/1000
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit()
		if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			speed = jumpforce
	speed -= grav*dt
	height += dt*(speed)
	speed -= grav*dt
	if height < 0:
		height = 0
		speed = 0
	window.fill((0,0,0))
	pygame.draw.rect(window,(255,0,0),(225,int(500-height-50),50,50))
	pygame.display.flip()
	if speed < 0:
		print(height)
	clock.tick(15)