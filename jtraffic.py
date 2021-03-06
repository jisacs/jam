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

class Link():
	def __init__(self,start=None,end=None):
		self.start=start
		self.end=end
		self.roads=list()
		
	def append(self,road):
		self.roads.append(road)
		
	def has(self,road):
		for exising_road in self.roads:
			if exising_road.pos == road.pos or \
			   road.pos == self.start.pos:
				return True
		return False
	
	def get_neighbours_remaining(self,road):
		result=list()
		neighbours = road.get_roads_neighbours()
		for neighbour in neighbours.values():
			if not self.has(neighbour): 
				   result.append(neighbour) 
		return result
	
	def clean(self):
		"""
		suppime les morceaux de route en cul de sac
		"""
		
		stop = False
		while(stop == False):
			to_remove = list()
			if len(self.roads) == 0 : return
			last = self.start
			
			counter = 0
			for road in self.roads[:]:
				counter+=1
				if abs(road.pos[X] - last.pos[X]) > 1 or abs(road.pos[Y] - last.pos[Y]) > 1 or \
					 (road.pos[X] != last.pos[X] and road.pos[Y] != last.pos[Y]) :
					to_remove.append(last)
					new_list = [item for item in self.roads if item not in to_remove]
					self.roads = new_list
					break
				else:
					last = road
					
			if counter == len(self.roads):
				stop = True
		
		
class Map():
	def __init__(self):
		self.roads=dict() # key (x,y) value = Road reference
		self.starts=dict()
		self.links=list()
		
	def set_roads_neighbour_instance(self):
		for road in self.roads.values():
			if road.road_type==Road.START:
				self.starts[(road.pos[X],road.pos[Y])] = road
				
			if (road.pos[X],road.pos[Y]-1)  in self.roads.keys():
				road.neighbours["UP"] = self.roads[(road.pos[X],road.pos[Y]-1)]
			
			if (road.pos[X],road.pos[Y]+1)  in self.roads.keys():
				road.neighbours["DOWN"] = self.roads[(road.pos[X],road.pos[Y]+1)]
			
			if (road.pos[X]-1,road.pos[Y])  in self.roads.keys():
				road.neighbours["LEFT"] = self.roads[(road.pos[X]-1,road.pos[Y])]
			
			if (road.pos[X]+1,road.pos[Y])  in self.roads.keys():
				road.neighbours["RIGHT"] = self.roads[(road.pos[X]+1,road.pos[Y])]

			

	def computeLinks(self):
		self.set_roads_neighbour_instance()
		
		for start in self.starts.values():
			for start_neigs in start.get_roads_neighbours().values():
				link = Link(start=start)
				current_road = start_neigs
				#print("append", current_road.pos)
				link.append(current_road)
				stop=False
				crossroads = list()
				while stop == False:
					for next_road in current_road.get_roads_neighbours().values():
						if len(link.get_neighbours_remaining(next_road)) > 1:
							crossroads.append(next_road)
						if not link.has( next_road):
							if next_road.road_type==Road.START: # Find the END
								link.end=next_road
								if link != None and link.end != None :
									link.clean()
									self.links.append(link)
								stop = True
								break
							else:
								link.append(next_road)
								current_road=next_road
								break
						else : # road already in link	
							if len(link.get_neighbours_remaining(current_road)) <= 0 :
								if len(crossroads) >= 1:
									current_road = crossroads.pop()
								else:
									stop=True
									break
					
		print("Map:computeLinks find ",len(self.links)," links")
		for link in self.links:
			if link.end!= None:
				print("start", link.start.pos,"end: ", link.end.pos,"len",len(link.roads))
			else:
				print("start", link.start.pos,"end: ", "NA" ,"len",len(link.roads))
			"""
			for block in link.roads:
				print(block.pos,end='')
			print("\n")
			"""


#Block.images = [ver,hor,br,bl,tl,tr,cross,tbr,tbl,tlr,blr,start,un]
class Block(pygame.sprite.Sprite):
	"""
	"""
	COLOR_START   = 0
	COLOR_UNKNOWN = 1
	COLOR_ROAD    = 2
	SIZE = (25,25)

	
	def __init__(self,pos,block_color_type):
		"""
		Parameters
		----------
		pos: tuple(x,y)
		"""
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.pos = pos
		self.image = load_image("unknow.jpg")
		val = (pos[X]*self.SIZE[X]+self.SIZE[X]/2 ,pos[Y]*self.SIZE[Y]+self.SIZE[Y]/2 )
		self.rect = self.image.get_rect(center=(val))
		self.reloading = 0
		self.origtop = self.rect.top
		

		
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
		

class Road(Block):
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
	
	def __init__(self,pos,neighbours,block_color_type):
		Block.__init__(self,pos,block_color_type)
		self.neighbours = neighbours
		if block_color_type == Block.COLOR_START :
			self.road_type = self.START
			self.image=load_image('road_start.jpg')
		elif block_color_type == Block.COLOR_ROAD : self.set_road_type(neighbours)

	def set_road_type(self,neighbours):
		if (self.neighbours['RIGHT'] and neighbours['UP'] and neighbours['DOWN'] and neighbours['LEFT']):
			self.road_type=Road.CROSS
			self.image=load_image('road_cross.jpg')
		elif (neighbours['RIGHT'] and neighbours['UP'] and neighbours['DOWN']):
			self.road_type=Road.TBR
			self.image=load_image('road_top_bottom_right.jpg')
		elif (neighbours['RIGHT'] and neighbours['UP'] and neighbours['LEFT']):
			self.road_type=Road.TLR
			self.image=load_image('road_top_left_right.jpg')
		elif (neighbours['LEFT'] and neighbours['UP'] and neighbours['DOWN']):
			self.road_type=Road.TBL
			self.image=load_image('road_top_bottom_left.jpg')
		elif (neighbours['RIGHT'] and neighbours['LEFT'] and neighbours['DOWN']):
			self.road_type=Road.BLR
			self.image=load_image('road_bottom_left_right.jpg')
		elif (neighbours['LEFT'] or neighbours['RIGHT']) and  ( not neighbours['UP'] and  not neighbours['DOWN']):
			self.road_type=Road.HORIZONTAL
			self.image=load_image('road_hor.jpg')
		elif (neighbours['UP'] or neighbours['DOWN']) and  ( not neighbours['LEFT'] and  not neighbours['RIGHT']):
			self.road_type=Road.VERTICAL
			self.image=load_image('road_ver.jpg')
		elif (neighbours['LEFT'] and  neighbours['DOWN']):
			self.road_type=Road.BL
			self.image=load_image('road_bottom_left.jpg')
		elif (neighbours['RIGHT'] and  neighbours['DOWN']):
			self.road_type=Road.BR
			self.image=load_image('road_bottom_right.jpg')
		elif (neighbours['LEFT'] and  neighbours['UP']):
			self.road_type=Road.TL
			self.image=load_image('road_top_left.jpg')
		elif (neighbours['RIGHT'] and  neighbours['UP']):
			self.road_type=Road.TR
			self.image=load_image('road_top_right.jpg')
		else:
			print("set_road_type: unknow type set CROSS")
			self.road_type=Road.CROSS
			self.image=load_image('road_cross.jpg')
		
		
	def get_roads_neighbours(self):
		result = dict()
		for block in self.neighbours.values():
			if type(block) is Road:
				result[block.pos]=block
		return result




class Player(pygame.sprite.Sprite):
	size = 10
	bounce = 24
			#Load images, assign to sprite classes
		#(do this before the classes are used, after screen setup)
	
	def __init__(self,pos):
		self.img_up = load_image('carup.jpg')
		self.img_down = load_image('cardown.jpg')
		self.img_right = load_image('carright.jpg')
		self.img_left = load_image('carleft.jpg')
		
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.img_up
		self.pos=pos
		val = (pos[X]*Block.SIZE[X]+Block.SIZE[X]/2,pos[Y]*Block.SIZE[Y]+Block.SIZE[Y]/2)
		self.rect = self.image.get_rect(center=val)
		self.reloading = 0
		self.origtop = self.rect.top
		self.direction=(0,0)

	

	def move(self, keystate,blocks):
		xdir= keystate[K_RIGHT] - keystate[K_LEFT]
		ydir = keystate[K_DOWN] - keystate[K_UP]
		if xdir == 0 and ydir == 0:
			return
		self.rect.move_ip(xdir*Block.SIZE[X], ydir*Block.SIZE[Y])
		#self.rect.move_ip(xdir, ydir)
		# See if the Sprite block has collided with anything in the Group block_list
		# The True flag will remove the sprite in block_list
		blocks_hit_list = pygame.sprite.spritecollide(self, blocks, False)
		#print("len",  len(blocks_hit_list))
		#print("blocks_hit_list[0]", blocks_hit_list[0].rect , "self.rect", self.rect)
		#rect(x, y, width, heigh)
		#block_rect = blocks_hit_list[0].rect
		
		if len(blocks_hit_list) == 0 or type(blocks_hit_list[0]) is not Road:# or\
			#self.rect[0] < block_rect[0] or self.rect[0]+self.rect[2] > block_rect[0] + block_rect[2] or \
			#self.rect[1] < block_rect[1] or self.rect[1]+self.rect[3] > block_rect[1] + block_rect[3]  : 
			
			self.rect.move_ip(-xdir*Block.SIZE[X], -ydir*Block.SIZE[Y])
			#self.rect.move_ip(-xdir, -ydir)
			rect = self.rect.clamp(SCREENRECT)
			return
		

		rect = self.rect.clamp(SCREENRECT)
		self.direction=(xdir,ydir)
		
		if xdir < 0:
			self.image = self.img_left
		elif xdir > 0:
			self.image = self.img_right
		elif ydir < 0:
			self.image = self.img_up
		elif ydir > 0:
			self.image = self.img_down


class Application():
	def main(self,winstyle = 0):
		# Initialize pygame
		pygame.init()
		t_map = Map()

		# Set the display mode
		winstyle = 0  # |FULLSCREEN
		bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
		screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)



		
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
		blocks = pygame.sprite.Group()
		all = pygame.sprite.LayeredUpdates() # more sophisticated, can draw sprites in layers 
		#assign default groups to each sprite class
		Player.containers = all
		Block.containers=blocks,all
		#Create Some Starting Values
		clock = pygame.time.Clock()
		pixels = getPixelArray(os.path.join (main_dir, 'data', 'easy.tif'))
		x_len,y_len,z_len = pixels.shape
		
		start = None
		for x in range(x_len):
			for y in range(y_len):
				color = pixels[x,y]
				block_color_type = Block.get_color_type(color)
				pos = (x,y)
				blk=None
				if block_color_type == Block.COLOR_ROAD or block_color_type == Block.COLOR_START:
					neighbours={'UP':False,'DOWN':False ,'RIGHT':False ,'LEFT':False}
					if y-1 >=0 and Block.get_color_type(pixels[x,y-1]) == Block.COLOR_ROAD:neighbours['UP']=True
					if y+1 < y_len and Block.get_color_type(pixels[x,y+1]) == Block.COLOR_ROAD:neighbours['DOWN']=True
					if x+1 < x_len and  Block.get_color_type(pixels[x+1,y]) == Block.COLOR_ROAD:neighbours['RIGHT']=True
					if x-1 >= 0 and Block.get_color_type(pixels[x-1,y]) == Block.COLOR_ROAD:neighbours['LEFT']=True
					blk=Road(pos,neighbours,block_color_type)
					
				if  block_color_type == Block.COLOR_START:
					blk=Road(pos,neighbours,block_color_type)
					if start == None : start = blk
					
				elif  block_color_type == Block.COLOR_UNKNOWN:
					blk=Block(pos,block_color_type)
					
				if type(blk) is Road :  t_map.roads[(x,y)]=blk
					
		t_map.computeLinks()
		#initialize our starting sprites
		if start != None:
			player = Player(start.pos)
		else: player = Player((0,0))
		
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
			clock.tick(20)

		pygame.time.wait(1000)
		pygame.quit()

