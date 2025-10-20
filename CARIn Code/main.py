"""
Filename: main.py
Author(s): Taliesin Reese
Version: 4.0
Date: 10/15/2025
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
storage.screensize = [720,480]
storage.window = pygame.display.set_mode(storage.screensize)
storage.spritecanvas = pygame.display.set_mode(storage.screensize).convert()
storage.spritecanvas.set_colorkey((255,0,255))
storage.uicanvas = pygame.display.set_mode(storage.screensize).convert()
storage.uicanvas.set_colorkey((255,0,255))
storage.writer = pygame.font.SysFont("Comic Sans MS",12)
storage.mousepos = []
storage.clicks = []
storage.newclicks = []
storage.keys = []
storage.newkeys = []

#create worldstate
storage.cutscene = 0
storage.objlist = []
storage.rendered = []
storage.persistobjs = [ ["camera3d",[0,0,0]],["uiobject",[]] ]
storage.partyspawn = [ ["character",[250,345,-500,50,50,50,3,"CARIn"]] ]
storage.party = []
storage.camfocus = [0,0]
storage.cambounds = [0,0,storage.screensize[0],storage.screensize[1]]
storage.debug = True
storage.menus = json.load(open("menulayouts.json"))
#the format for cutscene actions is [<affected element>,<details of effect>,<duration of affect>]
storage.cutscenes = {
			"test":[["ui",["adddialogue","..."]],["wait","enter"],["ui",["adddialogue","And that was the end of that conversation."]],["wait","enter"],["ui",["loadui","Blank"]],["wait",60],["char",["CARIn","jump"]]],
			"test2":[["ui",["loadui","Dialogue"]],["ui",["adddialogue","Would you like to keep having this conversation?"]],["ui",["addchoice",["yes","no"],["test2","test"]]],["wait","enter"],["loadfromui"]]}
storage.uipresets = {}
storage.levels = json.load(open("celllayouts.json"))
storage.animinfo = json.load(open("animinfo.json"))
storage.spritesheet = pygame.image.load(f"Assets/graphics/spritesheet.png").convert()
storage.spritesheet.set_colorkey((255,0,255))
genesis = menu.menubutton(0,0,0,0,"printwbutton","")
#genesis.loadmenu("testmain")
genesis.loadgame("test2")
storage.savestate = gameutils.save()

#Initialize Background Music
pygame.mixer.init()
try:
	pygame.mixer.music.load("music/video-game-boss-fiight-259885.mp3")
except pygame.error as e:
    print(f"Could not load music file: {e}")
    print("Please ensure 'background_music.mp3' exists in the correct location.")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

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
	storage.rendered = []
	for obj in storage.objlist:
		obj.update()
	storage.objlist.sort(key=lambda x: x.vertsort)
	
	for item in storage.objlist:
		if storage.rendered == []:
			storage.rendered.append(item)
		else:
			for obj in storage.rendered:
				index = storage.rendered.index(obj)
				if item.novertcollide(obj):
					if item.z > obj.z:
						break
			storage.rendered.insert(index,item)

	#draw to screen
	for obj in storage.rendered:
		#print(storage.renderorder, "HERE")
		obj.render()
	storage.window.blit(storage.spritecanvas,(0,0))
	storage.window.blit(storage.uicanvas,(0,0))
	pygame.display.flip()
	storage.window.fill((0,0,0))
	storage.spritecanvas.fill((255,0,255))
	storage.uicanvas.fill((255,0,255))	

	
