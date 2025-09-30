"""
Filename: menu.py
Author(s): Taliesin Reese
Version: 1.0
Date: 9/22/2025
Purpose: menu system for Project CARIn
"""
#setup
import sharedlib
import storage
import pygame

#class
class menubutton(sharedlib.gameobject):
	def __init__(self, x, y, w, h, funcname, args):
		super().__init__()
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.func = getattr(self,funcname)
		self.args = args
		
	def update(self):
		#reset to default state
		self.state = 0
		if storage.mousepos[0] > self.x and storage.mousepos[0] < self.x + self.w:
			if storage.mousepos[1] > self.y and storage.mousepos[1] < self.y + self.h:
				if 1 in storage.newclicks:
					#click
					self.state = 2
				elif 1 in storage.clicks:
					#hold click
					self.state = 3
				else:
					#hover
					self.state = 1
		if self.state == 2:
			self.func(*self.args)
					
	def render(self):
		match self.state:
			#default
			case 0:
				pygame.draw.rect(storage.window, (0,255,0), (self.x,self.y,self.w,self.h))
			#hover
			case 1:
				pygame.draw.rect(storage.window, (100,255,100), (self.x,self.y,self.w,self.h))
			#click
			case 2:
				pygame.draw.rect(storage.window, (0,100,0), (self.x,self.y,self.w,self.h))
			#hold click
			case 3:
				pygame.draw.rect(storage.window, (50,205,50), (self.x,self.y,self.w,self.h))
		storage.window.blit(
					storage.writer.render(str(self.args),False,(255,255,255)),
					(
						(self.x+self.w/2)-(storage.writer.size(str(self.args))[0]/2),
						(self.y+self.h/2)))

	def printwbutton(self,text):
		print(text)
	
	def loadmenu(self,name):
		sharedlib.loadmenu(name)
	def loadgame(self,name):
		sharedlib.loadgame(name)

#This is a horrid, clunky way to make sure the menu loading interface is accessible from the game interface. Please figure out something better.
def loadbluprint(name):
	storage.objlist = []
	for item in storage.menus.get(name):
		print(item)
		obj = globals()[item[0]](*item[1])

sharedlib.loadmenu = loadbluprint
	

