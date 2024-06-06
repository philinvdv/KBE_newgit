from math import radians, tan, cos
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.Skins import *

class Centerpiece(GeomBase):
    flange_length_skins = Input(0.02)
    flange_length_spars = Input(0.02)
    stringer_width_cp = Input(0.02)
    stringer_height_cp = Input(0.02)

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
    rib_pitch_cp = Input(2)

    nr_stringers_upper_inner = Input(4)
    nr_stringers_lower_inner = Input(4)
    nr_stringers_upper_outer = Input(4)
    nr_stringers_lower_outer = Input(4)

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
                                                   end=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord),
                           hidden=True
                         #  position = rotate(XOY, 'x', 90, deg=True)
                           )

    @Part  # Line from Skins file
    def line_root_low(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           end=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord),
                           hidden=True)
                           #  position = rotate(XOY, 'x', 90, deg=True)



    @Part  # Line from upper point of front spar to upper point of rear spar at centerpiece
    def line_root_upp_centerpiece(self):
        return LineSegment(start=self.points_skin_centerpiece[0],
                           end=self.points_skin_centerpiece[1],
                           #  position = rotate(XOY, 'x', 90, deg=True)
                           hidden=True)

    @Part
    def upperskin_centerpiece_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_upp, self.line_root_upp_centerpiece],
            mesh_deflection=0.0001)

    @Part  # Line from lower point of front spar to lower point of rear spar
    def line_root_low_centerpiece(self):
        return LineSegment(start=self.points_skin_centerpiece[4], end=self.points_skin_centerpiece[5],
                           #  position = rotate(XOY, 'x', 90, deg=True)
                           hidden=True)

    @Part
    def lowerskin_centerpiece_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_low, self.line_root_low_centerpiece],
            mesh_deflection=0.0001
        )

    """SPARS"""
    @Part  # Line for front spar root
    def line_root_front(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           hidden=True)

    @Part  # Line for front spar at root centerpiece
    def mirror_line_root_front(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, -self.width_centerpiece, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.root_chord, -self.width_centerpiece, self.front_spar_coordinates[1][1] * self.root_chord),
                           hidden=True)

    @Part #Make the frontspar of the centerpiece
    def frontspar_surf_centerpiece(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_front, self.mirror_line_root_front],
            mesh_deflection=0.0001
        )

    @Part #this is for the rear spar
    def line_root_rear(self):
        return LineSegment(start=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord),
                           hidden=True)

    @Part #Mirror to the left wing (move to Centerpiece()?)
    def mirror_line_root_rear(self):
        return LineSegment(start=Point(-0.3 * self.root_chord, -self.width_centerpiece, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.root_chord, -self.width_centerpiece, self.rear_spar_coordinates[1][1] * self.root_chord),
                           hidden=True)

    @Part #for the rear spar of the centerpiece
    def rearspar_loft_centerpiece(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_rear, self.mirror_line_root_rear],
            mesh_deflection=0.0001
        )

    @Part
    def fused_cp1(self):
        return Fused(shape_in=self.upperskin_centerpiece_loft,
                     tool=self.frontspar_surf_centerpiece, hidden=True)

    @Part
    def fused_cp2(self):
        return Fused(shape_in=self.lowerskin_centerpiece_loft,
                     tool=self.rearspar_loft_centerpiece, hidden=True)

    @Part
    def fused_centerpiece(self):
        return Fused(shape_in=self.fused_cp1,
                     tool=self.fused_cp2)

    """RIBS"""

    @Attribute
    def rib_pos_cp(self):
        return np.linspace(0, -self.width_centerpiece,
                           round(self.rib_pitch_cp * (self.width_centerpiece)) + 1)

    @Part
    def rib_surfaces_cp(self):
        return RectangularSurface(quantify=len(self.rib_pos_cp), width=2 * self.root_chord, length=0.5 * self.root_chord,
                                  position=translate(rotate90(translate(self.position, 'y', self.rib_pos_cp[0],
                                                                               'x', - self.root_chord),
                                                                     'x'),
                                                     'z', -self.rib_pos_cp[child.index]), hidden=True)

    @Part  # This gives the curves of the ribs in the shape of the wingbox
    def intersected_cp(self):
        return IntersectedShapes(quantify=len(self.rib_surfaces_cp),
                                 shape_in=self.fused_centerpiece,
                                 tool=self.rib_surfaces_cp[child.index], hidden=True)

    @Part  # This creates ribs
    def ribs_cp(self):
        return Face(quantify=len(self.intersected_cp),
                    island=self.intersected_cp[child.index].edges)

    """STRINGERS"""
    @Attribute
    def LE_stringer_points_upper_cp(self):
        return np.linspace(0.3 * self.root_chord, 0.8 * self.root_chord, (0.8 * self.root_chord - 0.3 * self.root_chord) / (self.nr_stringers_upper_inner + 1))

    @Attribute
    def kink_stringer_points_upper_cp(self):
        return np.linspace(0.3 * self.tip_chord_kink, 0.8 * self.tip_chord_kink,
                           (0.8 * self.tip_chord_kink - 0.3 * self.tip_chord_kink) / (self.nr_stringers_upper_inner + 1))

    # @Part
    # def box_1_str_cp(self):
    #     return Box(quantify = self.nr_stringers_upper_inner,width = self.stringer_width_cp, height=self.stringer_height_cp,
    #                length=self.width_centerpiece, position=translate('x', self.LE_stringer_points_upper_cp[1] * child.index))

    # @Attribute
    # def right_stringer_points_upper(self):
    #     return np.linspace(0.3 * self.root_chord, 0.8 * self.root_chord,
    #                        (0.8 * self.root_chord - 0.3 * self.root_chord) / (self.nr_stringers_upper + 1))
    #
    # @Part
    # def stringers_upper(self):
    #     return Line(reference=Point(self.right_stringer_points_upper[child.index], 0, 0),
    #                 direction=Vector(0,1,0))
