"""
Filename: main.py
Author(s): Taliesin Reese
Version: 6.0
Date: 11/4/2025
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
storage.objlist = []
storage.rendered = []
storage.carryovers = []
storage.persistobjs = [ ["camera3d",[0,0,0]],["uiobject",[]] ]
storage.partyspawn = [ ["character",[250,345,-500,50,50,50,3,"CARIn"]] ]
storage.party = []
storage.camfocus = [0,0]
storage.cambounds = [0,0,storage.screensize[0],storage.screensize[1]]
storage.debug = True
storage.menus = json.load(open("menulayouts.json"))
#the format for cutscene actions is [<affected element>,<details of effect>,<duration of affect>]
storage.missionprogress = {
	"main":0
}
storage.cutscenes = {
	"test":[["ui",["adddialogue","..."]],["wait","enter"],["ui",["adddialogue","And that was the end of that conversation."]],["wait","enter"],["ui",["loadui","Blank"]],["wait",60],["char",["CARIn","jump"]]],
	"test2":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","CARIn",0]],["ui",["adddialogue","Would you like to keep having this conversation?"]],["ui",["addchoice",["yes","no"],["test2","test"]]],["wait","enter"],["loadfromui"]]
}
storage.uipresets = {}
storage.combatactions = {
	"Nothing":[["wait",60]],
	"Win":[["wait",60],["wipe",0],["wait",60]],
	"staffattack":[["wait",1],["picktargethostile"],["staffattack"],["wait",600]],
	"PsychUp":[["checkavailabledata",10],["alterstat","spentdata",10],["alterstat","write",10],["addtimedfx","turnend",120,"alterstat",["write",-10]],["wait",600]],
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
storage.levels = json.load(open("celllayouts.json"))
storage.animinfo = json.load(open("animinfo.json"))
storage.spritesheet = pygame.image.load(f"Assets/graphics/spritesheet.png").convert()
storage.spritesheet.set_colorkey((255,0,255))
sharedlib.menu_active = True
sharedlib.loadmenu("testmain")
storage.savestate = gameutils.save()
storage.runstate = gameutils.save()
storage.winstate = gameutils.save()

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

	# (ADDED) clear off-screen canvases before drawing each frame
	storage.spritecanvas.fill((255,0,255))
	storage.uicanvas.fill((255,0,255))

	# (ADDED) draw the background onto the UI canvas only while the menu is active
	if getattr(sharedlib, "menu_active", False):
		menu.draw_background()

	for obj in storage.rendered:
		#print(storage.renderorder, "HERE")
		obj.render()
	storage.window.blit(storage.spritecanvas,(0,0))
	storage.window.blit(storage.uicanvas,(0,0))
	pygame.display.flip()
	storage.window.fill((0,0,0))
	storage.spritecanvas.fill((255,0,255))
	storage.uicanvas.fill((255,0,255))