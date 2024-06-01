from math import radians, tan, sin, cos
from parapy.geom import *
from parapy.core import *

import numpy as np
from parapy.geom.generic.positioning import VX, VY  # parapy.geom from 1.2.9

class Rib(GeomBase):
    rib_pitch = Input()
    root_chord = Input()
    leading_edge_sweep = Input()
    width_centerpiece = Input()
    span = Input()

    @Attribute
    def half_span(self):
        return self.span / 2

    @Attribute
    def rib_pos(self):
        return np.linspace(0, self.half_span -self.width_centerpiece/2,
                           round(self.rib_pitch * (self.half_span - self.width_centerpiece / 2)) + 1)

    @Attribute
    def LE_length(self):
        return (self.half_span - self.width_centerpiece/2) / cos(radians(self.leading_edge_sweep))

    @Attribute
    def LE_rib_pos(self):
        return np.linspace(0, self.LE_length, round(self.rib_pitch * (self.half_span-self.width_centerpiece/2)) + 1)

    @Part
    def root_rib(self):
        return RectangularSurface(width=2 * self.root_chord, length=0.5*self.root_chord,
                                  position=rotate(translate(self.position, 'y', self.rib_pos[0],
                                                            'x', - self.root_chord),
                                                  self.position.Vx, 90, deg=True))

    @Part
    def tip_rib(self):
        return RectangularSurface(width=2 * self.root_chord, length=0.5*self.root_chord,
                                  position=rotate(translate(self.position, 'y', self.rib_pos[-1],
                                                    'x', - self.root_chord + self.rib_pos[-1] * tan(radians(self.leading_edge_sweep))),
                                                  self.position.Vx, 90, deg=True))

    @Part
    def rib_surfaces(self):
        return RectangularSurface(quantify=len(self.rib_pos), width=2*self.root_chord, length=0.5*self.root_chord,
                                  position=translate(rotate(rotate90(translate(self.position, 'y', self.rib_pos[0],
                                                            'x', - self.root_chord),
                                                  'x'),'y', -self.leading_edge_sweep, deg=True),
                                  'z', -self.LE_rib_pos[child.index]))


# if __name__ == '__main__':
#     from parapy.gui import display
#     obj = Rib()
#     display(obj)
