"""
Filename: testgame.py
Author: Taliesin Reese
Version: 1.2
Date: 9/22/2025
Purpose: Demonstration of how a game may be loaded in Project CARIn's menu system. Also demonstrates usage of some other stuff.
"""
#setup
import sharedlib
import storage
import pygame

#classes
class player(sharedlib.gameobject):
	def __init__(self):
		super().__init__()
		self.x = 200
		self.y = 150
		self.w = 50
		self.h = 50
		self.speedx = 0
		self.speedy = 0
		self.grounded = False
	def update(self):
		self.grounded = False
		for thing in storage.objlist:
			if type(thing) == terrain:
				if self.y + self.h >= thing.y:
					self.y = thing.y-self.h
					self.grounded = True
		if self.grounded == False:
			self.speedy += 1
		else:
			self.speedy = 0
		if self.speedx > 0:
			self.speedx = self.speedx - 1
		elif self.speedx < 0:
			self.speedx = self.speedx + 1
		else:
			self.speedx = 0

		if self.grounded == True and pygame.K_SPACE in storage.newkeys:
			self.speedy = -200
		if storage.keys[pygame.K_a]:
			self.speedx = -10
		if storage.keys[pygame.K_d]:
			self.speedx = 10

		self.x += self.speedx * 0.01
		self.y += self.speedy * 0.01
	def render(self):
		pygame.draw.rect(storage.window, (0,0,255), (self.x,self.y,self.w,self.h))	

class terrain(sharedlib.gameobject):
	def __init__(self):
		super().__init__()
		self.y = 400
	def render(self):
		pygame.draw.rect(storage.window,  (255,255,255), [0,self.y,720,10])

#if you saw the earlier comment in the menu.py file about a horrid clunky solution, you already know the deal with this one.
def loadbluprint(name):
	storage.objlist = []
	for item in storage.levels.get(name):
		print(item)
		obj = globals()[item[0]](*item[1])

sharedlib.loadgame = loadbluprint