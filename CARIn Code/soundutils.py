"""
Filename: soundutils.py
Author(s): Taliesin Reese
Version: 2.1
Date: 11/18/2025
Purpose: Play sound for project CARIn
"""
import pygame
import sharedlib
import storage

def startup():
	storage.mChannel = pygame.mixer.Channel(0)
	storage.sChannel = pygame.mixer.Channel(1)

	storage.soundbacklog = []
	storage.soundbacklognames = []
	storage.songplaying = None
	storage.songpriority = False

	# --- GLOBAL VOLUME SUPPORT ---
	if not hasattr(storage, "volume"):
		storage.volume = 0.5
	apply_volume()

def apply_volume():
	"""Apply global volume (storage.volume) to music and sound effect channels."""
	vol = getattr(storage, "volume", 0.5)

	try:
		storage.mChannel.set_volume(vol)  # music channel
	except Exception:
		pass

	try:
		storage.sChannel.set_volume(vol)  # sfx channel
	except Exception:
		pass


def gettrack(name = "Christmas.wav"):
	if name in storage.soundbacklognames:
		i = storage.soundbacklognames.index(name)
		return storage.soundbacklog[i]
	else:
		if len(storage.soundbacklog) > 10:
			storage.soundbacklog = storage.soundbacklog[:-1]
			storage.soundbacklognames = storage.soundbacklognames[:-1]
		storage.soundbacklog.insert(0,pygame.mixer.Sound(f"assets/sound/{name}"))
		storage.soundbacklognames.insert(0,name)
		return(storage.soundbacklog[0])

def playsong(name = "Christmas.wav", fade = True):
	if name != storage.songplaying:
		print(name, storage.songplaying)
		song = gettrack(name)

		# ensure the channel volume matches global volume
		apply_volume()

		if fade:
			storage.mChannel.play(song, -1, fade_ms = 500)
		else:
			storage.mChannel.play(song, -1, fade_ms = 0)
		storage.songplaying = name

def playsound(name = "come on.wav"):
	song = gettrack(name)
	# ensure SFX volume matches global volume
	apply_volume()
	storage.sChannel.play(song)

def stopsong(force = False):
	if force:
		storage.mChannel.stop()
	else:
		storage.mChannel.fadeout(500)
	storage.songplaying = None
		