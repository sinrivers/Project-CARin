"""
Filename: gameutils.py
Author: Taliesin Reese
Version: 10.1
Date: 11/18/2025
Purpose: Gameplay tools for Project CARIn
"""
#setup
import sharedlib
import storage
import pygame
import math
import copy
import random
import ais
import soundutils

#classes
class object3d(sharedlib.gameobject):
	def __init__(self,x=0,y=0,z=0,w=0,h=0,d=0):
		super().__init__()
		self.x = x
		self.y = y
		self.z = z
		self.w = w
		self.h = h
		self.d = d
		self.speed = [0,0,0]
		self.grounded = True
		self.traction = 0.5
		self.gravity = 1

	def todata(self):
		return ["object3d",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded]]

	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.z = data[2]
		self.w = data[3]
		self.h = data[4]
		self.d = data[5]
		self.speed = copy.deepcopy(data[6])
		self.grounded = data[7]

	def render(self):
		pygame.draw.rect(storage.window, (255,0,0), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h))

	def collidepoint(self,point):
		if self.x <= point[0] <=self.x + self.w:
			if self.y <= point[1] <= self.y+self.h:
				if self.z >= point[2] >= self.z-self.d:
					return True
		return False

	def novertcollide(self,tester):
		if not isinstance(tester,object3d):
			return False
		if self.x<=tester.x<=self.x+self.w or self.x<=tester.x+tester.w<=self.x+self.w:
			if self.y<=tester.y-1<=self.y+self.h or self.y<=tester.y-1+tester.h<=self.y+self.h:
				return True
		return False
				
	def collidecheck(self,tester):
		pass

	def interact(self,hitter):
		#print("This is a test of the Emergency Brodcast Cube")
		cutsceneplayer("test2")

	def update(self):
		self.rendered = False
		self.vertsort = [self.y,self.z]

	def getpoints(self):
		self.center = [self.x+self.w/2, self.y+self.h/2, self.z-self.d/2]
		self.left = [self.x, self.y + self.h/2, self.z-self.d/2]
		self.right = [self.x + self.w, self.y + self.h/2, self.z-self.d/2]
		self.front = [self.x + self.w/2, self.y + self.h, self.z-self.d/2]
		self.back = [self.x + self.w/2, self.y, self.z-self.d/2]
		self.top = [self.x + self.w/2, self.y + self.h/2, self.z-self.d]
		self.bottom = [self.x + self.w/2, self.y + self.h/2, self.z]
		


class character(object3d):
	def __init__(self,x=0,y=0,z=0,w=0,h=0,d=0,state=0,name=None,id = None):
		super().__init__(x,y,z,w,h,d)
		self.name = name
		#NOTE: This number is here so we can uniquely identify characters--thus it MUST BE UNIQUE or it loses it's purpose.
		#NOTE 2: Minor NPCs and Enemies who aren't part of a cutscene can scrape by without this, thus it's initialized to Null.
		self.id = id
		#print("SPAWNING:",self.name,self.id)
		self.pullglobalstats()
		#the type of character we're dealing with is determined by self.state.
		#Note that self.state was originally supposed to lock or unlock certain actions (i.e. the second hit of a two-hit combo),
		#so this may need it's own variable if such a use ever arrives.
		#States are as follows: 0-NPC Scripted Behaviors. 1-Enemy. 2-NPC follower. 3-Active Player Character.
		self.state = state
		if self.state > 1:
			storage.party.append(self)
		if self.state == 3:
			storage.camera.target = self
		self.speed = [0,0,0]
		self.angle = 0

		self.framecounter = 0
		self.framenumber = 0
		self.animname = "stand0"
		self.animpriority = False

		self.grounded = True
		if self.name == None or not hasattr(ais,self.name+"Combat"):
			self.combatAI = getattr(ais, "MissingnoCombat")
		else:
			self.combatAI = getattr(ais, self.name+"Combat")
		self.traction = .5
		self.gravity = 1
		self.interactd = 50
		self.interactpoint = [self.x+self.w+self.interactd,self.y+self.h/2,self.z-self.d/2]
		self.combatactions = []
		self.combatactive = False
		self.combatactionsindex = 0
		self.combattarget = []
		self.iframes = 0
		self.getpoints()

	def todata(self):
		self.writeglobalstats()
		return ["character",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.framecounter,self.framenumber,self.name,self.combatactive,self.state,self.iframes,self.angle,self.id]]

	def fromdata(self,data):
		#NOTE: add updateable stats later
		self.x = data[0]
		self.y = data[1]
		self.z = data[2]
		self.w = data[3]
		self.h = data[4]
		self.d = data[5]
		self.speed = copy.deepcopy(data[6])
		self.angle = data[14]
		self.grounded = data[7]
		self.framecounter = data[8]
		self.framenumber = data[9]
		self.name = data[10]
		self.combatactive = data[11]
		self.state = data[12]
		self.iframes = data[13]
		self.id = data[15]
		self.animname = "stand0"
		self.animpriority = False
		self.pullglobalstats()
		if self.name == None or not hasattr(ais,self.name+"Combat"):
			self.combatAI = getattr(ais, "MissingnoCombat")
		else:
			self.combatAI = getattr(ais, self.name+"Combat")
		if self.state > 1:
			storage.party.append(self)
		if self.state == 3:
			storage.camera.target = self
	def interact(self,hitter):
		if self.name == None or (not hasattr(ais,self.name+"Interact") and not hasattr(ais,self.name+str(self.id)+"Interact")):
			name = "Missingno"
		elif not hasattr(ais, self.name+str(self.id)+"Interact"):
			name = self.name
		else:
			name = self.name + str(self.id)
		getattr(ais, name+"Interact")(self)
	def update(self):
		super().update()
		if self.iframes > 0:
			self.iframes -= storage.deltatime
		if self.getstat("damage") > self.getstat("maxhp"):
			self.setstat("damage",self.getstat("maxhp")-1)
		#process whatever actions needed for this character
		if storage.actlock == False:
			self.combatactions = []
			for item in self.timedfx:
				if item[0] in ["turnstart","turnend","time"]:
					item[1] -= 1
					if item[1] <= 0:
						self.timedfx.remove(item)
						getattr(self,item[2])(*item[3])
			match self.state:
				case 0:
					pass
				case 1:
					self.enemyupdates()
				case 2:
					self.followupdates()
				case 3:
					self.controlupdates()
			self.animpicker()
		else:
			#print("MAAHHH")
			#if self.combatactive == True:
			self.animpicker()
			if self.combatactions != []:
				doit = self.combatactions[self.combatactionsindex][0]
				getattr(self,doit)()

			#NOTE: It is stupid that this second check has to be here, but it does. Otherwise, we can't back out of target selection and stuff like that. Can somebody propose a better solution? Who am I kidding, nobody else reads these comments...
			if self.combatactions != []:
				if self.combatactionsindex == len(self.combatactions):
					self.combatactive = False
					self.combattarget = []
					self.combatactions = []
					self.combatactionsindex = 0
		#natural decrease of speed
		self.physics()
		#update locations based on speed
		self.x += self.speed[0]/2*storage.deltatime
		self.y += self.speed[1]/2*storage.deltatime
		self.z += self.speed[2]/2*storage.deltatime
		if not self.grounded:
			self.z += storage.deltatime * (self.speed[2]-storage.deltatime/2)
		self.getpoints()
		#check collisions with ground
		self.checkcollide()
		#this is for deltatime reasons.
		self.physics()

	def getstat(self,stat):
		mult = 1
		if stat == "maxhp":
			index = 0
		elif stat == "maxdata":
			index = 1
		elif stat == "priority":
			index = 2
			mult = 1.25
		elif stat == "read":
			index = 3
		elif stat == "write":
			index = 4
		elif stat == "execute":
			index = 5
		elif stat == "obfuscation":
			index = 6
		elif stat == "persistence":
			index = 7
		elif stat == "damage":
			return self.modstats[8]
		elif stat == "spentdata":
			return self.modstats[9]
		return (self.basestats[index] + self.modstats[index])*mult

	def alterstat(self,stat = None,amt = None):
		if stat == None:
			stat = self.combatactions[self.combatactionsindex][1]
		if amt == None:
			amt = self.combatactions[self.combatactionsindex][2]
		if stat == "maxHP":
			index = 0
		elif stat == "maxDATA":
			index = 1
		elif stat == "priority":
			index = 2
		elif stat == "read":
			index = 3
		elif stat == "write":
			index = 4
		elif stat == "execute":
			index = 5
		elif stat == "obfuscation":
			index = 6
		elif stat == "persistence":
			index = 7
		elif stat == "damage":
			index = 8
		elif stat == "spentdata":
			index = 9
		self.modstats[index] += amt
		if self.combatactive:
			self.combatactionsindex += 1

	def pullglobalstats(self):
		if self.name not in storage.basestats.keys():
			self.basestats = copy.deepcopy(storage.basestats["Missingno"])
		else:
			self.basestats = copy.deepcopy(storage.basestats[self.name])
		if self.name in storage.modstats.keys():
			self.modstats = copy.deepcopy(storage.modstats[self.name])
		else:
			self.modstats = copy.deepcopy(storage.modstats["Missingno"])
		if self.name not in storage.timedfx.keys():
			self.timedfx = copy.deepcopy(storage.timedfx["Missingno"])
		else:
			
			self.timedfx = copy.deepcopy(storage.timedfx[self.name])

	def writeglobalstats(self):
		if self.name == None:
			storage.basestats["Missingno"] = copy.deepcopy(self.basestats)
			storage.modstats["Missingno"] = copy.deepcopy(self.modstats)
			storage.timedfx["Missingno"] = copy.deepcopy(self.timedfx)
		else:
			storage.basestats[self.name] = copy.deepcopy(self.basestats)
			storage.modstats[self.name] = copy.deepcopy(self.modstats)
			storage.timedfx[self.name] = copy.deepcopy(self.timedfx)

	def addtimedfx(self,triggertype = None,triggermods = None,function = None,arguments = None):
		if triggertype == None:
			triggertype = self.combatactions[self.combatactionsindex][1]
		if triggermods == None:
			triggermods = self.combatactions[self.combatactionsindex][2]
		if function == None:
			function = self.combatactions[self.combatactionsindex][3]
		if arguments == None:
			arguments = self.combatactions[self.combatactionsindex][4]
		self.timedfx.append([triggertype,triggermods,function,arguments])
		if self.combatactive:
			self.combatactionsindex += 1

	def checkavailabledata(self,num = None):
		if num == None:
			num = self.combatactions[self.combatactionsindex][1]
		if num > self.getstat("maxdata") - self.getstat("spentdata"):
			if self.state > 1:
				self.combatactions = []
				self.combatactionsindex = 0
			else:
				self.combatAI(self)
		else:
			self.combatactionsindex += 1
			

	def setanim(self,name,angle = None,request=False):
		if angle != None:
			fullname = name + str(angle)
		else:
			fullname = name
		if self.animpriority == False or request == True:
			if self.animname != fullname:
				if name not in self.animname:
					self.framenumber = 0
					self.framecounter = 0
				self.animname = fullname
				self.animpriority = request
		else:
			self.queuedanim = fullname

	def animpicker(self):
		#pick an animation
		roundedangle = (45*round(self.angle/45))%360
		if abs(self.speed[0]) > 0 or abs(self.speed[1] > 0):
			self.setanim("walk",str(roundedangle))
		else:
			self.setanim("stand",str(roundedangle))
		if self.speed[2] < 0:
			self.setanim("airup",str(roundedangle))
		elif self.speed[2] > 0:
			self.setanim("airdown",str(roundedangle))
			
	def animupdate(self):
		self.framecounter += storage.deltatime
		#NOTE: This is butt-covering. It's here to prevent an animation change from crashing if angled animations have divers frame counts (which should be avoided, but just in case).
		if len(storage.animinfo[self.name]["anims"][self.animname]) <= self.framenumber:
			self.framenumber = 0
			self.framecounter = 0
		if storage.animinfo[self.name]["anims"][self.animname][self.framenumber][1] < self.framecounter:
			self.framecounter -= storage.animinfo[self.name]["anims"][self.animname][self.framenumber][1]
			self.framenumber += 1
			if self.framenumber >= len(storage.animinfo[self.name]["anims"][self.animname]):
				self.framenumber = 0
				if self.animpriority:
					if hasattr(self,"queuedanim"):
						self.animname = self.queuedanim

	def render(self):
		if self.name == None or self.name not in storage.animinfo.keys(): 
			if self.state == 3:
				pygame.draw.rect(storage.spritecanvas, (0,0,100), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
				pygame.draw.rect(storage.spritecanvas, (0,0,155), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
				pygame.draw.rect(storage.spritecanvas, (0,0,255), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
			elif self.state == 1:
				pygame.draw.rect(storage.spritecanvas, (100,0,0), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
				pygame.draw.rect(storage.spritecanvas, (155,0,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
				pygame.draw.rect(storage.spritecanvas, (255,0,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
			else:
				pygame.draw.rect(storage.spritecanvas, (0,100,100), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
				pygame.draw.rect(storage.spritecanvas, (0,155,155), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
				pygame.draw.rect(storage.spritecanvas, (0,255,255), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
		else:

			self.animupdate()
			pygame.draw.rect(storage.spritecanvas, (0,0,100), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
			
			holder=storage.animinfo[self.name]["frames"][storage.animinfo[self.name]["anims"][self.animname][self.framenumber][0]]
			if len(storage.animinfo[self.name]["anims"][self.animname][self.framenumber]) <= 2:
				storage.spritecanvas.blit(storage.spritesheet, [int(self.x+self.w/2-holder[2]/2-storage.camfocus[0]),
										int(self.y+self.h/2-holder[3]+self.z+self.d/2-storage.camfocus[1])],holder)
			else:
				holdermod = storage.spritesheet.get_width()-holder[0]-holder[2]
				storage.spritecanvas.blit(pygame.transform.flip(storage.spritesheet,1,0), [int(self.x+self.w/2-holder[2]/2-storage.camfocus[0]),
										int(self.y+self.h/2-holder[3]+self.z+self.d/2-storage.camfocus[1])],[holdermod,holder[1],holder[2],holder[3]])
	def checkcollide(self):
		self.grounded = False
		for obj in storage.objlist:
			if isinstance(obj,object3d):
				obj.collidecheck(self)
		if self.z >= 0:
			self.z = 0
			self.speed[2] = 0
			self.grounded = True

	def collidecheck(self,hitter):
		if self.iframes <= 0 and not storage.actlock:
			if self.state == 1 and hitter.state == 3:
				if self.collidepoint(hitter.center) != False:
					self.iframes = 300
					storage.runstate = save()
					self.delete()
					storage.winstate = save()
					sharedlib.loadgame("fighttest")
				else:
					pass

	def jump(self):
		self.grounded = False
		self.speed[2] = -self.getstat("priority")*3
		soundutils.playsound()

	def physics(self):
		if self.speed[0] > 0:
			if self.speed[0] < self.traction*storage.deltatime:
				self.speed[0] = 0
			else:
				self.speed[0] -= self.traction*storage.deltatime

		elif self.speed[0] < 0:
			if self.speed[0] > -self.traction*storage.deltatime:
				self.speed[0] = 0
			else:
				self.speed[0] += self.traction*storage.deltatime

		if self.speed[1] > 0:
			if self.speed[1] < self.traction*storage.deltatime:
				self.speed[1] = 0
			else:
				self.speed[1] -= self.traction*storage.deltatime

		elif self.speed[1] < 0:
			if self.speed[1] > -self.traction*storage.deltatime:
				self.speed[1] = 0
			else:
				self.speed[1] += self.traction*storage.deltatime
		if self.grounded == False:
			self.speed[2] += self.gravity*storage.deltatime

	def followupdates(self):
		for charac in storage.party:
			if charac.state == 3:
				dist = (charac.x-self.x)**2+(charac.y-self.y)**2+(charac.z-self.z)**2
				if dist > 5000:
					self.angle = math.atan2(self.y-charac.y,self.x-charac.x)*180/math.pi
					if self.z > charac.z and self.grounded == True:
						self.jump()
					self.speed[0] = -charac.getstat("priority")*math.cos(self.angle/180*math.pi)
					self.speed[1] = -charac.getstat("priority")*math.sin(self.angle/180*math.pi)
	def NPCupdates(self):
		if self.name == None:
			getattr(ais, "MissingnoIdle")(self)
		elif not hasattr(ais,self.name+str(self.id)+""):
			getattr(ais, self.name+"Idle")(self)
		else:
			getattr(ais, self.name+str(self.id)+"Idle")(self)
	def enemyupdates(self):
		self.NPCupdates()
		if self.iframes <= 0:
			for charac in storage.party:
				if charac.state == 3:
					dist = (charac.x-self.x)**2+(charac.y-self.y)**2+(charac.z-self.z)**2
					if dist < 100000:
						self.angle = math.atan2(self.y-charac.y,self.x-charac.x)*180/math.pi
						self.speed[0] = -self.getstat("priority")*math.cos(self.angle/180*math.pi)
						self.speed[1] = -self.getstat("priority")*math.sin(self.angle/180*math.pi)
					
	def controlupdates(self):
		#get control updates
		angleamt = [0,0]
		walk = False
		if storage.keys[pygame.K_a] or storage.dpad[0]:
			angleamt[0] = -1
			walk = True
		elif storage.keys[pygame.K_d] or storage.dpad[1]:
			angleamt[0] = 1
			walk = True
		if storage.keys[pygame.K_w] or storage.dpad[2]:
			angleamt[1] = -1
			walk = True
		elif storage.keys[pygame.K_s] or storage.dpad[3]:
			angleamt[1] = 1
			walk = True

		if angleamt[0] == 0:
			if angleamt[1] == 0:
				pass
			elif angleamt[1] > 0:
				self.angle = 270
			else:
				self.angle = 90
		elif angleamt[0] > 0:
			if angleamt[1] == 0:
				self.angle = 0
			elif angleamt[1] > 0:
				self.angle = 315
			else:
				self.angle = 45
		else:
			if angleamt[1] == 0:
				self.angle = 180
			elif angleamt[1] > 0:
				self.angle = 225
			else:
				self.angle = 135
		if pygame.K_SPACE in storage.newkeys and self.grounded:
			self.jump()
		
		if pygame.K_RETURN in storage.newkeys:
			print(self.x,self.y)
			for obj in storage.objlist:
				if isinstance(obj, object3d):
					if obj != self and obj.collidepoint(self.interactpoint):
						obj.interact(self)
		if pygame.K_9 in storage.newkeys:
			load(storage.savestate)
		if pygame.K_LSHIFT in storage.newkeys:
			cutsceneplayer("Pause")
		#TODO: add character swapping
		if walk:
			self.speed[0] = self.getstat("priority")*math.cos(self.angle/180*math.pi)
			self.speed[1] = -self.getstat("priority")*math.sin(self.angle/180*math.pi)
	
			self.interactpoint = [self.center[0]+(self.interactd)*math.cos(self.angle/180*math.pi),
				      self.center[1]-(self.interactd)*math.sin(self.angle/180*math.pi),
				      self.z-self.d/2]
	def skipturn(self):
		if self.combatactions[self.combatactionsindex][1] > 0:
			self.combatactions[self.combatactionsindex][1] -= 1
			self.combatactive = False
		else:
			self.combatactionsindex += 1
	def runmaster(self):
		target = findcombatman()
		target.aborted = True
		for guy in target.fighters:
			if self.state in [3,2] and guy.state in [3,2]:
				guy.combatactions = [["goto",[0-guy.w,guy.y]],["suicide"]]
				guy.combatactionsindex = 0
				guy.combatactive = True

	def staffattack(self):
		damage = 15 * (self.getstat("write")-self.combattarget[0].getstat("persistence"))
		if damage < 0:
			damage = 0
		print(damage)
		self.combattarget[0].alterstat("damage",damage)
		for item in self.combattarget[0].timedfx:
			if item[0] == "hit":
				self.combattarget[0].timedfx.remove(item)
				getattr(self.combattarget[0],item[2])(*item[3])
		if self.combattarget[0].getstat("damage") >= self.combattarget[0].getstat("maxhp"):
			self.combattarget[0].suicide()
		self.combattarget = self.combattarget[1:]
		self.combatactionsindex += 1
	

	def gotocutscenewait(self,pos = None,distance = 0):
		if pos == None:
			#print("WHY AM I REACHING YOU AT THE COORDINATES OF THE ABANDONED SPACE STATION")
			pos = self.combatactions[self.combatactionsindex][1]
		if [self.x,self.y] == [pos[0],pos[1]]:
			self.combatactionsindex += 1
		else:
			self.turnto(pos)
			if (self.x-pos[0])**2 + (self.y-pos[1])**2 < (self.getstat("priority")+distance)**2:
				self.x = pos[0]-distance*math.cos(-self.angle/180*math.pi)
				self.y = pos[1]-distance*math.sin(-self.angle/180*math.pi)
				self.speed = [0,0,0]
				self.combatactionsindex += 1
			else:
				for item in storage.objlist:
					if isinstance(item,plat):
						if item.collidepoint([self.x,self.y,self.z]) or item.collidepoint([self.x+self.w,self.y,self.z]) or item.collidepoint([self.x+self.w,self.y+self.h,self.z]) or item.collidepoint([self.x,self.y+self.h,self.z]):
							self.angle -= 90
				self.speed[0] = self.getstat("priority")*math.cos(self.angle/180*math.pi)
				self.speed[1] = -self.getstat("priority")*math.sin(self.angle/180*math.pi)
				self.animpicker()
				return False

	def goto(self,pos = None,distance = 0):
		if pos == None:
			#print("WHY AM I REACHING YOU AT THE COORDINATES OF THE ABANDONED SPACE STATION")
			pos = self.combatactions[self.combatactionsindex][1]
			print(pos)
		else:
			self.combatactions = [["goto",pos]]
			self.combatactionsindex = 0
		if [self.x,self.y] == [pos[0],pos[1]]:
			self.combatactionsindex += 1
		else:
			self.turnto(pos)
			if (self.x-pos[0])**2 + (self.y-pos[1])**2 < (self.getstat("priority")+distance)**2:
				self.x = pos[0]-distance*math.cos(-self.angle/180*math.pi)
				self.y = pos[1]-distance*math.sin(-self.angle/180*math.pi)
				self.speed = [0,0,0]
				self.combatactionsindex += 1
			else:
				for item in storage.objlist:
					if isinstance(item,plat):
						if item.collidepoint([self.x,self.y,self.z]) or item.collidepoint([self.x+self.w,self.y,self.z]) or item.collidepoint([self.x+self.w,self.y+self.h,self.z]) or item.collidepoint([self.x,self.y+self.h,self.z]):
							self.angle -= 90
				self.speed[0] = self.getstat("priority")*math.cos(self.angle/180*math.pi)
				self.speed[1] = -self.getstat("priority")*math.sin(self.angle/180*math.pi)
				self.animpicker()

	def turnto(self,point = None):
		if point == None:
			self.angle = 270
		else:
			self.angle = (180+180*math.atan2(point[1]-self.y,self.x-point[0])/math.pi)%360
			if self.angle < 0:
				self.angle = 360 + self.angle
	def warpto(self,point = None):
		#print("THAT ISN'T EVEN A REAL WORD")
		if point == None:
			point = self.combatactions[self.combatactionsindex][1]
			self.combatactionsindex += 1
		self.x = point[0]
		self.y = point[1]
		self.z = point[2]

	def gototarget(self):
		if self.combattarget[0].state < 2:
			pos = [self.combattarget[0].x-20-self.w,self.combattarget[0].y]
		else:
			pos = [self.combattarget[0].x+20+self.combattarget[0].w,self.combattarget[0].y]
		if [self.x,self.y] == [pos[0],pos[1]]:
			self.combatactionsindex += 1
		else:
			if (self.x-pos[0])**2 + (self.y-pos[1])**2 < self.getstat("priority")**2:
				self.x = pos[0]
				self.y = pos[1]
				self.speed = [0,0,0]
				self.combatactionsindex += 1
			else:
				self.turnto(pos)
				self.speed[0] = 2*self.getstat("priority")*math.cos(self.angle/180*math.pi)
				self.speed[1] = -2*self.getstat("priority")*math.sin(self.angle/180*math.pi)

	def wait(self):
		self.combatactions[self.combatactionsindex][1] -= storage.deltatime
		if self.combatactions[self.combatactionsindex][1] <= 0:
			self.combatactionsindex += 1

	def getcombatlocation(self):
		target = findcombatman()
		if target != False and target.fighters != []:
			allies = 0
			selforder = 0
			for char in target.fighters:
				if char == self:
					selforder = allies
				if self.state < 2 and char.state < 2:
					allies += 1
				elif self.state in [3,2] and char.state in [3,2]:
					allies += 1
			elbowroom = storage.screensize[1]/allies
			offset = elbowroom * selforder + elbowroom/2
			if self.state > 1:
				return [50, offset]
			else:
				return [670-self.w,offset]
		else:
			return [0,0]

	def picktargethostile(self):
		if self.state == 1:
			self.combattarget.append(random.choice(storage.party))
			self.combatactionsindex += 1
		elif self.state in [2,3]:
			target = findcombatman()
			if self.combattarget == []:
				for item in target.fighters:
					if item.state == 1:
						self.combattarget.append(item)
						break
	
			if pygame.K_RETURN in storage.newkeys:
				self.combatactionsindex += 1
			elif pygame.K_BACKSPACE in storage.newkeys:
				self.combatactions = []
				self.combatactionsindex = 0
			elif pygame.K_DOWN in storage.newkeys:
				index = index(target.fighters,self.combattarget[-1])
				for i in range(index+1,len(target.fighters)):
					if target.fighters[i].state < 2:
						self.combattarget.append(target.fighters[i])
						break
			elif pygame.K_UP in storage.newkeys:
				index = index(target.fighters,self.combattarget[-1])
				for i in range(index,0,-1):
					if target.fighters[i].state == 1:
						self.combattarget.append(target.fighters[i])
						break
			for item in self.combattarget[:-1]:
				pygame.draw.rect(storage.spritecanvas,(255,255,0),[item.x-10,item-10,item.w+20,item.h+20],5)
			pygame.draw.rect(storage.spritecanvas,(255,255,255),[self.combattarget[-1].x-10,self.combattarget[-1].y-10,self.combattarget[-1].w+20,self.combattarget[-1].h+20],5)
		

	def wipe(self):
		target = findcombatman()
		action = "wait"
		if not target:
			pass
		else:
			for item in target.fighters:
				if item not in storage.party:
					item.delete()
		self.combatactionsindex += 1
	def kill(self):
		#print("Why are we still here? Just to suffer?")
		self.combattarget[0].delete()
		self.combattarget = self.combattarget[1:]
		self.combatactionsindex += 1
	def suicide(self):
		self.delete()
		self.combatactive = False
	def testme(self):
		print("Well that just happened")
	def joinparty(self):
		self.state = 2
		storage.party.append(self)
		storage.partyspawn.append(["character",[250,350,-500,self.w,self.h,self.d,self.state,self.name,self.id]])
	

class collider(object3d):
	def __init__(self,x=0,y=0,z=0,w=0,h=0,d=0,angle = 0,descend = [0,0,0,0],image = None,offset = [0,0]):
		super().__init__(x,y,z,w,h,d)
		self.angle = angle/360*2*math.pi
		self.descend = descend
		self.image = image
		self.offset = offset

	def todata(self):
		return ["collider",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.angle,self.descend,self.image,self.offset]]

	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.z = data[2]
		self.w = data[3]
		self.h = data[4]
		self.d = data[5]
		self.speed = copy.deepcopy(data[6])
		self.grounded = data[7]
		self.angle = data[8]
		self.descend = data[9]
		self.image = data[10]
		self.offset = data[11]
				
	def collidepoint(self,basepoint):
		#for both angle and perpendicular of angle:
		#print([basepoint[0]-self.x,basepoint[1]-self.y,basepoint[2]], [(basepoint[0]-self.x)*math.cos(0)-(basepoint[1]-self.y)*math.sin(0),(basepoint[0]-self.x)*math.sin(0)+(basepoint[1]-self.y)*math.cos(0),basepoint[2]])
		if len(basepoint) < 3:
			basepoint.append(0)
		point = [(basepoint[0]-self.x)*math.cos(-self.angle)-(basepoint[1]-self.y)*math.sin(-self.angle),
			 (basepoint[0]-self.x)*math.sin(-self.angle)+(basepoint[1]-self.y)*math.cos(-self.angle),basepoint[2]]
		if 0 <= point[0] <= self.w:
			if 0 <= point[1] <= self.h:
				#NOTE: This is complicated maths stuff to do with triangle rasterizing and whatnot. I really wish there was an easier solution.
				#NOTE 2: go to https://jtsorlinis.github.io/rendering-tutorial/ for more information
				#get area
				area = self.w*self.h
				#Check in the TL-BR-BL tri
				height = 0
				if point[0]*self.h/self.w<=point[1]:
					#TL-BR-P
					BLWeight = ((self.w)*(point[1])-(self.h)*(point[0]))/area
					#TL-P-BL
					BRWeight = ((point[0])*(self.h))/area
					#P-BR-BL
					TLWeight = ((self.w-point[0])*(self.h-point[1])-(self.h-point[1])*(-point[0]))/area
					TRWeight = 0
				#if not there, check in the TL-TR-BR tri
				else:
					#TL-TR-P
					BRWeight = ((self.w)*(point[1]))/area
					#TL-P-BR
					TRWeight = ((point[0])*(self.h)-(point[1])*(self.w))/area
					#P-TR-BR
					TLWeight = ((self.w-point[0])*(self.h-point[1])-(-point[1])*(self.w-point[0]))/area
					BLWeight = 0
				height = TLWeight*self.descend[0] + TRWeight*self.descend[1] + BRWeight*self.descend[2] + BLWeight*self.descend[3]
				if self.z >= point[2] >= self.z-self.d+height:
					minx = min([-point[0],self.w-point[0]],key=abs)
					miny = min([-point[1],self.h-point[1]],key=abs)
					if abs(miny) < abs(minx):
						return [(0)*math.cos(self.angle)-(miny)*math.sin(self.angle),
							(0)*math.sin(self.angle)+(miny)*math.cos(self.angle),
							height]
					else:
						return [(minx)*math.cos(self.angle)-(0)*math.sin(self.angle),
							(minx)*math.sin(self.angle)+(0)*math.cos(self.angle),
							height]
		return False
	def collidecheck(self,hitter):
		if self.collidepoint(hitter.center) != False:
			if self.angle == 0:
				if self.collidepoint(hitter.center) != False:
					print(hitter,"COLLIDING")
			else:
				result = self.collidepoint(hitter.center)
				if result != False:
					print(hitter,"COLLIDING")
					
	def interact(self,hitter):
		pass
	def render(self):
		if False:#self.angle == 0:
			if storage.debug:
				pygame.draw.rect(storage.spritecanvas, (255,255,0), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
				pygame.draw.rect(storage.spritecanvas, (255,255,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d),2)
				pygame.draw.rect(storage.spritecanvas, (255,255,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h),2)
		else:
			if storage.debug:
				pygame.draw.polygon(storage.spritecanvas, (255,0,0), ([int(self.x-storage.camfocus[0]),
											int(self.y-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),2)
				if self.angle <= 90:
					pygame.draw.polygon(storage.spritecanvas, (0,0,255), ([int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[0]   -self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[1]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z   +self.descend[2]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),2)
				pygame.draw.polygon(storage.spritecanvas, (255,255,0), ([int(self.x-storage.camfocus[0]),
											int(self.y+self.z   +self.descend[0]   -self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z   +self.descend[1]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[2]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[3]   -self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),2)
class cutscenetrigger(collider):
	def __init__(self,x=0,y=0,z=0,w=0,h=0,d=0,angle = 0,descend = [0,0,0,0],script = "test3",once = True):
		super().__init__(x,y,z,w,h,d,angle,descend)
		self.script = script
		self.once = once
	def todata(self):
		return ["cutscenetrigger",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.angle,self.descend,self.script,self.once]]
	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.z = data[2]
		self.w = data[3]
		self.h = data[4]
		self.d = data[5]
		self.speed = copy.deepcopy(data[6])
		self.grounded = data[7]
		self.angle = data[8]
		self.descend = data[9]
		self.script = data[10]
		self.once = data[11]
	def collidecheck(self,hitter):
		print(self.x,self.y,self.z)
		if storage.actlock == False and hitter.state == 3  and (self.collidepoint(hitter.center)!=False):
			if self.once:
				self.delete()
			cutsceneplayer(self.script)	
class musiczone(collider):
	def __init__(self,x=0,y=0,z=0,w=0,h=0,d=0,angle = 0,descend = [0,0,0,0],song = "bosstest.mp3"):
		super().__init__(x,y,z,w,h,d,angle,descend)
		self.song = song
	def todata(self):
		return ["musiczone",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.angle,self.descend,self.song]]
	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.z = data[2]
		self.w = data[3]
		self.h = data[4]
		self.d = data[5]
		self.speed = copy.deepcopy(data[6])
		self.grounded = data[7]
		self.angle = data[8]
		self.descend = data[9]
		self.song = data[10]
	def collidecheck(self,hitter):
		if storage.actlock == False and hitter.state == 3 and (self.collidepoint(hitter.center)!=False):
			soundutils.playsong(self.song)
			storage.songpriority = True
	def delete(self):
		super().delete()
		soundutils.stopsong()

class warpzone(collider):
	def __init__(self,x=0,y=0,z=0,w=0,h=0,d=0,angle = 0,descend = [0,0,0,0],outloc = [0,0,0],warploc = [0,0,0],inloc = [0,0,0],preserveoffset = 0,cell = "test2"):
		super().__init__(x,y,z,w,h,d,angle,descend)
		#NOTE: outloc is the spot the chars will walk to while leaving the cell. warploc is where they will be teleported after the room reloads, inloc is where they walk to after that.
		self.outloc = copy.copy(outloc)
		self.warploc = copy.copy(warploc)
		self.inloc = copy.copy(inloc)
		self.preserveoffset = preserveoffset
		self.cell = cell
	def todata(self):
		return ["warpzone",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.angle,self.descend,self.outloc,self.warploc,self.inloc,self.preserveoffset,self.cell]]
	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.z = data[2]
		self.w = data[3]
		self.h = data[4]
		self.d = data[5]
		self.speed = copy.deepcopy(data[6])
		self.grounded = data[7]
		self.angle = data[8]
		self.descend = data[9]
		self.outloc = data[10]
		self.warploc = data[11]
		self.inloc = data[12]
		self.preserveoffset = data[13]
		self.cell = data[14]
	def collidecheck(self,hitter):
		if storage.actlock == False and hitter.state == 3:
			result = self.collidepoint(hitter.center)
			if result != False:
				#larger types of warp zones may benefit from allowing the player to preserve his position relative to the zone.
				print(self.inloc)
				match self.preserveoffset:
					#preserve x-offset
					case 1:
						self.warploc[0] -= self.x-hitter.x
						self.outloc[0] -= self.x-hitter.x
						self.inloc[0] -= self.x-hitter.x
					#preserve y-offset
					case 2:
						self.warploc[1] -= self.y-hitter.y
						self.outloc[1] -= self.y-hitter.y
						self.inloc[1] -= self.y-hitter.y
					#preserve x and y offsets
					case 3:
						self.warploc[0] -= self.x-hitter.x
						self.warploc[1] -= self.y-hitter.y
						self.outloc[0] -= self.x-hitter.x
						self.outloc[1] -= self.y-hitter.y
						self.inloc[0] -= self.x-hitter.x
						self.inloc[1] -= self.y-hitter.y
				print(self.inloc)

				base = [["loadgame",self.cell]]
				before = []
				after = []
				#for every character in the party
				for char in storage.party:
					#they should walk to a set point
					if char.state == 3:
						base = [["char",[char.name,char.id,"gotocutscenewait",self.outloc]]] + base
					else:
						before.append(["char",[char.name,char.id,"goto",self.outloc]])
					#then they should warp to a set point
					base.append(["char",[char.name,char.id,"warpto",self.warploc]])
					#then they should walk to ANOTHER point.
					if char.state != 3:
						base += [["char",[char.name,char.id,"goto",self.inloc]]]
					else:
						after.append(["char",[char.name,char.id,"gotocutscenewait",self.inloc]])
				base = before + base + after
				print(base)
				cutsceneplayer(base)
	
class plat(collider):
	def todata(self):
		return ["plat",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.angle,self.descend,self.image,self.offset]]

	def collidecheck(self, hitter):
		if self.collidepoint(hitter.top) != False:
			hitter.z -= hitter.z-self.d+self.z
			hitter.getpoints()
		result = self.collidepoint(hitter.bottom)
		if result != False:
			hitter.z -= hitter.z - (self.z-self.d+result[2])
			hitter.speed[2] = 0
			hitter.grounded = True
			hitter.getpoints()
		if self.angle == 0:
			if self.collidepoint(hitter.right) != False:
				hitter.x -= hitter.x+hitter.w-self.x
				hitter.getpoints()
			if self.collidepoint(hitter.left) != False:
				hitter.x -= hitter.x-(self.x+self.w)
				hitter.getpoints()
			if self.collidepoint(hitter.front) != False:
				hitter.y -= hitter.y+hitter.h-self.y
				hitter.getpoints()
			if self.collidepoint(hitter.back) != False:
				hitter.y -= hitter.y-(self.y+self.h)
				hitter.getpoints()
		else:
			result = self.collidepoint(hitter.right)
			if result != False:
				hitter.x += result[0]
				hitter.y += result[1]
				hitter.getpoints()
			result = self.collidepoint(hitter.left)
			if result != False:
				hitter.x += result[0]
				hitter.y += result[1]
				hitter.getpoints()
			result = self.collidepoint(hitter.front)
			if result != False:
				hitter.x += result[0]
				hitter.y += result[1]
				hitter.getpoints()
			result = self.collidepoint(hitter.back)
			if result != False:
				hitter.x += result[0]
				hitter.y += result[1]
				hitter.getpoints()
	def render(self):
		if False:#self.angle == 0:
			if storage.debug:
				pygame.draw.rect(storage.spritecanvas, (0,100,0), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
				pygame.draw.rect(storage.spritecanvas, (0,155,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
				pygame.draw.rect(storage.spritecanvas, (0,255,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
			else:
				pygame.draw.rect(storage.spritecanvas, (255,0,255), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
		else:
			if storage.debug:
				if self.image == "Blank":
					width = 2
				else:
					width = 0
				pygame.draw.polygon(storage.spritecanvas, (0,100,0), ([int(self.x-storage.camfocus[0]),
											int(self.y-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),2)
				if self.angle <= 90:
					pygame.draw.polygon(storage.spritecanvas, (0,155,0), ([int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[3]   -self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]),
											int(self.y+self.z   +self.descend[0]   -self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z   +self.descend[1]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),width)
				pygame.draw.polygon(storage.spritecanvas, (0,255,0), ([int(self.x-storage.camfocus[0]),
											int(self.y+self.z   +self.descend[0]   -self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z   +self.descend[1]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[2]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[3]   -self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),width)
			elif self.image == "Blank":
				pass
			elif self.image == None:
				pygame.draw.polygon(storage.spritecanvas, (255,0,255), ([int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[3]   -self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]),
											int(self.y+self.z   +self.descend[0]   -self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z   +self.descend[1]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.h*math.cos(self.angle)))]))
			else:
				holder = storage.animinfo["TerrainObjs"][self.image]
				storage.spritecanvas.blit(storage.spritesheet,[self.offset[0]+self.x+self.w/2-storage.camfocus[0],self.offset[1]+self.y+self.h/2-self.z-self.d/2-storage.camfocus[1]],holder[:5])


class roundplat(collider):
	#NOTE: IGNORE OTHER NOTES, THIS DOES NOT WORK YET
	#NOTE: For complex math reasons, these things must be buried at least 1 unit underground for the player to properly walk onto them. It's an oversight, I know. No, fixing it isn't worth our time right now.
	#NOTE 2: It works better if they're buried at least 2 units underground.
	def __init__(self,x=0,y=0,z=0,w=50,h=50,d=50,angle=0,w2=50,h2=50,image = None,offset = [0,0]):
		super().__init__(x,y,z,w,h,d)
		self.w2 = w2
		self.h2 = h2
		self.angle = angle/180*math.pi
		self.image = image
		self.offset = offset

	def todata(self):
		return ["collider",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.angle,self.image,self.offset,self.w2,self.h2]]

	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.z = data[2]
		self.w = data[3]
		self.h = data[4]
		self.d = data[5]
		self.speed = copy.deepcopy(data[6])
		self.grounded = data[7]
		self.angle = data[8]
		self.image = data[9]
		self.offset = data[10]
		self.w2 = data[11]
		self.h2 = data[12]
				
	def collidepoint(self,basepoint):
		if len(basepoint) < 3:
			basepoint.append(0)
		point = [(basepoint[0]-self.x)*math.cos(-self.angle)-(basepoint[1]-self.y)*math.sin(-self.angle),
			 (basepoint[0]-self.x)*math.sin(-self.angle)+(basepoint[1]-self.y)*math.cos(-self.angle),basepoint[2]]
		#first check: vertical
		if not (self.z >= point[2] >= self.z-self.d):
			return False
		else:
			#print([self.z-point[2],self.z-self.d-point[2]])
			vertdist = min([self.z-point[2],self.z-self.d-point[2]],key=abs)

			#second check: horrible annoying circle math
			planeangle = math.atan2(point[1],point[0])
			#print(180*planeangle/math.pi)
			pointB1=[self.w/2*math.cos(planeangle),self.h/2*math.sin(planeangle)]
			pointB2=[self.w/2*math.cos(math.pi+planeangle),self.h/2*math.sin(math.pi+planeangle)]
			pointT1=[self.w2/2*math.cos(planeangle),self.h2/2*math.sin(planeangle)]
			pointT2=[self.w2/2*math.cos(math.pi+planeangle),self.h2/2*math.sin(math.pi+planeangle)]
			#print(pointB1,pointT1,point,180*planeangle/math.pi)

			adjpoint = [point[0]*math.cos(-planeangle)-point[1]*math.sin(-planeangle),point[0]*math.sin(-planeangle)+point[1]*math.cos(-planeangle)]
			adjB1 = [pointB1[0]*math.cos(-planeangle)-pointB1[1]*math.sin(-planeangle),pointB1[0]*math.sin(-planeangle)+pointB1[1]*math.cos(-planeangle)]
			adjB2 = [pointB2[0]*math.cos(-planeangle)-pointB2[1]*math.sin(-planeangle),pointB2[0]*math.sin(-planeangle)+pointB2[1]*math.cos(-planeangle)]
			adjT1 = [pointT1[0]*math.cos(-planeangle)-pointT1[1]*math.sin(-planeangle),pointT1[0]*math.sin(-planeangle)+pointT1[1]*math.cos(-planeangle)]
			adjT2 = [pointT2[0]*math.cos(-planeangle)-pointT2[1]*math.sin(-planeangle),pointT2[0]*math.sin(-planeangle)+pointT2[1]*math.cos(-planeangle)]
			lineangle = (math.pi/2)-math.atan2(-self.d,adjB1[0]-adjT1[0])
			#print(180*lineangle/math.pi)
			flatpoint = adjpoint[0]*math.cos(lineangle)-(-point[2])*math.sin(lineangle)
			flatB1 = adjB1[0]*math.cos(lineangle)-(-self.z)*math.sin(lineangle)
			flatB2 = adjB2[0]*math.cos(lineangle)-(-self.z)*math.sin(lineangle)
			flatT1 = adjT1[0]*math.cos(lineangle)-(-self.z+self.d)*math.sin(lineangle)
			flatT2 = adjT2[0]*math.cos(lineangle)-(-self.z+self.d)*math.sin(lineangle)
			print(flatB1-flatT1)
			#print(flatpoint,flatB1,flatB2,flatT1,flatT2)
			mini = min(flatB1,flatB2,flatT1,flatT2)
			maxi = max(flatB1,flatB2,flatT1,flatT2)
			#print(mini,flatpoint,maxi)
			if not (mini <= flatpoint <= maxi):
				return False
			else:
				flatdist = min([mini-flatpoint,maxi-flatpoint],key=abs)
				#FINALLY, we can return directions based on whichever of these is smaller
				derotated = [flatdist*math.cos(-lineangle),flatdist*math.sin(-lineangle)]
				deplaned = [derotated[0]*math.cos(-planeangle),derotated[0]*math.sin(-planeangle),derotated[1]]
				#print(flatdist,vertdist)
				if abs(flatdist) <= abs(vertdist):
					return deplaned
				else:
					return [0,0,vertdist]
				

	def collidecheck(self,hitter):
		results = self.collidepoint(hitter.bottom)
		if results != False:
			hitter.speed[2] = 0
			hitter.grounded = True
			#hitter.x+=results[0]
			#hitter.y+=results[1]
			hitter.z+=results[2]
			hitter.getpoints()
		results = self.collidepoint(hitter.top)
		if results != False:
			hitter.speed[2] = 0
			#hitter.x+=results[0]
			#hitter.y+=results[1]
			hitter.z+=results[2]
			hitter.getpoints()
		results = self.collidepoint(hitter.right)
		if results != False:
			hitter.x+=results[0]
			#hitter.y+=results[1]
			#hitter.z+=results[2]
			hitter.getpoints()
		results = self.collidepoint(hitter.left)
		if results != False:
			hitter.x+=results[0]
			#hitter.y+=results[1]
			#hitter.z+=results[2]
			hitter.getpoints()
		results = self.collidepoint(hitter.front)
		if results != False:
			#hitter.x+=results[0]
			hitter.y+=results[1]
			#hitter.z+=results[2]
			hitter.getpoints()
		results = self.collidepoint(hitter.back)
		if results != False:
			#hitter.x+=results[0]
			hitter.y+=results[1]
			#hitter.z+=results[2]
			hitter.getpoints()

					
	def interact(self,hitter):
		pass
	def update(self):
		super().update()
		self.vertsort = [self.y-self.h/2,self.z]
	def render(self):
		if storage.debug:
			if self.image == "Blank":
				pass
			else:
				burner = pygame.Surface((self.w,self.h))
				burner.set_colorkey((0,255,255))
				burner.fill((0,255,255))
				pygame.draw.ellipse(burner,(0,100,0), [0,0,self.w,self.h])
				burner = pygame.transform.rotate(burner,self.angle*180/math.pi)
				storage.spritecanvas.blit(burner,[self.x-storage.camfocus[0]-burner.get_size()[0]/2,self.y+self.z-storage.camfocus[1]-burner.get_size()[1]/2])
				
				testangle = math.pi/2 - self.angle
				a = self.w/2
				m = math.tan(testangle)
				b = self.h/2
				x1 = (m*(a**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
				x2 = -(m*(a**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
				y1 = -((b**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
				y2 = ((b**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
				a = self.w2/2
				m = math.tan(testangle)
				b = self.h2/2
				x3 = (m*(a**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
				x4 = -(m*(a**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
				y3 = -((b**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
				y4 = ((b**2))/(math.sqrt((a**2)*(m**2)+(b**2)))
				pygame.draw.polygon(storage.spritecanvas,(0,100,0),[[self.x-storage.camfocus[0]+x1*math.cos(self.angle)-y1*math.sin(self.angle),
											self.y+self.z-storage.camfocus[1]+x2*math.sin(self.angle)+y2*math.cos(self.angle)],
								      		    [self.x-storage.camfocus[0]+x2*math.cos(self.angle)-y2*math.sin(self.angle),
											self.y+self.z-storage.camfocus[1]+x1*math.sin(self.angle)+y1*math.cos(self.angle)],
								      		    [self.x-storage.camfocus[0]+x4*math.cos(self.angle)-y4*math.sin(self.angle),
											self.y+self.z-storage.camfocus[1]+x3*math.sin(self.angle)+y3*math.cos(self.angle)-self.d],
								      		    [self.x-storage.camfocus[0]+x3*math.cos(self.angle)-y3*math.sin(self.angle),
											self.y+self.z-storage.camfocus[1]+x4*math.sin(self.angle)+y4*math.cos(self.angle)-self.d]])
				
				burner2 = pygame.Surface((self.w2,self.h2))
				burner2.set_colorkey((0,255,255))
				burner2.fill((0,255,255))
				pygame.draw.ellipse(burner2,(0,255,0), [0,0,self.w2,self.h2])
				burner2 = pygame.transform.rotate(burner2,self.angle*180/math.pi)
				storage.spritecanvas.blit(burner2,[self.x-storage.camfocus[0]-burner2.get_size()[0]/2,self.y+self.z-self.d-storage.camfocus[1]-burner2.get_size()[1]/2])

class mapdisplay(sharedlib.gameobject):
	def __init__(self,path="testmap",x=0,y=0,scale=1):
		super().__init__()
		self.x = x
		self.y = y
		self.image = pygame.transform.scale_by(pygame.image.load(f"Assets/graphics/{path}.png").convert(),scale)
		self.path = path
		self.scale = scale
		self.w,self.h = self.image.get_size()

	def todata(self):
		return ["mapdisplay",[self.x,self.y,self.w,self.h,self.path,self.scale]]

	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.w = data[2]
		self.h = data[3]
		self.path = data[4]
		self.scale = data[5]
		self.image = pygame.transform.scale_by(pygame.image.load(f"Assets/graphics/{self.path}.png").convert(),self.scale)

	def update(self):
		super().update()
		storage.cambounds[0] = self.x
		storage.cambounds[2] = self.x+self.w
		storage.cambounds[1] = self.y
		storage.cambounds[3] = self.y+self.h

	def render(self):
		storage.window.blit(self.image, [int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h])	

class camera3d(sharedlib.gameobject):
	def __init__(self,x=0,y=0,z=0):
		super().__init__()
		self.x = x
		self.y = y
		self.z = z
		self.target = self
		storage.camera = self

	def todata(self):
		return ["camera3d",[self.x,self.y,self.z]]

	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.z = data[2]

	def render(self):
		pass
	
	def setfocus(self,target=None):
		if target == None:
			self.target = self
		elif target == "partyleader":
			for item in storage.party:
				if item.state == 3:
					self.target = item
					break
		else:
			for item in storage.objlist:
				if isinstance(item,character):
					if item.name + str(item.id) == target:
						self.target = item
						break

	def moveto(self,pos = [0,0,0]):
		self.x = pos[0]
		self.y = pos[1]
		self.z = pos[2]

	def update(self):
		super().update()
		if pygame.K_3 in storage.newkeys:
			if self.state == 1:
				self.state = 0
			else:
				self.state = 1
		if self.state == 1:
			#get control updates
			if storage.keys[pygame.K_LEFT]:
				self.x -= 1
			elif storage.keys[pygame.K_RIGHT]:
				self.x += 1
			if storage.keys[pygame.K_UP]:
				self.y -= 1
			elif storage.keys[pygame.K_DOWN]:
				self.y += 1
			if storage.keys[pygame.K_1]:
				self.z -= 1
			elif storage.keys[pygame.K_2]:
				self.z += 1
		elif self.target != self:
			self.x = self.target.x+(self.target.w-storage.screensize[0])/2
			self.y = self.target.y+(self.target.h-storage.screensize[0])/2
			self.z = self.target.z
		if self.x < storage.cambounds[0]:
			self.x = storage.cambounds[0]
		if self.y+self.z < storage.cambounds[1]:
			self.y = storage.cambounds[1]
			self.z = 0
		if self.x > storage.cambounds[2]-storage.screensize[0]:
			self.x = storage.cambounds[2]-storage.screensize[0]
		if self.y+self.z > storage.cambounds[3]-storage.screensize[1]:
			self.y = storage.cambounds[3]-storage.screensize[1]
			self.z = 0
		storage.camfocus = [self.x,self.y+self.z]

class uiobject(sharedlib.gameobject):
	def __init__(self):
		super().__init__()
		self.mode = "Blank"
		self.diachars = []
		#NOTE: the dialogue is never cleared out of this--that's on purpose!
		#Eventually, I'd like the option to scroll thru a record of past dialogue, either via dialogue windows or a written record.
		#See Star Wars: KOTOR for an example of this in action.
		#now, the dialogue trailing off the top...Yeah, that needs fixed.
		self.color = [255,255,0]
		self.diamessages = []
		self.choices = []
		self.outcomes = []
		self.active = 0
		self.dictmode = 0
		self.dictoffset = 0
		self.submenu = "main"
		self.combattant = None
		self.focusspeaker = 0
		storage.ui = self

	def todata(self):
		return ["uiobject",[self.mode,copy.deepcopy(self.diachars),copy.deepcopy(self.diamessages),copy.deepcopy(self.choices),copy.deepcopy(self.outcomes),self.active,self.focusspeaker]]

	def fromdata(self,data):
		self.mode = data[0]
		self.diachars = copy.deepcopy(data[1])
		self.diamessages = copy.deepcopy(data[2])
		self.choices = copy.deepcopy(data[3])
		self.outcomes = copy.deepcopy(data[4])
		self.combattant = None
		self.submenu = "main"
		self.active = data[5]
		self.focusspeaker = data[6]
		storage.ui = self

	def update(self):
		if self.mode == "Dictionary":
			if pygame.K_a in storage.newkeys or pygame.K_d in storage.newkeys:
				if self.dictmode == 0:
					self.dictmode = 1
					size = len(storage.storydict.keys())
				else:
					self.dictmode = 0
					size = len(storage.cyberdict.keys())
				if self.active >= size:
					self.active = 0
				elif self.active < 0:
					self.active = size - 1

			if pygame.K_s in storage.newkeys:
				self.active += 1
			if pygame.K_w in storage.newkeys:
				self.active -= 1
			
			if self.dictmode == 0:
				size = len(storage.storydict.keys())
			else:
				size = len(storage.cyberdict.keys())
			if self.active >= size:
				self.active = 0
			elif self.active < 0:
				self.active = size - 1

			if self.dictmode == 0:
				total = 0
				itr = 0
				for item in storage.storydict.keys():
					size = 20#storage.writer.size(item)[1]
					if itr == self.active:
						if total + size + self.dictoffset > 380:
							self.dictoffset = 380-(total + size)
						elif total + self.dictoffset < 0:
							self.dictoffset = -total
					total += size
					itr += 1
			else:
				total = 0
				itr = 0
				for item in storage.cyberdict.keys():
					size = 20#storage.writer.size(item)[1]
					if itr == self.active:
						if total + size + self.dictoffset > 380:
							self.dictoffset = 380-(total + size)
						elif total + self.dictoffset < 0:
							self.dictoffset = -total
					total += size
					itr += 1
						
		elif self.mode == "Win" and pygame.K_RETURN in storage.newkeys:
			self.loadui("Blank")
			print("#winning")
			softload(storage.winstate)			
			
			
		if self.choices != []:
			if pygame.K_s in storage.newkeys:
				self.active += 1
			if pygame.K_w in storage.newkeys:
				self.active -= 1
			if self.active == len(self.choices):
				self.active = 0
			elif self.active < 0:
				self.active = len(self.choices) - 1
			if pygame.K_RETURN in storage.newkeys:
				#print(self.choices[self.active])
				if self.mode == "Dialogue":
					self.diamessages.append(">"+self.choices[self.active])
					self.choices = []
				elif self.mode == "Combat":
					if self.outcomes[self.active][0] == "menu":
						self.loadcombatmenu(self.outcomes[self.active][1])
					else:
						if self.combattant.state > 1:
							#self.combattant.combattarget = []
							action = self.outcomes[self.active]
							self.combattant.combatactions = copy.deepcopy(storage.combatactions[action])

	def adddialogue(self,text):
		#self.diamessages = []
		self.diamessages.append(text)

	def loadcombatmenu(self,menu):
		self.submenu = menu
		self.active = 0
		if self.combattant.name not in storage.charmenus:
			self.choices = copy.deepcopy(storage.charmenus["Default"][self.submenu][0])
			self.outcomes = copy.deepcopy(storage.charmenus["Default"][self.submenu][1])
		else:
			self.choices = copy.deepcopy(storage.charmenus[self.combattant.name][self.submenu][0])
			self.outcomes = copy.deepcopy(storage.charmenus[self.combattant.name][self.submenu][1])

	def addchoice(self,choices,outcomes):
		self.active = 0
		self.choices = choices
		self.outcomes = outcomes
	
	def setcombattant(self,combattant):
		self.combattant = combattant
		if combattant.name == None or combattant.name + str(combattant.id) not in storage.colors.keys():
			if combattant.name not in storage.colors.keys():
				self.color = storage.colors["Default"]
			else:
				self.color = storage.colors[combattant.name]
		else:
			self.color = storage.colors[combattant.name+str(combttant.id)]

	def cutspeaker(self,name,id = 0):
		for item in self.diachars:
			if item[0] == name and item[3] == id:
				self.diachars.remove(item)
				break

	def setspeaker(self,name,side = 0,id = 0,emote="Neutral"):
		found = False
		if name == "partyleader":
			for item in storage.party:
				if item.state == 3:
					name = item.name
					break
		for index in range(len(self.diachars)):
			item = self.diachars[index]
			if name == item[0] and id == item[3]:
				item[1] = emote
				self.focusspeaker = index
				found = True
				break
		if not found:
			self.diachars.append([name,emote,side,id])
			self.focusspeaker = len(self.diachars)-1

		if name + str(id) not in storage.colors.keys():
			if name not in storage.colors.keys():
				self.color = storage.colors["Default"]
			else:
				self.color = storage.colors[name]
		else:
			self.color = storage.colors[name+str(id)]

	def loadui(self,name):
		if name != "Dialogue" and self.mode == "Dialogue":
			self.diamessages.append("<END OF LINE>")
			self.diachars = []
		elif name == "Dialogue" and self.mode != "Dialogue":
			self.diamessages.append("<CONVERSATION STARTED>")
		elif name == "Dictionary":
			storage.actlock = True
		self.mode = name

	def render(self):
		if self.mode == "Blank":
			storage.uicanvas.blit(storage.writer.render("This area left intentionally blank",False,(255,255,255)),(0,0))#(self.x,self.y))
		if self.mode == "Win":
			storage.uicanvas.blit(storage.writer.render("THIS SCREEN CONTAINS WIN",False,(255,255,255)),(0,0))#(self.x,self.y))
		elif self.mode == "Dictionary":
			if self.dictmode == 0:
				storage.uicanvas.blit(storage.writer.render("Story Dictionary",False,self.color),(50,20))
				pygame.draw.rect(storage.uicanvas,(self.color[0]*0.5,self.color[1]*0.5,self.color[2]*0.5),[40,40,200,400])
				pygame.draw.rect(storage.uicanvas,(self.color[0]*0.5,self.color[1]*0.5,self.color[2]*0.5),[240,40,440,400])
				pygame.draw.rect(storage.uicanvas,self.color,[40,40,200,400],5)
				pygame.draw.rect(storage.uicanvas,self.color,[240,40,440,400],5)
				itr = 0
				for item in storage.storydict.keys():
					if itr == self.active:
						storage.uicanvas.blit(storage.writer.render(item,False,(255,255,255)),(50,50+itr*20+self.dictoffset))
						text = formattextforwidth(storage.storydict[item],420)
						linecounter = 0
						for line in text:
							storage.uicanvas.blit(storage.writer.render(line,False,(255,255,255)),(250,50+linecounter*10))
							linecounter += 1
					else:
						storage.uicanvas.blit(storage.writer.render(item,False,self.color),(50,50+itr*20+self.dictoffset))
					itr += 1
			else:
				storage.uicanvas.blit(storage.writer.render("Cybersecurity Dictionary",False,(255,255,255)),(50,20))
				pygame.draw.rect(storage.uicanvas,(127,127,127),[40,40,200,400])
				pygame.draw.rect(storage.uicanvas,(127,127,127),[240,40,440,400])
				pygame.draw.rect(storage.uicanvas,(255,255,255),[40,40,200,400],5)
				pygame.draw.rect(storage.uicanvas,(255,255,255),[240,40,440,400],5)
				itr = 0
				for item in storage.cyberdict.keys():
					if itr == self.active:
						storage.uicanvas.blit(storage.writer.render(item,False,(255,255,255)),(50,50+itr*20+self.dictoffset))
						text = formattextforwidth(storage.cyberdict[item],420)
						linecounter = 0
						for line in text:
							storage.uicanvas.blit(storage.writer.render(line,False,(255,255,255)),(250,50+linecounter*10))
							linecounter += 1
					else:
						storage.uicanvas.blit(storage.writer.render(item,False,(0,0,0)),(50,50+itr*20+self.dictoffset))
					itr += 1

		elif self.mode == "Combat":
			size = 0
			if self.combattant.combatactions == []:
				pygame.draw.rect(storage.uicanvas,(self.color[0]*0.5,self.color[1]*0.5,self.color[2]*0.5),[160,40,400,400])
				pygame.draw.rect(storage.uicanvas,self.color,[160,40,400,400],5)
				storage.uicanvas.blit(storage.writer.render(f"{self.combattant.name}:{self.combattant.getstat("maxhp")-self.combattant.getstat("damage")}/{self.combattant.getstat("maxhp")}HP {self.combattant.getstat("maxdata")-self.combattant.getstat("spentdata")}/{self.combattant.getstat("maxdata")}DATA ",False,(255,255,255)),[165,45])
				size += storage.writer.size(f"it is {self.combattant.name}'s turn.")[1]
				for index in range(len(self.choices)):
					size += 5
					if self.active == index:
						storage.uicanvas.blit(storage.writer.render(">"+self.choices[index],False,(255,255,255)),[165,45+size])
					else:
						storage.uicanvas.blit(storage.writer.render(self.choices[index],False,self.color),[165,45+size])
					size += storage.writer.size(self.choices[index])[1]

		elif self.mode == "Dialogue":
			pygame.draw.rect(storage.uicanvas,(self.color[0]*0.5,self.color[1]*0.5,self.color[2]*0.5),[160,40,400,400])
			pygame.draw.rect(storage.uicanvas,self.color,[160,40,400,400],5)
			itrL = 0
			itrR = 0
			numL = 0
			for item in self.diachars:
				if item[2] == 0:
					numL += 1
			numR = len(self.diachars)-numL
			if numL > 0:
				Lspacing = storage.screensize[1]/numL
			if numR > 0:
				Rspacing = storage.screensize[1]/numR
			for index in range(len(self.diachars)):
				item = self.diachars[index]
				if item[2] == 0:
					x = 110
					y = Lspacing * itrL + Lspacing/2
					itrL += 1
				else:
					x = 570
					y = Rspacing * itrR + Rspacing/2
					itrR += 1
				if index == self.focusspeaker:
					pygame.draw.rect(storage.uicanvas,(self.color[0]*0.5,self.color[1]*0.5,self.color[2]*0.5),[x-5,y-5,50,50])
					pygame.draw.rect(storage.uicanvas,self.color,[x-5,y-5,50,50],5)
				else:
					color = [0,0,0]
					if item[0] + str(item[3]) not in storage.colors.keys():
						if item[0] not in storage.colors.keys():
							color = storage.colors["Default"]
						else:
							color = storage.colors[item[0]]
					else:
						color = storage.colors[item[0]+str(item[3])]
					pygame.draw.rect(storage.uicanvas,[0,0,0],[x-5,y-5,50,50])
					pygame.draw.rect(storage.uicanvas,(color[0]*0.5,color[1]*0.5,color[2]*0.5),[x-5,y-5,50,50],5)
				
				if item[0] in storage.animinfo["Portraits"].keys():
					storage.uicanvas.blit(storage.spritesheet, [x,y],storage.animinfo["Portraits"][item[0]+item[1]])
				
			size = 0
			for item in self.diamessages:
				texttorender = formattextforwidth(item,390)#.split("\n")
				for line in texttorender:
					size += storage.writer.size(line)[1]
				size += 5
			for index in range(len(self.choices)):
				size += storage.writer.size(self.choices[index])[1]
				size += 5
			for item in self.diamessages:
				texttorender = formattextforwidth(item,390)#.split("\n")
				for line in texttorender:
					storage.uicanvas.blit(storage.writer.render(line,False,self.color),[165,440-size])
					size -= storage.writer.size(line)[1]
				size -= 5
			for index in range(len(self.choices)):
				size -= 5
				if self.active == index:
					storage.uicanvas.blit(storage.writer.render(">"+self.choices[index],False,(255,255,255)),[165,440-size])
				else:
					storage.uicanvas.blit(storage.writer.render(self.choices[index],False,self.color),[165,440-size])
				size -= storage.writer.size(self.choices[index])[1]
				
			
def formattextforwidth(text,width):
	words = text.split(" ")
	out = []
	buffer = ""
	for word in words:
		if storage.writer.size(buffer+word)[0] > width:
			out.append(buffer)
			buffer = word + " "
		else:
			buffer += word + " "
	out.append(buffer)
	return out

class enemyspawner(sharedlib.gameobject):
	#NOTE: Like characters, these all need to have unique IDs. It sucks, I know.
	#NOTE 2: We should only have one simultaneously extant instance of these per cell to avoid technical issues.
	def __init__(self,id = 0, spawns = [ [["character",[0,0,0,50,50,50,1,None]]] ]):
		super().__init__()
		self.id = id
		self.spawns = spawns
		self.spawned = []
		self.spawn = True
		if self.id not in (storage.enemyspawns.keys()) or storage.enemyspawns[self.id] == []:
			storage.enemyspawns[self.id] = copy.deepcopy(random.choice(self.spawns))

	def todata(self):
		self.update()
		print(storage.enemyspawns[self.id])
		return ["enemyspawner",[self.id,self.spawns,self.spawned]]
	def fromdata(self,data):
		self.id = data[0]
		self.spawns = data[1]
		self.spawned = []
		self.spawn = False
		for item in data[2]:
			for object in storage.objlist:
				if isinstance(object,character) and object.state == item.state and object.name == item.name and object.id == self.id and object not in self.spawned:
					self.spawned.append(object)

	def spawnsaved(self):
		self.spawn = False
		for item in storage.enemyspawns[self.id]:
			self.spawned.append(globals()[item[0]](*item[1]))
	def update(self):
		index = 0
		if self.spawn:
			self.spawnsaved()
		while index < len(self.spawned):
			item = self.spawned[index]
			if item not in storage.objlist:
				self.spawned.remove(item)
				storage.enemyspawns[self.id] = storage.enemyspawns[self.id][:index]+storage.enemyspawns[self.id][index+1:]
				index -= 1
			else:
				#print(item.x,item.y,item.z)
				storage.enemyspawns[self.id][index][1][0] = item.x
				storage.enemyspawns[self.id][index][1][1] = item.y
				storage.enemyspawns[self.id][index][1][2] = item.z
			index += 1
			#print(storage.enemyspawns)

#as the name suggests, this manages cutscenes. It finds objects in the loaded game cell and gives them instructions, after locking down their free will for a bit.
#however, this is also to be used for all dialog loading purposes and, if we ever make one, loading the pause menu.
#I did not set out to make a system where the pause menu was best classified as a "cutscene", but here we are anyway.
class cutsceneplayer(sharedlib.gameobject):
	def __init__(self,name="test"):
		super().__init__()
		#Ricardo has a similar option in his code for the VN cutscenes, so credit to him. 
		if isinstance(name,list):
			self.blueprint = name
		else:
			self.blueprint = copy.deepcopy(storage.cutscenes[name])
		self.name = name
		self.itr = 0
		storage.actlock = True

	def todata(self):
		return ["cutsceneplayer",[self.name,self.itr]]

	def fromdata(self,data):
		self.name = data[0] 
		if isinstance(self.name,list):
			self.blueprint = self.name
		else:
			self.blueprint = copy.deepcopy(storage.cutscenes[self.name])
		self.itr = data[1]
		print(self.itr)
		storage.actlock = True

	def render(self):
		pass

	def loadscene(self,name):
		self.blueprint = copy.deepcopy(storage.cutscenes[name])
		self.name = name
		self.itr = 0

	def update(self):
		action = self.blueprint[self.itr]
		#print(action)
		match action[0]:
			case "create":
				obj = globals()[action[1][0]](*action[1][1])
				self.itr += 1
			case "ui":
				target = self.findui()
				if not target:
					pass
				else:
					getattr(target,action[1][0])(*action[1][1:])
				self.itr += 1
			case "cam":
				getattr(storage.camera,action[1][0])(*action[1][1:])
				self.itr += 1
			case "char":
				if action[1][0] == "partyleader":
					for item in storage.party:
						if item.state == 3:
							action[1][0] = item.name
							action[1][1] = item.id
							break
				if isinstance(action[1][1],int) or action[1][1] == None:
					target = self.findchar(action[1][0],action[1][1])
					if not target:
						pass
						result = True
					else:
						result = getattr(target,action[1][2])(*action[1][3:])
				else:
					target = self.findchar(action[1][0],id)
					if not target:
						pass
						result = True
					else:
						result = getattr(target,action[1][1])(*action[1][2:])
				if result != False:
					self.itr += 1
			case "loadcutscene":
				self.loadscene(action[1])
			case "loadifprogress":
				if action[1][1] == storage.missionprogress[action[1][0]]:
					self.loadscene(action[1][2])
					return
				self.itr += 1
			case "loadiflessprogress":
				if action[1][1] > storage.missionprogress[action[1][0]]:
					self.loadscene(action[1][2])
					return
				self.itr += 1
			case "loadifinparty":
				for member in storage.party:
					if action[1][0] == member.name + str(member.id):
						self.loadscene(action[1][1])
						return
				self.itr += 1
			case "loadifleader":
				for member in storage.party:
					if member.state == 3:
						if action[1][0] == member.name + str(member.id):
							self.loadscene(action[1][1])
							return
				self.itr += 1
			case "doiffurther":
				for member in storage.party:
					if member.state == 3:
						if (member.x-action[1][0][0])**2+(member.y-action[1][0][1])**2>action[1][1]**2:
							action = action[1][2][0]
							return
				if len(action[1]) > 2:
					action = action[1][2][1]
					return
				self.itr += 1
			case "doifprogress":
				if action[1][1] == storage.missionprogress[action[1][0]]:
					self.blueprint[self.itr] = action[1][2]
					return
				self.itr += 1
			case "doifleader":
				for member in storage.party:
					if member.state == 3:
						if action[1][0] == member.name + str(member.id):
							self.blueprint[self.itr] = action[1][1][0]
							return
				if len(action[1][1]) > 1:
					self.blueprint[self.itr] = action[1][1][1]
					return
				self.itr += 1
			case "doifinparty":
				for member in storage.party:
					if action[1][0] == member.name + str(member.id):
						self.blueprint[self.itr] = action[1][1][0]
						return
				if len(action[1][1]) > 1:
					self.blueprint[self.itr] = action[1][1][1]
					return
				self.itr += 1
			case "loadfromui":
				target = self.findui()
				if not target:
					pass
				else:
					self.loadscene(target.outcomes[target.active])
			case "wait":
				if action[1] == "enter":
					if pygame.K_RETURN in storage.newkeys:
						self.itr += 1
				elif action[1] == "lshift":
					if pygame.K_LSHIFT in storage.newkeys:
						self.itr += 1
				else:
					action[1] -= storage.deltatime
					if action[1] <= 0:
						self.itr += 1
			case "partywarpto":
				itr = 0
				for member in storage.party:
					if member.state == 3:
						member.x = action[1][0]
						member.y = action[1][1]
						member.z = action[1][2]
					else:
						angle = itr*2*math.pi/len(storage.party)
						member.x = action[1][0]+(100*math.sin(angle))
						member.y = action[1][1]+(100*math.cos(angle))
						member.z = action[1][2]
					itr += 1
				self.itr += 1
			case "advancequest":
				if storage.missionprogress[action[1]] < action[2]:
					storage.missionprogress[action[1]] = action[2]
				self.itr += 1
			case "loadgame":
				sharedlib.loadgame(action[1])
				self.itr += 1
			case "loadvn":
				sharedlib.start_cutscene(action[1])
			case "theyfight":
				self.itr += 1
				storage.winstate = save()
				sharedlib.loadgame(action[1])
		if len(self.blueprint) == self.itr:
			self.delete()

	def findui(self):
		for obj in storage.objlist:
			if isinstance(obj,uiobject):
				return obj
		return False

	def findchar(self,name,id):
		#print(name,id,"Testing...")
		for obj in storage.objlist:
			if isinstance(obj,character) and obj.name == name:
				#print(obj.name,obj.id)
				if id == None or id == obj.id:
					#print("FOUND!")
					return obj
		return False

	def delete(self):
		if self in storage.objlist:
			storage.objlist.remove(self)
			storage.actlock = False

class combatmanager(sharedlib.gameobject):
	def __init__(self,mode):
		super().__init__()
		#NOTE: this requires the combat manager to be spawned AFTER all other gameobjects, so that it catches them.
		#Maybe we should add a clause to character spawining to drop newcomers in here if we're in combat mode?
		self.fighters = []
		for obj in storage.objlist:
			if isinstance(obj,character):
				self.fighters.append(obj)
			if isinstance(obj,cutsceneplayer):
				obj.delete()
		self.fighters.sort(key = lambda x:x.getstat("priority"),reverse = True)
		self.turn = 0
		storage.ui.setcombattant(self.fighters[self.turn])
		storage.ui.loadui("Combat")
		self.state = mode
		if self.state == 0:
			storage.ui.loadcombatmenu("main")
		elif self.state == 1:
			storage.ui.loadcombatmenu("mainnorun")
		storage.actlock = True
		self.fighters[self.turn].combatactive = True
		for obj in self.fighters:
			pos = obj.getcombatlocation()
			if [obj.x,obj.y] != pos:
				obj.x,obj.y = pos[0],pos[1]
		self.aborted = False

	def todata(self):
		return ["combatmanager",[self.fighters,self.turn]]

	def fromdata(self,data):
		self.name = data[0]
		self.blueprint = copy.deepcopy(storage.cutscenes[self.name])
		self.turn = data[1]
		storage.ui.setcombattant(self.fighters[self.turn])
		storage.ui.loadui("Combat")
		storage.ui.loadcombatmenu("main")
		storage.actlock = True
		self.aborted = False

	def findui(self):
		for obj in storage.objlist:
			if isinstance(obj,uiobject):
				return obj
		return False

	def render(self):
		pass

	def update(self):
		#print(self.turn)
		combattant = self.fighters[self.turn]
		#print(combattant.name)
		if combattant.combatactive == False:
			win = True
			lose = True
			index = 0
			while index < len(self.fighters):
				obj = self.fighters[index]
				if obj.combatactive == False:
					pos = obj.getcombatlocation()
					if [obj.x,obj.y] != pos:
						obj.warpto((pos[0],pos[1],0))
				if obj not in storage.objlist:
					self.fighters.remove(obj)
					index -= 1
				elif obj.state < 2:
					win = False
				elif obj.state in [3,2]:
					lose = False
				index += 1

			if win == True:
				self.win()
			elif lose == True:
				if self.aborted == False:
					self.gameover()
				else:
					self.run()
			else:
				for item in combattant.timedfx:
					if item[0] == "turnend":
						item[1] -= 60
						if item[1] <= 0:
							combattant.timedfx.remove(item)
							getattr(combattant,item[2])(*item[3])
				self.turn += 1
				if self.turn >= len(self.fighters):
					self.turn = 0
					self.fighters.sort(key = lambda x:x.getstat("priority"),reverse = True)
				combattant = self.fighters[self.turn]
				combattant.combatactive = True
				storage.ui.setcombattant(combattant)
				for item in combattant.timedfx:
					if item[0] == "turnstart":
						item[1] -= 60
						if item[1] <= 0:
							combattant.timedfx.remove(item)
							getattr(combattant,item[2])(*item[3])
				if combattant.state > 1:
					storage.ui.loadui("Combat")
					if self.state == 0:
						storage.ui.loadcombatmenu("main")
					elif self.state == 1:
						storage.ui.loadcombatmenu("mainnorun")
					storage.actlock = True
				else:
					combattant.combatAI(combattant)
			if self.turn >= len(self.fighters):
				self.turn = 0

	def gameover(self):
		sharedlib.loadmenu("testmain")
	
	def run(self):
		for man in self.fighters:
			for item in man.timedfx:
				if item[0] == "combatend":
					man.timedfx.remove(item)
					getattr(man,item[2])(*item[3])
			man.writeglobalstats()
		storage.ui.loadui("Blank")
		print("#running")
		softload(storage.runstate)

	def win(self):
		winanim = [["ui",["loadui","Win"]],["wait","enter"]]
		for man in self.fighters:
			if man.name != None and "Win" + man.name + str(man.id) in storage.cutscenes.keys():
				winanim.insert(1,*(storage.cutscenes["Win"+man.name+str(man.id)]))
			for item in man.timedfx:
				if item[0] == "combatend":
					man.timedfx.remove(item)
					getattr(man,item[2])(*item[3])
			man.writeglobalstats()
		self.delete()
		#print(winanim)
		cutsceneplayer(winanim)

	def findchar(self,name):
		for obj in storage.objlist:
			if isinstance(obj,character) and obj.name == name:
				return obj
		return False
	

class party(sharedlib.gameobject):
	def __init__(self,burner=0):
		for item in storage.partyspawn:
			obj = globals()[item[0]](*item[1])

class musicbg(sharedlib.gameobject):
	def __init__(self,song = "Christmas.wav",force = False):
		super().__init__()
		self.song = song
		self.force = force
	def todata(self):
		return ["musicbg",[self.song,self.force]]
	def fromdata(self,data):
		self.song = data[0]
		self.force = data[1]
	def update(self):
		if storage.songpriority == False:
			soundutils.playsong(self.song,not self.force)
	def delete(self):
		super().delete()
		#NOTE: This is commented out for now, and I don't THINK it should come up in the demo. HOWEVER, it is stupid and should be fixed.
		#soundutils.stopsong()
#save and load functions
def save():
	debug = storage.debug
	partyspawn = copy.deepcopy(storage.partyspawn)
	camerabounds = copy.deepcopy(storage.cambounds)
	missionprogress = copy.deepcopy(storage.missionprogress)
	actlock = storage.actlock
	modstats = copy.deepcopy(storage.modstats)
	statuseffects = copy.deepcopy(storage.timedfx)
	items = []
	# Skip known UI/non-persistent things
	for item in storage.objlist:
		if hasattr(item, "todata"):
			thing = item.todata()
			if thing != None:
				items.append(thing)
	enemyspawns = copy.deepcopy(storage.enemyspawns)
	return [debug,partyspawn,items,camerabounds,missionprogress,modstats,statuseffects,actlock,enemyspawns]

#NOTE: softload is here for loading out of combats. It is the same as load, but it neglects certain things so that story progression and item uses will carry over.
def softload(file):
	storage.orderreset = True
	storage.debug = file[0]
	storage.partyspawn = file[1]
	storage.party = []
	storage.objlist = []
	storage.cambounds = copy.deepcopy(file[3])
	for item in file[2]:
		globals()[item[0]]().fromdata(item[1])
	storage.actlock = file[7]
	storage.enemyspawns = copy.deepcopy(file[8])

def load(file):
	storage.orderreset = True
	storage.debug = file[0]
	storage.partyspawn = file[1]
	storage.party = []
	storage.objlist = []
	storage.cambounds = copy.deepcopy(file[3])
	storage.missionprogress = copy.deepcopy(file[4])
	storage.modstats = copy.deepcopy(file[5])
	storage.timedfx = copy.deepcopy(file[6])
	for item in file[2]:
		globals()[item[0]]().fromdata(item[1])
	storage.actlock = file[7]
	storage.enemyspawns = copy.deepcopy(file[8])

def findui():
	for obj in storage.objlist:
		if isinstance(obj,uiobject):
			return obj
	return False
def findcombatman():
	for obj in storage.objlist:
		if isinstance(obj,combatmanager):
			return obj
	return False

#if you saw the earlier comment in the menu.py file about a horrid clunky solution, you already know the deal with this one.
def loadbluprint(name):
	#NOTE: I hate this. However, we need it to keep cutscenes playing between cell loads, which is how I figured we should do transitions.
	index = 0
	storage.party = []
	while index < len(storage.objlist):
		item = storage.objlist[index]
		if not isinstance(item,cutsceneplayer):
			item.delete()
			index -= 1
		index += 1
	storage.orderreset = True
	for item in storage.persistobjs+storage.levels.get(name):
		#print(item)
		#NOTE: Every item has a spawn conditions array. Each entry is of the form [checktype,value1,value2...] and will stop the object from spawning if one of the entries represents a true condition.
		spawn = True
		if len(item) == 3:
			for cond in item[2]:
				match cond[0]:
					case "earlierinplot":
						if storage.missionprogress[cond[1]] < cond[2]:
							spawn = False
					case "laterinplot":
						if storage.missionprogress[cond[1]] > cond[2]:
							spawn = False
		if spawn:
			obj = globals()[item[0]](*item[1])

sharedlib.loadgame = loadbluprint
#NOTE: Hate. Let me tell you how much I've come to hate this solution since I implemented it. There are over 1300 cubic centimeters of of brain connections in tiny gray cells that fill my skull. If the word "hate" was engraved on each nanoangstrom of those thousands of centimeters it would honestly be a bit overkill. I'm just a bit annoyed and using this as a way of venting.
sharedlib.cutscenestart = cutsceneplayer