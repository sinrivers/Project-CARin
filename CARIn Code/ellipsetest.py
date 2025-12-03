import pygame
import math

pygame.init()
window = pygame.display.set_mode((500,500))
angle = 0
width = 100
height = 100
widthtop = 150
heighttop = 150
elevation = 100

while True:
	window.fill((0,0,0))

	burner = pygame.Surface((width,height))
	burner.set_colorkey((0,0,0))
	pygame.draw.ellipse(burner,(100,0,0), [0,0,width,height])
	burner = pygame.transform.rotate(burner,angle)
	window.blit(burner,[250-burner.get_size()[0]/2,250-burner.get_size()[1]/2])

	testangle = math.pi*(90-int(angle))/180
	displayangle = math.pi*(int(angle))/180
	a = width/2
	m = math.tan(testangle)
	b = height/2
	x1 = (m*(a**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
	x2 = -(m*(a**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
	y1 = -((b**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
	y2 = ((b**2))/(math.sqrt((a**2)*(m**2)+(b**2)))

	a = widthtop/2
	m = math.tan(testangle)
	b = heighttop/2
	x3 = (m*(a**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
	x4 = -(m*(a**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
	y3 = -((b**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
	y4 = ((b**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
	pygame.draw.polygon(window,(100,0,0),[[250+x1*math.cos(displayangle)-y1*math.sin(displayangle),250+x2*math.sin(displayangle)+y2*math.cos(displayangle)],
					      [250+x2*math.cos(displayangle)-y2*math.sin(displayangle),250+x1*math.sin(displayangle)+y1*math.cos(displayangle)],
					      [250+x4*math.cos(displayangle)-y4*math.sin(displayangle),250+x3*math.sin(displayangle)+y3*math.cos(displayangle)-elevation],
					      [250+x3*math.cos(displayangle)-y3*math.sin(displayangle),250+x4*math.sin(displayangle)+y4*math.cos(displayangle)-elevation]])
	


	burner2 = pygame.Surface((widthtop,heighttop))
	burner2.set_colorkey((0,0,0))
	pygame.draw.ellipse(burner2,(255,0,0), [0,0,widthtop,heighttop])
	burner2 = pygame.transform.rotate(burner2,angle)
	window.blit(burner2,[250-burner2.get_size()[0]/2,250-burner2.get_size()[1]/2-elevation])

	pygame.display.flip()

	keys = pygame.key.get_pressed()
	if keys[pygame.K_RETURN]:
		angle += 0.1
		if angle > 359.9:
			angle = 0
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit()