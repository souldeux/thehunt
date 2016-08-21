import random
import math



class Organism(object):
	"The base Organism class for the simulation."

	organism_counter = 0
	predator_counter = 0
	prey_counter = 0

	def __init__(self, **kwargs):
		"""
		If the organism is from generation 0, its base attributes are initialized 
		with random values. If the organism is the result of the mating of two parents, 
		we use values from those parents' attributes to set new values. 
		"""

		if kwargs.get('parent_dict', None) is not None:
			#Each attribute will be keyed to a tuple. The new raw attributes will fall in a range 
			#between the tuple's values
			d = kwargs['parent_dict']
			self.rawSpeed = random.randrange( sorted(d['Speed'])[0], sorted(d['Speed'])[1]+1 )
			self.rawWillpower = random.randrange( sorted(d['Willpower'])[0], sorted(d['Willpower'])[1]+1 )
			self.rawPerception = random.randrange( sorted(d['Perception'])[0], sorted(d['Perception'])[1]+1 )
			self.rawStealth = random.randrange( sorted(d['Stealth'])[0], sorted(d['Stealth'])[1]+1 )
			self.rawFortitude = random.randrange( sorted(d['Fortitude'])[0], sorted(d['Fortitude'])[1]+1 )
			self.rawPower = random.randrange( sorted(d['Power'])[0], sorted(d['Power'])[1]+1 )
			self.rawVirility = random.randrange( sorted(d['Virility'])[0], sorted(d['Virility'])[1]+1 )


		else:
			#generation 0, seed base non-derived attributes with random numbers
			self.rawSpeed = random.randrange(0,101)
			self.rawWillpower = random.randrange(0,101)
			self.rawPerception = random.randrange(0,101)
			self.rawStealth = random.randrange(0,101)
			self.rawFortitude = random.randrange(0,101)
			self.rawPower = random.randrange(0,101)
			self.rawVirility = random.randrange(0,101)




		#Now that raw attributes have been set, weight them against one another using set modulation rules
		"""
		Speed: Negatively impacted by Fortitude and Power, max negative impact = 10%, max +15 from willpower
		Stealth: Negatively impacted by Fortitude (max = 20%), Positively impacted by Perception (max = 35%)
		Perception: Positively impacted by Willpower (max = 10%)
		Willpower: Positively impacted by Power (max = 20%)
		Fortitude: Negatively impacted by Stealth (max = 20%), Positively impacted by Power (max = 10%)
		Power: Positively impacted by Fortitude (max = 10%), Positively impacted by Speed (max = 10%)
		Virility: Positive impacted by Fortitude
		To illustrate, let's take the raw numbers for a hypothetical organism and adjust them.

			Speed: 56
			Willpower: 88
			Perception: 23
			Stealth: 56
			Fortitude: 74
			Power: 34
			Virility: 45

		Speed is negatively impacted by Fortitude (74) and Power (34). The maximum negative impact is 10% 
		attribute = rawAttribute +/- (((sum of attributes) / (number of attributes)) * maxImpact)
		speed = rawSpeed - ((( self.rawFortitude + self.rawPower ) / (2) * 0.2)
		speed = 56 - ((( 74 + 34 ) / 2) * 0.2)
		"""

		self.speed = self.rawSpeed - int( float((self.rawFortitude + self.rawPower)/2) * 0.1 ) + int ( self.rawWillpower * 0.15)
		self.willpower = self.rawWillpower + int( self.rawPower * 0.2 )
		self.perception = self.rawPerception + int (self.rawWillpower * 0.1 )
		self.stealth = self.rawStealth - int( self.rawFortitude * 0.2 ) + int( self.rawPerception * 0.35 )
		self.fortitude = self.rawFortitude - int( self.rawStealth * 0.2 ) + int( self.rawPower * 0.1 )
		self.power = self.rawPower + int( self.rawSpeed * 0.1 ) + int( self.rawPower * 0.2 )
		self.virility = self.rawVirility + int( self.rawFortitude * 0.15 )

		#Hunger is the average of ALL variables
		self.hunger = int( float((self.speed + self.willpower + self.perception + self.stealth + self.fortitude + self.power + self.virility)/6) )
		
		#Finally, determine if the organism is viable (any negative attributes = nonviable)
		#Also set self.alive here; we flip this flag later if the organism dies during testing of their generation
		viability_checklist = [self.speed, self.willpower, self.perception, self.stealth, self.fortitude, self.power, self.virility]
		if any(attr < 0 for attr in viability_checklist):
			self.viable = False
			self.alive = False
		else:
			self.viable = True
			self.alive = True

		#set self.id equal to current organism counter and increment
		self.id = Organism.organism_counter
		Organism.organism_counter += 1

		#if this is generation 0, randomly assign the organism as predator/prey. if this is a mating, set it as the same type as
		#the parents
		if kwargs.get('parent_dict', None) is not None:
			self.predator = kwargs['parent_dict']['Predator']
		else:
			if random.randrange(0,2):
				self.predator = True
				Organism.predator_counter += 1
			else:
				self.predator = False
				Organism.prey_counter += 1


	def step(self, self_location, approach=None, retreat=None):
		"""
		Combat trials take place on an infinitely large coordinate grid. Organisms can move around the grid one horizontal,
		vertical, or diagonal step at a time. In practice this amounts to increment or decrementing the x and/or y coordinate.
		We structure the logic so that diagonal moves (in/decrementing both x and y) is preferred since it's technically "faster."
		If given a value for approach or retreat (a tuple of x,y coordinates), we will move towards/away from the coordinates
		as appropriate. If not, we wander around randomly.

		Returns new (x,y) coordinates relevant to the grid system
		"""

		if not approach and not retreat:
			#random wandering; add -1, 0 or 1 to current coordinates
			new_x = self_location[0] + random.randrange(-1,2)
			new_y = self_location[1] + random.randrange(-1,2)


		elif approach:
			if approach[0] > self_location[0]:
				new_x = self_location[0] + 1
			elif approach[0] < self_location[0]:
				new_x = self_location[0] - 1
			else:
				new_x = self_location[0]

			if approach[1] > self_location[1]:
				new_y = self_location[1] + 1
			elif approach[1] < self_location[1]:
				new_y = self_location[1] - 1
			else:
				new_y = self_location[1]


		elif retreat:
			if retreat[0] > self_location[0]:
				new_x = self_location[0] - 1 #widen the gap!
			elif retreat[0] < self_location[0]:
				new_x = self_location[0] + 1
			else: #retreat[0] == self_location[0]; panic and maybe go diagonally
				new_x = self_location[0] + random.randrange(-1,2)

			if retreat[1] > self_location[1]:
				new_y = self_location[1] - 1
			elif retreat[1] < self_location[1]:
				new_y = self_location[1] + 1
			else: #retreat[1] == self_location[1]
				new_y = self_location[1] + random.randrange(-1,2)


		return (new_x, new_y)


	
	def distance_to_other(self, self_location, other_location):
		"""
		Given an x,y location for both self and other, returns the distance between the points
		"""
		x_coords = (self_location[0], other_location[0])
		y_coords = (self_location[1], other_location[1])

		xlist = sorted(x_coords)
		ylist = sorted(y_coords)

		x_distance = xlist[1] - xlist[0]
		y_distance = ylist[1] - ylist[0]

		return math.sqrt( (x_distance**2) + (y_distance**2) )



	def sense_other(self, other, self_location, other_location):
		"""
		Given another Organism and its (x,y) location on the combat grid, determines if the referenced Organism (self) can 
		sense the other.
		"""

		true_distance = self.distance_to_other(self_location, other_location)

		#a given organism has a maximum perception distance of (self.perception * 0.50)
		if true_distance > ( self.perception * 0.50 ):
			return False

		else:
			#sensing organism performs a 1d20 perception check against the other organism's 1d20 stealth check
			return ( (self.perception + random.randrange(1,21)) > (other.stealth + random.randrange(1,21)) )


	def take_combat_turn(self, other, self_location, other_location):
		"""
		A combat turn has two phases, so long as Predator and Prey aren't occupying the same spot:
		1. Determine if we can sense another organism
		2. Take a step in the appropriate direction

		If P&P occupy the same spot at the beginning of a combat turn, there is a willpower check to see if 
		the prey runs away or is held down. If the prey fails the check there is a power check to see what damage 
		is done - prey can fight back, after all. Damage reduces fortitude, if fort falls below 0 the organism is killed.

		Will either return the new coordinates of the Organism taking a turn, or a victorious object if the turn results in a
		kill
		"""
		
		if self_location == other_location:
			if self.predator:
				#1d20 willpower to hold down the prey; escape == False if successful
				escape = ( (self.willpower + random.randrange(1,21)) < (other.willpower + random.randrange(1,21)) )
			else:
				escape = ( (self.willpower + random.randrange(1,21)) > (other.willpower + random.randrange(1,21)) )

			if escape:
				"""
				if this is the prey's move, the prey "runs away"
				if this is the predator's move, the predator is "forced off"
				Either way, the effect is the same - a successful escape moves the Organism taking the turn 1d(something) away
				"""
				if self.predator:
					#forced off!
					new_x = self_location[0] + random.randrange(0, int(self.fortitude * 0.1) + 1) + 1
					new_y = self_location[1] + random.randrange(0, int(self.fortitude * 0.1) + 1) + 1
				else:
					#ran away!
					new_x = self_location[0] + random.randrange(0, int(self.speed * 0.1) + 1) + 1
					new_y = self_location[1] + random.randrange(0, int(self.speed * 0.1) + 1) + 1

				return (new_x, new_y)

			else:
				#no escape; predator strikes prey. 
				if self.predator:
					#roll for damage; 1d5 plus power factor
					damage = random.randrange(1,6) + int(self.power * 0.05)
					#predators get a 5% chance to crit & deal double damage
					if random.randrange(0,20) == 0:
						damage *= 2
					
					other.fortitude -= damage
					if other.fortitude <= 0:
						other.alive = False
						return self

					#prey strikes back; no critical strikes for prey
 					revenge = random.randrange(1,6) + int(other.power * 0.05)
 					self.fortitude -= revenge
 					if self.fortitude <= 0:
 						self.alive = False
 						return other

 					#if any of these blows had been fatal to either party we'd have returned a value. since we haven't, just
 					#return current location
 					return self_location


 				else:
 					#predator still strikes first; sucks to be prey. should've been better at running away. no mortal strike though
 					damage = random.randrange(1,6) + int(other.power * 0.05)
 					self.fortitude -= damage
 					if self.fortitude <= 0:
 						self.alive = False
 						return other

 					revenge = random.randrange(1,6) + int(self.power * 0.05)
 					other.fortitude -= revenge
 					if other.fortitude <= 0:
 						other.alive = False
 						return self

 					return self_location


		elif self.sense_other(other, self_location, other_location):
			if self.predator:
				return self.step(self_location, approach=other_location)
			else:
				return self.step(self_location, retreat=other_location)
		else:
			return self.step(self_location)

	def reset_fort(self):
		#Resets Fortitude stat after surviving a combat round to prevent some weird lamarckian breeding of wounds
		self.fortitude = self.rawFortitude - int( self.rawStealth * 0.2 ) + int( self.rawPower * 0.1 )
		return self


	def quick_repr(self):
		print "Quick representation"
		print "ID#: {}".format(self.id)
		print "Speed: {} (Raw: {})".format(self.speed, self.rawSpeed)
		print "Willpower: {} (Raw: {})".format(self.willpower, self.rawWillpower)
		print "Perception: {} (Raw: {})".format(self.perception, self.rawPerception)
		print "Stealth: {} (Raw: {})".format(self.stealth, self.rawStealth)
		print "Fortitude: {} (Raw: {})".format(self.fortitude, self.rawFortitude)
		print "Power: {} (Raw: {})".format(self.power, self.rawPower)
		print "Virility: {} (Raw: {})".format(self.virility, self.rawVirility)
		print "Hunger: {}".format(self.hunger)
		print "Viable: {}".format(self.viable)

	def __repr__(self):
		return "Organism {} (p = {})".format(self.id, self.predator)


class Generation(object):
	"""
	A Generation is a population of Organisms. Generation 0 of the simulation will have no ancestors, so to create
	that generation simply supply the starting population size. Otherwise, initialize with a list of Organism
	objects (survivors of the previous generation, ancestors to the new one)
	"""

	generation_counter = 0


	def __init__(self, **kwargs):

		self.nonviable_predator_count = 0
		self.nonviable_prey_count = 0

		self.id = Generation.generation_counter
		Generation.generation_counter += 1

		if kwargs.get('n', None) is not None:
			#if n is supplied we are spawning generation 0. initalize n organisms. 
			self.predators = []
			self.prey = []
			for i in range(0,kwargs['n']):
				new_organism = Organism()
				if not new_organism.viable:
					#organism died in utero, does not make it to surviving population
					if new_organism.predator:
						self.nonviable_predator_count += 1
					else:
						self.nonviable_prey_count += 1
				elif new_organism.predator:
					self.predators.append(new_organism)
				else:
					self.prey.append(new_organism)

		else:
			#If we don't get an n object, we're getting a list of Organisms from the previous generation called Ancestors
			#These are the ones that survived. We use their genetics to initialize the next generation.
			self.predators = []
			self.prey = []

			#each Organism will mate with between 0 and 3 other Organisms, controlled by the Virility stat. 
			#Use python's weirdo division/int/whatever to get the numbers we actually want here

			#Iterate through ancestors; for each, determine # of mates
			for a in kwargs['ancestors']:
				mate_counter = a.virility/12

				#get random mates by sampling an appropriate number from the list of potential mates
				try:
					if a.predator:
						mates = random.sample([m for m in kwargs['ancestors'] if m.predator and m != a], mate_counter)
					else:
						mates = random.sample([m for m in kwargs['ancestors'] if not m.predator and m != a], mate_counter)
				except ValueError:
					#if the mate_counter for a given ancestor exceeds the available pool of mates, 
					#we get ValueError("sample larger than population"). In this scenario, we say the ancestor
					#doesn't get to mate AT ALL, simulating a sort of population collapse
					mates = []

				#now our current Organism will pair with its mates, creating a new Organism
				for m in mates:
					#Create a dictionary of tuples, representing each parent's contribution to the pairing
					parent_dict = {
						'Speed': (a.speed, m.speed),
						'Willpower': (a.speed, m.speed),
						'Power': (a.power, m.power),
						'Stealth': (a.stealth, m.stealth),
						'Virility': (a.virility, m.virility),
						'Fortitude': (a.fortitude, m.fortitude),
						'Perception': (a.perception, m.perception),
						'Predator': a.predator,
						'id': (a.id, m.id)
					}

					#Create a new Organism by passing this dict of tuples; remember, they get sorted in the Organism's init
					offspring = Organism(parent_dict=parent_dict)

					#Append viable offspring to self.predator/prey, update counters for nonviables
					if offspring.viable:
						if offspring.predator:
							self.predators.append(offspring)
						else:
							self.prey.append(offspring)
					else:
						if offspring.predator:
							self.nonviable_predator_count += 1
						else:
							self.nonviable_prey_count += 1




		self.initial_predator_count = len(self.predators)
		self.initial_prey_count = len(self.prey)
		self.initial_total_count = self.initial_predator_count + self.initial_prey_count

		self.nonviable_count = self.nonviable_prey_count + self.nonviable_predator_count

		#flag is set to False until we run the trials on a given generation
		self.simulation_has_run = False
		
		#we update these counters after the simulation has run
		self.post_combat_predator_count = 0
		self.post_combat_prey_count = 0
		self.post_combat_total_count = 0
		self.post_combat_population_imbalance = 0

		self.predator_hunger_death_count = 0
		self.prey_hunger_death_count = 0

		self.final_predator_count = 0
		self.final_prey_count = 0
		self.final_total_count = 0



	def generate_trial_pairings(self):
		#determines combat pairings & leftovers for the generation
		#recall that self.predators/self.prey are lists of objects (Organisms)

		#the population (predator or prey) with the smaller size is our "limiting reagent" - they'll all get matches
		if self.initial_predator_count > self.initial_prey_count:
			prey_list = self.prey
			shuffled_predators = [s for s in random.sample(self.predators, len(self.predators))]
			#we split this shuffled list into two parts; the first slice will be our "matchups"
			predator_list = shuffled_predators[:self.initial_prey_count]
			leftovers = shuffled_predators[self.initial_prey_count:]
			leftover_type = "Predator"

		else:
			predator_list = self.predators
			shuffled_prey = [s for s in random.sample(self.prey, len(self.prey))]
			prey_list = shuffled_prey[:self.initial_predator_count]
			leftovers = shuffled_prey[self.initial_predator_count:]
			leftover_type = "Prey"


		#at this point both predator_list and prey_list are of equal length
		pairings = zip(predator_list, prey_list)

		return {'pairings': pairings, 'leftovers': leftovers, 'leftover_type': leftover_type}



	def run_combat_trials(self, pairings, leftovers):
		#iterates through pairings and returns a list of victorious Organism objects
		#recall that pairings comes in as a list of tuples

		survivors = []
		survivors += leftovers
		#we seed the survivor list here with our leftovers, even though they're not in combat. This lets
		#us use some easy list comprehension later to reconstruct the total population after combat has taken place,
		#and lets us accurately calculate imbalance after combat


		for player_one, player_two in pairings:
			round_counter = 0
			#drop the participants on a grid
			player_one_location = ( random.randrange(-10,11), random.randrange(-10,11) )
			player_two_location = ( random.randrange(-10,11), random.randrange(-10,11) )

			while (player_one.alive and player_two.alive):
				#take_combat_turn(self, other, self_location, other_location) returns either a new location for the entity
				#taking the turn or a victorious organism

				#each player takes a certain number of turns per cycle, determined by their Speed stat
				round_counter += 1

				for x in range(0, (int( player_one.speed * .15 )+1) ):
					player_one_location = player_one.take_combat_turn(player_two, player_one_location, player_two_location)
					if player_one_location == player_one or player_one_location == player_two:
						victorious_organism = player_one_location.reset_fort() #victorious object; not necessarily player one!
						survivors.append(victorious_organism)
						break

				if not (player_one.alive and player_two.alive):
					break

				for x in range(0, (int( player_two.speed * .15)+1) ):
					player_two_location = player_two.take_combat_turn(player_one, player_two_location, player_one_location)
					if player_two_location == player_one or player_two_location == player_two:
						victorious_organism = player_two_location.reset_fort() #victorious object; not necessarily player two!
						survivors.append(victorious_organism)
						break
				
				if not (player_one.alive and player_two.alive):
					break	
					
			
				if round_counter >= 1000:
					#after 1000 rounds if both are alive, the prey escapes and the predator starves
					if player_one.predator:
						player_one.alive = False
						survivors.append(player_two.reset_fort())
					else:
						player_two.alive = False
						survivors.append(player_one.reset_fort())
					



		self.predators = [p for p in self.predators if p in survivors]
		self.prey = [p for p in self.prey if p in survivors]
		self.post_combat_predator_count = len(self.predators)
		self.post_combat_prey_count = len(self.prey)
		self.post_combat_total_count = self.post_combat_predator_count + self.post_combat_prey_count
		
		population_count_list = sorted((self.post_combat_prey_count, self.post_combat_predator_count))
		try:
			#populations of equal size would return 0 here
			#If one population is 2x the other, this would return 100, etc.
			self.post_combat_population_imbalance = ((float( population_count_list[1] ) / float( population_count_list[0] )) * 100.0) - 100
		except ZeroDivisionError:
			#population collapse!
			self.post_combat_population_imbalance = 9999

		return survivors

	def run_hunger_trials(self, leftovers, leftover_type):
		"""
		to be used after combat trials; iterates through leftovers and sees who starves to death;

		self.hunger means "I need the populations to be this percentage similar, or I am going to starve to death"
		In other words, "I can maintain a maximum percentage imbalance of (100 - self.hunger)."
		i.e., hunger = 90 means max imbalance is 10%. hunger = 40 means max imbalance is 60%.

		Our post_combat_population_imbalance basically says "after fighting, and including leftovers who didn't fight, 
		one population is now X%/ larger than the other." 

		So, if (100 - self.hunger) < imbalance, the organism starves.
		"""
		
		print "{} {}s for Hunger Trials".format(len(leftovers), leftover_type)
		print "Imbalance: {}".format(self.post_combat_population_imbalance)
		
		for o in leftovers:
			if (100 - o.hunger) < self.post_combat_population_imbalance and leftover_type == 'Predator':
				o.alive = False
				self.predators.remove(o)
				self.predator_hunger_death_count += 1

			elif (100 - o.hunger) < self.post_combat_population_imbalance and leftover_type == 'Prey':
				o.alive = False
				self.prey.remove(o)
				self.prey_hunger_death_count += 1

		return self

	
	def simulate_generation(self):
		#Runs combat trials and hunger trials, returns self
		print "Generating Pairing Dictionary for G{}".format(self.id)
		pairing_dict = self.generate_trial_pairings()
		print "...Done."

		print "Running Combat Trials for G{}".format(self.id)
		self.run_combat_trials(pairing_dict['pairings'], pairing_dict['leftovers'])
		print "...Done."

		print "Running Hunger Trials for G{}".format(self.id, len(pairing_dict['leftovers']))
		self.run_hunger_trials(pairing_dict['leftovers'], pairing_dict['leftover_type'])
		print "...Done."

		self.final_predator_count = len(self.predators)
		self.final_prey_count = len(self.prey)
		self.final_total_count = self.final_prey_count + self.final_predator_count

		self.simulation_has_run = True
		self.simulation_report()
		return self


	def reproduce(self):
		#Uses the current population to create the next generation
		return Generation(ancestors=(self.predators + self.prey))


	def simulation_report(self):
		"""
		Provides a summary of how a given Generation looks after simulation_has_run
		"""
		if not self.simulation_has_run:
			return False

		if len(self.predators) == 0 or len(self.prey) == 0:
			print "Population has collapsed!"
			return False

		mean_predator_speed = sum([o.speed for o in self.predators]) / len(self.predators)
		mean_prey_speed = sum([o.speed for o in self.prey]) / len(self.prey)
		
		mean_predator_willpower = sum([o.willpower for o in self.predators]) / len(self.predators)
		mean_prey_willpower = sum([o.willpower for o in self.prey]) / len(self.prey)
		
		mean_predator_power = sum([o.power for o in self.predators]) / len(self.predators)
		mean_prey_power = sum([o.power for o in self.prey]) / len(self.prey)
		
		mean_predator_fortitude= sum([o.fortitude for o in self.predators]) / len(self.predators)
		mean_prey_fortitude = sum([o.fortitude for o in self.prey]) / len(self.prey)
		
		mean_predator_stealth = sum([o.stealth for o in self.predators]) / len(self.predators)
		mean_prey_stealth = sum([o.stealth for o in self.prey]) / len(self.prey)
		
		mean_predator_perception = sum([o.perception for o in self.predators]) / len(self.predators)
		mean_prey_perception = sum([o.perception for o in self.prey]) / len(self.prey)
		
		mean_predator_virility = sum([o.virility for o in self.predators]) / len(self.predators)
		mean_prey_virility = sum([o.virility for o in self.prey]) / len(self.prey)

		mean_predator_hunger = sum([o.hunger for o in self.predators]) / len(self.predators)
		mean_prey_hunger = sum([o.hunger for o in self.prey]) / len(self.prey)

		print "Generation {} Report".format(self.id)
		print "    Average Stats    "
		print "---------------------"
		print "   Predator | Prey   "
		print "Spd:  {}         {}  ".format(mean_predator_speed, mean_prey_speed)
		print "WP:   {}         {}  ".format(mean_predator_willpower, mean_prey_willpower)
		print "Pwr:  {}         {}  ".format(mean_predator_power, mean_prey_power)
		print "Frt:  {}         {}  ".format(mean_predator_fortitude, mean_prey_fortitude)
		print "Sth:  {}         {}  ".format(mean_predator_stealth, mean_prey_stealth)
		print "Per:  {}         {}  ".format(mean_predator_perception, mean_prey_perception)
		print "Vir:  {}         {}  ".format(mean_predator_virility, mean_prey_virility)
		print "Hgr:  {}         {}  ".format(mean_predator_hunger, mean_prey_hunger)
		print "---------------------\n\r\n\r"
		print "{} Predators after combat (I:{})".format(self.post_combat_predator_count, self.initial_predator_count)
		print "{} Prey after combat (I:{})".format(self.post_combat_prey_count, self.initial_prey_count)
		print "{} Total after combat (I:{})".format(self.post_combat_total_count, self.initial_total_count)
		print "Deaths to starvation: {}".format(self.prey_hunger_death_count+self.predator_hunger_death_count)	
		print "Final size of Generation {}: {} (Initial viable: {}, NV: {})".format(self.id, self.final_total_count, self.initial_total_count, self.nonviable_predator_count+self.nonviable_prey_count)

		return self


	def __repr__(self):
		return "Generation {}".format(self.id)




class Epoch(object):

	"""
	An Epoch is made up of many Generations.
	"""

	epoch_counter = 0

	def __init__(self, initial_size, target_iterations, **kwargs):
		Epoch.epoch_counter += 1
		self.id = Epoch.epoch_counter
		self.generations = []
		self.population_collapse = False
		self.initial_size = initial_size
		self.target_iterations = target_iterations
		self.simulation_has_run = False

	def simulate(self):
		"""
		Creates a generation of size defined by initial_size, simulates it, runs a mating cycle to create a new generation,
		simulates it, etc. until the number of generations set in the arguments has been run.
		"""
		gen = Generation(n=self.initial_size)
		self.generations.append(gen)


		while len(self.generations) < self.target_iterations:
			print "Simulating G{}".format(gen.id)
			print "Initial: {} (Py: {}) (Pd: {}) (Nv: {})".format(gen.initial_total_count, gen.initial_prey_count, gen.initial_predator_count, gen.nonviable_prey_count+gen.nonviable_predator_count)
			gen = gen.simulate_generation()
			print "Beginning mating cycle to spawn G{}...".format(gen.id+1)
			gen = gen.reproduce()
			self.generations.append(gen)
			print "...Done\n\r\n\r"
			if len(gen.predators) == 0 or len(gen.prey) == 0:
				self.population_collapse = True
				self.simulation_has_run = True
				print "Population collapse. Terminating simulation."
				print "Pd: {}   Py: {}".format(gen.final_predator_count, gen.final_prey_count)
				return self

		print "Simulating G{}; FINAL ITERATION".format(gen.id)
		print "Initial: {} (Py: {}) (Pd: {}) (Nv: {})".format(gen.initial_total_count, gen.initial_prey_count, gen.initial_predator_count, gen.nonviable_prey_count+gen.nonviable_predator_count)
		gen = gen.simulate_generation()
		print "-----------------------\n\r\n\r"
		print "{} generations simulated".format(self.target_iterations)
		self.simulation_has_run = True
		print "G0 vs G{}".format(self.target_iterations)
		print "-----------------------\n\r\n\r"
		self.generations[0].simulation_report()
		self.generations[-1].simulation_report()
		return self

	def __repr__(self):
		return "Epoch {}".format(self.id)



if __name__ == "__main__":
		initial_size = int(raw_input("Enter size of initial generation:\n"))
		target_iterations = int(raw_input("Enter target number of generations:\n"))
		e = Epoch(initial_size = initial_size, target_iterations = target_iterations)
		e.simulate()
