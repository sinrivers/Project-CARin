"""
Filename: sharedlib.py
Author(s): Taliesin Reese
Version: 2.0
Date: 10/09/2025
Purpose: primary support file for Project CARIn
"""
#imports
import pygame
import storage
import copy

#classes
class gameobject:
	def __init__(self):
		self.state = 0
		self.vertsort = [0]
		storage.objlist.append(self)
		self.rendered = False
	def update(self):
		pass
	def render(self):
		pygame.draw.rect(storage.window, (255,255,255), (0,0,50,50))
	def delete(self):
		storage.objlist.remove(self)
	def novertcollide(self,hitter):
		pass
