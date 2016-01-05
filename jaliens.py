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
			print("---- clean list")
			for road in self.roads:
				print (road.pos, end='')
			print()
			to_remove = list()
			if len(self.roads) == 0 : return
			last = self.start
			
			counter = 0
			for road in self.roads[:]:
				counter+=1
				print("last: ", last.pos, "road: ", road.pos)
				if abs(road.pos[X] - last.pos[X]) > 1 or abs(road.pos[Y] - last.pos[Y]) > 1 or \
					 (road.pos[X] != last.pos[X] and road.pos[Y] != last.pos[Y]) :
					to_remove.append(last)
					new_list = [item for item in self.roads if item not in to_remove]
					self.roads = new_list
					print("break after having removed:", to_remove[0].pos )
					break
				else:
					last = road
					
			if counter == len(self.roads):
				print("stop = true")
				stop = True

			
		
		print("---- STOP clean list")
		for road in self.roads:
			print (road.pos, end='')
		print()
		
		
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
			#print("start", start.pos)
			for start_neigs in start.get_roads_neighbours().values():
				link = Link(start=start)
				current_road = start_neigs
				#print("append", current_road.pos)
				link.append(current_road)
				stop=False
				counter=30
				crossroads = list()
				while stop == False:# and counter >= 0:
					counter-=1
					#print("current road", current_road.pos)
					for next_road in current_road.get_roads_neighbours().values():
						#print("next_road", next_road.pos,"remaining neighbours: ", len(link.get_neighbours_remaining(next_road)))
						if len(link.get_neighbours_remaining(next_road)) > 1:
							crossroads.append(next_road)
							#print("---- Add crossroad")
							#for road in crossroads:
							#	print (road.pos, end='')
							#print()
							
						if not link.has( next_road):
							if next_road.road_type==Road.START: # Find the END
								link.end=next_road
								#print("============ end link", link.end.pos)
								stop = True
							else:
								link.append(next_road)
								current_road=next_road
								break
						if len(link.get_neighbours_remaining(current_road)) <= 0 :
							current_road = crossroads[-1]
							if len(link.get_neighbours_remaining(current_road)) <= 0:
								crossroads.pop()
								#print("---- Pop a crossroad")
								#for road in crossroads:
								#	print (road.pos, end='')
								#print()
							current_road = crossroads[-1]
							#print("current_road reset to crosseroad:", current_road.pos)
							break
				if link != None and link.end != None :
					link.clean()
					self.links.append(link)
					
		
		print("Map:computeLinks find ",len(self.links)," links")
		for link in self.links:
			if link.end!= None:
				print("start", link.start.pos,"end: ", link.end.pos,"len",len(link.roads))
			else:
				print("start", link.start.pos,"end: ", "NA" ,"len",len(link.roads))
			
			for block in link.roads:
				print(block.pos,end='')
			print("\n")
			


#Block.images = [ver,hor,br,bl,tl,tr,cross,tbr,tbl,tlr,blr,start,un]
class Block(pygame.sprite.Sprite):
	"""
	"""
	COLOR_START   = 0
	COLOR_UNKNOWN = 1
	COLOR_ROAD    = 2
	SIZE = (25,25)

	
	def __init__(self,pos,neighbours,block_color_type):
		"""
		Parameters
		----------
		pos: tuple(x,y)
		"""
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.neighbours=neighbours
		self.pos = pos
		self.image = load_image("unknow.tif")
		val = (pos[0]*self.SIZE[0]+self.SIZE[0]/2,pos[1]*self.SIZE[1]+self.SIZE[0]/2)
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
		Block.__init__(self,pos,neighbours,block_color_type)
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
	images = []
	def __init__(self,pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
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
	
	start = None
	for x in range(x_len):
		for y in range(y_len):
			color = pixels[x,y]
			block_color_type = Block.get_color_type(color)
			pos = (x,y)
			blk=None
			if block_color_type == Block.COLOR_ROAD or block_color_type == Block.COLOR_START:
				neighbours={'UP':False,'DOWN':False ,'RIGHT':False ,'LEFT':False}
				if Block.get_color_type(pixels[x,y-1]) == Block.COLOR_ROAD:neighbours['UP']=True
				if Block.get_color_type(pixels[x,y+1]) == Block.COLOR_ROAD:neighbours['DOWN']=True
				if Block.get_color_type(pixels[x+1,y]) == Block.COLOR_ROAD:neighbours['RIGHT']=True
				if Block.get_color_type(pixels[x-1,y]) == Block.COLOR_ROAD:neighbours['LEFT']=True
				blk=Road(pos,neighbours,block_color_type)
				
			if  block_color_type == Block.COLOR_START:
				blk=Road(pos,neighbours,block_color_type)
				if start == None : start = blk
				
			elif  block_color_type == Block.COLOR_UNKNOWN:
				blk=Block(pos,neighbours,block_color_type)
				
			if type(blk) is Road :  t_map.roads[(x,y)]=blk
				
	t_map.computeLinks()
	#initialize our starting sprites
	player = Player(start.pos)
	
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

