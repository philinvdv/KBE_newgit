from math import radians, tan, cos
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.Skins import *
from Parts.CustomPlane import *
from Parts.StringerPart import *

class Centerpiece(GeomBase):
    """This class creates the centerpiece. Since only one wing is analysed, the centerpiece is split in half and only
    one half is designed in detail. The other half would be a mirrored version with the exact same properties. This class
    makes all the parts for the centerpiece, so skins, spars, stringers and ribs."""
    flange_length_skins = Input(0.02) #size of the flanges
    stringer_width_cp = Input(0.1) #Size of the stringers

    # The attributes and inputs from Wing()
    start_wing_to_kink = Input()
    tip_chord_kink = Input()
    pts = Input()
    front_spar_coordinates = Input()
    rear_spar_coordinates = Input()
    span = Input()
    leading_edge_sweep = Input()  # deg
    root_chord = Input()
    kink_location = Input()  # measured from centerline of fuselage
    tip_chord = Input()
    width_centerpiece = Input()
    rib_pitch_cp = Input(2)

    nr_stringers_upper_CP = Input()
    nr_stringers_lower_CP = Input()

    """Upper&lower skin pannel centerpiece"""
    @Attribute #This gives the points needed to create the skin surface (from lines)
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

    @Part  # Line from upper point of front spar to upper point of rear spar at centerpiece
    def line_root_upp_centerpiece(self):
        return LineSegment(start=self.points_skin_centerpiece[0],
                           end=self.points_skin_centerpiece[1],
                           #  position = rotate(XOY, 'x', 90, deg=True)
                           hidden=True)

    @Part #The one at the wing root exists already, take from Skins and combine with new line
    def upperskin_centerpiece_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.parent.my_wingbox.my_skins.line_root_upp, self.line_root_upp_centerpiece],
            mesh_deflection=0.0001, hidden=False)

    @Part  # Mirror and transform to get the other half of the centerpiece
    def transform_mirror_CP_upperskin(self):
        return TransformedSurface(
            surface_in=MirroredSurface(surface_in=self.upperskin_centerpiece_loft, reference_point=Point(0, 0, 0),
                                       vector1=(1, 0, 0), vector2=(0, 0, 1)),  # Original curve to transform
            from_position=self.position,  # Reference position of the original curve
            to_position=translate(XOY, 'x', 0, 'y', -2*self.width_centerpiece)  # New position of the curve
        )

    @Part  # Line from lower point of front spar to lower point of rear spar
    def line_root_low_centerpiece(self):
        return LineSegment(start=self.points_skin_centerpiece[4], end=self.points_skin_centerpiece[5],
                           #  position = rotate(XOY, 'x', 90, deg=True)
                           hidden=True)

    @Part  #Lowerskin of the centerpiece
    def lowerskin_centerpiece_loft(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.parent.my_wingbox.my_skins.line_root_low, self.line_root_low_centerpiece],
            mesh_deflection=0.0001, hidden=False
        )

    @Part  # Mirror and transform the lowerskin to get the other half of the CP
    def transform_mirror_CP_lowerskin(self):
        return TransformedSurface(
            surface_in=MirroredSurface(surface_in=self.lowerskin_centerpiece_loft, reference_point=Point(0, 0, 0),
                                       vector1=(1, 0, 0), vector2=(0, 0, 1)),  # Original curve to transform
            from_position=self.position,  # Reference position of the original curve
            to_position=translate(XOY, 'x', 0, 'y', -2*self.width_centerpiece)  # New position of the curve
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
            mesh_deflection=0.0001, hidden=False
        )

    @Part  # Mirror and transform to the other half
    def transform_mirror_CP_frontspar(self):
        return TransformedSurface(
            surface_in=MirroredSurface(surface_in=self.frontspar_surf_centerpiece, reference_point=Point(0, 0, 0),
                                       vector1=(1, 0, 0), vector2=(0, 0, 1)),  # Original curve to transform
            from_position=self.position,  # Reference position of the original curve
            to_position=translate(XOY, 'x', 0, 'y', -2*self.width_centerpiece)  # New position of the curve
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
            mesh_deflection=0.0001, hidden=False
        )

    @Part  # Mirror and transform for other half
    def transform_mirror_CP_rearspar(self):
        return TransformedSurface(
            surface_in=MirroredSurface(surface_in=self.rearspar_loft_centerpiece, reference_point=Point(0, 0, 0),
                                       vector1=(1, 0, 0), vector2=(0, 0, 1)),  # Original curve to transform
            from_position=self.position,  # Reference position of the original curve
            to_position=translate(XOY, 'x', 0, 'y', -2*self.width_centerpiece)  # New position of the curve
        )

    """RIBS"""

    @Attribute #Similar approach as followed in RibPart.py
    def rib_pos_cp(self):
        return np.linspace(0, -self.width_centerpiece,
                           round(self.rib_pitch_cp * (self.width_centerpiece)) + 1)

    @Part #Make surfaces at the locations of the planes
    def rib_surfaces_cp(self):
        return RectangularSurface(quantify=len(self.rib_pos_cp), width=2 * self.root_chord, length=0.5 * self.root_chord,
                                  position=translate(rotate90(translate(self.position, 'y', self.rib_pos_cp[0],
                                                                               'x', - self.root_chord),
                                                                     'x'),
                                                     'z', -self.rib_pos_cp[child.index]), hidden=True)

    @Part  # This gives the curves of the ribs in the shape of the centerpiece wingbox
    def intersected_cp(self):
        return IntersectedShapes(quantify=len(self.rib_surfaces_cp),
                                 shape_in=self.parent.my_wingbox.fused_centerpiece,
                                 tool=self.rib_surfaces_cp[child.index], hidden=True)

    @Part  # This creates the ribs of the centerpiece
    def ribs_cp(self):
        return Face(quantify=len(self.intersected_cp),
                    island=self.intersected_cp[child.index].edges)

    """STRINGERS"""
    @Attribute #define the starting (and ending) points of the stringers
    def LE_stringer_points_upper_cp(self):
        space = np.linspace(0.3 * self.root_chord, 0.8 * self.root_chord,
                           self.nr_stringers_upper_CP + 2)
        points = np.delete(space, 0)
        points_ = np.delete(points, -1)
        return points_

    @Attribute #define the starting (and ending) points for lower skin
    def LE_stringer_points_lower_cp(self):
        space = np.linspace(0.3 * self.root_chord, 0.8 * self.root_chord,
                            self.nr_stringers_lower_CP + 2)
        points = np.delete(space, 0)
        points_ = np.delete(points, -1)
        return points_

    @Part #upper CP stringers
    def stringers_CP_upper(self): #Since symmetric and no sweep, the stringer locations are the same
        return CustomPlane(quantify = self.nr_stringers_upper_CP,
                           stringer_location_1 = self.LE_stringer_points_upper_cp[child.index],
                           stringer_location_2 = self.LE_stringer_points_upper_cp[child.index],
                           width_section = self.width_centerpiece,
                           chord = self.root_chord,
                           sign = -1, start_y=0, hidden=True)

    @Part #lower CP stringers
    def stringers_CP_lower(self):
        return CustomPlane(quantify = self.nr_stringers_lower_CP,
                           stringer_location_1 = self.LE_stringer_points_lower_cp[child.index],
                           stringer_location_2 = self.LE_stringer_points_lower_cp[child.index],
                           width_section = self.width_centerpiece,
                           chord = self.root_chord,
                           sign = -1, start_y=0, hidden=True)

    @Part  # This gives the curves on the wingbox at the location of the upper stringers
    def intersected_str_upper(self):
        return IntersectedShapes(
            quantify=len(self.stringers_CP_upper),
            shape_in=self.upperskin_centerpiece_loft,
            tool=self.stringers_CP_upper[child.index].custom_plane,
            hidden=False
        )

    @Part  # This gives the curves on the wingbox at the location of the lower stringers
    def intersected_str_lower(self):
        return IntersectedShapes(
            quantify=len(self.stringers_CP_lower),
            shape_in=self.lowerskin_centerpiece_loft,
            tool=self.stringers_CP_lower[child.index].custom_plane,
            hidden=False
        )

    @Part #This gives the L-stringer. The [0] is to prevent errors; there is only 1 line however in the 'edges' of the
    #intersection
    def stringer_upper_CP(self):
        return StringerPart(quantify=len(self.intersected_str_upper),
                             edge_in=self.intersected_str_upper[child.index].edges[0], up_down=1, angle_sign=1,
                             width_stringer=self.stringer_width_cp)

    @Part  # This gives the flat part of the stringer. The 0 is to prevent erros; there is only 1 line however
    def stringer_lower_CP(self):
        return StringerPart(quantify=len(self.intersected_str_lower),
                             edge_in=self.intersected_str_lower[child.index].edges[0], up_down=-1, angle_sign=1,
                             width_stringer=0.1)