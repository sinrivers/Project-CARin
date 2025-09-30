"""
Filename: main.py
Author(s): Taliesin Reese
Version: 1.0
Date: 9/27/2025
Purpose: master file for Project CARIn
"""

#imports
import pygame
import json

import storage

import sharedlib
import menu
import gameutils

#create Player Interaction Unit
pygame.init()
storage.window = pygame.display.set_mode((720,480))
storage.spritecanvas = pygame.display.set_mode((720,480)).convert()
storage.spritecanvas.set_colorkey((255,0,255))
storage.writer = pygame.font.SysFont("Comic Sans MS",12)
storage.mousepos = []
storage.clicks = []
storage.newclicks = []
storage.keys = []
storage.newkeys = []

#create worldstate
storage.objlist = []
storage.debug = False
storage.menus = json.load(open("menulayouts.json"))
storage.levels = json.load(open("celllayouts.json"))
genesis = menu.menubutton(0,0,0,0,"printwbutton","")
genesis.loadgame("test2")

#gameloop
#while true
while True:
	#TODO: calculate deltatime?

	#get input updates from the PIU
	storage.mousepos = pygame.mouse.get_pos()
	#TODO: We probably want to make the game resolution-agnostic by having all coordinates be in "units" rather than pixels. This is a spot that will require change.
	storage.clicks = pygame.mouse.get_pressed()
	storage.keys = pygame.key.get_pressed()
	storage.newkeys = []
	storage.newclicks = []
	for event in pygame.event.get():
        	#quit logic
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		elif event.type == pygame.KEYDOWN:
			#if a key is newly down on this frame, it's important. Add it to newkeys
			storage.newkeys.append(event.key)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			#if a mouse button is newly down on this frame, it's important. Add it to newclicks
			storage.newclicks.append(event.button)

	#update gameobjects
	for obj in storage.objlist:
		obj.update()
	storage.objlist.sort(key=lambda x: [x.y,-x.z+x.d])
	#draw to screen
	for obj in storage.objlist:
		obj.render()
	storage.window.blit(storage.spritecanvas,(0,0))
	pygame.display.flip()
	storage.window.fill((0,0,0))
	storage.spritecanvas.fill((255,0,255))	
	