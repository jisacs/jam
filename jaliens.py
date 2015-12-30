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
SCREENRECT     = Rect(0, 0,1000, 1000)

IMAGE_UP = 0
IMAGE_DOWN = 1
IMAGE_RIGHT = 2
IMAGE_LEFT = 3
X = 0
Y  = 1



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

def getPixelArray(filename):
	try:
		image = pygame.image.load(filename)
	except pygame.error, message:
		print ("Cannot load image:", filename)
		raise SystemExit, message
	
	return pygame.surfarray.array3d(image)


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
	START = 2
	BR = 3
	BL = 4
	TL = 5
	TR = 6

	bounce = 24
	SIZE = (10,10)
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
		self.rect = self.image.get_rect(topleft=(val))
		
	
		self.reloading = 0
		self.origtop = self.rect.top



class Player(pygame.sprite.Sprite):
	speed = 10
	bounce = 24
	images = []
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
		self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
		self.reloading = 0
		self.origtop = self.rect.top



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
	br = load_image('road_bottom_right.jpg')
	bl = load_image('road_bottom_left.jpg')
	tl = load_image('road_top_left.jpg')
	tr = load_image('road_top_right.jpg')
	start = load_image('one.jpg')
	Road.images = [ver,hor,start,br,bl,tl,tr]
	
	#decorate the game window
	pygame.display.set_caption('Pygame Aliens')
	#pygame.mouse.set_visible(0)
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
	allgroup = pygame.sprite.LayeredUpdates() # more sophisticated, can draw sprites in layers 

	#assign default groups to each sprite class
	Player.containers = all
	Road.containers = roads,all
	
	

	#Create Some Starting Values
	clock = pygame.time.Clock()

	
	"""
	roads=((0,0),(1,0),(2,0) ,(3,0), \
							 (3,1) , \
							 (3,2) , \
				(1,3) ,(2,3), (3,3) , \
				(1,4), \
				(1,5)
						 )
	"""
	
	pixels = getPixelArray(os.path.join (main_dir, 'data', 'real_map.jpg'))
	#roads =  pygame.PixelArray (surface)
	#print('road:',type(road))
	#Road(roads[0,0],Road.START) #note, this 'lives' because it goes into a sprite group7
	
	print('shape:', pixels.shape)
	x_len,y_len,z_len = pixels.shape
	print('shape:', pixels.shape)
	print(x_len,y_len)
	"""
	for i in range(1000):
		pos = (i,i)
		print('pos', pos)
		Road(pos,Road.START)
	"""
	
	for x in range(x_len):
		for y in range(y_len):
			color = pixels[x,y]
			print('x,y,color:',x,y,color[0])
			level = 200
			if color[0] < level or  color[1] < level or  color[2] < level:
				for i in range(10):
					pos = (x,y) 
					print('pos:',pos,color[0])
					Road(pos,Road.START)
	"""
		is_a_corner = False
		try:
			if road[X-1,Y] < road[X] and last[Y] > road[Y]:
				print('DEBUG TL')
				Road(road,Road.TL)
				is_a_corner = True
			elif next_r[X] > road[X] and last[Y] > road[Y]:
				Road(road,Road.TR)
				print('DEBUG TR')
				is_a_corner = True
			elif last[X] < road[X] and last[Y] > road[Y]:
				Road(road,Road.BL)
				print('DEBUG BL')
				is_a_corner = True
			elif next_r[X] < road[X] and last[Y] < road[Y]:
				Road(road,Road.BR)
				print('DEBUG BR')
				is_a_corner = True
		except:
			pass
		if not is_a_corner :
			if last[X] != road[X]:
				Road(road,Road.HORIZONTAL)
				print('DEBUG HOR')
			else:
				Road(road,Road.VERTICAL)
				print('DEBUG VER')
	"""
	#initialize our starting sprites
	#player = Player()
	

	
	#allgroup.change_layer(player,0)
	while True:#player.alive():

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
		#player.move(keystate)

		#draw the scene
		dirty = all.draw(screen)
		pygame.display.update(dirty)

		#cap the framerate
		clock.tick(40)

	pygame.time.wait(1000)
	pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()

