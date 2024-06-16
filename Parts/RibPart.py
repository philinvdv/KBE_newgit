from math import radians, tan, sin, cos
from parapy.geom import *
from parapy.core import *
import numpy as np
from parapy.geom.generic.positioning import VX, VY  # parapy.geom from 1.2.9
from parapy.core.validate import *

class Rib(GeomBase):
    """This class creates the ribs. It does so by first determining the positions, then creating surfaces which are then
    cut to be inside the wingbox. It also creates the closed airfoils at the root and tip that close the wing"""
    rib_pitch = Input(2, validator=GT(0, msg="Rib pitch cannot be smaller than " "{validator.limit}!"))  # pitch between the ribs in meters

    root_chord = Input()
    tip_chord = Input()
    leading_edge_sweep = Input()
    width_centerpiece = Input()
    span = Input()

    @Attribute #The ribs will be located from the start of the wing til the end of the wing, with the distance between
    #the ribs defined by the rib pitch
    def rib_pos(self):
        return np.linspace(0, self.span / 2 - self.width_centerpiece,
                           round(self.rib_pitch * (self.span / 2 - self.width_centerpiece)) + 1)

    @Attribute #Since the wing is swept, this needs to be accounted for in the actual length of the wing
    def LE_length(self):
        return (self.span / 2 - self.width_centerpiece) / cos(radians(self.leading_edge_sweep))

    @Attribute #Start with placing ribs at the start of the wingbox LE, not the wing LE
    def LE_rib_pos(self):
        start = cos(radians(90 - self.leading_edge_sweep)) * 0.2 * self.root_chord #Calculate position of wingbox start
        return np.linspace(start, self.LE_length, round(self.rib_pitch * (self.span / 2 - self.width_centerpiece)) + 1)

    @Part #Make planes (rectangular surfaces) at the locations as defined. They should be larger than the wingbox
    def rib_surfaces(self):
        return RectangularSurface(quantify=len(self.rib_pos), width=2 * self.root_chord, length=0.5 * self.root_chord,
                                  position=translate(rotate(rotate90(translate(self.position, 'y', self.rib_pos[0],
                                                                               'x', - self.root_chord),
                                                                     'x'), 'y', -self.leading_edge_sweep, deg=True),
                                                     'z', -self.LE_rib_pos[child.index]), hidden=True)

    @Attribute #To cut the ribs that close the wing, we need to use the closed version of the airfoil
    def pts_closed(self):
        """ Extract airfoil coordinates from a data file and create a list of 3D points for the closed airfoil"""
        with open('NACA_2412_closed.dat', 'r') as f:
            points_cl = []
            for line in f:
                x, y = line.split(' ', 1)  # separator = " "; max number of split = 1
                #Make them points
                points_cl.append(Point(float(x), float(y)))
        return points_cl

    @Part #gives the closed airfoil, fitted through the points
    def airfoil_closed(self):  # this curve is on the X-Y plane, with TE = (1, 0, 0) and LE = (0, 0, 0)
        return FittedCurve(points=self.pts_closed,
                           mesh_deflection=0.0001, hidden=True)

    @Part  # Transform, unscaled
    def airfoil_unscaled_root(self):
        return TransformedCurve(
            curve_in=self.airfoil_closed,
            from_position=rotate(translate(XOY, 'x', 1), 'x', -90, deg=True),
            to_position=self.position,
            hidden=True
        )

    @Part # scale it to the size of the root
    def airfoil_root(self):
        return ScaledCurve(
            curve_in=self.airfoil_unscaled_root,
            reference_point=self.airfoil_unscaled_root.start,
            factor=self.root_chord,
            mesh_deflection=0.0001, hidden=True
        )

    @Part #This part creates the rib that closes the wing at the root. It separates the wing from the centerpiece
    def root_rib(self):
        return Face(island=self.airfoil_root)

    #for tip rib do the same, but position it correctly
    @Part  # for the wing tip we use the same type of airfoil used for the wing root. We use again TransformedCurve
    def airfoil_unscaled_tip(self):
        return TransformedCurve(
            curve_in=self.airfoil_closed,
            # the curve to be repositioned
            from_position=rotate(translate(XOY, 'x', 0), 'x', -90, deg=True),
            to_position=translate(self.root_section_unscaled_inner.position,  # to_position, i.e. the wing tip section
                                  'y', self.span / 2 - self.width_centerpiece,
                                  'x', (self.span/2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep))
                                  + self.tip_chord - self.root_chord
                                  ),  # the sweep is applied
            hidden=True
        )

    @Part #scale it to size of tip
    def airfoil_tip(self):
        return ScaledCurve(
            curve_in=self.airfoil_unscaled_tip,
            reference_point=self.airfoil_unscaled_tip.start,
            factor=self.tip_chord, hidden=True
        )

    @Part #This part creates the rib that closes the wing at the tip
    def tip_rib(self):
        return Face(island=self.airfoil_tip)


    #Now lets get the actual ribs
    @Part  # This gives the curves of the ribs in the shape of the wingbox by intersecting them
    def intersected_edges_ribs(self):
        return IntersectedShapes(quantify=len(self.rib_surfaces),
                                 shape_in=self.fused_wingbox_centerpiece,
                                 tool=self.rib_surfaces[child.index], hidden=True)

    @Part  # This creates all ribs, but they go into the centerpiece still (since total wingbox is used)
    def rib_surface_all(self):
        return Face(
            quantify=len(self.intersected_edges_ribs),
            island=ComposedCurve(self.intersected_edges_ribs[child.index].edges, ordered=False),
            hidden=True
        )

    @Part  # This is purely to cut the ribs at the right locations, such that they do not go into the centerpiece
    def box_cp(self): #so this is a huge box at the location of the centerpiece
        return Box(width=self.root_chord, height=3, length=self.width_centerpiece,
                   position=translate(XOY, 'x', -self.root_chord, 'y', -self.width_centerpiece, 'z', -1.5),
                   hidden=True)

    @Part  # actual ribs
    def ribs_cut(self):  # Substract the box from the ribs to get them in the desired shape
        return Subtracted(quantify=len(self.rib_surface_all), shape_in=self.rib_surface_all[child.index],
                          tool=self.box_cp)

