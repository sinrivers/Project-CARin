"""
Filename: gameutils.py
Author: Taliesin Reese
Version: 8.1
Date: 11/10/2025
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
	def __init__(self,x=0,y=0,z=0,w=0,h=0,d=0,state=0,name=None):
		super().__init__(x,y,z,w,h,d)
		self.name = name
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
		self.walkspeed = self.getstat("priority")
		self.jumpspeed = 5 * self.getstat("priority")
		if self.name == None or not hasattr(ais,self.name):
			self.combatAI = getattr(ais, "Missingno")
		else:
			self.combatAI = getattr(ais, self.name)
		self.traction = .5
		self.gravity = 1
		self.interactd = 50
		self.interactpoint = [self.x+self.w+self.interactd,self.y+self.h/2,self.z-self.d/2]
		self.combatactions = []
		self.combatactive = False
		self.combatactionsindex = 0
		self.combattarget = []
		self.iframes = 0

	def todata(self):
		self.writeglobalstats()
		return ["character",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.framecounter,self.framenumber,self.name,self.combatactive,self.state,self.iframes,self.angle]]

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
		self.animname = "stand0"
		self.animpriority = False
		self.pullglobalstats()
		self.walkspeed = self.getstat("priority")
		self.jumpspeed = 5 * self.getstat("priority")
		if self.name == None or not hasattr(ais,self.name):
			self.combatAI = getattr(ais, "Missingno")
		else:
			self.combatAI = getattr(ais, self.name)
		if self.state == 3:
			storage.camera.target = self

	def update(self):
		super().update()
		if self.iframes > 0:
			self.iframes -= storage.deltatime
		#this is for deltatime reasons.
		self.physics()
		#update locations based on speed
		self.x += self.speed[0]/2*storage.deltatime
		self.y += self.speed[1]/2*storage.deltatime
		self.z += self.speed[2]/2*storage.deltatime
		self.getpoints()
		#check collisions with ground
		self.checkcollide()
		#natural decrease of speed
		self.physics()

		#process whatever actions needed for this character
		if storage.ui.actlock == False:
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
			if self.combatactive == True:
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
	def getstat(self,stat):
		if stat == "maxhp":
			index = 0
		elif stat == "maxdata":
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
			return self.modstats[8]
		elif stat == "spentdata":
			return self.modstats[9]
		return self.basestats[index] + self.modstats[index]

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
		if self.name == None:
			self.basestats = copy.deepcopy(storage.basestats["Missingno"])
			self.modstats = copy.deepcopy(storage.modstats["Missingno"])
			self.timedfx = copy.deepcopy(storage.timedfx["Missingno"])
		else:
			self.basestats = copy.deepcopy(storage.basestats[self.name])
			self.modstats = copy.deepcopy(storage.modstats[self.name])
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
			

	def setanim(self,name,request=False):
		if self.animpriority == False or request == True:
			if self.animname != name:
				self.animname = name
				self.animpriority = request
				self.framenumber = 0
				self.framecounter = 0
		else:
			self.queuedanim = name

	def animpicker(self):
		#pick an animation
		if self.speed[0] > 0 or self.speed[1] > 0:
			self.setanim("walk"+str(self.angle))
		else:
			self.setanim("stand"+str(self.angle))
		if self.speed[2] < 0:
			self.setanim("airup"+str(self.angle))
		elif self.speed[2] > 0:
			self.setanim("airdown"+str(self.angle))
			
	def animupdate(self):
		self.framecounter += storage.deltatime
		if storage.animinfo[self.name]["anims"][self.animname][self.framenumber][1] < self.framecounter:
			self.framecounter -= storage.animinfo[self.name]["anims"][self.animname][self.framenumber][1]
			self.framenumber += 1
			if self.framenumber >= len(storage.animinfo[self.name]["anims"][self.animname]):
				self.framenumber = 0
				if self.animpriority:
					if hasattr(self,"queuedanim"):
						self.animname = self.queuedanim

	def render(self):
		if self.name == None:
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
		if self.iframes <= 0:
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
		self.speed[2] = -self.jumpspeed

	def physics(self):
		if self.speed[0] > 0:
			if self.speed[0] < self.traction:
				self.speed[0] = 0
			else:
				self.speed[0] -= self.traction*storage.deltatime

		elif self.speed[0] < 0:
			if self.speed[0] > -self.traction:
				self.speed[0] = 0
			else:
				self.speed[0] += self.traction*storage.deltatime

		if self.speed[1] > 0:
			if self.speed[1] < self.traction:
				self.speed[1] = 0
			else:
				self.speed[1] -= self.traction*storage.deltatime

		elif self.speed[1] < 0:
			if self.speed[1] > -self.traction:
				self.speed[1] = 0
			else:
				self.speed[1] += self.traction*storage.deltatime
		if self.grounded == False:
			self.speed[2] += self.gravity*storage.deltatime

	def followupdates(self):
		for charac in storage.party:
			if charac.state == 3:
				dist = (charac.x-self.x)**2+(charac.y-self.y)**2+(charac.z-self.z)**2
				if dist < 2*5125:
					if self.x < charac.x:
						self.speed[0] = self.walkspeed
					elif self.x > charac.x:
						self.speed[0] = -self.walkspeed
					if self.y < charac.y:
						self.speed[1] = self.walkspeed
					elif self.y > charac.y:
						self.speed[1] = -self.walkspeed
					if self.z > charac.z and self.grounded == True:
						self.jump()
	def NPCupdates(self):
		pass
	def enemyupdates(self):
		self.NPCupdates()
		if self.iframes <= 0:
			for charac in storage.party:
				if charac.state == 3:
					dist = (charac.x-self.x)**2+(charac.y-self.y)**2+(charac.z-self.z)**2
					if True:
						if self.x < charac.x:
							self.speed[0] = self.walkspeed
						elif self.x > charac.x:
							self.speed[0] = -self.walkspeed
						if self.y < charac.y:
							self.speed[1] = self.walkspeed
						elif self.y > charac.y:
							self.speed[1] = -self.walkspeed
					
	def controlupdates(self):
		#get control updates
		#NOTE: This method for determining angles is inherently flawed, and as a result you will almost never see the non-cardinal idle sprites. Maybe fix later?
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
			for obj in storage.objlist:
				if isinstance(obj, object3d):
					if obj != self and obj.collidepoint(self.interactpoint):
						obj.interact(self)
		if pygame.K_9 in storage.newkeys:
			load(storage.savestate)
		if pygame.K_LSHIFT in storage.newkeys:
			cutsceneplayer("Pause")
		if walk:
			self.speed[0] = self.walkspeed*math.cos(self.angle/180*math.pi)
			self.speed[1] = -self.walkspeed*math.sin(self.angle/180*math.pi)
	
			self.interactpoint = [self.center[0]+(self.interactd)*math.cos(self.angle/180*math.pi),
				      self.center[1]-(self.interactd)*math.sin(self.angle/180*math.pi),
				      self.z-self.d/2]
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
	

	def goto(self):
		pos = self.combatactions[self.combatactionsindex][1]
		if [self.x,self.y] == pos:
			self.combatactionsindex += 1
		else:
			if (self.x-pos[0])**2 + (self.x-pos[0])**2 <= self.walkspeed:
				self.x = pos[0]
				self.y = pos[1]
				self.combatactionsindex += 1
			else:
				if self.x-pos[0] != 0:
					if self.y-pos[1] != 0:
						self.angle = math.atan((self.y-pos[1]) / (self.x-pos[0]))
					elif self.x > pos[0]:
						self.angle = 180
					else:
						self.angle = 0
				elif self.y < pos[1]:
					self.angle = 90
				else:
					self.angle = 270
				self.speed[0] = self.walkspeed*math.cos(self.angle/180*math.pi)
				self.speed[1] = -self.walkspeed*math.sin(self.angle/180*math.pi)

	def gototarget(self):
		if self.combattarget[0].state < 2:
			pos = [self.combattarget[0].x-20-self.w,self.combattarget[0].y]
		else:
			pos = [self.combattarget[0].x+20,self.combattarget[0].y]
		if [self.x,self.y] == pos:
			self.combatactionsindex += 1
		else:
			if (self.x-pos[0])**2 + (self.x-pos[0])**2 <= self.walkspeed:
				self.x = pos[0]
				self.y = pos[1]
				self.combatactionsindex += 1
			else:
				if self.x-pos[0] != 0:
					if self.y-pos[1] != 0:
						self.angle = math.atan((self.y-pos[1]) / (self.x-pos[0]))
					elif self.x > pos[0]:
						self.angle = 180
					else:
						self.angle = 0
				elif self.y < pos[1]:
					self.angle = 90
				else:
					self.angle = 270
				self.speed[0] = self.walkspeed*math.cos(self.angle/180*math.pi)
				self.speed[1] = -self.walkspeed*math.sin(self.angle/180*math.pi)

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
		print("Why are we still here? Just to suffer?")
		self.combattarget[0].delete()
		self.combattarget = self.combattarget[1:]
		self.combatactionsindex += 1
	def suicide(self):
		self.delete()
		self.combatactive = False
	

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

class plat(collider):
	def todata(self):
		return ["plat",[self.x,self.y,self.z,self.w,self.h,self.d,self.speed,self.grounded,self.angle,self.descend,self.image,self.offset]]

	def collidecheck(self, hitter):
		if self.angle == 0:
			if self.collidepoint(hitter.right) != False:
				hitter.x -= hitter.x+hitter.w-self.x
			if self.collidepoint(hitter.left) != False:
				hitter.x -= hitter.x-(self.x+self.w)
			if self.collidepoint(hitter.front) != False:
				hitter.y -= hitter.y+hitter.h-self.y
			if self.collidepoint(hitter.back) != False:
				hitter.y -= hitter.y-(self.y+self.h)
		else:
			result = self.collidepoint(hitter.right)
			if result != False:
				hitter.x += result[0]
				hitter.y += result[1]
			result = self.collidepoint(hitter.left)
			if result != False:
				hitter.x += result[0]
			result = self.collidepoint(hitter.front)
			if result != False:
				hitter.x += result[0]
				hitter.y += result[1]
			result = self.collidepoint(hitter.back)
			if result != False:
				hitter.x += result[0]
				hitter.y += result[1]
		if self.collidepoint(hitter.top) != False:
			hitter.z -= hitter.z-self.d+self.z
		result = self.collidepoint(hitter.bottom)
		if result != False:
			hitter.z -= hitter.z - (self.z-self.d+result[2])
			hitter.speed[2] = 0
			hitter.grounded = True
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
											int(self.y+(self.z)-storage.camfocus[1]+(self.h*math.cos(self.angle)))]))
				pygame.draw.polygon(storage.spritecanvas, (0,255,0), ([int(self.x-storage.camfocus[0]),
											int(self.y+self.z   +self.descend[0]   -self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z   +self.descend[1]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[2]   -self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z   +self.descend[3]   -self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))]))
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
				storage.spritecanvas.blit(storage.spritesheet,[self.offset[0]+self.x+self.w/2,self.offset[1]+self.y+self.h/2-self.z-self.d/2],holder[:5])



class mapdisplay(sharedlib.gameobject):
	def __init__(self,path="testmap",x=0,y=0):
		super().__init__()
		self.x = x
		self.y = y
		self.image = pygame.image.load(f"Assets/graphics/{path}.png").convert()
		self.path = path
		self.w,self.h = self.image.get_size()

	def todata(self):
		return ["mapdisplay",[self.x,self.y,self.w,self.h,self.path]]

	def fromdata(self,data):
		self.x = data[0]
		self.y = data[1]
		self.w = data[2]
		self.h = data[3]
		self.path = data[4]
		self.image = pygame.image.load(f"Assets/graphics/{self.path}.png").convert()

	def update(self):
		super().update()
		if self not in storage.objlist:
			print("Why is this still happening?")
		if self.x < storage.cambounds[0]:
			storage.cambounds[0] = self.x
		if self.x+self.w > storage.cambounds[2]:
			storage.cambounds[2] = self.x+self.w
			print(self.path)
		if self.y < storage.cambounds[1]:
			storage.cambounds[1] = self.y
		if self.y+self.h > storage.cambounds[3]:
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
		else:
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
		self.diamessages = []
		self.choices = []
		self.outcomes = []
		self.active = 0
		self.dictmode = 0
		self.dictoffset = 0
		self.submenu = "main"
		self.combattant = None
		self.actlock = False
		storage.ui = self

	def todata(self):
		return ["uiobject",[self.mode,copy.deepcopy(self.diachars),copy.deepcopy(self.diamessages),copy.deepcopy(self.choices),copy.deepcopy(self.outcomes),self.active]]

	def fromdata(self,data):
		self.mode = data[0]
		self.diachars = copy.deepcopy(data[1])
		self.diamessages = copy.deepcopy(data[2])
		self.choices = copy.deepcopy(data[3])
		self.outcomes = copy.deepcopy(data[4])
		self.combattant = None
		self.actlock = False
		self.submenu = "main"
		self.active = data[5]

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
		self.actlock = True
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

	def setspeaker(self,name,side = 0,emote="Neutral"):
		for item in self.diachars:
			if name == item[0]:
				item[1] = emote
				return
		self.diachars.append([name,emote,side])

	def loadui(self,name):
		if name != "Dialogue" and self.mode == "Dialogue":
			self.diamessages.append("<END OF LINE>")
			self.diachars = []
		elif name == "Dialogue" and self.mode != "Dialogue":
			self.diamessages.append("<CONVERSATION STARTED>")
		elif name == "Dictionary":
			self.actlock = True
		self.mode = name

	def render(self):
		if self.mode == "Blank":
			storage.uicanvas.blit(storage.writer.render("This area left intentionally blank",False,(255,255,255)),(0,0))#(self.x,self.y))
		if self.mode == "Win":
			storage.uicanvas.blit(storage.writer.render("THIS SCREEN CONTAINS WIN",False,(255,255,255)),(0,0))#(self.x,self.y))
		elif self.mode == "Dictionary":
			if self.dictmode == 0:
				storage.uicanvas.blit(storage.writer.render("Story Dictionary",False,(255,255,0)),(50,20))
				pygame.draw.rect(storage.uicanvas,(127,127,0),[40,40,200,400])
				pygame.draw.rect(storage.uicanvas,(127,127,0),[240,40,440,400])
				pygame.draw.rect(storage.uicanvas,(255,255,0),[40,40,200,400],5)
				pygame.draw.rect(storage.uicanvas,(255,255,0),[240,40,440,400],5)
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
						storage.uicanvas.blit(storage.writer.render(item,False,(255,255,0)),(50,50+itr*20+self.dictoffset))
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
				pygame.draw.rect(storage.uicanvas,(127,127,0),[160,40,400,400])
				pygame.draw.rect(storage.uicanvas,(255,255,0),[160,40,400,400],5)
				storage.uicanvas.blit(storage.writer.render(f"{self.combattant.name}:{self.combattant.getstat("maxhp")-self.combattant.getstat("damage")}/{self.combattant.getstat("maxhp")}HP {self.combattant.getstat("maxdata")-self.combattant.getstat("spentdata")}/{self.combattant.getstat("maxdata")}DATA ",False,(255,255,255)),[165,45])
				size += storage.writer.size(f"it is {self.combattant.name}'s turn.")[1]
				for index in range(len(self.choices)):
					size += 5
					if self.active == index:
						storage.uicanvas.blit(storage.writer.render(">"+self.choices[index],False,(255,255,255)),[165,45+size])
					else:
						storage.uicanvas.blit(storage.writer.render(self.choices[index],False,(255,255,0)),[165,45+size])
					size += storage.writer.size(self.choices[index])[1]

		elif self.mode == "Dialogue":
			pygame.draw.rect(storage.uicanvas,(127,127,0),[160,40,400,400])
			pygame.draw.rect(storage.uicanvas,(255,255,0),[160,40,400,400],5)
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
			for item in self.diachars:
				if item[2] == 0:
					x = 110
					y = Lspacing * itrL + Lspacing/2
					itrL += 1
				else:
					x = 570
					y = Rspacing * itrR + Rspacing/2
					itrR += 1
				pygame.draw.rect(storage.uicanvas,(127,127,0),[x-5,y-5,50,50])
				pygame.draw.rect(storage.uicanvas,(255,255,0),[x-5,y-5,50,50],5)
				storage.uicanvas.blit(storage.spritesheet, [x,y],storage.animinfo["Portraits"][item[0]+item[1]])
				
			size = 0
			for item in self.diamessages:
				texttorender = item.split("\n")
				for line in texttorender:
					size += storage.writer.size(line)[1]
				size += 5
			for index in range(len(self.choices)):
				size += storage.writer.size(self.choices[index])[1]
				size += 5
			for item in self.diamessages:
				texttorender = item.split("\n")
				for line in texttorender:
					storage.uicanvas.blit(storage.writer.render(line,False,(255,255,0)),[165,440-size])
					size -= storage.writer.size(line)[1]
				size -= 5
			for index in range(len(self.choices)):
				size -= 5
				if self.active == index:
					storage.uicanvas.blit(storage.writer.render(">"+self.choices[index],False,(255,255,255)),[165,440-size])
				else:
					storage.uicanvas.blit(storage.writer.render(self.choices[index],False,(255,255,0)),[165,440-size])
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

#as the name suggests, this manages cutscenes. It finds objects in the loaded game cell and gives them instructions, after locking down their free will for a bit.
#however, this is also to be used for all dialog loading purposes and, if we ever make one, loading the pause menu.
#I did not set out to make a system where the pause menu was best classified as a "cutscene", but here we are anyway.
class cutsceneplayer(sharedlib.gameobject):
	def __init__(self,name="test"):
		super().__init__()
		self.blueprint = copy.deepcopy(storage.cutscenes[name])
		self.name = name
		self.itr = 0
		storage.ui.actlock = True

	def todata(self):
		return ["cutsceneplayer",[self.name,self.itr]]

	def fromdata(self,data):
		self.name = data[0]
		self.blueprint = copy.deepcopy(storage.cutscenes[self.name])
		self.itr = data[1]

	def render(self):
		pass

	def loadscene(self,name):
		self.blueprint = copy.deepcopy(storage.cutscenes[name])
		self.itr = 0

	def update(self):
		action = self.blueprint[self.itr]
		match action[0]:
			case "ui":
				target = self.findui()
				if not target:
					pass
				else:
					getattr(target,action[1][0])(*action[1][1:])
				self.itr += 1
			case "char":
				target = self.findchar(action[1][0])
				if not target:
					pass
				else:
					getattr(target,action[1][1])(*action[1][2:])
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
		if len(self.blueprint) == self.itr:
			self.delete()

	def findui(self):
		for obj in storage.objlist:
			if isinstance(obj,uiobject):
				return obj
		return False

	def findchar(self,name):
		for obj in storage.objlist:
			if isinstance(obj,character) and obj.name == name:
				return obj
		return False

	def delete(self):
		if self in storage.objlist:
			storage.objlist.remove(self)
			storage.ui.actlock = False

class combatmanager(sharedlib.gameobject):
	def __init__(self,mode):
		super().__init__()
		#NOTE: this requires the combat manager to be spawned AFTER all other gameobjects, so that it catches them.
		#Maybe we should add a clause to character spawining to drop newcomers in here if we're in combat mode?
		self.fighters = []
		for obj in storage.objlist:
			if isinstance(obj,character):
				self.fighters.append(obj)
		self.turn = 0
		storage.ui.setcombattant(self.fighters[self.turn])
		storage.ui.loadui("Combat")
		self.state = mode
		if self.state == 0:
			storage.ui.loadcombatmenu("main")
		elif self.state == 1:
			storage.ui.loadcombatmenu("mainnorun")
		storage.ui.actlock = True
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
		storage.ui.actlock = True
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
		if combattant.combatactive == False:
			win = True
			lose = True
			index = 0
			while index < len(self.fighters):
				obj = self.fighters[index]
				if obj.combatactive == False:
					pos = obj.getcombatlocation()
					if [obj.x,obj.y] != pos:
						obj.x,obj.y = pos[0],pos[1]
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
					self.fighters.sort(key = lambda x:x.getstat("priority"))
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
					storage.ui.actlock = True
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
		for man in self.fighters:
			for item in man.timedfx:
				if item[0] == "combatend":
					man.timedfx.remove(item)
					getattr(man,item[2])(*item[3])
			man.writeglobalstats()
		self.delete()
		cutsceneplayer("Win")

	def findchar(self,name):
		for obj in storage.objlist:
			if isinstance(obj,character) and obj.name == name:
				return obj
		return False
	

class party(sharedlib.gameobject):
	def __init__(self,burner=0):
		for item in storage.partyspawn:
			obj = globals()[item[0]](*item[1])

#save and load functions
def save():
	debug = storage.debug
	partyspawn = copy.deepcopy(storage.partyspawn)
	camerabounds = copy.deepcopy(storage.cambounds)
	missionprogress = copy.deepcopy(storage.missionprogress)
	modstats = copy.deepcopy(storage.modstats)
	statuseffects = copy.deepcopy(storage.timedfx)
	items = []
	data = None
# Skip known UI/non-persistent things
	if getattr(items, "persist", True) is False or getattr(items, "is_ui", False):
		data = None
	elif hasattr(items, "todata"):
		data = items.todata()

	if data is not None:
		items.append(data)
	return [debug,partyspawn,items,camerabounds,missionprogress,modstats,statuseffects]

#NOTE: softload is here for loading out of combats. It is the same as load, but it neglects certain things so that story progression and item uses will carry over.
def softload(file):
	storage.orderreset = True
	storage.debug = file[0]
	storage.partyspawn = file[1]
	storage.objlist = []
	storage.cambounds = copy.deepcopy(file[3])
	for item in file[2]:
		globals()[item[0]]().fromdata(item[1])

def load(file):
	storage.orderreset = True
	storage.debug = file[0]
	storage.partyspawn = file[1]
	storage.objlist = []
	storage.cambounds = copy.deepcopy(file[3])
	storage.missionprogress = copy.deepcopy(file[4])
	storage.modstats = copy.deepcopy(file[5])
	storage.timedfx = copy.deepcopy(file[6])
	for item in file[2]:
		globals()[item[0]]().fromdata(item[1])

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
	storage.objlist = []
	for item in storage.persistobjs+storage.levels.get(name):
		print(item)
		obj = globals()[item[0]](*item[1])

sharedlib.loadgame = loadbluprint