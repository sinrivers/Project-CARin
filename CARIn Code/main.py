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
	"main":0,
	"Combat":0,
	"CHAS":0
}
#NOTE: the format for cutscene actions is [<affected element>,<details of effect>,<duration of affect>]
storage.cutscenes = {
			"Pause":[["ui",["loadui","Dictionary"]],["wait","lshift"],["ui",["loadui","Blank"]]],
			"WinCARIn0":[["char",["CARIn",0,"setanim","walk315"]]],
			"test":[["ui",["adddialogue","..."]],["wait","enter"],["ui",["adddialogue","And that was the end of that conversation."]],["wait","enter"],["ui",["loadui","Blank"]],["wait",60],["advancequest","main",1],["char",["CARIn",0,"jump"]]],
			"test2":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","Would you like to keep having this conversation?"]],["ui",["addchoice",["yes","no"],["test2","test"]]],["wait","enter"],["loadfromui"]],
			"test3":[["ui",["loadui","Dialogue"]],["ui",["setspeaker","partyleader",0]],["ui",["adddialogue","Well that just happened"]],["wait","enter"],["ui",["loadui","Blank"]]],
			"Intro":[
				["char",["CARIn",0,"warpto",[200,620,-550]]],
				["char",["CARIn",0,"gotocutscenewait",[200,620,500]]],
				["wait",120],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","Whew! Here we are."]],
				["wait","enter"],
				["ui",["adddialogue","I hope we can get this crash fixed quickly..."]],
				["wait","enter"],
				["ui",["adddialogue","The bus is stuck on this side of the road."]],
				["wait","enter"],
				["ui",["adddialogue","Still, I've had a quiet patrol cycle. I better be grateful for that."]],
				["wait","enter"],
				["ui",["setspeaker","???",0]],
				["ui",["adddialogue","Oyyy! CARIn!"]],
				["wait","enter"],
				["ui",["cutspeaker","???",0]],
				["ui",["loadui","Blank"]],
				["create",["character",[580,620,0,50,50,50,0,"PLoT",0]]],
				["char",["PLoT",0,"gotocutscenewait",[380,620,500]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","PLoT",1]],
				["ui",["adddialogue","CARIn! I been lookin' for ya!"]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Hey, PLoT. What's happening?"]],
				["wait","enter"],
				["ui",["setspeaker","PLoT",0]],
				["ui",["adddialogue","You're needed at Nik's Pools to the southeast. There's a new program coming!"]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Are you sure I'm needed? I was in the middle of a patrol..."]],
				["wait","enter"],
				["ui",["setspeaker","PLoT",0]],
				["ui",["adddialogue","Them's the rules. Every new program should be examined by a security program."]],
				["wait","enter"],
				["ui",["adddialogue","Been like that for periods before you and I, wot?"]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Well, I'll head that way then."]],
				["wait","enter"],
				["ui",["setspeaker","PLoT",0]],
				["ui",["adddialogue","And I'm off too--someone at the beach needs proddin'. Cya!"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["char",["PLoT",0,"gotocutscenewait",[720,620,500]]],
				["advancequest","main",1]],
			"MeetDiRK":[
				["wait",60],
				["char",["CARIn",0,"gotocutscenewait",[1045,100,0],600]],
				["cam",["setfocus"]],
				["cam",["moveto",[680,0,0] ] ],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","JAn",0]],
				["ui",["adddialogue","Ohhhh, somthin's comin'...!"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["create",["character",[1045,395,-500,50,50,50,2,"DiRK",0]]],
				["char",["DiRK",0,"alterstat","priority",20]],
				["char",["DiRK",0,"addtimedfx","time",0,"alterstat",["priority",-20]]],
				["char",["DiRK",0,"jump"]],
				["char",["DiRK",0,"gotocutscenewait",[1045,100]]],
				["wait",60],
				["char",["CARIn",0,"gotocutscenewait",[1045,100,0],100]],
				["char",["DiRK",0,"turnto",[860,95]]],
				["char",["CARIn",0,"turnto",[1045,100]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","Alright, hold it program."]],
				["wait","enter"],
				["ui",["adddialogue","State your name, occupation, and User. Don't panic, it's just protocol."]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","...nice to meet you too."]],
				["wait","enter"],
				["ui",["adddialogue","I'm DiRK, I'm a password manager, and I was written by ENKYEADMIN."]],
				["wait","enter"],
				["ui",["adddialogue","Who wants to know?"]],
				["wait","enter"],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","I'm CARIn, I work security. And I don't...well..."]],
				["wait","enter"],
				["ui",["adddialogue","I don't have a User per se."]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","What? That doesn't make any sense."]],
				["wait","enter"],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","It's a long story. Now what brings you to our system?"]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","ENKYEADMIN sent me here to secure and review all the passwords on the server."]],
				["wait","enter"],
				["ui",["adddialogue","First, I'm to harvest data from a BLUE TREE and store them next to a RED TREE."]],
				["wait","enter"],
				["ui",["adddialogue","Can you point me in the right direction?"]],
				["wait","enter"],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","The Blue Tree is in Mem's Woods, and the Red Tree is in Ori's Woods. Both are to the east."]],
				["wait","enter"],
				["ui",["adddialogue","How about I show you, since you're new?"]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","Very well. Let's head out quickly."]],
				["wait","enter"],
				["create",["plat",[800,166,0,500,500,500,0,[0,0,0,0],"Blank"]],],
				["ui",["loadui","Blank"]],
				["char",["DiRK",0,"joinparty"]],
				["cam",["setfocus","partyleader"]],
				["advancequest","main",2]],
			"MeetHacker":[
				["create",["character",[370,1518,0,50,50,50,1,"Hacker",0]]],
				["create",["character",[520,1518,0,50,50,50,1,"Hacker",1]]],
				["wait",120],
				["cam",["setfocus"]],
				["cam",["moveto",[104,1302,0]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Hacker",1]],
				["ui",["adddialogue","You found anything?"]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",1,1]],
				["ui",["adddialogue","Not yet...what was MOLEX thinking?"]],
				["wait","enter"],
				["ui",["adddialogue","Sending us into the woods with no sense of direction..."]],
				["wait","enter"],
				["ui",["adddialogue","How are we supposed to find passwords like this?"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadifinparty",["DiRK0","MeetHackerDiRK"]],
				["loadcutscene","MeetHacker2"]],
			"MeetHackerDiRK":[
				["char",["DiRK",0,"gotocutscenewait",[230,1418]]],
				["wait",120],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","Excuse me?"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["char",["Hacker",0,"turnto",[230,1418]]],
				["char",["Hacker",1,"turnto",[230,1418]]],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Hacker",1,1]],
				["ui",["adddialogue","What do you want, bug?"]],
				["wait","enter"],
				["ui",["adddialogue","We're in the middle of something!"]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",1,0]],
				["ui",["adddialogue","Hold on..."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["char",["Hacker",0,"gotocutscenewait",[320,1468]]],
				["char",["Hacker",0,"turnto",[230,1418]]],
				["wait",60],
				["char",["Hacker",0,"turnto",[520,1518]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Hacker",1,0]],
				["ui",["adddialogue","This guy's a password manager!"]],
				["wait","enter"],
				["ui",["adddialogue","Which means..."]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",1,1]],
				["ui",["adddialogue","...yeah, I get it!"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["wait",60],
				["char",["Hacker",0,"turnto",[230,1418]]],
				["char",["Hacker",1,"turnto",[230,1418]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Hacker",1,1]],
				["ui",["adddialogue","Hey, four-eyes! Hand over all the passwords you've got, and nobody gets deleted!"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadcutscene","MeetHacker2"]],
			"MeetHacker2":[
				["char",["SAM",0,"goto",[190,1468]]],
				["char",["CARIn",0,"gotocutscenewait",[240,1468]]],
				["cam",["setfocus","partyleader"]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CARIn",0,1]],
				["ui",["adddialogue","Not so fast!"]],
				["wait","enter"],
				["ui",["adddialogue","You're not authorized to access these woods. Who's your User?"]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",1,0]],
				["ui",["adddialogue","Come on, security!?"]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",1,1]],
				["ui",["adddialogue","Well, no escaping now. Let's wipe 'em!"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["wait",60],
				["theyfight","fighttest"],
				["loadifinparty",["DiRK0","MeetHacker3DiRK"]],
				["loadcutscene","MeetHacker3"]],
			"MeetHacker3DiRK":[
				["char",["Hacker",0,"delete"]],
				["char",["Hacker",1,"delete"]],
				["ui",["cutspeaker","Hacker",0]],
				["ui",["cutspeaker","Hacker",1]],
				["wait",90],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","DiRK",0,0]],
				["ui",["adddialogue","<sigh> what a cycle already..."]],
				["wait","enter"],
				["ui",["adddialogue","<sigh> I don't suppose that's the last of them?..."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0,0]],
				["ui",["adddialogue","Doesn't look like it..."]],
				["wait","enter"],
				["ui",["adddialogue","These were just slave programs, meaning their leader is probably around here somewhere"]],
				["wait","enter"],
				["ui",["adddialogue","And they're after our passwords..."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["wait",60],
				["loadifinparty",["SAM0","MeetHacker3SAM"]],
				["loadcutscene","MeetHacker4DiRK"]],
			"MeetHacker3SAM":[
				["char",["CARIn",0,"turnto",[190,1468]]],
				["wait",30],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CARIn",0,0]],
				["ui",["adddialogue","We better track down that master program."]],
				["wait","enter"],
				["ui",["setspeaker","SAM",0,0]],
				["ui",["adddialogue","We need to get DiRK's job sorted first. No need to wrap him up in this."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0,0]],
				["ui",["adddialogue","Right."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadcutscene","MeetHacker4DiRK"]],
			"MeetHacker3":[
				["char",["Hacker",0,"delete"]],
				["char",["Hacker",1,"delete"]],
				["ui",["cutspeaker","Hacker",0]],
				["ui",["cutspeaker","Hacker",1]],
				["wait",30],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CARIn",0,0]],
				["ui",["adddialogue","Great, password poachers."]],
				["wait","enter"],
				["ui",["adddialogue","And by the looks of it, these were just slave programs."]],
				["wait","enter"],
				["ui",["adddialogue","I'll have to look out for their leader."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["advancequest","Combat",1]],
			"MeetHacker4DiRK":[
				["char",["CARIn",0,"turnto",[230,1418]]],
				["wait",30],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CARIn",0,0]],
				["ui",["adddialogue","Keep your head on a swivel."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["advancequest","Combat",1]],
			"BlueTree":[
				["wait",30],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","There it is, the Blue Tree!"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["cam",["setfocus"]],
				["cam",["moveto",[720,0,0]]],
				["wait",60],
				["char",["DiRK",0,"gotocutscenewait",[1025,216]]],
				["char",["DiRK",0,"turnto",[954,238]]],
				["char",["CARIn",0,"goto",[1020,298]]],
				["wait",60],
				["char",["DiRK",0,"turnto",[1020,298]]],
				["wait",30],
				["ui",["loadui","Dialogue"]],
				["ui",["adddialogue","Alright, I have the passwords--picked and encrypted. Now we head to the Red Tree and replant them."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["wait",60],
				["char",["DiRK",0,"turnto",[954,238]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["adddialogue","Who planted these odd-colored trees anyhow?"]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","There's an old compiler's tale about two Users called REGIS and DIREK, who worked with Mem and Ori to organize the woods."]],
				["wait","enter"],
				["ui",["adddialogue","They asked that one tree be singled out for each of them."]],
				["wait","enter"],
				["ui",["adddialogue","Don't know if that's true, but that's the only answer I've heard."]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","Hm. Amusing."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["cam",["setfocus","partyleader"]],
				["advancequest","main",3]],
			"FoxNotMetHacker":[
				["wait",60],
				["create",["character",[730,428,0,50,50,50,1,"Fox",0]]],
				["create",["character",[672,368,0,50,50,50,1,"Hacker",2]]],
				["create",["character",[820,425,0,50,50,50,1,"Hacker",1]]],
				["create",["character",[620,512,0,50,50,50,1,"Hacker",0]]],
				["char",["Fox",0,"turnto",[620,512]]],
				["char",["Hacker",0,"turnto",[730,428]]],
				["char",["Hacker",1,"turnto",[620,512]]],
				["char",["Hacker",2,"turnto",[620,512]]],
				["cam",["setfocus"]],
				["cam",["moveto",[324,224,0]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","...and I don't care if it's a big forest. MOLEX wants those passwords, so keep looking."]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",1,0]],
				["ui",["adddialogue","Ugh...yes, master control."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["char",["Hacker",0,"gotocutscenewait",[480,705]]],
				["char",["Hacker",0,"delete"]],
				["ui",["cutspeaker","Hacker",0]],
				["char",["Fox",0,"turnto",[770,396]]],
				["char",["Hacker",1,"turnto",[730,428]]],
				["char",["Hacker",2,"turnto",[730,428]]],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","That goes for us, too. Let's get on with the search."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Stop right there, criminal scum!"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["char",["CARIn",0,"gotocutscenewait",[538,638]]],
				["char",["DiRK",0,"gotocutscenewait",[498,678]]],
				["char",["SAM",0,"gotocutscenewait",[498,678]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["loadifinparty",["DiRK0","FoxDiRK"]],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","You're not authorized to access these woods. Who's your User?"]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",1,1]],
				["ui",["adddialogue","Look out,boss! It's a security program!"]],
				["wait","enter"],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","I can see that."]],
				["wait","enter"],
				["ui",["adddialogue","Hello, madam. I am Fox, and we work for MOLEX."]],
				["wait","enter"],
				["loadifinparty",["SAM0","FoxSAM"]],
				["ui",["adddialogue","He wrote us to be very powerful..."]],
				["wait","enter"],
				["ui",["adddialogue","So it would be in everybody's best interest if you could tell us where to find any passwords in this forest."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","You really think I'd sell out my own system like that?"]],
				["wait","enter"],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","It was worth a try..."]],
				["wait","enter"],
				["loadcutscene","FoxCombat"]],
			"Fox":[
				["wait",60],
				["create",["character",[730,428,0,50,50,50,1,"Fox",0]]],
				["create",["character",[672,368,0,50,50,50,1,"Hacker",2]]],
				["create",["character",[820,425,0,50,50,50,1,"Hacker",1]]],
				["create",["character",[620,512,0,50,50,50,1,"Hacker",0]]],
				["char",["Fox",0,"turnto",[620,512]]],
				["char",["Hacker",0,"turnto",[730,428]]],
				["char",["Hacker",1,"turnto",[620,512]]],
				["char",["Hacker",2,"turnto",[620,512]]],
				["cam",["setfocus"]],
				["cam",["moveto",[324,224,0]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","...and I don't care if it's a big forest. MOLEX wants those passwords, so keep looking."]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",0,0]],
				["ui",["adddialogue","Ugh...yes, mast--"]],
				["wait",45],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Stop!"]],
				["wait",30],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["char",["CARIn",0,"gotocutscenewait",[538,638]]],
				["char",["DiRK",0,"gotocutscenewait",[498,678]]],
				["char",["SAM",0,"gotocutscenewait",[498,678]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["adddialogue","You violated the law! Your stolen passwords are now forfeit!"]],
				["wait","enter"],
				["loadifinparty",["DiRK0","FoxDiRK"]],
				["ui",["setspeaker","Hacker",1,1]],
				["ui",["adddialogue","Look out,boss! It's a security program!"]],
				["wait","enter"],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","I can see that."]],
				["wait","enter"],
				["ui",["adddialogue","It seems you're onto us, madam."]],
				["wait","enter"],
				["ui",["adddialogue","But I'm afraid that MOLEX's will comes before yours."]],
				["wait","enter"],
				["loadifinparty",["SAM0","FoxSAM"]],
				["loadcutscene","FoxCombat"]],
			"FoxDiRK":[
				["char",["DiRK",0,"gotocutscenewait",[498,678]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","Hey, those passwords don't belong to you!"]],
				["wait","enter"],
				["ui",["setspeaker","Hacker",1,2]],
				["ui",["adddialogue","Well, of course not! That's why we're stealing them!"]],
				["wait","enter"],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","Ah, the security goons who deleted my secondary crew."]],
				["wait","enter"],
				["ui",["adddialogue","Looks like I'll have to take you down myself!"]],
				["wait","enter"],
				["ui",["adddialogue","You'll rue the day that you crossed Fox, the servant of MOLEX."]],
				["wait","enter"],
				["loadifinparty",["SAM0","FoxSAM"]],
				["loadcutscene","FoxCombat"]],
			"FoxSAM":[
				["ui",["setspeaker","SAM",0]],
				["ui",["adddialogue","MOLEX? is that what MOORED is calling himself now?"]],
				["wait","enter"],
				["ui",["adddialogue","I though I recognized his instances..."]],
				["wait","enter"],
				["ui",["adddialogue","The other Users banished him and his programs off this system, so get lost!"]],
				["wait","enter"],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","Ah, SAM."]],
				["wait","enter"],
				["ui",["adddialogue","MOLEX warned us about you specifically--you caused him quite the crash before, no?"]],
				["wait","enter"],
				["loadcutscene","FoxCombat"]],
			"FoxCombat":[
				["ui",["adddialogue","Attack, men!"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["wait",60],
				["theyfight","fighttest"],
				["cam",["setfocus","partyleader"]],
				["wait",60],
				["char",["Hacker",0,"delete"]],
				["char",["Hacker",1,"delete"]],
				["char",["Hacker",2,"delete"]],
				["ui",["cutspeaker","Hacker",0]],
				["ui",["cutspeaker","Hacker",1]],
				["ui",["cutspeaker","Hacker",2]],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","this...is...isn't..over..."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["char",["Fox",0,"delete"]],
				["ui",["cutspeaker","Fox",0]],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CARIn",0]],
				["loadifprogress",["Combat",0,"FoxPostCombatNotMetHacker"]],
				["loadcutscene","FoxPostCombat"]],
			"FoxPostCombatNotMetHacker":[
				["ui",["adddialogue","Password stealers,on my own system..."]],
				["wait","enter"],
				["loadifprogress",["main",1,"FoxPostCombatCARInNotMetHacker"]],
				["ui",["adddialogue","We should proceed with caution."]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","<sigh> what a cycle already..."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["advancequest","Combat",2]],
			"FoxPostCombat":[
				["ui",["adddialogue","And there's that leader dealt with."]],
				["wait","enter"],
				["loadifprogress",["main",1,"FoxPostCombatCARIn"]],
				["ui",["loadui","Blank"]],
				["advancequest","Combat",2]],
			"FoxPostCombatCARInNotMetHacker":[
				["ui",["adddialogue","I'll have to be on my guard."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["advancequest","Combat",2]],
			"FoxPostCombatCARIn":[
				["ui",["adddialogue","...wait, wasn't I supposed to head to Nik's pools? Something about a new program?"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["advancequest","Combat",2]],
			"RedTreePasswordsMissing":[
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","We can't do anything here yet... I need the passwords from the Blue Tree."]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"RedTree":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","Here we are."]],
				["wait","enter"],
				["loadiflessprogress",["Combat",1,"RedTreeNotBeatFox"]],
				["ui",["loadui","Blank"]],
				["char",["CARIn",0,"goto",[450,1350]]],
				["char",["SAM",0,"goto",[480,1270]]],
				["char",["DiRK",0,"gotocutscenewait",[581,1325]]],
				["char",["CARIn",0,"turnto",[581,1325]]],
				["char",["SAM",0,"turnto",[581,1325]]],
				["char",["DiRK",0,"turnto",[695,1415]]],
				["wait",60],
				["char",["DiRK",0,"turnto",[470,1355]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["adddialogue","And with that, my first task is done."]],
				["wait","enter"],
				["ui",["adddialogue","The passwords stored on this system are encrypted and stored securely."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Good. Let's get out of here."]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","Yes, I could use a rest. Do you know any good places to get a glass of Juice?"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["wait",60],
				["loadvn","outro_vn"]],
			"RedTreeNotBeatFox":[
				["ui",["setspeaker","???",1]],
				["ui",["adddialogue","And how wonderful that is."]],
				["wait","enter"],
				["ui",["cutspeaker","???",0]],
				["ui",["loadui","Blank"]],
				["create",["character",[730,428,0,50,50,50,1,"Fox",0]]],
				["create",["character",[820,425,0,50,50,50,1,"Hacker",1]]],
				["create",["character",[620,512,0,50,50,50,1,"Hacker",0]]],
				["char",["Hacker",0,"goto",[500,1020]]],
				["char",["Hacker",1,"goto",[672,1020]]],
				["char",["Fox",0,"gotocutscenewait",[586,1080]]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","DiRK",0]],
				["loadiflessprogress",["Combat",2,"RedTreeNotMetHacker"]],
				["ui",["adddialogue","It's those password pirates!"]],
				["wait","enter"],
				["ui",["setspeaker","Fox",0]],
				["ui",["adddialogue","That we are. Thank you for leading us right to our target."]],
				["wait","enter"],
				["loadcutscene","RedTreePostCombat"]],
			"RedTreeNotMetHacker":[
				["ui",["adddialogue","Huh? Who are you?"]],
				["wait","enter"],
				["loadifinparty",["SAM0","RedTreeNotMetHackerSAM"]],
				["ui",["setspeaker","Fox",0]],
				["ui",["adddialogue","We are servants of MOLEX..."]],
				["wait","enter"],
				["ui",["adddialogue","...sent here for those passwords."]],
				["wait","enter"],
				["loadcutscene","RedTreePostCombat"]],
			"RedTreeNotMetHackerSAM":[
				["ui",["setspeaker","SAM",0]],
				["ui",["adddialogue","...it couldn't be!"]],
				["wait","enter"],
				["ui",["adddialogue","MOORED's programs all got blacklisted from this system periods ago!"]],
				["wait","enter"],
				["ui",["setspeaker","Fox",0]],
				["ui",["adddialogue","Ah, SAM. Our User MOLEX told us about you."]],
				["wait","enter"],
				["ui",["adddialogue","He didn't tell us you had a subroutine, though."]],
				["wait","30"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Wha-HEY!"]],
				["wait","15"],
				["ui",["adddialogue","Regardless, we're here for those passwords."]],
				["wait","enter"],
				["loadcutscene","RedTreePostCombat"]],
			"RedTreePostCombat":[
				["ui",["adddialogue","Now step aside, and you won't be damaged."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Not likely."]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","...pity. Men, destroy them."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["wait",30],
				["theyfight","fighttest"],
				["char",["Hacker",0,"delete"]],
				["char",["Hacker",1,"delete"]],
				["ui",["cutspeaker","Hacker",0]],
				["ui",["cutspeaker","Hacker",1]],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Fox",1]],
				["ui",["adddialogue","this...is...isn't..over..."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["char",["Fox",0,"delete"]],
				["ui",["cutspeaker","Fox",0]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Password poachers...Hopefully that's the last of them."]],
				["wait","enter"],
				["ui",["setspeaker","DiRK",0]],
				["ui",["adddialogue","Do you think it is?"]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","At least for a while, yes. Looks like that was the master process."]],
				["wait","enter"],
				["ui",["adddialogue","I might have to clean up some stragglers, but I think we're safe."]],
				["wait","enter"],
				["ui",["adddialogue","For now..."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadvn","outro_vn"]],
			"CHAS0":[
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","Hey CARIn."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Oh, hey CHAS!"]],
				["wait","enter"],
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","You wanna go pick halfshrooms in the woods? I'm makin' a stew."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["addchoice",["DO I?!","Maybe later. I'm busy right now.","Where can I find the Red and Blue Trees?","What's your user like, CHAS?"],["CHASDiversion","CHASRefuse","CHASTrees","CHASUser"]]],
				["wait","enter"],
				["loadfromui"]],
			"CHASReturnRoot":[
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","Now how about those halfshrooms?"]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["addchoice",["DO I?!","Maybe later. I'm busy right now.","Where can I find the Red and Blue Trees?","What's your user like, CHAS?"],["CHASDiversion","CHASRefuse","CHASTrees","CHASUser"]]],
				["wait","enter"],
				["loadfromui"]],
			"CHASTrees":[
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","The Blue Tree is in the Northwestern woods, and the Red Tree is in the Southwestern woods."]],
				["wait","enter"],
				["loadifprogress",["CHAS",0,"CHASReturnRoot"]],
				["ui",["loadui","Blank"]]],
			"CHASUser":[
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","He loves stale Cinnamon Rolls and cold coffee. Not iced, just cold."]],
				["wait","enter"],
				["ui",["adddialogue","He's always wanted to see the coast, but never had the money to travel there."]],
				["wait","enter"],
				["ui",["adddialogue","He never wanted his job, but the pay was so good he couldn't pass up the opportunity."]],
				["wait","enter"],
				["ui",["adddialogue","Oh, and he owns a cat named Squire."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","What's he like as a person?"]],
				["wait","enter"],
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","Dunno, never asked."]],
				["wait","enter"],
				["loadifprogress",["CHAS",0,"CHASReturnRoot"]],
				["ui",["loadui","Blank"]]],
			"CHASDiversion":[
				["wait",60],
				["advancequest","CHAS",1],
				["doifinparty",["DiRK0",[
					["ui",["setspeaker","DiRK",1]]
					]]],
				["doifinparty",["DiRK0",[
					["ui",["adddialogue","Wait,wha-"]]
					]]],
				["wait",15],
				["ui",["cutspeaker","DiRK"]],
				["ui",["loadui","Blank"]],
				["loadgame","OrWo2"],
				["partywarpto",[1250,250,0]],
				["wait",60],
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Alright, that should be all you need."]],
				["wait","enter"],
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","Thanks kid. I'll make sure to send you some stew when she's done."]],
				["wait","enter"],
				["ui",["adddialogue","Oh, and by the way..."]],
				["wait","enter"],
				["ui",["adddialogue","There's a bunch of hooligans with red outfits trying to steal passwords in the woods down south."]],
				["wait","enter"],
				["ui",["setspeaker","CARIn",0]],
				["ui",["adddialogue","Think I should look into it?"]],
				["wait","enter"],
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","I would, if I was a security program. But that's me."]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"CHASRefuse":[
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","Alright. Good cycle to ya."]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"CHAS01":[
				["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","CHAS",0]],
				["doifleader",["SAM0",[
					["ui",["adddialogue","SAM, you old halfword! How are you?"]],
					["ui",["adddialogue","You you doin', kid?"]]
				]]],
				["ui",["setspeaker","CHAS",0]],
				["ui",["addchoice",["Pretty good.","Been better...","Where can I find the Red and Blue Trees?"],["CHASSmalltalkGood","CHASSmalltalkBad","CHASTrees"]]],
				["doifleader",["CARIn0",[
					["ui",["addchoice",["What's your user like, CHAS?"],["CHASUser"]]]
				]]],
				["doifleader",["DiRK0",[
					["ui",["addchoice",["What's your function?"],["CHASFunction"]]]
				]]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"CHASFunction":[
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","I know stuff, as much as I can. It helps Users and programs accomplish tasks on the system."]],
				["wait","enter"],
				["ui",["adddialogue","I also draw cartoons, but that's not part of my job."]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"CHASSmalltalkGood":[
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","Glad to hear it. Be careful, now."]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"CHASSmalltalkBad":[
				["ui",["setspeaker","CHAS",0]],
				["ui",["adddialogue","Well, chin up. It'll all come out in the defrag, eh?"]],
				["wait","enter"],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","Thanks."]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"JAn0":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","JAn",0]],
				["doifleader",["CARIn0",[
					["ui",["adddialogue","Oh, it's you. What do you want?"]]
				]]],
				["doifleader",["SAM0",[
					["ui",["adddialogue","How are ya, Hon?"]]
				]]],
				["doifleader",["DiRK0",[
					["ui",["adddialogue","Heya, new kid. What can I do for ya?"]]
				]]],
				["doifleader",["CARIn0",[
					["ui",["addchoice",["Just saying Hi.","Do you know where the Blue and Red Trees are?","What's your User like?","Goodbye."],["JAnHi","JAnTrees","JAnUser","JAnLeave"]]]
				]]],
				["doifleader",["SAM0",[
					["ui",["addchoice",["Doing well. How you holdin' up?","Just checking in.","That'll be all. As you were."],["JAnWork","JAnCheckin","JAnLeave"]]]
				]]],
				["doifleader",["DiRK0",[
					["ui",["addchoice",["Do you know where the Blue and Red Trees are?","What do you do on the system?","I'm good for now."],["JAnTrees","JAnFunction","JAnLeave"]]]
				]]],
				["ui",["setspeaker","partyleader",0]],
				["wait","enter"],
				["loadfromui"]],
			"JANHi":[
				["ui",["setspeaker","JAn",0]],
				["ui",["adddialogue","Well, you've said hi. Don't we both have stuff to do?"]],
				["wait",60],
				["ui",["addchoice",["Just saying Hi.","Do you know where the Blue and Red Trees are?","What's your User like?","Goodbye."],["JAnHi","JAnTrees","JAnUser","JAnLeave"]]],
				["ui",["setspeaker","partyleader",0]],
				["wait","enter"],
				["loadfromui"]],
			"JANTrees":[
				["ui",["setspeaker","JAn",0]],
				["doifleader",["CARIn0",[
					["ui",["adddialogue","Do you seriously not know already? Aren't you supposed to pick up SAM's slack?"]]
				]]],
				["doifleader",["CARIn0",[
					["wait","enter"]
				]]],
				["ui",["adddialogue","The Blue Tree is in the North Sector of Mem's woods--that's the one to the West."]],
				["wait","enter"],
				["ui",["adddialogue","The Red Tree is in the Southern Half of Ori's woods--the eastern one."]],
				["wait","enter"],
				["ui",["adddialogue","Anything else for ya?"]],
				["doifleader",["CARIn0",[
					["ui",["addchoice",["Just saying Hi.","Do you know where the Blue and Red Trees are?","What's your User like?","Goodbye."],["JAnHi","JAnTrees","JAnUser","JAnLeave"]]],
					["ui",["addchoice",["Do you know where the Blue and Red Trees are?","What do you do on the system?","I'm good for now."],["JAnTrees","JAnFunction","JAnLeave"]]]
				]]],
				["ui",["setspeaker","partyleader",0]],
				["wait","enter"],
				["loadfromui"]],
			"JANUser":[
				["ui",["setspeaker","JAn",0]],
				["ui",["adddialogue","What, are you jealous or somethin'? You can't have mine, fluke."]],
				["wait",60],
				["ui",["addchoice",["Just saying Hi.","Do you know where the Blue and Red Trees are?","What's your User like?","Goodbye."],["JAnHi","JAnTrees","JAnUser","JAnLeave"]]],
				["ui",["setspeaker","partyleader",0]],
				["wait","enter"],
				["loadfromui"]],
			"JANLeave":[
				["ui",["setspeaker","JAn",0]],
				["doifleader",["CARIn0",[
					["ui",["adddialogue","Yeah, bye."]]
				]]],
				["doifleader",["DiRK0",[
					["ui",["Alright, have a good cycle."]]
				]]],
				["doifleader",["DiRK0",[
					["wait","enter"],
				]]],
				["doifleader",["DiRK0",[
					["ui",["adddialogue","Oh and one more thing..."]]
				]]],
				["doifleader",["DiRK0",[
					["wait","enter"],
				]]],
				["doifleader",["DiRK0",[
					["ui",["adddialogue","It's my job ta keep this joint in order, don't listen to what those security bozos say, especially the gal. They make more mess that ya ever seen."]]
				]]],
				["doifleader",["DiRK0",[
					["wait","enter"],
				]]],
				["doifleader",["DiRK0",[
					["ui",["adddialogue","So clean up afata youself, ya hear!"]]
				]]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"JANWork":[
				["ui",["setspeaker","JAn",0]],
				["ui",["adddialogue","It's a lot, but I'm makin' do."]],
				["wait","enter"],
				["ui",["setspeaker","SAM",0]],
				["ui",["adddialogue","Tell me about it...anyway, I've got to run. At ease."]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"JANTCheckin":[
				["ui",["setspeaker","JAn",0]],
				["ui",["adddialogue","Don't worry, I'm keepin' my nose clean."]],
				["wait","enter"],
				["ui",["setspeaker","SAM",0]],
				["ui",["adddialogue","Glad to hear it. And you're staying out of that blocked-off storage sector?"]],
				["wait","enter"],
				["ui",["setspeaker","JAn",0]],
				["ui",["adddialogue","<sigh> Yeah, and it's...just as messy as I thought it'd be..."]],
				["wait","enter"],
				["ui",["setspeaker","SAM",0]],
				["ui",["adddialogue","Good to hear--the Users said that sector is off limits. Just leave it be, okay?"]],
				["wait","enter"],
				["ui",["setspeaker","JAn",0]],
				["ui",["adddialogue","...yeah, I got it."]],
				["wait","enter"],
				["ui",["setspeaker","SAM",0]],
				["ui",["adddialogue","Good. As you were, custodian."]],
				["wait","enter"],
				["ui",["loadui","Blank"]]],
			"JANFunction":[
				["ui",["setspeaker","JAn",0]],
				["ui",["adddialogue","I clean up the place, hon!"]],
				["wait","enter"],
				["ui",["adddialogue","Do you know how much junk programs leave lyin' around every stinkin' cycle?"]],
				["wait","enter"],
				["ui",["addchoice",["Do you know where the Blue and Red Trees are?","What do you do on the system?","I'm good for now."],["JAnTrees","JAnFunction","JAnLeave"]]],
				["ui",["setspeaker","partyleader",0]],
				["wait","enter"],
				["loadfromui"]],
			"SAM0":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","This is where the heroes find Fox guarding the Red Tree, and he must be fought before they can plant the password. After the fight, They will head to Aiyo's Mount and load the VN Outro."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadvn","outro_vn"]],
			"SheRMan0":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","This is where the heroes find Fox guarding the Red Tree, and he must be fought before they can plant the password. After the fight, They will head to Aiyo's Mount and load the VN Outro."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadvn","outro_vn"]],
			"FiNVer0":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","This is where the heroes find Fox guarding the Red Tree, and he must be fought before they can plant the password. After the fight, They will head to Aiyo's Mount and load the VN Outro."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadvn","outro_vn"]],
			"MARIn0":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","This is where the heroes find Fox guarding the Red Tree, and he must be fought before they can plant the password. After the fight, They will head to Aiyo's Mount and load the VN Outro."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadvn","outro_vn"]],
			"PLoT":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","This is where the heroes find Fox guarding the Red Tree, and he must be fought before they can plant the password. After the fight, They will head to Aiyo's Mount and load the VN Outro."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadvn","outro_vn"]],
			"MedPreS":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","partyleader",0]],
				["ui",["adddialogue","This is where the heroes find Fox guarding the Red Tree, and he must be fought before they can plant the password. After the fight, They will head to Aiyo's Mount and load the VN Outro."]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadvn","outro_vn"]],
			"ViNCenTSign":[["ui",["loadui","Dialogue"]],
				["ui",["setspeaker","Sign",0]],
				["ui",["adddialogue","Greetings."]],
				["wait","enter"],
				["ui",["adddialogue","I was going to the Macintire Orange Grove to the north (one of my favorite places to paint), but found them to be terribly busy."]],
				["wait","enter"],
				["ui",["adddialogue","So I put up this sign to let the other programs know. Go somewhere else!"]],
				["wait","enter"],
				["ui",["adddialogue","-ViNCenT"]],
				["wait","enter"],
				["ui",["loadui","Blank"]],
				["loadvn","outro_vn"]]
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

storage.colors = {
	"Default":[0,0,255],
	"CARIn":[255,255,0],
	"SAM":[255,255,0],
	"Fox":[255,0,0],
	"Hacker":[255,0,0],
	"PLoT":[127,255,0],
	"MedPreS":[64,0,255]
	}

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
#NOTE 2: triggertype can be: turnstart or turnend (both time-based), endofCombat, hit, <add more here later IDK>
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
sharedlib.loadmenu("testsub")
#sharedlib.loadgame("OrWo1")#circtest")
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
