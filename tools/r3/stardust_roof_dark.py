"""The Stardust roof with the sign off (Case 3, scene 4, before the breaker): the same set as stardust_roof.py, lit
only by the stairwell behind Ray, the city's glow and the Blue Note two roofs over. Two hotspots: the darkness and
the door back down."""
import stardust_roof


def build(hide=()):
    return stardust_roof.build(hide, dark=True)
