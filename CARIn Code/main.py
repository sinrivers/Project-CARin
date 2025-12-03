"""
Filename: main.py
Author(s): Taliesin Reese, Ricardo Ochoa
Version: 9.1
Date: 11/18/2025
Purpose: master file for Project CARIn
"""

#imports
import pygame
import json
import copy
import vn_system

import storage

import sharedlib
import menu
import gameutils
import soundutils

#create Player Interaction Unit
pygame.init()
soundutils.startup()
storage.screensize = [720,480]
storage.clock = pygame.time.Clock()
storage.window = pygame.display.set_mode(storage.screensize)
storage.spritecanvas = pygame.display.set_mode(storage.screensize).convert()
storage.spritecanvas.set_colorkey((255,0,255))
storage.uicanvas = pygame.display.set_mode(storage.screensize).convert()
storage.uicanvas.set_colorkey((255,0,255))
storage.writer = pygame.font.SysFont("Liberation Mono",12)
storage.userwriter = pygame.font.SysFont("Comic Sans MS",12)
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
storage.framerate = 60
storage.deltatime = storage.framerate/60

#create worldstate
storage.objlist = []
storage.rendered = []
storage.carryovers = []
storage.persistobjs = [ ["camera3d",[0,0,0]],["uiobject",[]] ]
storage.partyspawn = [ ["character",[250,350,-500,50,50,50,3,"CARIn",0]] ]#,["character",[250,345,-500,50,50,50,2,None,0]] ]
storage.enemyspawns = {}
storage.party = []
storage.camfocus = [0,0]
storage.cambounds = [0,0,storage.screensize[0],storage.screensize[1]]
storage.debug = True
storage.orderreset = False
storage.actlock = False
storage.menus = json.load(open("menulayouts.json"))
storage.songplaying = None
storage.missionprogress = {
	"main":0
}
#NOTE: the format for cutscene actions is [<affected element>,<details of effect>,<duration of affect>]
storage.cutscenes = {
			"Pause":[["ui",["loadui","Dictionary"]],["wait","lshift"],["ui",["loadui","Blank"]]],
			"WinCARIn0":[["char",["CARIn",0,"setanim","walk315"]]],
			"test":[["ui",["adddialogue","..."]],["wait","enter"],["ui",["adddialogue","And that was the end of that conversation."]],["wait","enter"],["ui",["loadui","Blank"]],["wait",60],["advancequest","main",1],["char",["CARIn",0,"jump"]]],
			"test2":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","Would you like to keep having this conversation?"]],["ui",["addchoice",["yes","no"],["test2","test"]]],["wait","enter"],["loadfromui"]],
			"test3":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","Well that just happened"]],["wait","enter"],["ui",["loadui","Blank"]]],
			"Intro":[["char",["CARIn",0,"warpto",[200,620,500]]],["wait",120],["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","This is the opening cutscene, where CARIn Arrives on the scene and PLoT tells her to head to Nik's Pools."]],["wait","enter"],["ui",["loadui","Blank"]]],
			"MeetDiRK":[["char",["CARIn",0,"goto",[720,75]]],["create",["character",[250,345,-500,50,50,50,2,"DiRK",0]]],["char",["DiRK",0,"goto",[720,75]]],["wait",120],["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","This is the cutscene where we are introduced to DiRK, and He joins our party."]],["wait","enter"],["ui",["loadui","Blank"],["advancequest","main",1]]],
			"MeetOverdrawn":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","This is the Part where CARIn and DiRK find the first of the Overdrawn programs. A battle ensues."]],["wait","enter"],["ui",["loadui","Blank"]]],
			"GetPasswords":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","This is where DiRK pulls the passwords off the blue tree and encrypts them."]],["wait","enter"],["ui",["loadui","Blank"]]],
			"FightFox":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","This is where the heroes find Fox guarding the Red Tree, and he must be fought before they can plant the password. After the fight, They will head to Aiyo's Mount and load the VN Outro."]],["wait","enter"],["ui",["loadui","Blank"]],["loadvn","outro_vn"]]

		}
storage.combatactions = {
			"Nothing":[["wait",60]],
			"Win":[["wait",60],["wipe",0],["wait",60]],
			"staffattack":[["wait",1],["picktargethostile"],["gototarget"],["staffattack"],["wait",60]],
			"PsychUp":[["checkavailabledata",10],["alterstat","spentdata",10],["alterstat","write",10],["addtimedfx","turnend",120,"alterstat",["write",-10]],["wait",60]],
			"Runmaster":[["runmaster"]],
			"SkipTwo":[["skipturn",2]]
			}

#NOTE: These VN cutscenes are stored separately. Even I am not entirely sure why.
storage.cutscenes["test_vn"] = [
	["Flyngal","Normal",1,[20,0]],
	{"speaker": "CARIn", "text": "Welcome to Project CARIn."},
	["Flyngal","EmoteTest",0,[500,0]],
	{"speaker": "CARIn", "text": "Your journey begins here."},
	{"speaker": "???", "text": "Let’s see how this story unfolds..."},
	"SiVa1"
]
storage.cutscenes["intro_vn"] = [
	{"speaker": None, "text": "You are running this game on a computer."},
	{"speaker": None, "text": "One of the most advanced tools ever made by the hands of man."},
	{"speaker": None, "text": "Yet a tool and nothing more."},
	{"speaker": None, "text": "Yet look behind the screen, beneath the plastic and aluminium. Deeper, deep within the gold, copper and silicon..."},
	{"speaker": None, "text": "Here is a fantastical world, a world where code walks and talks as we do."},
	{"speaker": None, "text": "In this world, a great tale is about to unfold."},
	{"speaker": None, "text": "A tale of noble warriors, depraved enemies, and monsterous beasts."},
	{"speaker": None, "text": "A tale of duty, sacrifice, and destiny."},
	{"speaker": None, "text": "A tale from which you might learn something..."},
	{"speaker": None, "text": "...If you'll only listen."},
	"SiVa1"
]
storage.cutscenes["outro_vn"] = [
	{"speaker": None, "text":">Meanwhile, in the real world...<"},
	{"speaker": "Locke Enkye", "text":"Hey, Allie!"},
	{"speaker": "Alicia Flyngal", "text":"Mr. Enkye! How can I help you?"},
	{"speaker": "Locke Enkye", "text":"Just checking how that password manager I sent down here is doing."},
	{"speaker": "Alicia Flyngal", "text":"Oh, DiRK? It's doing well. We got the client installed on the IT mainframe with no issues."},
	{"speaker": "Alicia Flyngal", "text":"All our department's passwords are now encrypted and stored securely. It even gave a report on any weak passwords."},
	{"speaker": "Locke Enkye", "text":"Do I wanna know how many 'password123's the IT department has?"},
	{"speaker": "Alicia Flyngal", "text":"More than I'd like...maybe you'll have to run us through some more training."},
	{"speaker": "Steven Gates", "text":"Hey Mr. E, I've got something for you!"},
	{"speaker": "Locke Enkye", "text":"What is it, Steve?"},
	{"speaker": "Steven Gates", "text":"Just got a report back from one of our access programs--we had a security breach!"},
	{"speaker": "Locke Enkye", "text":"What's the damage?"},
	{"speaker": "Steven Gates", "text":"Don't worry, we caught it early. Nothing looks amiss so far, but the boys and I are gonna triple-check everything."},
	{"speaker": "Steven Gates", "text":"The attackers weren't even remote-accessing yet--they had an automated script to scrape higher-privilege passwords."},
	{"speaker": "Locke Enkye", "text":"Did it get any?"},
	{"speaker": "Steven Gates", "text":"We can't be sure, but it doesn't look like it."},
	{"speaker": "Alicia Flyngal", "text":"How did it get in?"},
	{"speaker": "Steven Gates", "text":"You know Davis in accounting?"},
	{"speaker": "Alicia Flyngal", "text":"We busted him for having a crummy password not a year ago!"},
	{"speaker": "Steven Gates", "text":"Well, he's got another one. By the looks of it, it's his wife's maiden name."},
	{"speaker": "Steven Gates", "text":"His password got cracked, and that's how the attackers got in. We're still figuring what they did to cross from the Accounting systems to IT."},
	{"speaker": "Locke Enkye", "text":"Keep researching that, and let me know as soon as you figure out the loophole."},
	{"speaker": "Locke Enkye", "text":"We'll have to get DiRK installed across the whole network. In the meantime, have Davis change his password."},
	{"speaker": "Locke Enkye", "text":"We better have the admins change theirs as well, just be safe. Oh, and make sure they meet the pending company standard."},
	{"speaker": "Steven Gates", "text":"The ones you suggested at that meeting, right? 8 plus characters, Uppercase AND lowercase letters, numbers, at least one special character?"},
	{"speaker": "Alicia Flyngal", "text":"AND nothing that could easily be guessed by knowing things about the user!"},
	{"speaker": "Steven Gates", "text":"Right, right."},
	{"speaker": "Locke Enkye", "text":"Lastly, I'd like to see the logs myself."},
	{"speaker": "Steven Gates", "text":"Right, right. From some program called CARIn, I think."},
	{"speaker": "Steven Gates", "text":"That's one of yours, right Allie?"},
	{"speaker": "Alicia Flyngal", "text":"No, you must have the name wrong or something."},
	{"speaker": "Alicia Flyngal", "text":"I'm still working on CARIn--it won't compile."},
	{"speaker": "Steven Gates", "text":"Huh, odd. I could've sworn that was it."},
	{"speaker": None, "text":"..."},
	{"speaker": None, "text":"The demo is over now. You can leave."}
]

storage.charmenus = {
	"Default":{
		"main":[["Fight","Subroutines","Pass","Run"],["staffattack",["menu","subroutines"],"Nothing","Runmaster"]],
		"mainnorun":[["Fight","Subroutines","Pass"],["staffattack",["menu","subroutines"],"Nothing"]],
		"subroutines":[["Back"],[["menu","main"]]]},
	"CARIn":{
		"main":[["Fight","Subroutines","Pass","Run"],["staffattack",["menu","subroutines"],"Nothing","Runmaster"]],
		"mainnorun":[["Fight","Subroutines","Pass"],["staffattack",["menu","subroutines"],"Nothing"]],
		"subroutines":[["Back","Psych Up","Skip your next two turns, for some reason"],[["menu","main"],"PsychUp","SkipTwo"]]}

}
#NOTE: Stats are ordered thus: Max HP, Max DATA, Priority, Read, Write, Execute, Obfuscation, Persistance. modstats has extra slots at the end for damage and spent data.
#NOTE 2: basestats is character's default stats. This is NEVER to be altered in-game. modstats is for modifications via buffs, level-ups, damage, etc.
storage.basestats = {
	"Missingno":[100,0,5,1,2,1,1,1],
	"CARIn":[100,50,5,5,5,5,4,6],
	"DiRK":[100,100,3,5,2,7,4,4],
	"Fox":[150,100,4,5,5,8,5,3],
	"Hacker":[50,10,2,3,3,3,5,2],
	"Short":[25,0,7,5,2,0,4,4]
}
storage.modstats = {
	"Missingno":[0,0,0,0,0,0,0,0,0,0],
	"CARIn":[0,0,0,0,0,0,0,0,0,0],
	"DiRK":[0,0,0,0,0,0,0,0,0,0]
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
sharedlib.menu_active = False
#sharedlib.loadmenu("testsub")
sharedlib.loadgame("OrWo1")#circtest")
storage.savestate = gameutils.save()
storage.runstate = gameutils.save()
storage.winstate = gameutils.save()

#gameloop
#while true
while True:
	#print(storage.cambounds)
	#print(storage.enemyspawns)
	#NOTE: Hate that this has to be here
	storage.songpriority = False
	#NOTE: these Deltatime calculations inherently introduce bugs at super-low framerates.
	#I feel like I fixed these in my last game, but can't recall or rediscover how. 
	#We should have an option to turn on/off timescaling.
	if storage.timeadjust:
		storage.deltatime = 60*storage.clock.get_time()/1000
		#print(storage.deltatime)
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

	storage.objlist.sort(key=lambda x: x.vertsort if isinstance(x.vertsort, (int, float)) else x.vertsort[0])

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
	storage.clock.tick(storage.framerate)
