import copy, random

class Player:
	def __init__(self, number, isHuman=False):
		self.number = number
		self.hand = [0 for i in range(13)]

	def dealHand(self,arr):
		for i in arr:
			self.hand[i] += 1