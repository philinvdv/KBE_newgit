from parapy.geom import *
from parapy.core import *
from math import radians
import math
import numpy as np

class Stringer_Part(GeomBase):
    """This custom-made class is designed to create the L-shaped stringers and put them on the locations as determined
    with the CustomPlane class. The only necessary inputs are the width of the section, the desired width of the
    stringer and the edge/ line at which the stringer needs to be located"""

    width_stringer = Input() # Width of the rectangular surface=stringer. The width is also the height
    #height_stringer = Input(0.10)
    edge_in = Input()  # Input edge. This will probs be a list like the stringer locations in the custom plane class
    up_down = Input() #If the L-stringer is poiting up (lower skin), the value should be +1. If pointing down (upper) then -1
    angle_sign = Input() #1 for all but lower outer
    #angle_y = Input() #this is the angle around the y azis, which depends on the orientation of the wingbox
    fillet_radius = Input(0.02)  # Radius for the fillet

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
        #angle_updown = np.arctan2(self.edge_vector.z, self.edge_vector.y) #- 0.115
        angle_updown = np.arcsin(self.edge_vector.z / self.edge_length)
        #angle_updown = np.arctan((self.end_point.z - self.start_point.z)/(self.end_point.y - self.start_point.y))
        angle_leftright = np.arctan2(self.edge_vector.x, self.edge_vector.y)
        return rotate(rotate(translate(self.position, 'x', mid_point.x,
                                       'y', mid_point.y,
                                       'z',mid_point.z),
                             'x', angle_updown, deg=False),
                            'z', -1*self.angle_sign*angle_leftright, deg=False)#,
               # 'y', self.angle_y, deg = False)


    @Part
    def rectangular_surface(self):
        return RectangularSurface(
            width=self.width_stringer,
            length=self.edge_length,
            position=self.surface_position, hidden=True
        )


    @Attribute #NOT USING THIS ANYMORE
    def surface_position_90(self):  # Position of the rectangular surface
        mid_point = self.start_point + 0.5 * self.edge_vector
        #angle_updown = np.arctan2(self.edge_vector.z, self.edge_vector.y)  # - 0.115
        angle_updown = np.arcsin(self.edge_vector.z / self.edge_length)
        #angle_updown = np.arctan((self.end_point.z - self.start_point.z) / (self.end_point.y - self.start_point.y))
        angle_leftright = np.arctan2(self.edge_vector.x, self.edge_vector.y)
        return rotate90(rotate(rotate(translate(self.position, 'x', mid_point.x - 0.5 * self.width_stringer * np.cos(angle_leftright),
                                                'y', mid_point.y + 0.5 * self.width_stringer * (np.sin(angle_leftright) +self.up_down* np.sin(angle_updown)),
                                                'z', mid_point.z + self.up_down * 0.5 * self.width_stringer * np.cos(angle_updown)),
                             'x', self.angle_sign*angle_updown, deg=False),
                             #   'y', self.angle_y, deg=False),
                      'z', -1* angle_leftright, deg=False), 'y')

    @Part #in the rotated frame, move it along new x and z to get the right positioning
    def rectangular_surface_90(self):
        return RectangularSurface(
            width=self.width_stringer,
            length=self.edge_length,
            position=rotate90(translate(self.surface_position, 'x', - 0.5 * self.width_stringer,
                                        'z', self.up_down * 0.5 * self.width_stringer),
                              'y'),
        hidden=True)

    @Part
    def lofted_stringer(self):
        # Loft between the two profiles to create the L-shaped stringer with a smooth transition
        return Fused(shape_in=self.rectangular_surface, tool=self.rectangular_surface_90)

    # @Part
    # def final_stringer(self):
    #     # Create the final part with fillets applied
    #     return FilletedSolid(built_from=self.lofted_stringer, radius=self.fillet_radius, edge_table=self.lofted_stringer.edges)

    # @Attribute
    # def solid_1(self):
    #     return ExtrudedSolid(self.rectangular_surface, depth=self.width_stringer)
    #
    # @Attribute
    # def solid_2(self):
    #     return ExtrudedSolid(self.rectangular_surface_90, depth=self.width_stringer)
    #
    # @Part
    # def fused_solid(self):
    #     return Fused(shape_in=self.solid_1, tool=self.solid_2)
    #
    # @Part
    # def filleted_solid(self):
    #     return FilletedSolid(built_from=self.fused_solid, radius=self.fillet_radius, edges=[edge for edge in self.fused_solid.edges if edge.length < self.width_stringer])
