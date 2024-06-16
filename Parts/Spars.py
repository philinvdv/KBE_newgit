from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.Meshing import *

class Spar(GeomBase):
    """This class contains the spar geometry, for the front and rear spar of the inner and outer wingbox. It works with
    making lines, then from these lines making a surface."""
    length_flange_spar = Input(0.01) #m

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

    """Frontspar inner"""
    @Part  # Line for front spar at root. It connects the upper with the lower point, using the frontspar coordinates
    def line_root_front(self):
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           )

    @Part  # Similarly, line for front spar at kink
    def line_kink_front(self):
        return LineSegment(start=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink,
                                       self.front_spar_coordinates[0][1] * self.tip_chord_kink),
                           end=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink,
                                     self.front_spar_coordinates[1][1] * self.tip_chord_kink),
                           )

    @Part #Make the frontspar from the defined lines at root and kink
    def front_spar_inner(self):
        return LoftedSurface(
            profiles=[self.line_root_front, self.line_kink_front],
            mesh_deflection=0.0001
        )

    """Rear spar inner"""
    @Part #this part is the line at the root chord for the rear spar
    def line_root_rear(self):
        return LineSegment(start=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.root_chord, 0, self.rear_spar_coordinates[1][1] * self.root_chord))

    @Part #This is the line for the rearspar at the kink
    def line_kink_rear(self):
        return LineSegment(start=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                                       self.rear_spar_coordinates[0][1] * self.tip_chord_kink),
                           end=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part #Create the rearspar of the inner wing
    def rearspar_inner(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_root_rear, self.line_kink_rear],
            mesh_deflection=0.0001
        )

    """Front spar outer section"""
    @Part  # this part is the line at the tip chord for the frontspar. For this, some geometry was applied to determine
    #where the points are located. This is more difficult than for the inner wingbox, since both the leading edge and
    #trailing edge are swept, though not by the same amount
    def line_tip_front(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep))
                                       + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.front_spar_coordinates[0][1] * self.tip_chord), #z
                           end=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep))
                                     + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.front_spar_coordinates[1][1] * self.tip_chord)) #z

    @Part #Make the frontspar
    def frontspar_outer(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_kink_front, self.line_tip_front],
            mesh_deflection=0.0001
        )

    """Rearspar outer section"""
    @Part  # this part is the line at the tip chord for the rear spar. AGain, geometry is applied
    def line_tip_rear(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep))
                                       + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.rear_spar_coordinates[0][1] * self.tip_chord), #z
                           end=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) +
                                     self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.rear_spar_coordinates[1][1] * self.tip_chord)) #z


    @Part #Make the rearspar
    def rearspar_outer(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.line_kink_rear, self.line_tip_rear],
            mesh_deflection=0.0001
        )


    """Flanges, inner""" #use the same, but translated along the chord. 1 is the line moved to the side along the chord,
    # 2 along skin. These flanges are there to connect the wingbox to the wing
    @Part
    def flangeline1_front_upper_inner(self): #flangeline of the front spar, upper inner
        return LineSegment(start=Point(-0.8 * self.root_chord - self.length_flange_spar, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.tip_chord_kink - self.length_flange_spar, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flangeline2_front_upper_inner(self): #flangeline2 of the front spar, upper inner
        return LineSegment(start=Point(-0.8 * self.root_chord, 0, self.front_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part #Generate the flange of the frontspar upper inner
    def flange_front_upper_inner(self):
        return LoftedSurface(
            profiles=[self.flangeline1_front_upper_inner, self.flangeline2_front_upper_inner],
            mesh_deflection=0.0001
        )

    #Repeat procedure for the other flanges as well
    @Part
    def flangeline1_front_lower_inner(self): #flangeline for the frontspar, lower part inner box
        return LineSegment(start=Point(-0.8 * self.root_chord - self.length_flange_spar, 0, self.front_spar_coordinates[1][1] * self.root_chord),
                           end=Point(-0.8 * self.tip_chord_kink - self.length_flange_spar, self.start_wing_to_kink, self.front_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flangeline2_front_lower_inner(self): #flangeline2 for the frontspar, lower part inner box
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
        return LineSegment(start=Point(-0.3 * self.root_chord + self.length_flange_spar, 0, self.rear_spar_coordinates[0][1] * self.root_chord),
                           end=Point(-0.3 * self.tip_chord_kink + self.length_flange_spar, self.start_wing_to_kink,
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
        return LineSegment(start=Point(-0.3 * self.root_chord + self.length_flange_spar, 0, self.rear_spar_coordinates[1][1] * self.root_chord),
                           end=Point(-0.3 * self.tip_chord_kink + self.length_flange_spar, self.start_wing_to_kink,
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
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord - self.length_flange_spar, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.front_spar_coordinates[0][1] * self.tip_chord),
                           end=Point(-0.8 * self.tip_chord_kink - self.length_flange_spar, self.start_wing_to_kink, self.front_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flangeline2_front_upper_outer(self):  # flang of the front spar, upper inner
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece, #y
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
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord - self.length_flange_spar, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.front_spar_coordinates[1][1] * self.tip_chord),
                           end=Point(-0.8 * self.tip_chord_kink - self.length_flange_spar, self.start_wing_to_kink, self.front_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flangeline2_front_lower_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.8 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.front_spar_coordinates[1][1] * self.tip_chord),
                           end=Point(-0.8 * self.tip_chord_kink, self.start_wing_to_kink, self.front_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flange_front_lower_outer(self):
        return LoftedSurface(
            profiles=[self.flangeline1_front_lower_outer, self.flangeline2_front_lower_outer],
            mesh_deflection=0.0001
        )

    #REARSPAR UPPER OUTER flanges
    @Part  # For rearspar, upper outer
    def flangeline1_rear_upper_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord + self.length_flange_spar, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.rear_spar_coordinates[0][1] * self.tip_chord),
                           end=Point(-0.3 * self.tip_chord_kink + self.length_flange_spar, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[0][1] * self.tip_chord_kink))

    @Part
    def flangeline2_rear_upper_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece, #y
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
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord + self.length_flange_spar, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.rear_spar_coordinates[1][1] * self.tip_chord),
                           end=Point(-0.3 * self.tip_chord_kink + self.length_flange_spar, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flangeline2_rear_lower_outer(self):
        return LineSegment(start=Point((self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                            -0.3 * self.tip_chord, #x
                                       self.span/2 - self.width_centerpiece, #y
                                       self.rear_spar_coordinates[1][1] * self.tip_chord),
                           end=Point(-0.3 * self.tip_chord_kink, self.start_wing_to_kink,
                                     self.rear_spar_coordinates[1][1] * self.tip_chord_kink))

    @Part
    def flange_rear_lower_outer(self):
        return LoftedSurface(
            profiles=[self.flangeline1_rear_lower_outer, self.flangeline2_rear_lower_outer],
            mesh_deflection=0.0001
        )