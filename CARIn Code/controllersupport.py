#This isn't a real file for the game, this is for testing controllers.
import pygame

pygame.init()
controller = None
selectmapping = 0
#these map to bottom button, left button, select, and start on 1) a standard xbox pad, and 2) a terrible snes-like usb I have. Maybe we should have a way to set this up dynamically?
controllermappings = [[0,2,6,7],[2,3,]]

def getcontroller():
	global controller
	print(pygame.joystick.get_count())
	if pygame.joystick.get_count() > 0:
		controller = pygame.joystick.Joystick(0)
		controller.init()
		print(controller.get_guid())
	else:
		controller = None
def getcontrolin():
	global controller
	for button in range(controller.get_numbuttons()):
		print(controller.get_button(button),end = ",")
	print()

getcontroller()
while True:
	pygame.event.get()
	getcontrolin()