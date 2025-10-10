"""
Filename: gameutils.py
Author: Taliesin Reese
Version: 3.0
Date: 10/09/2025
Purpose: Gameplay tools for Project CARIn
"""
#setup
import sharedlib
import storage
import pygame
import math

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
		print("This is a test of the Emergency Brodcast Cube")
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
	def __init__(self,x,y,z,w,h,d,state,name=None):
		super().__init__(x,y,z,w,h,d)
		#the type of character we're dealing with is determined by self.state.
		#Note that self.state was originally supposed to lock or unlock certain actions (i.e. the second hit of a two-hit combo),
		#so this may need it's own variable if such a use ever arrives.
		#States are as follows: 0-NPC Scripted Behaviors. 1-Cutscene Actor. 2-NPC follower. 3-Active Player Character.
		self.state = state
		if self.state > 1:
			storage.party.append(self)
		if self.state == 3:
			storage.camera.target = self
		self.speed = [0,0,0]
		self.framecounter = 0
		self.framenumber = 0
		self.grounded = True
		self.walkspeed = 10
		self.jumpspeed = 200
		self.traction = 1
		self.gravity = 1
		self.interactd = 50
		self.interactpoint = [self.x+self.w+self.interactd,self.y+self.w/2,self.z-self.d/2]
		self.name = name
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
	def animupdate(self):
		self.animname = "walk"
		print("AHHHHHH")
		self.framecounter += 1
		if storage.animinfo[self.name]["anims"][self.animname][self.framenumber][1] < self.framecounter:
			self.framecounter = 0
			self.framenumber += 1
			if self.framenumber >= len(storage.animinfo[self.name]["anims"][self.animname]):
				self.framenumber = 0
	def render(self):
		if self.name == None:
			if self.state == 3:
				pygame.draw.rect(storage.spritecanvas, (0,0,100), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
				pygame.draw.rect(storage.spritecanvas, (0,0,155), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
				pygame.draw.rect(storage.spritecanvas, (0,0,255), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
			else:
				pygame.draw.rect(storage.spritecanvas, (0,100,100), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
				pygame.draw.rect(storage.spritecanvas, (0,155,155), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d))
				pygame.draw.rect(storage.spritecanvas, (0,255,255), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h))
		else:
			self.animupdate()
			pygame.draw.rect(storage.spritecanvas, (0,0,100), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
			
			holder=storage.animinfo[self.name]["frames"][storage.animinfo[self.name]["anims"][self.animname][self.framenumber][0]]
			storage.spritecanvas.blit(storage.spritesheet, [int(self.x+self.w/2-holder[2]/2-storage.camfocus[0]),
								int(self.y+self.h/2-holder[3]+self.z+self.d/2-storage.camfocus[1])],holder)

	def checkcollide(self):
		self.grounded = False
		for obj in storage.objlist:
			if isinstance(obj,object3d):
				obj.collidecheck(self)
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
				dist = (charac.x-self.x)**2+(charac.y-self.y)**2+(charac.z-self.z)**2
				if dist > 5125:
					if self.x < charac.x:
						self.speed[0] = self.walkspeed
					elif self.x > charac.x:
						self.speed[0] = -self.walkspeed
					if self.y < charac.y:
						self.speed[1] = self.walkspeed
					elif self.y > charac.y:
						self.speed[1] = -self.walkspeed
					if self.z > charac.z and self.grounded == True:
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

class collider(object3d):
	def __init__(self,x,y,z,w,h,d,angle = 0,ascend = 0):
		super().__init__(x,y,z,w,h,d)
		self.angle = angle/360*2*math.pi
		self.ascend = ascend
				
	def collidepoint(self,basepoint):
		#for both angle and perpendicular of angle:
		#print([basepoint[0]-self.x,basepoint[1]-self.y,basepoint[2]], [(basepoint[0]-self.x)*math.cos(0)-(basepoint[1]-self.y)*math.sin(0),(basepoint[0]-self.x)*math.sin(0)+(basepoint[1]-self.y)*math.cos(0),basepoint[2]])
		point = [(basepoint[0]-self.x)*math.cos(-self.angle)-(basepoint[1]-self.y)*math.sin(-self.angle),
			 (basepoint[0]-self.x)*math.sin(-self.angle)+(basepoint[1]-self.y)*math.cos(-self.angle),basepoint[2]]
		if 0 <= point[0] <= self.w:
			if 0 <= point[1] <= self.h:
				if self.z >= point[2] >= self.z-self.d:
					minx = min([-point[0],self.w-point[0]],key=abs)
					miny = min([-point[1],self.h-point[1]],key=abs)
					if abs(miny) < abs(minx):
						return [(0)*math.cos(self.angle)-(miny)*math.sin(self.angle),
							(0)*math.sin(self.angle)+(miny)*math.cos(self.angle)]
					else:
						return [(minx)*math.cos(self.angle)-(0)*math.sin(self.angle),
							(minx)*math.sin(self.angle)+(0)*math.cos(self.angle)]
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
		if self.angle == 0:
			if storage.debug:
				pygame.draw.rect(storage.spritecanvas, (255,255,0), (int(self.x-storage.camfocus[0]),int(self.y-storage.camfocus[1]),self.w,self.h),2)
				pygame.draw.rect(storage.spritecanvas, (255,255,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h+self.d),2)
				pygame.draw.rect(storage.spritecanvas, (255,255,0), (int(self.x-storage.camfocus[0]),int(self.y+self.z-self.d-storage.camfocus[1]),self.w,self.h),2)
		else:
			if storage.debug:
				pygame.draw.polygon(storage.spritecanvas, (255,255,0), ([int(self.x-storage.camfocus[0]),
											int(self.y-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),2)
				if self.angle <= 90:
					pygame.draw.polygon(storage.spritecanvas, (255,255,0), ([int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),2)
				pygame.draw.polygon(storage.spritecanvas, (255,255,0), ([int(self.x-storage.camfocus[0]),
											int(self.y+self.z-self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))]),2)

class plat(collider):
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
		if self.collidepoint(hitter.bottom) != False:
			hitter.z -= hitter.z - (self.z-self.d)
			hitter.speed[2] = 0
			hitter.grounded = True
	def render(self):
		if self.angle == 0:
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
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]),
											int(self.y+self.z-self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.h*math.cos(self.angle)))]))
				pygame.draw.polygon(storage.spritecanvas, (0,255,0), ([int(self.x-storage.camfocus[0]),
											int(self.y+self.z-self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))]))
			else:
				pygame.draw.rect(storage.spritecanvas, (255,0,255), ([int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]),
											int(self.y+self.z-self.d-storage.camfocus[1])],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+self.z-self.d-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)))],
											[int(self.x-storage.camfocus[0]+(self.w*math.cos(self.angle)-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.w*math.sin(self.angle)+self.h*math.cos(self.angle)))],
											[int(self.x-storage.camfocus[0]+(-self.h*math.sin(self.angle))),
											int(self.y+(self.z)-storage.camfocus[1]+(self.h*math.cos(self.angle)))]))


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
	for item in storage.levels.get(name)+storage.persistobjs+storage.partyspawn:
		print(item)
		obj = globals()[item[0]](*item[1])

sharedlib.loadgame = loadbluprint