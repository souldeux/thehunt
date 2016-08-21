TheHunt is an evolution simulator based on a predator-prey relationship between lots of dots.

At the start of the simulation, 1000 random predators and 1000 random prey are generated. Each has a set of 
characteristics that determines how it behaves in the game:

	Speed - how far an organism can move in one cycle
	Willpower - for prey, how "slippery" an organism is; for predators, how "sticky" an organism is (escape/snare)
	Perception - how skilled an organism is at perceiving other organisms
	Stealth - how difficult it is for other oganisms to perceive this organism
	Fortitude - how "tough" an organism is (like hitpoints)
	Power - how "strong" an organism is
	Virility - breeding power; how many viable offspring tend to result from a successful mating
	Hunger - how often an organism needs to eat; used for population control. unique in that it is calculated from other variables, not set and then modulated by them

The Predator and Prey populations "face off" against each other one at a time on a large grid system. At the start of each trial, one Predator and one Prey are placed at random points on a 100 x 100 grid. After 1000 "moves", one of the two dots will be dead - either the Prey from being eaten, or the Predator from starvation.

The Prey moves around randomly until it senses the Predator, then moves directly away until it no longer senses it. The grid system is effectively infinitely large to avoid "cornering" mechanics.

The Predator wanders around randomly, too. When it senses Prey, it moves straight towards it.

On each "move" of the simulation, the organism with the higher speed stat will go first and take an appropriate number of steps. After each step, a check is made to determine whether or not the organism senses anything. If so, movement is altered appropriately.

If, after a Predator move, the Predator and Prey occupy the same coordinate, the two organisms are locked in combat. Various checks are made to determine the outcome:
	
	Power vs Fortitude - organisms damage each other in combat, reducing Fortitude to 0 results in organism death
	Perception+Willpower vs Perception+Willpower - does the prey escape after being caught, or does the predator hold it down?

Combat continues until one organism is killed or the prey escapes. If the prey makes a successful escape attempt, they move a number of spots away determined by their Speed attribute before the next "move" begins.

Trials run until we run out of either Predators or Prey. We take the organisms from whichever population has "leftovers" and determine who survives based on their hunger attribute. Hungrier organisms starve either from a depleted Prey population (Predator death) or depletion of scavengable food (Prey death). Unlike the other attributes like Speed and Fortitude which are "genetic," Hunger is calculated/derived from an individual organism's overall attributes. In general, larger, stronger, faster, better at sex = hungrier.

Individual attributes, aside from Hunger, modulate one another (higher Fortitude generally means lower Speed, for example). When an organism is first created, we start with "raw" numbers for all of these attributes and then adjust them to account for these modulations. These raw numbers numbers range from 0-100. Recalculation effects are as follows:

	Speed: Negatively impacted by Fortitude and Power, max negative impact = 10%, max +15 from willpower
		Stealth: Negatively impacted by Fortitude (max = 20%), Positively impacted by Perception (max = 35%)
		Perception: Positively impacted by Willpower (max = 10%)
		Willpower: Positively impacted by Power (max = 20%)
		Fortitude: Negatively impacted by Stealth (max = 20%), Positively impacted by Power (max = 10%)
		Power: Positively impacted by Fortitude (max = 10%), Positively impacted by Speed (max = 10%)
		Virility: Positively impacted by Fortitude


To illustrate, let's take the raw numbers for a hypothetical organism and adjust them.

	Speed: 56
	Willpower: 88
	Perception: 23
	Stealth: 56
	Fortitude: 74
	Power: 34
	Virility: 45

Virility is positively impacted by Fortitude (+15%). Therefore, our final Virility score for this organism would be 45 + int(74 * 0.15).

If, after all adjustments are made, an organism has a NEGATIVE score for any trait they are considered "nonviable" and die in utero.

In each population trial the "limiting reagent" (Predator or Prey) is matched up with one opposing organism each. They all run their trials, then "leftovers" from the larger population go through the Hunger Games. Each one's Hunger attribute is compared to the size of the mismatch between the populations. If the mismatch is greater than the Hunger attribute, the organism starves. In other words, if the Predator population is 2x the size of the Prey population, there is a 100% mismatch between the two (one is 100% larger than the other). All "leftovers" would die in such a scenario. If the mismatch was 150% (1.5x), organisms with Hunger values of 50+ would die.

After the Hunger culls, each surviving organism mates with a certain number of other organisms in their population. The number of mates for a given offspring is determined by their individual virility stat. The number of offspring is determined by the virility stats of BOTH mates. 

At this point, new pairings are made, chase/combat trials ensue, hunger culls follow, mating cycle ... 

Eventually, we hope to evolve apex Predators and apex Prey. Or find some kind of weird equilibrium. We'll see.

To run: python thehunt.py and enter numbers at the prompts. 