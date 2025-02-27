from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np
from parapy.core.decorators import action
from parapy.exchange import STEPWriter
from parapy.core.widgets import (
    Button, CheckBox, ColorPicker, Dropdown, FilePicker, MultiCheckBox,
    ObjectPicker, SingleSelection, TextField)
from parapy.core.validate import *
import warnings

import os
import pandas as pd

from Parts.Skins import *
from Parts.Spars import *
from Parts.RibPart import *
from Parts.Centerpiece import *
from Parts.Wingbox import *
from Parts.Meshing import *
from Parts.Stringers import *


class Wing(GeomBase):
    """This class contains the wing itself, from the loaded airfoil points. Contains the wingbox, since this is an
    essential part of the wing. Would also contain for example flap systems (not in this program)"""

    width_centerpiece = Input(2.5, validator=GT(0, #needed to determine the effective span of the wing
        msg="Centre section width cannot be smaller than " "{validator.limit}!"))  # This is the width of half the
    # total centerpiece, so basically from the middle of the fuselage until where the actual wing starts
    # (outside of the fuselage)
    span_inp = Input(35.8, validator=GT(0,
                    msg="Wing span cannot be smaller than " "{validator.limit}!"))  # span of the aircraft in meters
    leading_edge_sweep = Input(25, validator=Between(-60, 60,
                                msg="Leading edge sweep angle cannot be greater than +-{60}!"))  # in degrees
    root_chord = Input(5.9, validator=Between(0, 30, msg="Root chord cannot be smaller than " "{validator.limit}!"))
    tip_chord = Input(1.64, validator=GT(0, msg="{value} cannot be greater than " "{validator.limit}!"))
    kink_location = Input(6, validator=GreaterThan(0,
            msg="{value} cannot be smaller than " "{validator.limit}!"))  # measured from centerline of fuselage
    material = Input()

    popup_gui = True

    @Input #This gives the distance between the kink and the start of the wing
    def start_wing_to_kink(self):
        return self.kink_location - self.width_centerpiece

    @Input #This gives the chord at the location of the kink
    def tip_chord_kink_calc(self):
        return self.root_chord - self.start_wing_to_kink \
               * np.tan(radians(self.leading_edge_sweep))  # if trailing edge kink has zero sweep

    @Attribute
    def span(self):
        """Checks wheter the kink chord becomes 0 or negative (twisted wing)"""
        if self.span_inp / 2 < self.kink_location:
            msg = f"The halfspan ({self.span_inp/2}) should be larger than the spanwise location of the kink " \
                  f"({self.kink_location}). Input will be ignored, and the span will be set equal to 36."
            # print warning message in console:
            warnings.warn(msg)
            if self.popup_gui:  # invoke pop-up dialogue box using Tk"""
                generate_warning("Warning: Invalid input", msg)
            return 36
        else:
            return self.span_inp

    @Attribute
    def tip_chord_kink(self):
        """Checks wheter the kink chord becomes 0 or negative (twisted wing)"""
        if self.tip_chord_kink_calc < 0.3:
            msg = f"The combination of root chord, tip chord, leading edge sweep, kink location and span that you have " \
                  "provided would lead to an impossible geometry that could not exist in reality. Please modify your " \
                  "geometry accordingly."
            # print warning message in console:
            warnings.warn(msg)
            if self.popup_gui:  # invoke pop-up dialogue box using Tk"""
                generate_warning("Warning: Impossible geometry", msg)
            return 0.3
        else:
            return self.tip_chord_kink_calc


    @Attribute
    def pts_pre(self):
        """ Extract airfoil coordinates from a data file and create a list of 3D points.
        Also create points for spars (20% and 70%)"""
        front_spar_coordinates = []
        rear_spar_coordinates = []
        with open('NACA_2412_points.dat', 'r') as f:
            points = []
            for line in f:
                x, y = line.split(' ', 1)  # separator = " "; max number of split = 1
                # Convert the strings to numbers & make 3D points for the FittedCurve class
                points.append(Point(float(x), float(y)))
                if float(x) == 0.2: #The frontspar is located at 20%
                    front_spar_coordinates.append([float(x), float(y), 0])
                if float(x) == 0.7: #The rearspar is located at 70%
                    rear_spar_coordinates.append([float(x), float(y), 0])
        return points, front_spar_coordinates, rear_spar_coordinates

    @Attribute  # split into the different components
    def pts(self):
        points, front_spar_coordinates, rear_spar_coordinates = self.pts_pre
        return points

    @Attribute #These are the frontspar coordinates of the unit airfoil
    def front_spar_coordinates(self):
        points, front_spar_coordinates, rear_spar_coordinates = self.pts_pre
        return front_spar_coordinates

    @Attribute #These are the rearspar coordinates of the unit airfoil
    def rear_spar_coordinates(self):
        points, front_spar_coordinates, rear_spar_coordinates = self.pts_pre
        return rear_spar_coordinates

    @Part #get the airfoil from the points
    def airfoil_from_3D_points(self):  # this curve is on the X-Y plane, with TE = (1, 0, 0) and LE = (0, 0, 0)
        return FittedCurve(points=self.pts,
                           mesh_deflection=0.0001, hidden=True)

    @Part  # TransformedCurve moves the (copy of) fitted curve to the desired location.
    # In this case we want to position the fitted curve in the x-z plane of the wing reference system, with its
    # TE in the origin. To get this, we rotate and translate
    def root_section_unscaled_inner(self):
        return TransformedCurve(
            curve_in=self.airfoil_from_3D_points,
            from_position=rotate(translate(XOY, 'x', 0), 'x', -90, deg=True),
            to_position=self.position,
            hidden=True
        )

    @Part  # for the wing tip we use the same type of airfoil used for the wing root. We use again TransformedCurve
    def tip_section_unscaled_inner(self):
        return TransformedCurve(
            curve_in=self.root_section_unscaled_inner,
            # the curve to be repositioned
            from_position=self.root_section_unscaled_inner.position,
            to_position=translate(self.root_section_unscaled_inner.position,  # to_position, i.e. the wing tip section
                                  'y', self.start_wing_to_kink,
                                  'x', 0
                                  ),  # the sweep is applied
            hidden=True
        )

    @Part
    def root_section_inner(self):  # This scales the unit airfoil to in this case the root airfoil
        return ScaledCurve(
            curve_in=self.root_section_unscaled_inner,
            reference_point=self.root_section_unscaled_inner.start,
            # this point (the curve TE in this case) / is kept fixed during scaling
            # Can also use "self.position.point" - This extracts the (x,y,z) origin of the wing class position.
            factor=self.root_chord,  # uniform scaling
            mesh_deflection=0.0001, hidden=True
        )

    @Part
    def tip_section_inner(self): #Same but for tip inner, which is the airfoil at the location of the tip
        return ScaledCurve(
            curve_in=self.tip_section_unscaled_inner,
            reference_point=self.tip_section_unscaled_inner.start,
            factor=self.tip_chord_kink, hidden=True
        )

    @Part #This gives the wing surface for the inner wing part
    def wing_loft_surf_inner(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.root_section_inner, self.tip_section_inner],
            mesh_deflection=0.0001
        )

    @Part  # Mirror and transform to get it for the left wing as well
    def transform_mirror_wing_inner(self):
        return TransformedSurface(
            surface_in=MirroredSurface(surface_in=self.wing_loft_surf_inner, reference_point=Point(0, 0, 0),
                                       vector1=(1, 0, 0), vector2=(0, 0, 1)),  # Original curve to transform
            from_position=self.position,  # Reference position of the original curve
            to_position=translate(XOY, 'x', -1, 'y', -2*self.width_centerpiece)  # New position of the curve
        )

    """Outer wing"""
    @Part  # for the wing tip we use the same type of airfoil used for the wing root. We use again TransformedCurve
    def tip_section_unscaled_outer(self):
        return TransformedCurve(
            curve_in=self.tip_section_unscaled_inner,
            # the curve to be repositioned
            from_position=self.root_section_unscaled_inner.position,
            to_position=translate(self.root_section_unscaled_inner.position,  # to_position, i.e. the wing tip section
                                  'y', self.span / 2 - self.width_centerpiece - self.start_wing_to_kink,
                                  'x', (self.span / 2 - self.width_centerpiece) * np.tan(
                    radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                  # 'x', (self.span / 2 - self.kink_location) * tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.tip_chord_kink + self.start_wing_to_kink * tan(radians(self.leading_edge_sweep))
                                  ),  # the sweep is applied
            hidden=True
        )

    @Part #Scale it to tip chord size
    def tip_section_outer(self):
        return ScaledCurve(
            curve_in=self.tip_section_unscaled_outer,
            reference_point=self.tip_section_unscaled_outer.start,
            factor=self.tip_chord, hidden=True
        )

    @Part #The outer part of the wing
    def wing_loft_surf_outer(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.tip_section_inner, self.tip_section_outer],
            mesh_deflection=0.0001
        )

    @Part  # Mirror and move outer wing (for left wing)
    def transform_mirror_wing_outer(self):
        return TransformedSurface(
            surface_in=MirroredSurface(surface_in=self.wing_loft_surf_outer, reference_point=Point(0, 0, 0),
                                       vector1=(1, 0, 0),
                                       vector2=(0, 0, 1)),  # Original curve to transform
            from_position=self.position,  # Reference position of the original curve
            to_position=translate(XOY, 'x', -1, 'y', -2*self.width_centerpiece)  # New position of the curve
        )

    @Part #Initiate the wingbox, which inherits quite some things from the wing
    def my_wingbox(self):
        return Wingbox(start_wing_to_kink=self.start_wing_to_kink, tip_chord_kink=self.tip_chord_kink, pts=self.pts,
                       front_spar_coordinates=self.front_spar_coordinates,
                       rear_spar_coordinates=self.rear_spar_coordinates,  # these are attributes
                       span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                       wing_material=self.wing_material,
                       kink_location=self.kink_location, tip_chord=self.tip_chord,
                       width_centerpiece=self.width_centerpiece,
                       position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))

    @Part #Same for the centerpiece
    def my_centerpiece(self):
        return Centerpiece(start_wing_to_kink=self.start_wing_to_kink, tip_chord_kink=self.tip_chord_kink, pts=self.pts,
                           front_spar_coordinates=self.front_spar_coordinates,
                           rear_spar_coordinates=self.rear_spar_coordinates,  # these are attributes
                           span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                           kink_location=self.kink_location, tip_chord=self.tip_chord,
                           width_centerpiece=self.width_centerpiece,
                           position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))


def generate_warning(warning_header, msg):
    """
    This function generates the warning dialog box
    :param warning_header: The text to be shown on the dialog box header
    :param msg: the message to be shown in dialog box
    :return: None as it is GUI operation
    """
    from tkinter import Tk, messagebox

    # initialization
    window = Tk()
    window.withdraw()

    # generates message box and waits for user to close it
    messagebox.showwarning(warning_header, msg)

    # kills the gui
    window.deiconify()
    window.destroy()
    window.quit()


# if __name__ == '__main__':
#     from parapy.gui import display
#
#     obj = Wing_me()
#     display(obj)