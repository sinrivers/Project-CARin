"""
Filename: soundutils.py
Author(s): Taliesin Reese
Version: 1.0
Date: 11/13/2025
Purpose: Play sound for project CARIn
"""
import pygame
pygame.init()

"""import sharedlib
import storage

class speaker(sharedlib.gameobject):"""
	
mChannel = pygame.mixer.Channel(0)
sChannel = pygame.mixer.Channel(1)
music1 = pygame.mixer.Sound("Christmas.wav")
music2 = pygame.mixer.Sound("bosstest.mp3")

soundbacklog = []
soundbacklognames = []

def gettrack(name = "Christmas.wav"):
	global soundbacklognames
	global soundbacklog
	if name in soundbacklognames:
		i = soundbacklognames.index(name)
		return soundbacklog[i]
	else:
		if len(soundbacklog) > 10:
			soundbacklog = soundbacklog[:-1]
			soundbacklognames = soundbacklognames[:-1]
		soundbacklog.insert(0,pygame.mixer.Sound(name))
		soundbacklognames.insert(0,name)
		return(soundbacklog[0])

window = pygame.display.set_mode([10,10])
lastkeys = []
while True:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				music = gettrack("Christmas.wav")
				mChannel.play(music,-1)
			elif event.key == pygame.K_s:
				music = gettrack("bosstest.mp3")
				mChannel.play(music,-1)
			elif event.key == pygame.K_a:
				sound = gettrack("come on.wav")
				sChannel.play(sound)
			print(soundbacklognames)
	