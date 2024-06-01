from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.Meshing import MeshingFunc


class Skins(GeomBase):
    """In this class, the different skin pannels are defined. This is done from different curves, formig rectangles,
    forming curves, forming lofts. For upper and lower inner and upper and lower outer"""
    # Define the points for the lines
    length_flanges = Input(0.02)

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

    """Upper skin pannel inner"""
    @Attribute
    def points_root_upper_skin(self):
        point_2 = Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord)
        point_3 = Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord)
        point_2fl = Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord - self.length_flanges)
        point_3fl = Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord - self.length_flanges)
        return [point_2, point_3, point_2fl, point_3fl] #[point_1, point_2, point_3, point_4]

    @Part #Line from upper point of front spar to upper point of rear spar
    def line_root_upp(self):
        return LineSegment(start=self.points_root_upper_skin[0], end=self.points_root_upper_skin[1],
                    hidden=True)
                         #  position = rotate(XOY, 'x', 90, deg=True)


    """At kink, upper inner"""
    @Attribute
    def points_kink_upper_skin(self):
        point2 = Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink)
        point3 = Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink, self.rear_spar_coordinates[0][1] * self.tip_chord_kink)
        point2fl = Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink,
                       self.front_spar_coordinates[0][1] * self.tip_chord_kink - self.length_flanges)
        point3fl = Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                       self.rear_spar_coordinates[0][1] * self.tip_chord_kink - self.length_flanges)
        return [point2, point3, point2fl, point3fl]

    @Part  # Line from upper point of front spar to upper point of rear spar
    def line_kink_upp(self):
        return LineSegment(start=self.points_kink_upper_skin[0], end=self.points_kink_upper_skin[1],
                           position=rotate(XOY, 'x', 90, deg=True),
                    hidden=True)

    @Part
    def inner_upperskin_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_upp, self.line_kink_upp],
            mesh_deflection=0.0001,
                    hidden=True)
    """Lower skin panel inner"""
    @Attribute
    def points_root_lower_skin(self):
        # point_1 = Point(0,0,0)
        point_2l = Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord)
        point_3l = Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord)
        point_2fl = Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord + self.length_flanges)
        point_3fl = Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord + self.length_flanges)
        return [point_2l, point_3l, point_2fl, point_3fl]

    # Define four separate lines
    @Part  # Line from upper point of front spar to upper point of rear spar
    def line_root_low(self):
        return LineSegment(start=self.points_root_lower_skin[0], end=self.points_root_lower_skin[1],
                    hidden=True)
                           #  position = rotate(XOY, 'x', 90, deg=True)


    """At kink, lower pannel inner"""
    @Attribute
    def points_kink_lower_skin(self):
        point2l = Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink,
                       self.front_spar_coordinates[1][1] * self.tip_chord_kink)
        point3l = Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                       self.rear_spar_coordinates[1][1] * self.tip_chord_kink)
        point2_fl = Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink,
                        self.front_spar_coordinates[1][1] * self.tip_chord_kink + self.length_flanges)
        point3_fl = Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                        self.rear_spar_coordinates[1][1] * self.tip_chord_kink + self.length_flanges)
        return [point2l, point3l, point2_fl, point3_fl]

    #Define four separate lines
    @Part  # Line from upper point of front spar to upper point of rear spar
    def line_kink_low(self):
        return LineSegment(start=self.points_kink_lower_skin[0], end=self.points_kink_lower_skin[1],
                           position=rotate(XOY, 'x', 90, deg=True),
                    hidden=True)

    @Part
    def inner_lowerskin_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_low, self.line_kink_low],
            mesh_deflection=0.0001,
                    hidden=True)

    """Outer skin panels, tip"""
    @Attribute
    def points_tip_upper_skin(self):
        # point_1 = Point(0,0,0)
        point_2t = Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord-0.8 * self.tip_chord,
                         self.span/2 - self.width_centerpiece/2,
                         self.front_spar_coordinates[0][1] * self.tip_chord)
        point_3t = Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord-0.3 * self.tip_chord,
                         self.span/2 - self.width_centerpiece/2, self.rear_spar_coordinates[0][1] * self.tip_chord)
        point_2_fl = Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord-0.8 * self.tip_chord,
                         self.span/2 - self.width_centerpiece/2,
                         self.front_spar_coordinates[0][1] * self.tip_chord - self.length_flanges)
        point_3_fl = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.3 * self.tip_chord,
                         self.span / 2 - self.width_centerpiece / 2, self.rear_spar_coordinates[0][1] * self.tip_chord -self.length_flanges)
        return [point_2t, point_3t, point_2_fl, point_3_fl]

    # Define four separate lines
    @Part  # Line from upper point of front spar to upper point of rear spar
    def line_tip_upp(self):
        return LineSegment(start=self.points_tip_upper_skin[0], end=self.points_tip_upper_skin[1],
                    hidden=True)
                           #  position = rotate(XOY, 'x', 90, deg=True)

    #At the kink it already exists, take that one from previously
    @Part
    def outer_upperskin_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_kink_upp, self.line_tip_upp],
            mesh_deflection=0.0001,
                    hidden=True)

    """Lower skin panel outer"""
    @Attribute
    def points_tip_lower_skin(self):
        # point_1 = Point(0,0,0)
        point_2lt = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.8 * self.tip_chord,
                          self.span/2 - self.width_centerpiece/2, self.front_spar_coordinates[1][1] * self.tip_chord)

        point_3lt = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.3 * self.tip_chord,
                          self.span/2 - self.width_centerpiece/2, self.rear_spar_coordinates[1][1] * self.tip_chord)
        point_2lt_fl = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.8 * self.tip_chord,
                          self.span / 2 - self.width_centerpiece / 2,
                          self.front_spar_coordinates[1][1] * self.tip_chord + self.length_flanges)

        point_3lt_fl = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.3 * self.tip_chord,
                          self.span / 2 - self.width_centerpiece / 2, self.rear_spar_coordinates[1][1] * self.tip_chord + self.length_flanges)
        return [point_2lt, point_3lt, point_2lt_fl, point_3lt_fl]

    # Define four separate lines
    @Part  # Line from upper point of front spar to upper point of rear spar
    def line_tip_low(self):
        return LineSegment(start=self.points_tip_lower_skin[0], end=self.points_tip_lower_skin[1],
                    hidden=True)

    @Part #Again, kink exists already
    def outer_lowerskin_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_tip_low, self.line_kink_low],
            mesh_deflection=0.0001,
                    hidden=True)

    """Flanges"""
    @Part  # flange for upper skin inner along frontspar
    def flange_upperskin_inner_front(self):
        return LoftedSurface(
            profiles=[LineSegment(start=self.points_root_upper_skin[2], end=self.points_kink_upper_skin[2]),
                      LineSegment(start=self.points_root_upper_skin[0], end=self.points_kink_upper_skin[0])],
                    hidden=True)

    @Part  # flange for upper skin inner along rearspar
    def flange_upperskin_inner_rear(self):
        return LoftedSurface(
            profiles=[LineSegment(start=self.points_root_upper_skin[3], end=self.points_kink_upper_skin[3]),
                      LineSegment(start=self.points_root_upper_skin[1], end=self.points_kink_upper_skin[1])],
                    hidden=True)

    @Part  # flange for lower skin inner along frontspar
    def flange_lowerskin_inner_front(self):
        return LoftedSurface(
            profiles=[LineSegment(start=self.points_root_lower_skin[2], end=self.points_kink_lower_skin[2]),
                      LineSegment(start=self.points_root_lower_skin[0], end=self.points_kink_lower_skin[0])],
                    hidden=True)

    @Part  # flange for lower skin inner along rearspar
    def flange_lowerskin_inner_rear(self):
        return LoftedSurface(
            profiles=[LineSegment(start=self.points_root_lower_skin[3], end=self.points_kink_lower_skin[3]),
                      LineSegment(start=self.points_root_lower_skin[1], end=self.points_kink_lower_skin[1])],
                    hidden=True)

    @Part  # flange for lower skin outer along frontspar
    def flange_lowerskin_outer_front(self):
        return LoftedSurface(
            profiles=[LineSegment(start=self.points_tip_lower_skin[2], end=self.points_kink_lower_skin[2]),
                      LineSegment(start=self.points_tip_lower_skin[0], end=self.points_kink_lower_skin[0])],
                    hidden=True)

    @Part  # flange for lower skin outer along rearspar
    def flange_lowerskin_outer_rear(self):
        return LoftedSurface(
            profiles=[LineSegment(start=self.points_tip_lower_skin[3], end=self.points_kink_lower_skin[3]),
                      LineSegment(start=self.points_tip_lower_skin[1], end=self.points_kink_lower_skin[1])],
                    hidden=True)

    @Part  # flange for upper skin outer along frontspar
    def flange_upperskin_outer_front(self):
        return LoftedSurface(
            profiles=[LineSegment(start=self.points_tip_upper_skin[2], end=self.points_kink_upper_skin[2]),
                      LineSegment(start=self.points_tip_upper_skin[0], end=self.points_kink_upper_skin[0])],
                    hidden=True)

    @Part  # flange for upper skin outer along rearspar
    def flange_upperskin_outer_rear(self):
        return LoftedSurface(
            profiles=[LineSegment(start=self.points_tip_upper_skin[3], end=self.points_kink_upper_skin[3]),
                      LineSegment(start=self.points_tip_upper_skin[1], end=self.points_kink_upper_skin[1])],
                    hidden=True)

    @Part
    def fused_inner_upperskin_and_flanges(self):
        return Fused(shape_in=self.inner_upperskin_loft,
                          tool = (self.flange_upperskin_inner_rear, self.flange_upperskin_inner_front))

    @Part
    def fused_inner_lowerskin_and_flanges(self):
        return Fused(shape_in=self.inner_lowerskin_loft,
                          tool = (self.flange_lowerskin_inner_rear, self.flange_lowerskin_inner_front))

    @Part
    def fused_outer_upperskin_and_flanges(self):
        return Fused(shape_in=self.outer_upperskin_loft,
                          tool = (self.flange_upperskin_outer_rear, self.flange_upperskin_outer_front))

    @Part
    def fused_outer_lowerskin_and_flanges(self):
        return Fused(shape_in=self.outer_lowerskin_loft,
                          tool = (self.flange_lowerskin_outer_rear, self.flange_lowerskin_outer_front))
    # @Part
    # def mesh_fused_inner_upper_skin(self):
    #     return MeshingFunc(part_class=self.fused_inner_upperskin_and_flanges, n_mesh_points=50)
    #
    # @Part
    # def mesh_fused_inner_lower_skin(self):
    #     return MeshingFunc(part_class=self.fused_inner_lowerskin_and_flanges, n_mesh_points=50)
    #
    # @Part
    # def mesh_fused_outer_upper_skin(self):
    #     return MeshingFunc(part_class=self.fused_outer_upperskin_and_flanges, n_mesh_points=50)
    #
    # @Part
    # def mesh_fused_outer_lower_skin(self):
    #     return MeshingFunc(part_class=self.fused_outer_lowerskin_and_flanges, n_mesh_points=50)



