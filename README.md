#Cargo Lander
==================
This game brings you to a world in the far future, where parcels are delivered by delivery drones ... well, maybe not too far in the future. Ok, ok this is rather in the past. However, your task is to land the parcel drones safely next to the designated recipient. But be aware that time and fuel are limited.

I called the game cargo lander because it is an enhanced clone of the classical game lunar lander.

##prerequisites
==================
Python 2.7
Pygame

To install Pygame use `apt-get install python-pygame` under Debian or `pip install pygame` on some other systems.

##How does it work
==================
Just start game.py and see for yourself. In the start screen you can hold TAB for help with the controls.

In some more detail:
	1. Try to land you drone safely (green indicator light)
	2. Try to land your drone on the correct platform (color-coded)
	3. Try to make as many points as possible within the given time

Challenges:
	* Time
	* More than one drone (by hitting SPACE)
	* only 4 lives (don't crash into other drones or hit the ground too hard)
	* limited fuel (green/yellow/red indicator bar)