import pygame
pygame.init()

mChannel = pygame.mixer.Channel(0)
sChannel = pygame.mixer.Channel(1)
music1 = pygame.mixer.Sound("Christmas.wav")
music2 = pygame.mixer.Sound("bosstest.mp3")
sound1 = pygame.mixer.Sound("come on.wav")
mChannel.play(music1,-1)
window = pygame.display.set_mode([10,10])
lastkeys = []
while True:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				if mChannel.get_sound()==music1:
					mChannel.play(music2,-1)
				else:
					mChannel.play(music1,-1)
			elif event.key == pygame.K_a:
				sound1 = pygame.mixer.Sound("come on.wav")
				sChannel.play(sound1)
	