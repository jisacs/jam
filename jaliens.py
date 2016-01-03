#!/usr/bin/env python
from __future__ import print_function
import random, os.path
#import basic pygame modules
import pygame
from pygame.locals import *

#see if we can load more than standard BMP
if not pygame.image.get_extended():
	raise SystemExit("Sorry, extended image module required")

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

class Map():
	def __init__(self):
		self.blocks=dict() # key (x,y) value = Blaock reference
		self.starts=dict()
		self.links=list()
		
	def init_roads(self):
		for block in self.blocks.values():
			if block.block_type==Road.START:
				self.starts[(block.pos[X],block.pos[Y])] = block
				
			if (block.pos[X],block.pos[Y]-1)  in self.blocks.keys():
				block.neighbours["UP"] = self.blocks[(block.pos[X],block.pos[Y]-1)]
			
			if (block.pos[X],block.pos[Y]+1)  in self.blocks.keys():
				block.neighbours["DOWN"] = self.blocks[(block.pos[X],block.pos[Y]+1)]
			
			if (block.pos[X]-1,block.pos[Y])  in self.blocks.keys():
				block.neighbours["LEFT"] = self.blocks[(block.pos[X]-1,block.pos[Y])]
			
			if (block.pos[X]+1,block.pos[Y])  in self.blocks.keys():
				block.neighbours["RIGHT"] = self.blocks[(block.pos[X]+1,block.pos[Y])]

			if (block.pos[X]-1,block.pos[Y]-1)  in self.blocks.keys():
				block.neighbours["TL"] = self.blocks[(block.pos[X]-1,block.pos[Y]-1)]
			
			if (block.pos[X]+1,block.pos[Y]-1)  in self.blocks.keys():
				block.neighbours["TR"] = self.blocks[(block.pos[X]+1,block.pos[Y]-1)]
			
			if (block.pos[X]-1,block.pos[Y]+1)  in self.blocks.keys():
				block.neighbours["DL"] = self.blocks[(block.pos[X]-1,block.pos[Y]+1)]
			
			if (block.pos[X]+1,block.pos[Y]+1)  in self.blocks.keys():
				block.neighbours["DR"] = self.blocks[(block.pos[X]+1,block.pos[Y]+1)]
		
		"""
		for start in self.starts.values():
			print("---------start:", start.pos)
			start_neighbours = start.get_blocks_neighbours()
			print("-----start_neighbours:", start_neighbours)
			for current in start_neighbours.values():
				print("---current:", current.pos)
				l2_neighbours = current.get_blocks_neighbours() 
				print("---l2_neighbours", l2_neighbours)
				while len(l2_neighbours) >= 2:
					link=list()
					if current not in link:
						link.append(current)
						print("-New list append current:", current.pos)
					for l2_neighbour in l2_neighbours.values():
						if l2_neighbour.block_type != Road.START and l2_neighbour not in link :
							break
					
						if l2_neighbour not in link:
							link.append(l2_neighbour)
							print("-link.append(l2_neighbour:",l2_neighbour.pos)
					print("link", link)
					l2_neighbours = l2_neighbour.get_blocks_neighbours()
					print("-l2_neighbours", l2_neighbours)
		"""		
				
		
		print("link:", self.links)
		for link in self.links:
			print("-- New Link ---")
			for block in link:
				print(block.pos)
				
		
		

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
	START=11



#Block.images = [ver,hor,br,bl,tl,tr,cross,tbr,tbl,tlr,blr,start,un]
class Block(pygame.sprite.Sprite):
	"""
	"""

	COLOR_UNKNOWN = 1
	COLOR_ROAD=2
	COLOR_START = 0

	bounce = 24
	SIZE = (25,25)
	images = []


	
	def __init__(self,pos,neighbours,block_color_type):
		"""
		Parameters
		----------
		pos: tuple(x,y)
		"""
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.neighbours=neighbours
		
		if block_color_type == Block.COLOR_START:
			self.block_type=Road.START
			
		elif block_color_type == Block.COLOR_ROAD:
			self.init_road_type(self.neighbours)
	
		else:
			return

		self.pos = pos
		self.image = self.images[self.block_type]
		val = (pos[0]*self.SIZE[0]+self.SIZE[0]/2,pos[1]*self.SIZE[1]+self.SIZE[0]/2)
		self.rect = self.image.get_rect(center=(val))
		self.reloading = 0
		self.origtop = self.rect.top

	
	def init_road_type(self,neighbours):
		if (self.neighbours['RIGHT'] and neighbours['UP'] and neighbours['DOWN'] and neighbours['LEFT']):
			self.block_type=Road.CROSS
		elif (neighbours['RIGHT'] and neighbours['UP'] and neighbours['DOWN']):
			self.block_type=Road.TBR
		elif (neighbours['RIGHT'] and neighbours['UP'] and neighbours['LEFT']):
			self.block_type=Road.TLR
		elif (neighbours['LEFT'] and neighbours['UP'] and neighbours['DOWN']):
			self.block_type=Road.TBL
		elif (neighbours['RIGHT'] and neighbours['LEFT'] and neighbours['DOWN']):
			self.block_type=Road.BLR
		elif (neighbours['LEFT'] or neighbours['RIGHT']) and  ( not neighbours['UP'] and  not neighbours['DOWN']):
			self.block_type=Road.HORIZONTAL
		elif (neighbours['UP'] or neighbours['DOWN']) and  ( not neighbours['LEFT'] and  not neighbours['RIGHT']):
			self.block_type=Road.VERTICAL
		elif (neighbours['LEFT'] and  neighbours['DOWN']):
			self.block_type=Road.BL
		elif (neighbours['RIGHT'] and  neighbours['DOWN']):
			self.block_type=Road.BR
		elif (neighbours['LEFT'] and  neighbours['UP']):
			self.block_type=Road.TL
		elif (neighbours['RIGHT'] and  neighbours['UP']):
			self.block_type=Road.TR
		else:
			self.block_type=Road.CROSS
	
	def get_blocks_neighbours(self):
		result = dict()
		for block in self.neighbours.values():
			if type(block) is Block:
				result[block.pos]=block
		return result
		
	@staticmethod
	def get_color_type(color):
		level = 2
		if color[0] < level and  color[1] < level and  color[2] < level:
			return Block.COLOR_ROAD
		elif color[0] > 180  and color[1] < 50 and  color[2] < 50:
			return Block.COLOR_START
		elif color[0] > 250 and color[1] > 250 and color[2] > 250: # WHITE
			return None
		else:
			return Block.COLOR_UNKNOWN
		


class Player(pygame.sprite.Sprite):
	size = 10
	bounce = 24
	images = []
	def __init__(self,pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
		#pos = (SCREENRECT.midbottom[X],SCREENRECT.midbottom[Y]-50)
		
		#pos.y = pos.y + self.image.eight
		val = (pos[X]*Block.SIZE[X]+Block.SIZE[X]/2,pos[Y]*Block.SIZE[Y]++Block.SIZE[Y]/2)
		self.rect = self.image.get_rect(center=val)
		self.reloading = 0
		self.origtop = self.rect.top
		self.direction=(0,0)
		self.offset=[0,0]
		self.pos=pos
	

	def move(self, keystate,blocks):
		xdir= keystate[K_RIGHT] - keystate[K_LEFT]
		ydir = keystate[K_DOWN] - keystate[K_UP]
		if xdir == 0 and ydir == 0:
			return
		self.rect.move_ip(xdir*Block.SIZE[X], ydir*Block.SIZE[Y])
		# See if the Sprite block has collided with anything in the Group block_list
		# The True flag will remove the sprite in block_list
		blocks_hit_list = pygame.sprite.spritecollide(self, blocks, False)
		if len(blocks_hit_list) == 0:
			self.rect.move_ip(-xdir*Block.SIZE[X], -ydir*Block.SIZE[Y])
			return 
		
		rect = self.rect.clamp(SCREENRECT)
		self.direction=(xdir,ydir)
		
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
	t_map = Map()


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
	
	starts=[]
	for x in range(x_len):
		for y in range(y_len):
			color = pixels[x,y]
			block_color_type = Block.get_color_type(color)
			pos = (x,y)
			blk=None
			if block_color_type == Block.COLOR_ROAD or block_color_type == Block.COLOR_START:
				neighbours={'UP':False,'DOWN':False ,'RIGHT':False ,'LEFT':False,'TR':False,'TL':False,'DR':False,'DL':False}
				if Block.get_color_type(pixels[x,y-1]) == Block.COLOR_ROAD:neighbours['UP']=True
				if Block.get_color_type(pixels[x,y+1]) == Block.COLOR_ROAD:neighbours['DOWN']=True
				if Block.get_color_type(pixels[x+1,y]) == Block.COLOR_ROAD:neighbours['RIGHT']=True
				if Block.get_color_type(pixels[x-1,y]) == Block.COLOR_ROAD:neighbours['LEFT']=True
				if Block.get_color_type(pixels[x+1,y+1]) == Block.COLOR_ROAD:neighbours['DR']=True
				if Block.get_color_type(pixels[x-1,y+1]) == Block.COLOR_ROAD:neighbours['DL']=True
				if Block.get_color_type(pixels[x+1,y-1]) == Block.COLOR_ROAD:neighbours['TR']=True
				if Block.get_color_type(pixels[x-1,y-1]) == Block.COLOR_ROAD:neighbours['TL']=True
				blk=Block(pos,neighbours,block_color_type)
				
			if  block_color_type == Block.COLOR_START:
				blk=Block(pos,neighbours,block_color_type)
				starts.append(blk)
				
			elif  block_color_type == Block.COLOR_UNKNOWN:
				blk=Block(pos,neighbours,block_color_type)
			if blk != None : t_map.blocks[(x,y)]=blk
				
	t_map.init_roads()
	#initialize our starting sprites
	pos=starts[0].pos
	player = Player(pos)
	
	piste=list()
	
	
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

		#update all the sprites1
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
		clock.tick(10)

	pygame.time.wait(1000)
	pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()

