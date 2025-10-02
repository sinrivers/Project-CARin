"""
Filename: gameutils.py
Author: Taliesin Reese
Version: 1.0
Date: 9/27/2025
Purpose: Gameplay tools for Project CARIn
"""
#setup
import sharedlib
import storage
import pygame

#classes
class object3d(sharedlib.gameobject):
	def __init__(self,x,y,z,w,h,d):
		super().__init__()
		self.x = x
		self.y = y
		self.z = z
		self.w = w
		self.h = h
		self.d = d
		self.speed = [0,0,0]
		self.grounded = True
		self.walkspeed = 1
		self.jumpspeed = 10
		self.traction = 0.5
		self.gravity = 1
	def render(self):
		pygame.draw.rect(storage.window, (255,0,0), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h))
	def collidepoint(self,point):
		if self.x <= point[0] <=self.x + self.w:
			if self.y <= point[1] <= self.y+self.h:
				if self.z >= point[2] >= self.z-self.d:
					return True
	def collidebox(self,tester):
		if self.collidepoint([tester.x,tester.y,tester.z]) or self.collidepoint([tester.x+tester.w,tester.y,tester.z]) or self.collidepoint([tester.x,tester.y+tester.h,tester.z]) or self.collidepoint([tester.x+tester.h,tester.y+tester.h,tester.z]):
			if self.z >= tester.z >=self.z - self.d or self.z >= tester.z-tester.d >= self.z - self.d:
				return True
	def interact(self,hitter):
		print("This is a test of the Emergency Brodcast Cube")
	def update(self):
		self.vertsort = [self.y,-self.z+self.d]
	def getpoints(self):
		self.center = [self.x+self.w/2, self.y+self.h/2, self.z-self.d/2]
		self.left = [self.x, self.y + self.h/2, self.z-self.d/2]
		self.right = [self.x + self.w, self.y + self.h/2, self.z-self.d/2]
		self.front = [self.x + self.w/2, self.y + self.h, self.z-self.d/2]
		self.back = [self.x + self.w/2, self.y, self.z-self.d/2]
		self.top = [self.x + self.w/2, self.y + self.h/2, self.z-self.d]
		self.bottom = [self.x + self.w/2, self.y + self.h/2, self.z]

class character(object3d):
	def __init__(self,x,y,z,w,h,d,state):
		super().__init__(x,y,z,w,h,d)
		#the type of character we're dealing with is determined by self.state.
		#Note that self.state was originally supposed to lock or unlock certain actions (i.e. the second hit of a two-hit combo),
		#so this may need it's own variable if such a use ever arrives.
		#States are as follows: 0-NPC Scripted Behaviors. 1-Cutscene Actor. 2-NPC follower. 3-Active Player Character.
		self.state = state
		if self.state == 3:
			storage.camera.target = self
		self.speed = [0,0,0]
		self.grounded = True
		self.walkspeed = 10
		self.jumpspeed = 200
		self.traction = 1
		self.gravity = 1
		self.interactd = 50
		self.interactpoint = [self.x+self.w+self.interactd,self.y+self.w/2,self.z-self.d/2]
	def update(self):
		super().update()
		self.getpoints()
		#check collisions with ground
		self.checkcollide()
		#natural decrease of speed
		self.physics()
		#process whatever actions needed for this character
		match self.state:
			case 0:
				pass
			case 1:
				pass
			case 2:
				self.followupdates()
			case 3:
				self.controlupdates()
		#update locations based on speed
		self.x += self.speed[0]/100
		self.y += self.speed[1]/100
		self.z += self.speed[2]/100

	def render(self):
		if self.state == 3:
			pygame.draw.rect(storage.spritecanvas, (0,0,100), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
			pygame.draw.rect(storage.spritecanvas, (0,0,155), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
			pygame.draw.rect(storage.spritecanvas, (0,0,255), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
		else:
			pygame.draw.rect(storage.spritecanvas, (0,100,100), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
			pygame.draw.rect(storage.spritecanvas, (0,155,155), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
			pygame.draw.rect(storage.spritecanvas, (0,255,255), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
	def checkcollide(self):
		self.grounded = False
		for obj in storage.objlist:
			if isinstance(obj,plat):
				if obj.collidepoint(self.right):
					self.x -= self.x+self.w-obj.x
				if obj.collidepoint(self.left):
					self.x -= self.x-(obj.x+obj.w)
				if obj.collidepoint(self.front):
					self.y -= self.y+self.h-obj.y
				if obj.collidepoint(self.back):
					self.y -= self.y-(obj.y+obj.h)
				if obj.collidepoint(self.top):
					self.z -= self.z-obj.d+obj.z
				if obj.collidepoint(self.bottom):
					self.z -= self.z - (obj.z-obj.d)
					self.speed[2] = 0
					self.grounded = True
		if self.z >= 0:
			self.z = 0
			self.speed[2] = 0
			self.grounded = True
	def physics(self):
		if self.speed[0] > 0:
			self.speed[0] -= self.traction
		elif self.speed[0] < 0:
			self.speed[0] += self.traction
		if self.speed[1] > 0:
			self.speed[1] -= self.traction
		elif self.speed[1] < 0:
			self.speed[1] += self.traction
		if self.grounded == False:
			self.speed[2] += self.gravity
	def followupdates(self):
		for charac in storage.party:
			if charac.state == 3:
				dist = charac.x+charac.y+charac.z
				if dist > 30:
					if self.x < charac.x:
						self.speed[0] = self.walkspeed
					elif self.x > charac.x:
						self.speed[0] = -self.walkspeed
					if self.y < charac.y:
						self.speed[1] = self.walkspeed
					elif self.y > charac.y:
						self.speed[1] = -self.walkspeed
					if self.z > charac.z:
						self.grounded = False
						self.speed[2] = -self.jumpspeed
						
					
	def controlupdates(self):
		#get control updates
		#print(self.interactpoint)
		if storage.keys[pygame.K_a]:
			self.speed[0] = -self.walkspeed
			self.interactpoint = [self.x-self.interactd,self.y+self.w/2,self.z-self.d/2]
		elif storage.keys[pygame.K_d]:
			self.speed[0] = self.walkspeed
			self.interactpoint = [self.x+self.w+self.interactd,self.y+self.w/2,self.z-self.d/2]
		if storage.keys[pygame.K_w]:
			self.speed[1] = -self.walkspeed
			self.interactpoint = [self.x+self.w/2,self.y-self.interactd,self.z-self.d/2]
		elif storage.keys[pygame.K_s]:
			self.speed[1] = self.walkspeed
			self.interactpoint = [self.x+self.w/2,self.y+self.w/2+self.interactd,self.z-self.d/2]
		if pygame.K_SPACE in storage.newkeys and self.grounded:
			self.grounded = False
			self.speed[2] = -self.jumpspeed
		if pygame.K_RETURN in storage.newkeys:
			for obj in storage.objlist:
				if isinstance(obj, object3d):
					if obj != self and obj.collidepoint(self.interactpoint):
						obj.interact(self)

class plat(object3d):
	def __init__(self,x,y,z,w,h,d,mode = 0):
		super().__init__(x,y,z,w,h,d)
		self.undermode = mode
	def collideresolve(self,hitter):
		if hitter.speed[0] > 0:
			xdist= self.x - hitter.x + hitter.w
		elif hitter.speed[0] < 0:
			xdist= self.x + self.y - hitter.x
		hitter.grounded = True
	def interact(self,hitter):
		pass
	def render(self):
		if storage.debug:
			pygame.draw.rect(storage.spritecanvas, (0,100,0), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
			pygame.draw.rect(storage.spritecanvas, (0,155,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
			pygame.draw.rect(storage.spritecanvas, (0,255,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
		else:
			pygame.draw.rect(storage.spritecanvas, (255,0,255), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
	
class mapdisplay(sharedlib.gameobject):
	def __init__(self,path,x,y):
		super().__init__()
		self.x = x
		self.y = y
		self.image = pygame.image.load(f"Assets/graphics/{path}.png").convert()
		self.w,self.h = self.image.get_size()
	def update(self):
		super().update()
		if self.x < storage.cambounds[0]:
			storage.cambounds[0] = self.x
		if self.x+self.w > storage.cambounds[2]:
			storage.cambounds[2] = self.x+self.w
		if self.y < storage.cambounds[1]:
			storage.cambounds[1] = self.y
		if self.y+self.h > storage.cambounds[3]:
			storage.cambounds[3] = self.y+self.h
	def render(self):
		storage.window.blit(self.image, [int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h])

class camera3d(sharedlib.gameobject):
	def __init__(self,x,y,z):
		super().__init__()
		self.x = x
		self.y = y
		self.z = z
		self.target = self
		storage.camera = self

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
	

#if you saw the earlier comment in the menu.py file about a horrid clunky solution, you already know the deal with this one.
def loadbluprint(name):
	storage.objlist = []
	for item in storage.levels.get(name)+storage.persistobjs+storage.party:
		print(item)
		obj = globals()[item[0]](*item[1])

sharedlib.loadgame = loadbluprint