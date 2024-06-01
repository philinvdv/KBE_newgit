from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.Meshing import MeshingFunc

class Spars(GeomBase):
    """This class contains the spar geometry, for the front and rear spar of the inner and outer wingbox."""
    thickness_frontspar = Input(0.02)#m
    thickness_rearspar = Input(0.02)
    #The attributes and inputs from Wing()
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
    """Front spar inner"""
    @Part  # Line for front spar at root NEW
    def line_root_front(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           )

    @Part  # Line for front spar at root NEW
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


    # @Part
    # def mesh_front_spar_inner(self):
    #     return MeshingFunc(part_class=self.my_spars.front_spar_inner, n_mesh_points=50, hidden=self.hide_mesh)
    #
    # @Part
    # def mesh_front_spar_outer(self):
    #     return MeshingFunc(part_class=self.my_spars.frontspar_outer, n_mesh_points=50, hidden=self.hide_mesh)
    #
    # @Part
    # def mesh_rear_spar_inner(self):
    #     return MeshingFunc(part_class=self.my_spars.rearspar_inner, n_mesh_points=50, hidden=self.hide_mesh)
    #
    # @Part
    # def mesh_rear_spar_outer(self):
    #     return MeshingFunc(part_class=self.my_spars.rearspar_outer, n_mesh_points=50, hidden=self.hide_mesh)

