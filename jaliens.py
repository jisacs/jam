#!/usr/bin/env python
from __future__ import print_function
import random, os.path


#import basic pygame modules
import pygame
from pygame.locals import *

#see if we can load more than standard BMP
if not pygame.image.get_extended():
	raise SystemExit("Sorry, extended image module required")


#game constants
MAX_SHOTS      = 2      #most player bullets onscreen
ALIEN_ODDS     = 22     #chances a new alien appears
BOMB_ODDS      = 60    #chances a new bomb will drop
ALIEN_RELOAD   = 12     #frames between new aliens
SCREENRECT     = Rect(0, 0, 640*2, 480*2)

IMAGE_UP = 0
IMAGE_DOWN = 1
IMAGE_RIGHT = 2
IMAGE_LEFT = 3



main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
	"loads an image, prepares it for play"
	file = os.path.join(main_dir, 'data', file)
	try:
		surface = pygame.image.load(file)
	except pygame.error:
		raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
	return surface.convert()

def load_images(*files):
	imgs = []
	for file in files:
		imgs.append(load_image(file))
	return imgs



# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard



class Road(pygame.sprite.Sprite):
	"""
	"""
	VERTICAL = 0
	HORIZONTAL = 1
	speed = 10
	bounce = 24
	SIZE = (200,200)
	images = []
	
	def __init__(self,pos,direction=VERTICAL):
		"""
		Parameters
		----------
		pos: tuple(x,y)
		"""
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[direction]
		
		val = (pos[0]*self.SIZE[0],pos[1]*self.SIZE[1])
		print('val: ', val)
		self.rect = self.image.get_rect(topleft=(val))
		
		print('self.rect ', self.rect )
		self.reloading = 0
		self.origtop = self.rect.top
		print('SCREENRECT.midbottom',SCREENRECT.midbottom)


class Player(pygame.sprite.Sprite):
	speed = 10
	bounce = 24
	images = []
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
		self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
		print('self.rect ', self.rect )
		self.reloading = 0
		self.origtop = self.rect.top
		print('SCREENRECT.midbottom',SCREENRECT.midbottom)


	def move(self, keystate):
		"""
		UP DOWN LEFT RIGHT
		272 273 274   275
		"""
		
		#direction = keystate[K_RIGHT] - keystate[K_LEFT]
		
		#if direction: self.facing = direction
		xdir= keystate[K_RIGHT] - keystate[K_LEFT]
		ydir = keystate[K_DOWN] - keystate[K_UP]
		self.rect.move_ip(xdir*self.speed, ydir*self.speed)
		
		
		self.rect = self.rect.clamp(SCREENRECT)
		
		if xdir < 0:
			self.image = self.images[IMAGE_LEFT]
		elif xdir > 0:
			self.image = self.images[IMAGE_RIGHT]
		elif ydir < 0:
			self.image = self.images[IMAGE_UP]
		elif ydir > 0:
			self.image = self.images[IMAGE_DOWN]
		#self.rect.top = self.origtop - (self.rect.left//self.bounce%2)


def main(winstyle = 0):
	# Initialize pygame
	pygame.init()

	# Set the display mode
	winstyle = 0  # |FULLSCREEN
	bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
	screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

	#Load images, assign to sprite classes
	#(do this before the classes are used, after screen setup)
	up = load_image('carup.jpg')
	down = load_image('cardown.jpg')
	right = load_image('carright.jpg')
	left = load_image('carleft.jpg')
	Player.images = [up,down,right,left]

	hor = load_image('road_hor.jpg')
	ver = load_image('road_ver.jpg')
	Road.images = [ver,hor]
	
	#decorate the game window
	pygame.display.set_caption('Pygame Aliens')
	pygame.mouse.set_visible(0)
	"""
	#create the background, tile the bgd image
	"""
	bgdtile = load_image('white_map.jpg')
	background = pygame.Surface(SCREENRECT.size)
	for x in range(0, SCREENRECT.width, bgdtile.get_width()):
		for y in range(0, SCREENRECT.width, bgdtile.get_height()):
			background.blit(bgdtile, (x, y))
	screen.blit(background, (0,0))
	pygame.display.flip()
	
	
	roads = pygame.sprite.Group()
	all = pygame.sprite.RenderUpdates()

	#assign default groups to each sprite class
	Player.containers = all
	Road.containers = roads,all

	#Create Some Starting Values
	clock = pygame.time.Clock()

	#initialize our starting sprites
	
	Road((0,0),Road.VERTICAL) #note, this 'lives' because it goes into a sprite group7
	Road((0,1),Road.VERTICAL) #note, this 'lives' because it goes into a sprite group7
	Road((1,1),Road.HORIZONTAL) #note, this 'lives' because it goes into a sprite group
	player = Player()

	while player.alive():

		#get input
		for event in pygame.event.get():
			if event.type == QUIT or \
				(event.type == KEYDOWN and event.key == K_ESCAPE) :
					return
		keystate = pygame.key.get_pressed()

		# clear/erase the last drawn sprites
		all.clear(screen, background)

		#update all the sprites
		all.update()
		#handle player input
		"""
		UP DOWN LEFT RIGHT
		272 273 274   275
		"""
		player.move(keystate)

		#draw the scene
		dirty = all.draw(screen)
		pygame.display.update(dirty)

		#cap the framerate
		clock.tick(40)

	pygame.time.wait(1000)
	pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()

