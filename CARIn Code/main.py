"""
Filename: main.py
Author(s): Taliesin Reese
Version: 7.1
Date: 11/10/2025
Purpose: master file for Project CARIn
"""

#imports
import pygame
import json
import copy

import storage

import sharedlib
import menu
import gameutils

#create Player Interaction Unit
pygame.init()
storage.screensize = [720,480]
storage.clock = pygame.time.Clock()
storage.window = pygame.display.set_mode(storage.screensize)
storage.spritecanvas = pygame.display.set_mode(storage.screensize).convert()
storage.spritecanvas.set_colorkey((255,0,255))
storage.uicanvas = pygame.display.set_mode(storage.screensize).convert()
storage.uicanvas.set_colorkey((255,0,255))
storage.writer = pygame.font.SysFont("Liberation Mono",12)
if pygame.joystick.get_count() > 0:
	storage.controller = pygame.joystick.Joystick(0)
	#NOTE: this controller mapping is for a crummy SNES-like usb pad I have. No idea if other controllers use the same mapping. Maybe we can add reconfigurable buttons later?
	if storage.controller.get_guid() == "03007e411008000001e5000000000000":
		storage.controllermapping = [0,pygame.K_RETURN,pygame.K_SPACE,0,0,0,0,0,pygame.K_LSHIFT,0]
	else:
		storage.controllermapping = [pygame.K_RETURN,pygame.K_SPACE,0,0,0,0,pygame.K_LSHIFT,0,0,0,0,0,0,0,0,0,0]
else:
	storage.controller = None
storage.lastaxis = [0,0]
storage.dpad = [0,0,0,0]
storage.mousepos = []
storage.clicks = []
storage.newclicks = []
storage.keys = []
storage.newkeys = []
storage.timeadjust = False
storage.deltatime = 1

#create worldstate
storage.objlist = []
storage.rendered = []
storage.carryovers = []
storage.persistobjs = [ ["camera3d",[0,0,0]],["uiobject",[]] ]
storage.partyspawn = [ ["character",[250,345,-500,50,50,50,3,"CARIn"]] ]
storage.party = []
storage.camfocus = [0,0]
storage.cambounds = [0,0,storage.screensize[0],storage.screensize[1]]
storage.debug = True
storage.orderreset = False
storage.menus = json.load(open("menulayouts.json"))
#the format for cutscene actions is [<affected element>,<details of effect>,<duration of affect>]
storage.missionprogress = {
				"main":0
			}
storage.cutscenes = {
			"Pause":[["ui",["loadui","Dictionary"]],["wait","lshift"],["ui",["loadui","Blank"]]],
			"Win": [["char",["CARIn","setanim","walk315"]],["ui",["loadui","Win"]],["wait","enter"]],
			"test":[["ui",["adddialogue","..."]],["wait","enter"],["ui",["adddialogue","And that was the end of that conversation."]],["wait","enter"],["ui",["loadui","Blank"]],["wait",60],["char",["CARIn","jump"]]],
			"test2":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","CARIn",0]],["ui",["adddialogue","Would you like to keep having this conversation?"]],["ui",["addchoice",["yes","no"],["test2","test"]]],["wait","enter"],["loadfromui"]]
		}
storage.uipresets = {}
storage.combatactions = {
			"Nothing":[["wait",60]],
			"Win":[["wait",60],["wipe",0],["wait",60]],
			"staffattack":[["wait",1],["picktargethostile"],["gototarget"],["staffattack"],["wait",60]],
			"PsychUp":[["checkavailabledata",10],["alterstat","spentdata",10],["alterstat","write",10],["addtimedfx","turnend",120,"alterstat",["write",-10]],["wait",60]],
			"Runmaster":[["runmaster"]]
			}
storage.charmenus = {
			"Default":{
			"main":[["Fight","Subroutines","Pass","Run"],["staffattack",["menu","subroutines"],"Nothing","Runmaster"]],
			"mainnorun":[["Fight","Subroutines","Pass"],["staffattack",["menu","subroutines"],"Nothing"]],
			"subroutines":[["Back"],[["menu","main"]]]},
			"CARIn":{
			"main":[["Fight","Subroutines","Pass","Run"],["staffattack",["menu","subroutines"],"Nothing","Runmaster"]],
			"mainnorun":[["Fight","Subroutines","Pass"],["staffattack",["menu","subroutines"],"Nothing"]],
			"subroutines":[["Back","Psych Up"],[["menu","main"],"PsychUp"]]}

		}
#NOTE: Stats are ordered thus: Max HP, Max DATA, Priority, Read, Write, Execute, Obfuscation, Persistance. modstats has extra slots at the end for damage and spent data.
#NOTE 2: basestats is character's default stats. This is NEVER to be altered in-game. modstats is for modifications via buffs, level-ups, damage, etc.
storage.basestats = {
			"Missingno":[999,0,1,1,1,1,1,1],
			"CARIn":[100,50,5,3,7,5,4,6]
			}
storage.modstats = {
			"Missingno":[0,0,0,0,0,0,0,0,0,0],
			"CARIn":[0,0,0,0,0,0,0,0,0,0]
			}
#NOTE: format for timed effects will be [triggertype,triggermods,function,arguments]
#NOTE 2: triggertype can be: turnstart or turnend (both time-based), endofcombat, hit, <add more here later IDK>
storage.timedfx = {
			"Missingno":[],
			"CARIn":[]
			}
storage.storydict = {
			"CARIn":"Computer Access Regulation INterface. A Security Program who was written on accident. Her job is to keep the system safe and running smoothly.",
			"DiRK":"DIgital Registry Keyring. A Password Management and encryption program. His job is to find passwords on the system and put them in secure places.",
			"PLoT":"Program LOcation Tool.",
			"MArIn":"Music ARrangement INtegration."
			}
storage.cyberdict = {
			"User": "You!",
			"Password":"A word, phrase, or other sequence of characters used to access resources. One of the most common forms of user authentication with computers. Best practice as of writing is to make passwords that are eight characters or longer, and which use uppercase letters, lowercase letters, numbers, and special characters (punctuation marks and such)."
			}
storage.levels = json.load(open("celllayouts.json"))
storage.animinfo = json.load(open("animinfo.json"))
storage.spritesheet = pygame.image.load(f"Assets/graphics/spritesheet.png").convert()
storage.spritesheet.set_colorkey((255,0,255))
genesis = menu.menubutton(0,0,0,0,"printwbutton","")
#genesis.loadmenu("testmain")
genesis.loadgame("test2")
storage.savestate = gameutils.save()
storage.runstate = gameutils.save()
storage.winstate = gameutils.save()

#gameloop
#while true
while True:
	#print(storage.cambounds)
	#NOTE: these Deltatime calculations inherently introduce bugs at super-low framerates.
	#I feel like I fixed these in my last game, but can't recall or rediscover how. 
	#We should have an option to turn on/off timescaling.
	if storage.timeadjust:
		storage.deltatime = 60*storage.clock.get_time()/1000
	#get input updates from the PIU
	storage.mousepos = pygame.mouse.get_pos()
	#TODO: We probably want to make the game resolution-agnostic by having all coordinates be in "units" rather than pixels. This is a spot that will require change.
	storage.clicks = pygame.mouse.get_pressed()
	storage.keys = pygame.key.get_pressed()
	if storage.controller != None:
		storage.dpad = [False,False,False,False]
		axis = storage.controller.get_axis(0)
		if axis < -0.5:
			storage.dpad[0] = True
		elif axis > 0.5:
			storage.dpad[1] = True
		axis = storage.controller.get_axis(1)
		if axis < -0.5:
			storage.dpad[2] = True
		elif axis > 0.5:
			storage.dpad[3] = True
		#This probably won't come back to bite me in the rear, right?...right?
		"""for buttonnum in range(len(storage.controllermapping)-1):
			if storage.controller.get_button(buttonnum):
				storage.keys[storage.controllermapping[buttonnum]] = True"""
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
		elif event.type == pygame.JOYBUTTONDOWN:
			storage.newkeys.append(storage.controllermapping[event.button])
		elif event.type == pygame.JOYAXISMOTION:
			if event.axis == 1:
				if event.value >= 0.9 and abs(event.value-storage.lastaxis[1]) > 0.1:
					storage.newkeys.append(pygame.K_s)
				elif event.value <= -0.9 and abs(event.value-storage.lastaxis[1]) > 0.1:
					storage.newkeys.append(pygame.K_w)
				storage.lastaxis[1] = event.value
			elif event.axis == 0:
				if event.value >= 0.9 and abs(event.value-storage.lastaxis[0]) > 0.1:
					storage.newkeys.append(pygame.K_a)
				elif event.value <= -0.9 and abs(event.value-storage.lastaxis[0]) > 0.1:
					storage.newkeys.append(pygame.K_d)
				storage.lastaxis[0] = event.value
			#storage.newkeys.append(storage.controllermapping[event.button])

	#update gameobjects
	storage.rendered = []
	for obj in storage.objlist:
		obj.update()
		if storage.orderreset:
			storage.orderreset = False
			break
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
	storage.clock.tick(60)
	