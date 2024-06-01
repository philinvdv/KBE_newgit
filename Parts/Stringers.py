from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np

class Stringer(GeomBase):
    """In this class, the stringers are defined as well as their locations. You can have a different amount of stringers
    for the inner and outer wingbox, as well as for the upper and lower panels."""
    nr_stringers_upper_inner = Input()
    nr_stringers_lower_inner = Input()
    nr_stringers_upper_outer = Input()
    nr_stringers_lower_outer = Input()
    root_chord = Input()

    @Attribute
    def points(self):
        #Location of wingbox at the root is -0.3 *root_chord to -0.8 * root_chord
        spacing_upper_inner = (0.8 * self.root_chord - 0.3 * self.root_chord) / (self.nr_stringers_upper_inner + 1) #stringers are this much apart
        root_upper_pts = Point(-0.3 * self.root_chord + child.index *  spacing_upper_inner,#x
            0, #y
        0) #z