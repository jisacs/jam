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
SCREENRECT     = Rect(0, 0,800, 600)

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

class Road():
	VERTICAL = 0
	HORIZONTAL = 1
	BR = 2
	BL = 3
	TL = 4
	TR = 5
	CROSS =6
	TBR=7
	TBL=8
	TLR=9
	BLR=10



#Block.images = [ver,hor,br,bl,tl,tr,cross,tbr,tbl,tlr,blr,start,un]
class Block(pygame.sprite.Sprite):
	"""
	"""

	UNKNOWN = 1
	ROAD=2
	START = 11

	bounce = 24
	SIZE = (25,25)
	images = []
	
	def __init__(self,pos,block_type=UNKNOWN):
		"""
		Parameters
		----------
		pos: tuple(x,y)
		"""
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.block_type = block_type
		self.pos = pos
		self.image = self.images[self.block_type]
		val = (pos[0]*self.SIZE[0]+self.SIZE[0]/2,pos[1]*self.SIZE[1]+self.SIZE[0]/2)
		self.rect = self.image.get_rect(center=(val))
		self.reloading = 0
		self.origtop = self.rect.top
	

		
	@staticmethod
	def get_type(color):
		level = 2
		if color[0] < level and  color[1] < level and  color[2] < level:
			return Block.ROAD
		elif color[0] > 180  and color[1] < 50 and  color[2] < 50:
			return Block.START
		elif color[0] > 250 and color[1] > 250 and color[2] > 250: # WHITE
			return None
		else:
			return Block.UNKNOWN
		


class Player(pygame.sprite.Sprite):
	size = 10
	bounce = 24
	images = []
	def __init__(self,pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
		#pos = (SCREENRECT.midbottom[X],SCREENRECT.midbottom[Y]-50)
		
		#pos.y = pos.y + self.image.eight
		#print('pos', pos)
		val = (pos[X]*Block.SIZE[X],pos[Y]*Block.SIZE[Y])
		self.rect = self.image.get_rect(center=val)
		self.reloading = 0
		self.origtop = self.rect.top



	def move(self, keystate,blocks):
		"""
		UP DOWN LEFT RIGHT
		272 273 274   275
		"""
		
		#direction = keystate[K_RIGHT] - keystate[K_LEFT]
		
		#if direction: self.facing = direction
		xdir= keystate[K_RIGHT] - keystate[K_LEFT]
		ydir = keystate[K_DOWN] - keystate[K_UP]
		self.rect.move_ip(xdir*self.size, ydir*self.size)
		# See if the Sprite block has collided with anything in the Group block_list
		# The True flag will remove the sprite in block_list
		blocks_hit_list = pygame.sprite.spritecollide(self, blocks, False)
		if len(blocks_hit_list) == 0:
			self.rect.move_ip(-xdir*self.size, -ydir*self.size)
			return 
			
		self.rect = self.rect.clamp(SCREENRECT)
		
		if xdir < 0:
			self.image = self.images[IMAGE_LEFT]
		elif xdir > 0:
			self.image = self.images[IMAGE_RIGHT]
		elif ydir < 0:
			self.image = self.images[IMAGE_UP]
		elif ydir > 0:
			self.image = self.images[IMAGE_DOWN]


def main(winstyle = 0):
	# Initialize pygame
	pygame.init()
	
	print('DEBUG 2', SCREENRECT.size)

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
	cross = load_image('road_cross.jpg')
	tbr = load_image('road_top_bottom_right.jpg')
	tbl = load_image('road_top_bottom_left.jpg')
	tlr = load_image('road_top_left_right.jpg')
	blr = load_image('road_bottom_left_right.jpg')	
	start = load_image('road_start.jpg')
	un = load_image('unknow.tif')
	Block.images = [ver,hor,br,bl,tl,tr,cross,tbr,tbl,tlr,blr,start,un]
	
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
	
	
	#roads = pygame.sprite.Group()
	#all = pygame.sprite.RenderUpdates()
	blocks = pygame.sprite.Group()
	all = pygame.sprite.LayeredUpdates() # more sophisticated, can draw sprites in layers 

	#assign default groups to each sprite class
	Player.containers = all
	#Block.containers = roads,all
	Block.containers=blocks,all
	
	

	#Create Some Starting Values
	clock = pygame.time.Clock()

	
	pixels = getPixelArray(os.path.join (main_dir, 'data', 'easy.tif'))
	#roads =  pygame.PixelArray (surface)
	#print('road:',type(road))
	#Block(roads[0,0],Block.START) #note, this 'lives' because it goes into a sprite group7
	
	x_len,y_len,z_len = pixels.shape
	print(x_len,y_len)
	
	starts=[]
	for x in range(x_len):
		for y in range(y_len):
			color = pixels[x,y]
			block_type = Block.get_type(color)
			pos = (x,y) 
			if block_type == Block.ROAD:
				types={'UP':False,'DOWN':False ,'RIGHT':False ,'LEFT':False,'TR':False,'TL':False,'DR':False,'DL':False}
				for x_neig in  range(x_len):
					for y_neig in  range(y_len):
						neig_color = pixels[x_neig,y_neig]
						if Block.get_type(neig_color) == Block.ROAD:
							if x_neig == x - 1:
								if y_neig == y - 1 : types['TL'] = True
								if y_neig == y + 1 : types['DL'] = True
								if y_neig == y : types['LEFT'] = True
							elif x_neig == x + 1:
								if y_neig == y - 1 : types['TR'] = True
								if y_neig == y + 1 : types['DR'] = True
								if y_neig == y : types['RIGHT'] =True
							elif x_neig == x :
								if y_neig == y - 1 : types['UP'] = True
								if y_neig == y + 1 : types['DOWN'] = True
				if (types['RIGHT'] and types['UP'] and types['DOWN'] and types['LEFT']):
					Block(pos,Road.CROSS)
				#TBR=7 TBL=8 TLR=9 BLR=10
				elif (types['RIGHT'] and types['UP'] and types['DOWN']):
					Block(pos,Road.TBR)
				elif (types['RIGHT'] and types['UP'] and types['LEFT']):
					Block(pos,Road.TLR)
				elif (types['LEFT'] and types['UP'] and types['DOWN']):
					Block(pos,Road.TBL)
				elif (types['RIGHT'] and types['LEFT'] and types['DOWN']):
					Block(pos,Road.BLR)
					
				elif (types['LEFT'] or types['RIGHT']) and  ( not types['UP'] and  not types['DOWN']):
					Block(pos,Road.HORIZONTAL)
					
				elif (types['UP'] or types['DOWN']) and  ( not types['LEFT'] and  not types['RIGHT']):
					Block(pos,Road.VERTICAL)
					
				elif (types['LEFT'] and  types['DOWN']):
					Block(pos,Road.BL)
				elif (types['RIGHT'] and  types['DOWN']):
					Block(pos,Road.BR)
				elif (types['LEFT'] and  types['UP']):
					Block(pos,Road.TL)
				elif (types['RIGHT'] and  types['UP']):
					Block(pos,Road.TR)
				
			if  block_type == Block.START:
				
				starts.append(Block(pos,Block.START))
					
			elif  block_type == Block.UNKNOWN:
				Block(pos,Block.UNKNOW)
				
	#initialize our starting sprites
	pos = starts[0].pos
	player = Player(pos)
	
	
	#allgroup.change_layer(player,0)
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
		player.move(keystate,blocks)

		#draw the scene
		dirty = all.draw(screen)
		pygame.display.update(dirty)

		#cap the framerate
		clock.tick(40)

	pygame.time.wait(1000)
	pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()

