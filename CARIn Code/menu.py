"""
Filename: menu.py
Author(s): Taliesin Reese, Ricardo Ochoa
Version: 2.2 (patched with options and safer loader)
Date: 11/14/2025
Purpose: menu system for Project CARIn (simple image button version)
"""

import sys
import pygame
import storage
import sharedlib
import soundutils
import options_menu


class menusongplayer(sharedlib.gameobject):
	def __init__(self, song):
		super().__init__()
		self.song = song

	def update(self):
		# play the menu song if not already playing
		try:
			soundutils.playsong(self.song)
		except Exception as e:
			print(f"[WARN] couldn't play menu song {self.song!r}: {e}")


class menubutton(sharedlib.gameobject):
	def __init__(self, x, y, w, h, funcname, arg, label=""):
		super().__init__()
		self.x, self.y, self.w, self.h = map(int, (x, y, w, h))
		self.funcname = funcname
		self.arg = arg

		# keep original label text for drawing
		self.label = label
		label_lower = label.lower()

		# default: no image yet
		self.image = None

		# --- Load image based on label text (names stay the same) ---
		img_path = None
		if "click to begin" in label_lower:
			img_path = "assets/graphics/Click_to_Begin_Button.png"
		elif "start" in label_lower:
			img_path = "assets/graphics/start_button.png"
		elif "options" in label_lower:
			img_path = "assets/graphics/options_button.png"
		elif "quit" in label_lower:
			img_path = "assets/graphics/exit_button.png"

		if img_path is not None:
			try:
				img = pygame.image.load(img_path).convert_alpha()
				self.image = pygame.transform.smoothscale(img, (self.w, self.h))
			except FileNotFoundError:
				print(f"[WARN] button image {img_path!r} not found; using text fallback")
				self.image = None
			except Exception as e:
				print(f"[WARN] error loading {img_path!r}: {e}")
				self.image = None

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
			# be safe in case writer isn't set
			try:
				text = storage.writer.render(self.label, True, (255, 255, 255))
				surface.blit(
					text,
					(
						self.x + self.w // 2 - text.get_width() // 2,
						self.y + self.h // 2 - text.get_height() // 2,
					),
				)
			except Exception:
				pass

	def _trigger_action(self):
		if self.funcname == "printwbutton":
			print(self.arg)

		elif self.funcname == "loadmenu":
			sharedlib.loadmenu(self.arg)

		elif self.funcname == "loadgame":
			sharedlib.menu_active = False
			sharedlib.loadgame(self.arg)

		elif self.funcname == "loadvn":
			sharedlib.menu_active = False
			sharedlib.start_cutscene(self.arg)

		elif self.funcname == "quit":
			pygame.quit()
			sys.exit()

		# --- open the external options menu screen ---
		elif self.funcname == "openoptions":


			screen = pygame.display.get_surface()

			# start options menu using current global volume
			initial_vol = getattr(storage, "volume", 0.5)
			options = options_menu.OptionsMenu(screen, initial_volume=initial_vol)

			sharedlib.menu_active = False
			new_volume = options.run()  # this already updates storage.volume + channels

			# (optional) re-apply, just to be safe
			soundutils.apply_volume()

			sharedlib.menu_active = True
			sharedlib.loadmenu("MainMenu")
			return


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
			background_img = pygame.image.load(
				"assets/graphics/background.png"
			).convert()
			background_img = pygame.transform.smoothscale(
				background_img, storage.screensize
			)
			background_loaded = True
		except Exception as e:
			print(f"[WARN] Couldn't load background: {e}")
			background_img = None
			background_loaded = True  # stop retrying

	if background_img:
		storage.uicanvas.blit(background_img, (0, 0))
	else:
		storage.uicanvas.fill((30, 30, 30))  # fallback gray


# --- Menu Loader (safer) ---
def loadbluprint(name):
	storage.objlist = []
	sharedlib.menu_active = True
	layout = storage.menus.get(name, [])
	if not layout:
		print(f"[WARN] menu layout {name!r} not found in storage.menus")
		return

	for item in layout:
		# item must look like ["ClassName", [args...]]
		if not isinstance(item, (list, tuple)) or len(item) < 2:
			print(f"[WARN] malformed menu entry in {name!r}: {item!r}")
			continue

		cls_name, ctor_args = item[0], item[1]
		cls = globals().get(cls_name)
		if cls is None:
			print(f"[WARN] class {cls_name!r} not found")
			continue
		try:
			obj = cls(*ctor_args)
			storage.objlist.append(obj)
		except Exception as e:
			print(f"[WARN] error constructing {cls_name!r} with {ctor_args!r}: {e}")


sharedlib.loadmenu = loadbluprint
