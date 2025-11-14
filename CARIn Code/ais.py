"""
Filename: ais.py
Author: Taliesin Reese
Version: 2.0
Date: 11/14/2025
Purpose: NPC combat behaviors for Project CARIn
"""
import storage
import sharedlib
import random
import copy

def MissingnoCombat(agent):
	agent.combatactions = copy.deepcopy(storage.combatactions[random.choice(["staffattack"])])
def MissingnoInteract(agent):
	sharedlib.cutscenestart("test2")
def MissingnoIdle(agent):
	pass