import pygame
pygame.init()

window = pygame.display.set_mode((500,500))
playerholder = pygame.Surface((500,500))
playerholder.set_colorkey((0,255,0))
tilemap = [
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,2,0,0],
[0,0,0,0,0,0,0,2,0,0],
[0,0,0,0,0,0,0,2,0,0],
[0,0,0,0,0,0,0,3,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0]
]

boundingbox = [1,25,[7*50,5*50,1*50,3*50]]

playerpos = [100,100,0]
height = 13
grounded = True
playerspeed = [0,0,0]

while True: 
	playerpos[0] += playerspeed[0]
	playerpos[1] += playerspeed[1]
	playerpos[2] += playerspeed[2]

	if playerspeed[0] > 0:
		playerspeed[0] -= 0.1
	elif playerspeed[0] < 0:
		playerspeed[0] += 0.1
	if playerspeed[1] > 0:
		playerspeed[1] -= 0.1
	elif playerspeed[1] < 0:
		playerspeed[1] += 0.1

	if grounded == True:
		playerspeed[2] = 0
		grounded = True
	else:
		playerspeed[2] -= 0.005
		print("AHHH")
	

	if boundingbox[2][1] <= playerpos[1] and playerpos[1] <= boundingbox[2][1]+boundingbox[2][3]:
		if boundingbox[2][0] <= playerpos[0]+7 <= boundingbox[2][0]+boundingbox[2][2] or boundingbox[2][0] <= playerpos[0]-7 <= boundingbox[2][0]+boundingbox[2][2]:
			if boundingbox[1] > playerpos[2]:
				xdist = min(boundingbox[2][0] - playerpos[0]-7,boundingbox[2][0]+boundingbox[2][2] - playerpos[0]+7,key = abs)
				ydist = min(boundingbox[2][1] - playerpos[1],boundingbox[2][1]+boundingbox[2][3] - playerpos[1],key = abs)
				if abs(xdist) > abs(ydist):
					playerpos[1] += ydist
				else:
					playerpos[0] += xdist
	if playerpos[2] < 0:
		playerpos[2] = 0
		grounded = True
		playerspeed[2] = 0
					
				
	
	#render
	for row in range(len(tilemap)):
		for tile in range(len(tilemap[row])):
			if tilemap[row][tile] == 0:
				pygame.draw.rect(window, (200,200,200), (tile*50,row*50,50,50))
			elif tilemap[row][tile] == 2:
				pygame.draw.rect(window, (255,255,255), (tile*50,row*50,50,50))
			elif tilemap[row][tile] == 3:
				pygame.draw.rect(window, (100,100,100), (tile*50,row*50,50,50))

	playerholder.fill((0,255,0))
	#pygame.draw.rect(playerholder,(0,0,255),(int(boundingbox[2][0]),int(boundingbox[2][1]),boundingbox[2][2],boundingbox[2][3]))
	pygame.draw.rect(playerholder,(100,100,100),(int(playerpos[0])-13,int(playerpos[1])-13,25,25))
	pygame.draw.rect(playerholder,(255,0,0),(int(playerpos[0])-13,int(playerpos[1])-25-int(playerpos[2]),25,25))
	for row in range(len(tilemap)):
		for tile in range(len(tilemap[row])):
			if tilemap[row][tile] == 2:
				pygame.draw.rect(playerholder, (0,255,0), (tile*50,row*50,50,50))
	window.blit(playerholder,(0,0))

	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			quit()
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			playerspeed[2] = 1
			grounded = False
	keys = pygame.key.get_pressed()
	if keys[pygame.K_a]:
		playerspeed[0] = -0.1
	elif keys[pygame.K_d]:
		playerspeed[0] = 0.1
	if keys[pygame.K_w]:
		playerspeed[1] = -0.1
	elif keys[pygame.K_s]:
		playerspeed[1] = 0.1

	pygame.display.flip()