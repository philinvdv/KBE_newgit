from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np

class Stringer(GeomBase):
    """In this class, the stringers are defined as well as their locations. You can have a different amount of stringers
    for the inner and outer wingbox, as well as for the upper and lower panels."""
    nr_stringers_upper_inner = Input(4)
    nr_stringers_lower_inner = Input(4)
    nr_stringers_upper_outer = Input(4)
    nr_stringers_lower_outer = Input(4)
    stringer_width = Input(0.02)
    stringers_height = Input(0.02)

    tip_chord_kink = Input()
    span = Input()
    leading_edge_sweep = Input()  # deg
    root_chord = Input()
    kink_location = Input()  # measured from centerline of fuselage
    tip_chord = Input()
    width_centerpiece = Input()

    @Attribute
    def start_wing_to_kink(self):
        return self.kink_location - self.width_centerpiece / 2

    @Attribute
    def points(self):
        #Location of wingbox at the root is -0.3 *root_chord to -0.8 * root_chord
        spacing_root_upper_inner = (0.8 * self.root_chord - 0.3 * self.root_chord) / (self.nr_stringers_upper_inner + 1) #stringers are this much apart
        root_upper_pts = Point(-0.3 * self.root_chord + child.index *  spacing_root_upper_inner,#x
            0, #y
        0) #z

    @Attribute
    def LE_stringer_points_upper(self):
        return np.linspace(0.3 * self.root_chord, 0.8 * self.root_chord, (0.8 * self.root_chord - 0.3 * self.root_chord) / (self.nr_stringers_upper_inner + 1))

    @Attribute
    def kink_stringer_points_upper(self):
        return np.linspace(0.3 * self.tip_chord_kink, 0.8 * self.tip_chord_kink,
                           (0.8 * self.tip_chord_kink - 0.3 * self.tip_chord_kink) / (self.nr_stringers_upper_inner + 1))

    # @Part
    # def lines_upper_inner(self):
    #     return RectangularSurface(quantify=len(self.LE_stringer_points_upper), width=self.stringer_width,
    #                               position=translate(rotate(rotate90(translate(self.position, 'y', self.rib_pos[0],
    #                                                                            'x', - self.root_chord),
    #                                                                  'x'), 'y', -self.leading_edge_sweep, deg=True),
    #                                                  'z', -self.LE_rib_pos[child.index]))

    # @Part
    # def lines_upper_inner(self):
    #     return Rectangle(quantity=len(self.LE_stringer_points_upper),
    #         start=Point(self.LE_stringer_points_upper[child.index], 0, 0),
    #                        end=Point(self.kink_stringer_points_upper[child.index], self.start_wing_to_kink, 0))

    @Attribute
    def stringer_lines(self):
        le_points = self.LE_stringer_points_upper
        kink_points = self.kink_stringer_points_upper
        lines = []
        for le, kink in zip(le_points, kink_points):
            line = Line(start=Point(le, 0, 0), end=Point(kink, 1, 0))  # Adjust y, z coordinates as needed
            lines.append(line)
        return lines

    # @Part
    # def LE_points_stringers(self):
    #     return Point(self.LE_stringer_points_upper[child.index], 0, 0
    #     ) #change y
    # #
    # @Attribute
    # def stringer_pos(self):
    #     return np.linspace(0, self.LE_length, round(self.rib_pitch * (self.half_span-self.width_centerpiece/2)) + 1)
