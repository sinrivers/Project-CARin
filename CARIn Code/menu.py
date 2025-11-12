"""
Filename: menu.py
Author(s): Taliesin Reese, Ricardo Ochoa
Version: 2.0
Date: 11/11/2025
Purpose: menu system for Project CARIn (simple image button version)
"""

import pygame
import storage
import sharedlib


class menubutton(sharedlib.gameobject):
	def __init__(self, x, y, w, h, funcname, arg, label=""):
		super().__init__()
		self.x, self.y, self.w, self.h = map(int, (x, y, w, h))
		self.funcname = funcname
		self.arg = arg
		self.label = label.lower()

		# --- Load image directly
		if "start" in self.label:
			self.image = pygame.image.load("assets/graphics/start_button.png").convert_alpha()
		elif "exit" in self.label:
			self.image = pygame.image.load("assets/graphics/exit_button.png").convert_alpha()
		else:
			self.image = None

		# Resize if needed
		if self.image:
			self.image = pygame.transform.smoothscale(self.image, (self.w, self.h))

		# Make rect for hit detection
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

	def update(self):
		mx, my = storage.mousepos
		if self.rect.collidepoint(mx, my):
			if 1 in storage.newclicks:
				self._trigger_action()

	def render(self):
		surface = storage.uicanvas
		if self.image:
			surface.blit(self.image, (self.x, self.y))
		else:
			# fallback if image not found
			pygame.draw.rect(surface, (255, 100, 100), self.rect)
			text = storage.writer.render(self.label, True, (255, 255, 255))
			surface.blit(text, (self.x + self.w // 2 - text.get_width() // 2,
								self.y + self.h // 2 - text.get_height() // 2))

	def _trigger_action(self):
		if self.funcname == "printwbutton":
			print(self.arg)
		elif self.funcname == "loadmenu":
			sharedlib.loadmenu(self.arg)
		elif self.funcname == "loadgame":
			sharedlib.menu_active = False
			sharedlib.loadgame(self.arg)
			sharedlib.start_cutscene("intro_vn")
		elif self.funcname == "quit":            # <-- add this
			import sys
			pygame.quit()
			sys.exit()
		else:
			print(f"[WARN] Unknown action {self.funcname!r}({self.arg!r})")


# ---------------------- BACKGROUND SUPPORT ----------------------
background_img = None
background_loaded = False

def draw_background():
	"""Draw background before any buttons."""
	global background_img, background_loaded

	# Load it once, after pygame.display is initialized
	if not background_loaded:
		try:
			background_img = pygame.image.load("assets/graphics/background.png").convert()
			background_img = pygame.transform.smoothscale(background_img, storage.screensize)
			background_loaded = True
		except Exception as e:
			print(f"[WARN] Couldn't load background: {e}")
			background_img = None
			background_loaded = True  # stop retrying

	if background_img:
		storage.uicanvas.blit(background_img, (0, 0))
	else:
		storage.uicanvas.fill((30, 30, 30))  # fallback gray




# --- Menu Loader (same as before) ---
def loadbluprint(name):
	storage.objlist = []
	sharedlib.menu_active = True
	layout = storage.menus.get(name, [])
	for item in layout:
		cls_name, ctor_args = item[0], item[1]
		cls = globals().get(cls_name)
		if cls is None:
			print(f"[WARN] class {cls_name!r} not found")
			continue
		obj = cls(*ctor_args)
		storage.objlist.append(obj)

sharedlib.loadmenu = loadbluprint