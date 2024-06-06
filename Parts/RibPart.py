from math import radians, tan, sin, cos
from parapy.geom import *
from parapy.core import *

from Parts.LoftedWingSurfaces import *
import numpy as np
from parapy.geom.generic.positioning import VX, VY  # parapy.geom from 1.2.9

class Rib(GeomBase):
    rib_pitch = Input()
    root_chord = Input()
    tip_chord = Input()
    leading_edge_sweep = Input()
    width_centerpiece = Input()
    span = Input()

    @Attribute
    def rib_pos(self):
        return np.linspace(0, self.span / 2 -self.width_centerpiece/2,
                           round(self.rib_pitch * (self.span / 2 - self.width_centerpiece / 2)) + 1)

    @Attribute
    def LE_length(self):
        return (self.span / 2 - self.width_centerpiece/2) / cos(radians(self.leading_edge_sweep))

    @Attribute
    def LE_rib_pos(self):
        return np.linspace(0, self.LE_length, round(self.rib_pitch * (self.span / 2-self.width_centerpiece/2)) + 1)

    #I now did this just with the closed airfoil shape, easier than cutting
    # def root_rib(self):
    #     return RectangularSurface(width=2 * self.root_chord, length=0.5*self.root_chord,
    #                               position=rotate(translate(self.position, 'y', self.rib_pos[0],
    #                                                         'x', - self.root_chord),
    #                                               self.position.Vx, 90, deg=True))

    # @Part
    # def tip_rib(self):
    #     return RectangularSurface(width=2 * self.root_chord, length=0.5*self.root_chord,
    #                               position=rotate(translate(self.position, 'y', self.rib_pos[-1],
    #                                                 'x', - self.root_chord + self.rib_pos[-1] * tan(radians(self.leading_edge_sweep))),
    #                                               self.position.Vx, 90, deg=True))

    @Part
    def rib_surfaces(self):
        return RectangularSurface(quantify=len(self.rib_pos), width=2*self.root_chord, length=0.5*self.root_chord,
                                  position=translate(rotate(rotate90(translate(self.position, 'y', self.rib_pos[0],
                                                            'x', - self.root_chord),
                                                  'x'),'y', -self.leading_edge_sweep, deg=True),
                                  'z', -self.LE_rib_pos[child.index]))


    @Attribute
    def pts_closed(self):
        """ Extract airfoil coordinates from a data file and create a list of 3D points for the closed airfoil"""
        with open('NACA_2412_closed.dat', 'r') as f:
            points_cl = []
            for line in f:
                x, y = line.split(' ', 1)  # separator = " "; max number of split = 1
                # Convert the strings to numbers and make 3D points for the FittedCurve class
                points_cl.append(Point(float(x), float(y)))
                # Note that the points are imported in the X-Y plane. A rotation below (line 79) could be avoided if
                # points were imported in the X-Z plane, e.g. points.append(Point(float(x), 0, float(y)))
        return points_cl

    @Part #gives the closed airfoil
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
            reference_point=self.airfoil_unscaled_root.start,  # this point (the curve TE in this case) / is kept fixed during scaling
            # Can also use "self.position.point" - This extracts the (x,y,z) origin of the wing class position.
            factor=self.root_chord,  # uniform scaling
            mesh_deflection=0.0001
        )

    @Part #This part creates the rib that closes the wing at the root (do we need it?)
    def root_rib(self):
        return Face(island=self.airfoil_root)

    #for tip rib
    @Part  # for the wing tip we use the same type of airfoil used for the wing root. We use again TransformedCurve
    def airfoil_unscaled_tip(self):
        return TransformedCurve(
            curve_in=self.airfoil_closed,
            # the curve to be repositioned
            from_position=rotate(translate(XOY, 'x', 0), 'x', -90, deg=True),#self.root_section_unscaled_inner.position,
            to_position=translate(self.root_section_unscaled_inner.position,  # to_position, i.e. the wing tip section
                                  'y', self.span / 2 - self.width_centerpiece / 2, # - self.start_wing_to_kink,
                                  'x', (self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                  #'x', (self.span / 2 - self.kink_location) * tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.tip_chord_kink + self.start_wing_to_kink * tan(radians(self.leading_edge_sweep))
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

    @Part #This part creates the rib that closes the wing at the tip
    def tip_rib(self):
        return Face(island=self.airfoil_tip)

    # @Part
    # def cutted_rib(self):
    #     return TrimmedSurface(built_from=self.root_rib, island=self.airfoil_closed)

    # @Part
    # def inner_surface(self):
    #     return CurveNetwork(curves=[self.airfoil_closed])

    # @Part
    # def box_less_cone(self):  # Substract the airfoil from the rib
    #     return SubtractedSolid(shape_in=self.root_rib, tool=self.airfoil_closed)

    @Part
    def my_reference_line(self):
        return LineSegment(start=Point(0, 0, 0), end=Point(1, 0, 0))

    # @Part
    # def rib_root_(self):
    #     return LoftedSurface(
    #         profiles=[self.root_section_inner, self.tip_section_inner],
    #         mesh_deflection=0.0001
    #     )

# if __name__ == '__main__':
#     from parapy.gui import display
#     obj = Rib()
#     display(obj)
