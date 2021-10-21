import pygame
import numpy as np
from math import sqrt
import time
import random
from methodtools import lru_cache
import cProfile
WHITE = (255,255,255)
GRAY = (100,100,100)
DRED = (150,0,0)
MARGIN = 200
CELL_S = 160

coherence_VR = 50**2
separation_VR = 15**2
alignment_VR = 50**2


class Boid:
	def __init__(self, boid_id, x, y, color):
		self.boid_id = boid_id
		self.x = x
		self.y = y
		self.x_v = random.random()*10-5
		self.y_v = random.random()*10-5
		self.grid_id = self.update_grid_id()
		self.color = color
		self.radius = 4

	def distance_to(self, other_boid):
		return (self.x - other_boid.x)**2 + (self.y - other_boid.y)**2

	def update_grid_id(self):
		return int(int(self.y/CELL_S)*int(current_w/CELL_S) + int(self.x/CELL_S))

	def get_neighbours(self, hash_table, boids):


		if self.grid_id in hash_table:
			return hash_table[self.grid_id] - {self.boid_id}
		else:
			return []

	def update(self, screen, current_w, current_h, boids, hash_table):

		self.grid_id = self.update_grid_id()

		if self.color != WHITE:
			for n in self.get_neighbours(hash_table, boids):
				other_boid = boids[n]
				pygame.draw.line(screen, (0,255,0), (int(self.x),int(self.y)), (int(other_boid.x), int(other_boid.y)), width=3)

		def cap_speed(speed_cap):
			speed = sqrt(self.x_v**2 + self.y_v**2)

			if speed > speed_cap:
				self.x_v = (self.x_v / speed)*speed_cap
				self.y_v = (self.y_v / speed)*speed_cap
			
		def keep_within_bounds(turn_factor):
			if self.x < MARGIN:
				self.x_v += turn_factor

			if self.x > current_w - MARGIN:
				self.x_v -= turn_factor

			if self.y < MARGIN:
				self.y_v += turn_factor

			if self.y > current_h - MARGIN:
				self.y_v -= turn_factor

		def coherence(neighbors, visual_range, coherence_factor):

			target_x = 0
			target_y = 0
			n_neighbors = 0

			for n in neighbors:
				other_boid = boids[n]
				if self.distance_to(other_boid) < visual_range:
					target_x += other_boid.x
					target_y += other_boid.y
					n_neighbors += 1

			if n_neighbors > 0:
				self.x_v += (target_x/n_neighbors - self.x) * coherence_factor 
				self.y_v += (target_y/n_neighbors - self.y) * coherence_factor 

		def separation(neighbors, visual_range, separation_factor):

			move_x = 0
			move_y = 0

			for n in neighbors:
				other_boid = boids[n]
				d = self.distance_to(other_boid)
				if d < visual_range:
					move_x += self.x - other_boid.x
					move_y += self.y - other_boid.y


			self.x_v += move_x * separation_factor
			self.y_v += move_y * separation_factor

		def alignment(neighbors, visual_range, alignment_factor):
			avg_vx = 0
			avg_vy = 0
			n_neighbors = 0

			for n in neighbors:
				other_boid = boids[n]
				if self.distance_to(other_boid) < visual_range:
					avg_vx += other_boid.x_v
					avg_vy += other_boid.y_v
					n_neighbors += 1

				if n_neighbors > 0:
					self.x_v += (avg_vx/n_neighbors - self.x_v) * alignment_factor
					self.y_v += (avg_vy/n_neighbors - self.y_v) * alignment_factor


		'''
		TODO
		pasar de 3 a 1 "distance to"
		"hash pivot table"

		'''
		neighbors = self.get_neighbours(hash_table, boids)
		coherence(neighbors, visual_range = coherence_VR, coherence_factor = 0.005)
		separation(neighbors, visual_range = separation_VR, separation_factor = 0.05)
		alignment(neighbors, visual_range = alignment_VR, alignment_factor = 0.005)
		cap_speed(speed_cap = 10)
		keep_within_bounds(turn_factor = 1)

		self.x += self.x_v
		self.y += self.y_v

		return True
		

	def draw(self, screen):
		#pygame.draw.circle(screen, DRED, (int(self.x),int(self.y)), self.radius+35, width=1)
		#pygame.draw.circle(screen, GRAY, (int(self.x),int(self.y)), self.radius+75, width=1)
		pygame.draw.circle(screen, self.color, (int(self.x),int(self.y)), self.radius, width=0)
		#pygame.draw.circle(screen, (0,0,0), (int(self.x),int(self.y)), self.radius, width=1)

		vector = (int(self.x_v+self.x),int(self.y_v+self.y))
		pygame.draw.line(screen, WHITE, (int(self.x),int(self.y)), vector, width=3)


if __name__ == '__main__':

	pygame.init()
	clock = pygame.time.Clock()
	infoObject = pygame.display.Info()
	current_w, current_h = infoObject.current_w, infoObject.current_h
	screen = pygame.display.set_mode((current_w,current_h), pygame.FULLSCREEN)

	boids = []
	hash_table = {i:set() for i in range(int(current_h*current_w/CELL_S**2))}
	
	for i in range(500):
		if i == 0:
			color = (255,0,0)
		else:
			color = WHITE
		boids.append(Boid(i, random.random()*current_w,random.random()*current_h, color))
		hash_table[boids[-1].grid_id].add(i)


	running = True
	count_f = 0

	while running:
		
		screen.fill((0,0,0))

		for i in range(0, current_h, CELL_S):
			pygame.draw.line(screen, GRAY, (0, i), (current_w, i), width=1)
		for i in range(0, current_w, CELL_S):
			pygame.draw.line(screen, GRAY, (i, 0), (i, current_h), width=1)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		#cProfile.run('for i, b in enumerate(boids):b.update(screen, current_w, current_h, boids, hash_table)')
		#exit()
		for i, b in enumerate(boids):
			
			last_g_id = b.grid_id
			b.update(screen, current_w, current_h, boids, hash_table)
			
			if last_g_id != b.grid_id:
				if b.grid_id in hash_table and last_g_id in hash_table:
					hash_table[last_g_id].remove(i)
					hash_table[b.grid_id].add(i)
				

			b.draw(screen)
		
		
		count_f += 1
		if count_f >= 60:
			count_f = 0
			print('fps:',int(clock.get_fps()), 'boids:', len(boids))

		clock.tick(30)
		pygame.display.update()