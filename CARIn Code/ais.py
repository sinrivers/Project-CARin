"""
Filename: ais.py
Author: Taliesin Reese
Version: 1.0
Date: 11/4/2025
Purpose: NPC combat behaviors for Project CARIn
"""
import storage
import random
import copy

def Missingno(agent):
	agent.combatactions = copy.deepcopy(storage.combatactions[random.choice(["staffattack"])])