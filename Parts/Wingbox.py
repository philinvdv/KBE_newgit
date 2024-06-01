from math import radians, tan, cos
from parapy.geom import *
from parapy.core import *
import numpy as np
from Meshing import *

class Wingbox(GeomBase):
    """This class contains the spar geometry, for the front and rear spar of the inner and outer wingbox."""
    thickness_flange = Input(0.02) #m for spars
    length_flanges = Input(0.02) #for skins
    #The attributes and inputs from Wing() (thus inherited)
    start_wing_to_kink = Input()
    tip_chord_kink = Input()
    pts = Input()
    front_spar_coordinates =Input()
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
    hide_mesh = Input(True)
    # Define the points for the lines

    rib_pitch = Input()


    """SPARS"""

    """Front spar inner"""
    @Part  # Line for front spar at root NEW
    def line_root_front(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           )

    #Moved this to Centerpiece class
    # @Part  # Line for front spar at root centerpiece NEW
    # def mirror_line_root_front(self):
    #     return LineSegment(start=Point(-0.8 * self.root_chord, -self.width_centerpiece, self.front_spar_coordinates[0][1] * self.root_chord),
    #                        end=Point(-0.8 * self.root_chord, -self.width_centerpiece, self.front_spar_coordinates[1][1] * self.root_chord),
    #                        )
    #
    # @Part #Make the frontspar of the centerpiece
    # def frontspar_surf_centerpiece(self):  # generate a surface
    #     return LoftedSurface(
    #         profiles=[self.line_root_front, self.mirror_line_root_front],
    #         mesh_deflection=0.0001
    #     )

    @Part  # Line for front spar at kink NEW
    def line_kink_front(self):
        return LineSegment(start=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink),
                           end=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[1][1] * self.tip_chord_kink),
                           )

    @Part
    def front_spar_inner(self):
        return LoftedSurface(
            profiles=[self.line_root_front, self.line_kink_front],
            mesh_deflection=0.0001
        )

    """Rear spar inner"""
    @Part #this part is the rectangle at the root chord for the rear spar
    def line_root_rear(self):
        return LineSegment(start=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord))

    #Moved to Centerpiece class
    # @Part #Mirror to the left wing (move to Centerpiece()?)
    # def mirror_line_root_rear(self):
    #     return LineSegment(start=Point(-0.3 * self.root_chord, -self.width_centerpiece, self.rear_spar_coordinates[0][1] * self.root_chord),
    #                        end=Point(-0.3 * self.root_chord, -self.width_centerpiece, self.rear_spar_coordinates[1][1] * self.root_chord))
    #
    # @Part #for the rear spar of the centerpiece
    # def rearspar_loft_centerpiece(self):  # generate a surface
    #     return LoftedSurface(
    #         profiles=[self.line_root_rear, self.mirror_line_root_rear],
    #         mesh_deflection=0.0001
    #     )

    @Part
    def line_kink_rear(self):
        return LineSegment(start=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink, self.rear_spar_coordinates[0][1] * self.tip_chord_kink),
                           end=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink, self.rear_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def rearspar_inner(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_rear, self.line_kink_rear],
            mesh_deflection=0.0001
        )

    """Front spar outer section"""
    @Part  # this part is the line at the tip chord for the for spar
    def line_tip_front(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.front_spar_coordinates[0][1] * self.tip_chord), #z
                           end=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.front_spar_coordinates[1][1] * self.tip_chord)) #z

    @Part
    def frontspar_outer(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_kink_front, self.line_tip_front],
            mesh_deflection=0.0001
        )

    # """Rear spar outer section"""
    # @Part  # this part is the line at the tip chord for the rear spar
    # def line_tip_rear(self):
    #     return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
    #                                         -0.3 * self.tip_chord, #x
    #                                    self.span/2 - self.width_centerpiece/2, #y
    #                                    self.rear_spar_coordinates[0][1] * self.tip_chord), #z
    #                        end=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
    #                                         -0.3 * self.tip_chord, #x
    #                                    self.span/2 - self.width_centerpiece/2, #y
    #                                    self.rear_spar_coordinates[1][1] * self.tip_chord)) #z
    #
    #
    # @Part
    # def rearspar_outer(self):  # generate a surface
    #     return LoftedSurface(
    #         profiles=[self.line_kink_rear, self.line_tip_rear],
    #         mesh_deflection=0.0001
    #     )

    """Rear spar outer section"""
    @Part  # this part is the line at the tip chord for the rear spar
    def line_tip_rear(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.rear_spar_coordinates[0][1] * self.tip_chord), #z
                           end=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.rear_spar_coordinates[1][1] * self.tip_chord)) #z


    @Part
    def rearspar_outer(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_kink_rear, self.line_tip_rear],
            mesh_deflection=0.0001
        )


    """Flanges, inner""" #use the same, but translated along the chord. 1 is the line moved to the side along the chord, 2 along skin
    @Part
    def flangeline1_front_upper_inner(self): #flang of the front spar, upper inner
        return LineSegment(start=Point(-0.8 * self.root_chord - self.thickness_flange, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.tip_chord_kink - self.thickness_flange, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flangeline2_front_upper_inner(self): #flang of the front spar, upper inner
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flange_front_upper_inner(self):
        return LoftedSurface(
            profiles=[self.flangeline1_front_upper_inner, self.flangeline2_front_upper_inner],
            mesh_deflection=0.0001
        )

    @Part
    def flangeline1_front_lower_inner(self): #flange for the frontspar, lower part inner box
        return LineSegment(start=Point(-0.8 * self.root_chord - self.thickness_flange, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           end=Point(-0.8 * self.tip_chord_kink - self.thickness_flange, self.start_wing_to_kink, self.front_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flangeline2_front_lower_inner(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           end=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flange_front_lower_inner(self):
        return LoftedSurface(
            profiles=[self.flangeline1_front_lower_inner, self.flangeline2_front_lower_inner],
            mesh_deflection=0.0001
        )

    @Part #For rearspar, upper inner
    def flangeline1_rear_upper_inner(self):
        return LineSegment(start=Point(-0.3 * self.root_chord + self.thickness_flange, 0, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.tip_chord_kink + self.thickness_flange, self.start_wing_to_kink,
                                       self.rear_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flangeline2_rear_upper_inner(self):
        return LineSegment(start=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flange_front_rear_upper_inner(self):
        return LoftedSurface(
            profiles=[self.flangeline1_rear_upper_inner, self.flangeline2_rear_upper_inner],
            mesh_deflection=0.0001
        )

    @Part #For rearspar, lower inner
    def flangeline1_rear_lower_inner(self):
        return LineSegment(start=Point(-0.3 * self.root_chord + self.thickness_flange, 0, self.rear_spar_coordinates[1][1] * self.root_chord),
                           end=Point(-0.3 * self.tip_chord_kink + self.thickness_flange, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flangeline2_rear_lower_inner(self):
        return LineSegment(start=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord),
                           end=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flange_front_rear_lower_inner(self):
        return LoftedSurface(
            profiles=[self.flangeline1_rear_lower_inner, self.flangeline2_rear_lower_inner],
            mesh_deflection=0.0001
        )



    """Flanges, outer"""
    @Part
    def flangeline1_front_upper_outer(self):  # flang of the front spar, upper outer
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord - self.thickness_flange, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.front_spar_coordinates[0][1] * self.tip_chord),
                           end=Point(-0.8 * self.tip_chord_kink - self.thickness_flange, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flangeline2_front_upper_outer(self):  # flang of the front spar, upper inner
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.front_spar_coordinates[0][1] * self.tip_chord),
                           end=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink))


    @Part
    def flange_front_upper_outer(self):
        return LoftedSurface(
            profiles=[self.flangeline1_front_upper_outer, self.flangeline2_front_upper_outer],
            mesh_deflection=0.0001
        )

    @Part
    def flangeline1_front_lower_outer(self):  # flange for the frontspar, lower part outer box
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord - self.thickness_flange, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.front_spar_coordinates[1][1] * self.tip_chord),
                           end=Point(-0.8 * self.tip_chord_kink - self.thickness_flange, self.start_wing_to_kink, self.front_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flangeline2_front_lower_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.front_spar_coordinates[1][1] * self.tip_chord),
                           end=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flange_front_lower_outer(self):
        return LoftedSurface(
            profiles=[self.flangeline1_front_lower_outer, self.flangeline2_front_lower_outer],
            mesh_deflection=0.0001
        )


    """REARSPAR UPPER OUTER"""

    @Part  # For rearspar, upper outer
    def flangeline1_rear_upper_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord + self.thickness_flange, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.rear_spar_coordinates[0][1] * self.tip_chord),
                           end=Point(-0.3 * self.tip_chord_kink + self.thickness_flange, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flangeline2_rear_upper_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.rear_spar_coordinates[0][1] * self.tip_chord),
                           end=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flange_rear_upper_outer(self):
        return LoftedSurface(
            profiles=[self.flangeline1_rear_upper_outer, self.flangeline2_rear_upper_outer],
            mesh_deflection=0.0001
        )

    @Part  # For rearspar, lower outer
    def flangeline1_rear_lower_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord + self.thickness_flange, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.rear_spar_coordinates[1][1] * self.tip_chord),
                           end=Point(-0.3 * self.tip_chord_kink + self.thickness_flange, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flangeline2_rear_lower_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece/2, #y
                                       self.rear_spar_coordinates[1][1] * self.tip_chord),
                           end=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flange_rear_lower_outer(self):
        return LoftedSurface(
            profiles=[self.flangeline1_rear_lower_outer, self.flangeline2_rear_lower_outer],
            mesh_deflection=0.0001
        )


    #What i need to get a wingbox:
    #front_spar_inner, rearspar_inner, frontspar_outer, rearspar_outer


    # """Meshes"""
    # @Part
    # def mesh_front_spar_inner(self):
    #     return MeshingFunc(part_class=self.my_spars.front_spar_inner, n_mesh_points=50, hidden=True)
    #
    # @Part
    # def mesh_front_spar_outer(self):
    #     return MeshingFunc(part_class=self.my_spars.frontspar_outer, n_mesh_points=50, hidden=True)
    #
    # @Part
    # def mesh_rear_spar_inner(self):
    #     return MeshingFunc(part_class=self.my_spars.rearspar_inner, n_mesh_points=50, hidden=True)
    #
    # @Part
    # def mesh_rear_spar_outer(self):
    #     return MeshingFunc(part_class=self.my_spars.rearspar_outer, n_mesh_points=50, hidden=True)


    """SKINS"""

    """Upper skin pannel inner"""

    @Attribute
    def points_root_upper_skin(self):
        point_2 = Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord)
        point_3 = Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord)
        point_2fl = Point(-0.8 * self.root_chord, 0,
                          self.front_spar_coordinates[0][1] * self.root_chord - self.length_flanges)
        point_3fl = Point(-0.3 * self.root_chord, 0,
                          self.rear_spar_coordinates[0][1] * self.root_chord - self.length_flanges)
        return [point_2, point_3, point_2fl, point_3fl]  # [point_1, point_2, point_3, point_4]

    @Part  # Line from upper point of front spar to upper point of rear spar
    def line_root_upp(self):
        return LineSegment(start=self.points_root_upper_skin[0], end=self.points_root_upper_skin[1],
                           hidden=True)
        #  position = rotate(XOY, 'x', 90, deg=True)

    """At kink, upper inner"""

    @Attribute
    def points_kink_upper_skin(self):
        point2 = Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink,
                       self.front_spar_coordinates[0][1] * self.tip_chord_kink)
        point3 = Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                       self.rear_spar_coordinates[0][1] * self.tip_chord_kink)
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
        point_2fl = Point(-0.8 * self.root_chord, 0,
                          self.front_spar_coordinates[1][1] * self.root_chord + self.length_flanges)
        point_3fl = Point(-0.3 * self.root_chord, 0,
                          self.rear_spar_coordinates[1][1] * self.root_chord + self.length_flanges)
        return [point_2l, point_3l, point_2fl, point_3fl]

    @Part  # Line from lower point of front spar to lower point of rear spar
    def line_root_low(self):
        return LineSegment(start=self.points_root_lower_skin[0], end=self.points_root_lower_skin[1])  # ,
        # hidden=True)
        #  position = rotate(XOY, 'x', 90, deg=True)

    """Upper&lower skin pannel centerpiece"""

    @Attribute
    def points_skin_centerpiece(self):  # first four are for upper, last four are for lower
        point_2cp = Point(-0.8 * self.root_chord, -self.width_centerpiece,
                          self.front_spar_coordinates[0][1] * self.root_chord)
        point_3cp = Point(-0.3 * self.root_chord, -self.width_centerpiece,
                          self.rear_spar_coordinates[0][1] * self.root_chord)
        point_2flcp = Point(-0.8 * self.root_chord, -self.width_centerpiece,
                            self.front_spar_coordinates[0][1] * self.root_chord - self.length_flanges)
        point_3flcp = Point(-0.3 * self.root_chord, -self.width_centerpiece,
                            self.rear_spar_coordinates[0][1] * self.root_chord - self.length_flanges)
        point_2lcp = Point(-0.8 * self.root_chord, -self.width_centerpiece,
                           self.front_spar_coordinates[1][1] * self.root_chord)
        point_3lcp = Point(-0.3 * self.root_chord, -self.width_centerpiece,
                           self.rear_spar_coordinates[1][1] * self.root_chord)
        point_2fllcp = Point(-0.8 * self.root_chord, -self.width_centerpiece,
                             self.front_spar_coordinates[1][1] * self.root_chord + self.length_flanges)
        point_3fllcp = Point(-0.3 * self.root_chord, -self.width_centerpiece,
                             self.rear_spar_coordinates[1][1] * self.root_chord + self.length_flanges)
        return [point_2cp, point_3cp, point_2flcp, point_3flcp, point_2lcp, point_3lcp, point_2fllcp, point_3fllcp]

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

    # Define four separate lines
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
        point_2t = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.8 * self.tip_chord,
                         self.span / 2 - self.width_centerpiece / 2,
                         self.front_spar_coordinates[0][1] * self.tip_chord)
        point_3t = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.3 * self.tip_chord,
                         self.span / 2 - self.width_centerpiece / 2, self.rear_spar_coordinates[0][1] * self.tip_chord)
        point_2_fl = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.8 * self.tip_chord,
                           self.span / 2 - self.width_centerpiece / 2,
                           self.front_spar_coordinates[0][1] * self.tip_chord - self.length_flanges)
        point_3_fl = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.3 * self.tip_chord,
                           self.span / 2 - self.width_centerpiece / 2,
                           self.rear_spar_coordinates[0][1] * self.tip_chord - self.length_flanges)
        return [point_2t, point_3t, point_2_fl, point_3_fl]

    # Define four separate lines
    @Part  # Line from upper point of front spar to upper point of rear spar
    def line_tip_upp(self):
        return LineSegment(start=self.points_tip_upper_skin[0], end=self.points_tip_upper_skin[1],
                           hidden=True)
        #  position = rotate(XOY, 'x', 90, deg=True)

    # At the kink it already exists, take that one from previously
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
        point_2lt = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.8 * self.tip_chord,
                          self.span / 2 - self.width_centerpiece / 2,
                          self.front_spar_coordinates[1][1] * self.tip_chord)

        point_3lt = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.3 * self.tip_chord,
                          self.span / 2 - self.width_centerpiece / 2, self.rear_spar_coordinates[1][1] * self.tip_chord)
        point_2lt_fl = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.8 * self.tip_chord,
                             self.span / 2 - self.width_centerpiece / 2,
                             self.front_spar_coordinates[1][1] * self.tip_chord + self.length_flanges)

        point_3lt_fl = Point((self.span / 2 - self.width_centerpiece / 2) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord - 0.3 * self.tip_chord,
                             self.span / 2 - self.width_centerpiece / 2,
                             self.rear_spar_coordinates[1][1] * self.tip_chord + self.length_flanges)
        return [point_2lt, point_3lt, point_2lt_fl, point_3lt_fl]

    # Define four separate lines
    @Part  # Line from upper point of front spar to upper point of rear spar
    def line_tip_low(self):
        return LineSegment(start=self.points_tip_lower_skin[0], end=self.points_tip_lower_skin[1],
                           hidden=True)

    @Part  # Again, kink exists already
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

    # Fused with flanges
    @Part
    def fused_inner_upperskin_and_flanges(self):
        return Fused(shape_in=self.inner_upperskin_loft,
                     tool=(self.flange_upperskin_inner_rear, self.flange_upperskin_inner_front))

    @Part
    def fused_inner_lowerskin_and_flanges(self):
        return Fused(shape_in=self.inner_lowerskin_loft,
                     tool=(self.flange_lowerskin_inner_rear, self.flange_lowerskin_inner_front))

    @Part
    def fused_outer_upperskin_and_flanges(self):
        return Fused(shape_in=self.outer_upperskin_loft,
                     tool=(self.flange_upperskin_outer_rear, self.flange_upperskin_outer_front))

    @Part
    def fused_outer_lowerskin_and_flanges(self):
        return Fused(shape_in=self.outer_lowerskin_loft,
                     tool=(self.flange_lowerskin_outer_rear, self.flange_lowerskin_outer_front))

    @Part
    def fused_wingbox_inner(self):
        return Fused(shape_in=self.fused_inner_upperskin_and_flanges,
                     tool=(self.front_spar_inner, self.fused_inner_lowerskin_and_flanges, self.rearspar_inner)
                     )

    @Part
    def fused_wingbox_outer(self):
        return Fused(shape_in= self.fused_outer_upperskin_and_flanges,
                     tool=(self.frontspar_outer, self.fused_outer_lowerskin_and_flanges, self.rearspar_outer))
    @Part
    def fused_wingbox_total(self):
        return Fused(shape_in=self.fused_wingbox_inner,
                     tool=self.fused_wingbox_outer)


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

    """RIBS"""

    @Attribute
    def rib_pos(self):
        return np.linspace(0, self.span / 2 - self.width_centerpiece / 2,
                           round(self.rib_pitch * (self.span / 2 - self.width_centerpiece / 2)) + 1)

    @Attribute
    def LE_length(self):
        return (self.span / 2 - self.width_centerpiece / 2) / cos(radians(self.leading_edge_sweep))

    @Attribute
    def LE_rib_pos(self):
        return np.linspace(0, self.LE_length, round(self.rib_pitch * (self.span / 2 - self.width_centerpiece / 2)) + 1)

    @Part
    def rib_surfaces(self):
        return RectangularSurface(quantify=len(self.rib_pos), width=2 * self.root_chord, length=0.5 * self.root_chord,
                                  position=translate(rotate(rotate90(translate(self.position, 'y', self.rib_pos[0],
                                                                               'x', - self.root_chord),
                                                                     'x'), 'y', -self.leading_edge_sweep, deg=True),
                                                     'z', -self.LE_rib_pos[child.index]))

    @Attribute
    def pts_closed(self):
        """ Extract airfoil coordinates from a data file and create a list of 3D points for the closed airfoil"""
        with open('../NACA_2412_closed.dat', 'r') as f:
            points_cl = []
            for line in f:
                x, y = line.split(' ', 1)  # separator = " "; max number of split = 1
                # Convert the strings to numbers and make 3D points for the FittedCurve class
                points_cl.append(Point(float(x), float(y)))
                # Note that the points are imported in the X-Y plane. A rotation below (line 79) could be avoided if
                # points were imported in the X-Z plane, e.g. points.append(Point(float(x), 0, float(y)))
        return points_cl

    @Part  # gives the closed airfoil
    def airfoil_closed(self):  # this curve is on the X-Y plane, with TE = (1, 0, 0) and LE = (0, 0, 0)
        return FittedCurve(points=self.pts_closed,
                           mesh_deflection=0.0001)

    @Part  # TransformedCurve is making a carbon copy of the fitted curve, which can be moved (rotated and translated) /
    # from one position to another. /
    # In this case we want to position the fitted curve copy in the x-z plane of the wing reference system, with its /
    # TE in the origin (location) of this reference system. This requires a rotation and a few translations.
    def airfoil_unscaled_root(self):
        return TransformedCurve(
            curve_in=self.airfoil_closed,
            from_position=rotate(translate(XOY, 'x', 1), 'x', -90, deg=True),
            to_position=self.position,
            hidden=False
        )

    @Part
    def airfoil_root(self):  # the ScaledCurve primitive allows scaling a given curve. Here it is used to scale /
        # the unit chord airfoil generated from the .dat file according to their actual chord length
        return ScaledCurve(
            curve_in=self.airfoil_unscaled_root,
            reference_point=self.airfoil_unscaled_root.start,
            # this point (the curve TE in this case) / is kept fixed during scaling
            # Can also use "self.position.point" - This extracts the (x,y,z) origin of the wing class position.
            factor=self.root_chord,  # uniform scaling
            mesh_deflection=0.0001
        )

    @Part  # This part creates the rib that closes the wing at the root (do we need it?)
    def root_rib(self):
        return Face(island=self.airfoil_root)

    # for tip rib
    @Part  # for the wing tip we use the same type of airfoil used for the wing root. We use again TransformedCurve
    def airfoil_unscaled_tip(self):
        return TransformedCurve(
            curve_in=self.airfoil_closed,
            # the curve to be repositioned
            from_position=rotate(translate(XOY, 'x', 0), 'x', -90, deg=True),
            # self.root_section_unscaled_inner.position,
            to_position=translate(self.root_section_unscaled_inner.position,  # to_position, i.e. the wing tip section
                                  'y', self.span / 2 - self.width_centerpiece / 2,  # - self.start_wing_to_kink,
                                  'x', (self.span / 2 - self.width_centerpiece / 2) * np.tan(
                    radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                  # 'x', (self.span / 2 - self.kink_location) * tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.tip_chord_kink + self.start_wing_to_kink * tan(radians(self.leading_edge_sweep))
                                  ),  # the sweep is applied
            hidden=True
        )

    @Part
    def airfoil_tip(self):
        return ScaledCurve(
            curve_in=self.airfoil_unscaled_tip,
            reference_point=self.airfoil_unscaled_tip.start,
            factor=self.tip_chord
        )

    @Part  # This part creates the rib that closes the wing at the tip
    def tip_rib(self):
        return Face(island=self.airfoil_tip)

    # @Part
    # def cutted_rib(self):
    #     return TrimmedSurface(built_from=self.root_rib, island=self.airfoil_closed)

    # @Part
    # def inner_surface(self):
    #     return CurveNetwork(curves=[self.airfoil_closed])

    # Define the trimmed rib surfaces
    # @Part
    # def trimmed_rib_surfaces(self):
    #     return BooleanIntersection(quantify=len(self.rib_surfaces),
    #                                 shape_in=self.rib_surfaces[child.index],
    #                                 tool=self.fused_wingbox_total)

    # @Part
    # def trimmed_rib_surfaces(self):
    #     return Split(quantify=len(self.rib_surfaces),
    #                  shape_in=self.rib_surfaces[child.index],
    #                  tool=self.fused_wingbox_total).parts[0]

    @Part
    def box_less_cone(self):  # Substract the airfoil from the rib
        return Subtracted(shape_in=self.fused_wingbox_total, tool=self.rib_surfaces)





