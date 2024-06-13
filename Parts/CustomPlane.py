from parapy.geom import *
from parapy.core import *
from math import radians
import numpy as np

class CustomPlane(GeomBase):
    """This custom-made class is designed to put planes at the location of the stringers, depending on the """
    # nr_stringers = Input()
    # chord_1 = Input() #Chord at the left
    # chord_2 = Input() #Chord at the right

    stringer_location_1 = Input() #left
    stringer_location_2 = Input() #right
    width_section = Input() #This is either the width of the centerpiece, the inner wingbox or the outer wingbox
    chord = Input()
    sign = Input() #-1 for centerpiece, 1 for the rest
    start_y = Input() #0 for centerpiece and inner, start_wing_to_kink for outer

    @Attribute #returns the angle in degrees
    def angle_stringer(self):
        alpha = np.arctan((self.stringer_location_1 - self.stringer_location_2) / self.width_section)
        return np.degrees(alpha)

    @Attribute
    def length_stringer(self):
        return self.width_section / np.cos(radians(self.angle_stringer))

    @Part
    def custom_plane(self): #Have to position the middle point of the stringer
        return RectangularSurface(width=0.25 * self.chord, length=self.length_stringer,
                       position=rotate(rotate90(translate(self.position,
                                            'y', self.start_y+
                                                    self.sign*0.5*np.cos(radians(self.angle_stringer))*self.length_stringer,
                                            'x', - self.stringer_location_1 +
                                                    0.5*np.sin(radians(self.angle_stringer))*self.length_stringer),
                                            'y'),'x', self.angle_stringer, deg=True))
    #rotate90(translate(rotate('x', 30, deg=True),
                                                  # self.position, 'y', -0.5*self.width_section,
                                                  #                  'x', - self.root_chord),'y'))

    # @Part
    # def custom_plane(self): #Have to position the middle point of the stringer
    #     return Rectangle(width=0.25 * self.chord, length=self.length_stringer,
    #                    position=rotate(rotate90(translate(self.position,
    #                                         'y', self.start_y+
    #                                                 self.sign*0.5*np.cos(radians(self.angle_stringer))*self.length_stringer,
    #                                         'x', - self.stringer_location_1 +
    #                                                 0.5*np.sin(radians(self.angle_stringer))*self.length_stringer),
    #                                         'y'),'x', self.angle_stringer, deg=True))


    # @Attribute
    # def shape(self):
    #     return self.custom_plane.TopoDS_Shape