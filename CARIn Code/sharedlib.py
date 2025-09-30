"""
Filename: sharedlib.py
Author(s): Taliesin Reese
Version: 1.0
Date: 9/20/2025
Purpose: primary support file for Project CARIn
"""
#imports
import pygame
import storage

#classes
class gameobject:
	def __init__(self):
		self.state = 0
		storage.objlist.append(self)
	def update(self):
		pass
	def render(self):
		pygame.draw.rect(storage.window, (255,255,255), (0,0,50,50))
	def delete(self):
		storage.objlist.remove(self)