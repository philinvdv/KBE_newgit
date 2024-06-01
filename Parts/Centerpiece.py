from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np
from Skins import *

class Centerpiece(GeomBase):
    flange_length_skins = Input(0.02)
    flange_length_spars = Input(0.02)

    # The attributes and inputs from Wing()
    start_wing_to_kink = Input()
    tip_chord_kink = Input()
    pts = Input()
    front_spar_coordinates = Input()
    rear_spar_coordinates = Input()
    span = Input()
    leading_edge_sweep = Input()  # deg
    root_chord = Input()
    twist_angle = Input()
    dihedral_angle = Input()
    wing_material = Input()  # should somehow get the properties from this
    kink_location = Input()  # measured from centerline of fuselage
    tip_chord = Input()
    width_centerpiece = Input()

    """Upper&lower skin pannel centerpiece"""
    @Attribute
    def points_skin_centerpiece(self):  # first four are for upper, last four are for lower
        point_2cp = Point(-0.8 * self.root_chord, -self.width_centerpiece,
                          self.front_spar_coordinates[0][1] * self.root_chord)
        point_3cp = Point(-0.3 * self.root_chord, -self.width_centerpiece,
                          self.rear_spar_coordinates[0][1] * self.root_chord)
        point_2flcp = Point(-0.8 * self.root_chord, -self.width_centerpiece,
                            self.front_spar_coordinates[0][1] * self.root_chord - self.flange_length_skins)
        point_3flcp = Point(-0.3 * self.root_chord, -self.width_centerpiece,
                            self.rear_spar_coordinates[0][1] * self.root_chord - self.flange_length_skins)
        point_2lcp = Point(-0.8 * self.root_chord, -self.width_centerpiece,
                           self.front_spar_coordinates[1][1] * self.root_chord)
        point_3lcp = Point(-0.3 * self.root_chord, -self.width_centerpiece,
                           self.rear_spar_coordinates[1][1] * self.root_chord)
        point_2fllcp = Point(-0.8 * self.root_chord, -self.width_centerpiece,
                             self.front_spar_coordinates[1][1] * self.root_chord + self.flange_length_skins)
        point_3fllcp = Point(-0.3 * self.root_chord, -self.width_centerpiece,
                             self.rear_spar_coordinates[1][1] * self.root_chord + self.flange_length_skins)
        return [point_2cp, point_3cp, point_2flcp, point_3flcp, point_2lcp, point_3lcp, point_2fllcp, point_3fllcp]

    @Part #This line comes from the Skins file
    def line_root_upp(self):
        return LineSegment(start = Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                                                   end=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord)
                         #  position = rotate(XOY, 'x', 90, deg=True)
                           )

    @Part  # Line from Skins file
    def line_root_low(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           end=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord))
                           #  position = rotate(XOY, 'x', 90, deg=True)



    @Part  # Line from upper point of front spar to upper point of rear spar at centerpiece
    def line_root_upp_centerpiece(self):
        return LineSegment(start=self.points_skin_centerpiece[0],
                           end=self.points_skin_centerpiece[1],
                           #  position = rotate(XOY, 'x', 90, deg=True)
                           )

    @Part
    def upperskin_centerpiece_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_upp, self.line_root_upp_centerpiece],
            mesh_deflection=0.0001)

    @Part  # Line from lower point of front spar to lower point of rear spar
    def line_root_low_centerpiece(self):
        return LineSegment(start=self.points_skin_centerpiece[4], end=self.points_skin_centerpiece[5],
                           #  position = rotate(XOY, 'x', 90, deg=True)
                           )

    @Part
    def lowerskin_centerpiece_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_low, self.line_root_low_centerpiece],
            mesh_deflection=0.0001
        )

    """Spars"""
    @Part  # Line for front spar root
    def line_root_front(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           )

    @Part  # Line for front spar at root centerpiece
    def mirror_line_root_front(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, -self.width_centerpiece, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.root_chord, -self.width_centerpiece, self.front_spar_coordinates[1][1] * self.root_chord),
                           )

    @Part #Make the frontspar of the centerpiece
    def frontspar_surf_centerpiece(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_front, self.mirror_line_root_front],
            mesh_deflection=0.0001
        )

    @Part #this is for the rear spar
    def line_root_rear(self):
        return LineSegment(start=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord))

    @Part #Mirror to the left wing (move to Centerpiece()?)
    def mirror_line_root_rear(self):
        return LineSegment(start=Point(-0.3 * self.root_chord, -self.width_centerpiece, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.root_chord, -self.width_centerpiece, self.rear_spar_coordinates[1][1] * self.root_chord))

    @Part #for the rear spar of the centerpiece
    def rearspar_loft_centerpiece(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_rear, self.mirror_line_root_rear],
            mesh_deflection=0.0001
        )