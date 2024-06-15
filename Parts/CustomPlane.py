from parapy.geom import *
from parapy.core import *
from math import radians
import numpy as np

class CustomPlane(GeomBase):
    """This custom-made class is designed to put planes at the location of the stringers, depending on the locations
    defined along x at the start and end point. This plane will help to also determine the y and z locations of the
    stringers when these planes are intersected with the skin."""

    stringer_location_1 = Input() #location along x for left
    stringer_location_2 = Input() #location along x for right
    width_section = Input() #This is either the width of the centerpiece, the inner wingbox or the outer wingbox
    chord = Input() #just there to determine the size of the planes
    sign = Input() #-1 for centerpiece (since it is going in the -y direction), 1 for the rest
    start_y = Input() #0 for centerpiece and inner, start_wing_to_kink for outer (since you dont start at y=0)

    @Attribute #returns the angle that the stringer makes in degrees
    def angle_stringer(self):
        alpha = np.arctan((self.stringer_location_1 - self.stringer_location_2) / self.width_section)
        return np.degrees(alpha)

    @Attribute #calculate the length using trigonometry
    def length_stringer(self):
        return self.width_section / np.cos(radians(self.angle_stringer))

    @Part #This makes the anctual custom plane: calculate the position of the stringer(line)
    def custom_plane(self): #Have to position the middle point of the stringer
        return RectangularSurface(width=0.25 * self.chord, length=self.length_stringer,
                       position=rotate(rotate90(translate(self.position,
                                            'y', self.start_y+
                                                    self.sign*0.5*np.cos(radians(self.angle_stringer))*self.length_stringer,
                                            'x', - self.stringer_location_1 +
                                                    0.5*np.sin(radians(self.angle_stringer))*self.length_stringer),
                                            'y'),'x', self.angle_stringer, deg=True))

