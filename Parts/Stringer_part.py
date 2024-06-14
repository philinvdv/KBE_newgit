from parapy.geom import *
from parapy.core import *
from math import radians
import numpy as np

class Stringer_Part(GeomBase):
    """This custom-made class is designed to create the L-shaped stringers and put them on the locations as determined
    with the CustomPlane class. The only necessary inputs are the width of the section, the desired width of the
    stringer and the edge/ line at which the stringer needs to be located"""

    width_stringer = Input(0.1) # Width of the rectangular surface=stringer. The width is also the height
    #height_stringer = Input(0.10)
    edge_in = Input()  # Input edge. This will probs be a list like the stringer locations in the custom plane class
    up_down = Input() #If the L-stringer is poiting up, the value should be +1. If pointing down then -1

    @Attribute
    def start_point(self): #Start point of the edge
        return self.edge_in.start

    @Attribute
    def end_point(self): #End point of the edge
        return self.edge_in.end

    @Attribute
    def edge_vector(self): #Vector representing the direction of the edge
        return self.end_point - self.start_point

    @Attribute
    def edge_length(self): #Length of the edge
        return self.edge_vector.length


    @Attribute
    def surface_position(self): #Position of the rectangular surface
        mid_point = self.start_point + 0.5 * self.edge_vector
        angle_updown = np.arctan2(self.edge_vector.z, self.edge_vector.x) #- 0.115
        angle_leftright = np.arctan2(self.edge_vector.x, self.edge_vector.y)
        return rotate(rotate(translate(self.position, 'x', mid_point.x,
                                       'y', mid_point.y,
                                       'z', mid_point.z),
                             'y', angle_updown, deg=False),
                            'z', -angle_leftright, deg=False)


    @Part
    def rectangular_surface(self):
        return RectangularSurface(
            width=self.width_stringer,
            length=self.edge_length,
            position=self.surface_position
        )

    @Attribute
    def surface_position_90(self):  # Position of the rectangular surface
        mid_point = self.start_point + 0.5 * self.edge_vector
        angle_updown = np.arctan2(self.edge_vector.z, self.edge_vector.x)  # - 0.115
        angle_leftright = np.arctan2(self.edge_vector.x, self.edge_vector.y)
        return rotate90(rotate(rotate(translate(self.position, 'x', mid_point.x - 0.5 * self.width_stringer,
                                                'y', mid_point.y,
                                                'z', mid_point.z + self.up_down * 0.5 * self.width_stringer),
                             'y', angle_updown, deg=False),
                      'z', -angle_leftright, deg=False), 'y')

    @Part
    def rectangular_surface_90(self):
        return RectangularSurface(
            width=self.width_stringer,
            length=self.edge_length,
            position=self.surface_position_90
        )
