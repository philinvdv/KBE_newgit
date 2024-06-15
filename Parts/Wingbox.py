from math import radians, tan, cos
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.Meshing import *
from Parts.CustomPlane import *
from Parts.Skins import *
from Parts.Spars import *
from Parts.Stringers import *
from Parts.RibPart import *

class Wingbox(GeomBase):
    """This class contains the spar geometry, for the front and rear spar of the inner and outer wingbox."""
    thickness_flange = Input(0.02) #m for spars
    length_flanges = Input(0.02) #for skins
    flange_length_skins = Input(0.02) #for centerpiece
    flange_length_spars = Input(0.02)
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
    # Define the points for the lines

    rib_pitch = Input()
    nr_stringers_upper_inner = Input(4)
    nr_stringers_lower_inner = Input(4)
    nr_stringers_upper_outer = Input(4)
    nr_stringers_lower_outer = Input(4)

    @Part
    def my_stringers(self):
        return Stringer(tip_chord_kink=self.tip_chord_kink,
                        span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                        kink_location=self.kink_location, tip_chord=self.tip_chord,
                        width_centerpiece=self.width_centerpiece,
                        position=translate(self.position, 'x', 0, 'y', 0, 'z', 0))

    @Part
    def my_skins(self):
        return Skins(start_wing_to_kink=self.start_wing_to_kink, tip_chord_kink=self.tip_chord_kink, pts=self.pts,
                     front_spar_coordinates=self.front_spar_coordinates,
                     rear_spar_coordinates=self.rear_spar_coordinates,  # these are attributes
                     span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                     twist_angle=self.twist_angle, dihedral_angle=self.dihedral_angle, wing_material=self.wing_material,
                     kink_location=self.kink_location, tip_chord=self.tip_chord,
                     width_centerpiece=self.width_centerpiece,
                     position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))

    @Part
    def fused_inner_upperskin_and_flanges(self):
        return Fused(shape_in=self.my_skins.inner_upperskin_loft,
                     tool=(self.my_skins.flange_upperskin_inner_rear, self.my_skins.flange_upperskin_inner_front),hidden=False)

    @Part
    def fused_inner_lowerskin_and_flanges(self):
        return Fused(shape_in=self.my_skins.inner_lowerskin_loft,
                     tool=(self.my_skins.flange_lowerskin_inner_rear, self.my_skins.flange_lowerskin_inner_front),hidden=False)

    @Part
    def fused_outer_upperskin_and_flanges(self):
        return Fused(shape_in=self.my_skins.outer_upperskin_loft,
                     tool=(self.my_skins.flange_upperskin_outer_rear, self.my_skins.flange_upperskin_outer_front),hidden=False)

    @Part
    def fused_outer_lowerskin_and_flanges(self):
        return Fused(shape_in=self.my_skins.outer_lowerskin_loft,
                     tool=(self.my_skins.flange_lowerskin_outer_rear, self.my_skins.flange_lowerskin_outer_front),hidden=False)

    @Part
    def my_spars(self):
        return Spars(start_wing_to_kink=self.start_wing_to_kink, tip_chord_kink=self.tip_chord_kink, pts=self.pts,
                     front_spar_coordinates=self.front_spar_coordinates,
                     rear_spar_coordinates=self.rear_spar_coordinates,  # these are attributes
                     span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                     twist_angle=self.twist_angle, dihedral_angle=self.dihedral_angle, wing_material=self.wing_material,
                     kink_location=self.kink_location, tip_chord=self.tip_chord,
                     width_centerpiece=self.width_centerpiece,

                     position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))

    @Part
    def fused_wingbox_inner(self):
        return Fused(shape_in=self.fused_inner_upperskin_and_flanges,
                     tool=(self.my_spars.front_spar_inner, self.fused_inner_lowerskin_and_flanges,
                           self.my_spars.rearspar_inner),
                     hidden=True)

    @Part
    def fused_wingbox_outer(self):
        return Fused(shape_in= self.fused_outer_upperskin_and_flanges,
                     tool=(self.my_spars.frontspar_outer, self.fused_outer_lowerskin_and_flanges,
                           self.my_spars.rearspar_outer),
                     hidden=True)

    @Part
    def fused_wingbox_total(self):
        return Fused(shape_in=self.fused_wingbox_inner,
                     tool=self.fused_wingbox_outer)

    @Part
    def fused_cp1(self):
        return Fused(shape_in=self.parent.centerpiece.upperskin_centerpiece_loft,
                     tool=self.parent.centerpiece.frontspar_surf_centerpiece,hidden=True)

    @Part
    def fused_cp2(self):
        return Fused(shape_in=self.parent.centerpiece.lowerskin_centerpiece_loft,
                     tool=self.parent.centerpiece.rearspar_loft_centerpiece,hidden=True)

    @Part
    def fused_centerpiece(self):
        return Fused(shape_in=self.fused_cp1,
                     tool=self.fused_cp2, hidden=True)


    @Part
    def fused_wingbox_centerpiece(self):
        return Fused(shape_in=self.fused_wingbox_total,
                     tool=self.fused_centerpiece, hidden=True)

    """RIBS"""
    @Part
    def my_ribs(self):
        return Rib(rib_pitch=self.rib_pitch, root_chord=self.root_chord, tip_chord=self.tip_chord,
                   leading_edge_sweep=self.leading_edge_sweep, width_centerpiece=self.width_centerpiece, span=self.span,
                   position=translate(self.position, 'x', 0, 'y', 0, 'z', 0))

    """Try it for only good parts"""
    # @Attribute
    # def where_closed_curve(self):
    #     new_rib_positions = []
    #     new_LE_rib_pos = []
    #     tolerance = cos(radians(self.leading_edge_sweep)) * (self.root_chord * cos(np.pi/2 - radians(self.leading_edge_sweep))) #This determines where the lines become closed curves
    #     for i in range(len(self.rib_pos)):
    #         if self.rib_pos[i] >= tolerance:
    #             new_rib_positions.append(self.rib_pos[i])
    #             new_LE_rib_pos.append(self.LE_rib_pos[i])
    #     print(new_rib_positions)
    #
    #     return new_rib_positions, new_LE_rib_pos
    #
    # @Part
    # def rib_surfaces_new(self):
    #     return RectangularSurface(quantify=len(self.where_closed_curve[1]), width=2 * self.root_chord, length=0.5 * self.root_chord,
    #                               position=translate(rotate(rotate90(translate(self.position, 'y', self.where_closed_curve[1][0],
    #                                                                            'x', - self.root_chord),
    #                                                                  'x'), 'y', -self.leading_edge_sweep, deg=True),
    #                                                  'z', -self.where_closed_curve[1][child.index]))