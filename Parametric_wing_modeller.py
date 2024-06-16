from parapy.geom import *
from parapy.core import *

from parapy.core.validate import *
from Parts import *
import Parts.output
from parapy.exchange import STEPWriter
import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from parapy.core.widgets import (
    Button, CheckBox, ColorPicker, Dropdown, FilePicker, MultiCheckBox,
    ObjectPicker, SingleSelection, TextField)
import math
import numpy as np
from csv import DictReader
import operator
import csv
import glob
from parapy.core.widgets import FilePicker
import warnings

DIR = os.path.dirname(__file__) #to be able to read the material from Excel file
material_library = pd.read_excel(io='Parts/Material_library.xlsx')
material_names=[]
for name in range(len(material_library.iloc[:, 0])):
    material_names.append(material_library.iloc[name, 0])


class Aircraft(GeomBase):
    """This is the Superclass. It only contains the Wing class."""
    aircraft_name = Input("my_aircraft_name")
    saved_aircraft_configuration = Input('Parts/output/my_aircraft_name_configuration.csv',
                                         widget=FilePicker(wildcard="*.csv", default_dir="Parts/output"))

    load_factor = Input(2.5, validator=GT(0, msg="Load factor cannot be smaller than " "{validator.limit}!"))
    aircraft_mass = Input(10000, validator=GT(0, msg="Aircraft mass cannot be smaller than " "{validator.limit}!"))
    engine_position = Input([4])  # , validator=Between(0, 60, msg="Engine position has to be between wing root and tip!"))
    engine_mass = Input(1000, validator=GE(0, msg="Engine mass cannot be smaller than " "{validator.limit}!"))
    material = Input(material_names[0], widget=Dropdown(material_names, autocompute=False))

    @Input
    def material_properties(self):
        index = material_names.index(self.material)
        density = material_library.iloc[index, 1]
        elastic_modulus = material_library.iloc[index, 2]
        poisson_ratio = material_library.iloc[index, 3]
        yield_strength = material_library.iloc[index, 4]
        return [density, elastic_modulus, poisson_ratio, yield_strength]

    @Part  # Since the centerpiece depends fully on the geometry of the wing and is basically an extended part of the wing
    #as well as the connection between the wings , it is a subclass of the wing
    def my_wing(self):
        return Parts.Wing(material=self.material,
                             position=translate(self.position, 'x', -1, 'y', 0, 'z',
                                                0))  # Puts the origin at the trailing edge of the kink

    @Part
    def write_inp(self):
        return Parts.AbaqusINPwriter(path=self.my_wing,
                                     density=self.my_wing.material_properties[0],
                                     elastic_modulus=self.my_wing.material_properties[1],
                                     poisson_ratio=self.my_wing.material_properties[2],
                                     skin_thickness=self.my_wing.skin_thickness,
                                     upper_inner_skin_thickness=self.my_wing.upper_inner_skin_thickness,
                                     upper_outer_skin_thickness=self.my_wing.upper_outer_skin_thickness,
                                     lower_inner_skin_thickness=self.my_wing.lower_inner_skin_thickness,
                                     lower_outer_skin_thickness=self.my_wing.lower_outer_skin_thickness,
                                     spar_thickness=self.my_wing.spar_thickness,
                                     rib_thickness=self.my_wing.rib_thickness,
                                     centre_section_skin_thickness=self.my_wing.centre_section_skin_thickness,
                                     centre_section_spar_thickness=self.my_wing.centre_section_spar_thickness,
                                     centre_section_rib_thickness=self.my_wing.centre_section_rib_thickness,
                                     span=self.span,
                                     width_centerpiece=self.width_centerpiece,
                                     load_factor=self.load_factor,
                                     aircraft_mass=self.aircraft_mass,
                                     engine_position=self.engine_position,
                                     engine_mass=self.engine_mass,
                                     hidden=False)

    @action()
    def INP_file_writer(self):
        os.chdir(os.getcwd())
        self.write_inp.my_inp_writer.write('Parts//output//wing_box.inp')
        print('INP file was written successfully')

    @action()
    def run_abaqus(self):
        os.chdir('Parts/output')
        subprocess.run('python ODBinterpreter.py')
        # os.chdir(os.getcwd())
        print('Done running abaqus. Check directory for results')
        os.chdir(DIR)

    @action()
    def process_results(self):
        # os.chdir(DIR)
        # print(os.getcwd())
        stresses = pd.read_csv('Parts/output/mises_stress.csv', delimiter=",", dtype=object)
        U3 = pd.read_csv('Parts/output/U3.csv', delimiter=",", dtype=object)
        print('processing files, please wait')
        def check_if_float(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        mises = []
        X = []
        Y = []
        Z = []
        for i in range(len(stresses.iloc[:, ])):
            if check_if_float(stresses.iloc[i, -1]) and any("SPOS" in item for item in stresses.iloc[i, :]):
                mises.append(float(stresses.iloc[i, -1]))
                X.append(float(stresses.iloc[i, :].get('X')))
                Y.append(float(stresses.iloc[i, :].get('Y')))
                Z.append(float(stresses.iloc[i, :].get('Z')))
            else:
                continue

        yield_exceeded = []
        Y_for_yield_exceeded = []
        for i in range(len(mises)):
            if mises[i] > self.my_wing.material_properties[3]:
                yield_exceeded.append(mises[i])
                Y_for_yield_exceeded.append(Y[i])
            else:
                continue
                # yield_exceeded.append(0)

        print('Plotting results, please wait')

        plt.scatter(Y, mises)
        plt.scatter(Y_for_yield_exceeded, yield_exceeded, color='red', s=5)
        plt.xlabel('Spanwise direction [m]')
        plt.ylabel('Mises stress [Pa]')
        plt.title('Mises stress along wingspan')
        plt.legend(['Mises stress', 'Mises stress > yield strength'])
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        plt.savefig('Parts/output/mises_stress_distribution.png')
        plt.show()

        U3_magnitude = []
        U3_X = []
        U3_Y = []
        U3_Z = []
        # check_if_float(stresses.iloc[i, -1])
        for i in range(len(U3.iloc[:, ])):
            if check_if_float(U3.iloc[i, -1]):
                U3_magnitude.append(float(U3.iloc[i, -1]))
                U3_X.append(float(U3.iloc[i, :].get('X')))
                U3_Y.append(float(U3.iloc[i, :].get('Y')))
                U3_Z.append(float(U3.iloc[i, :].get('Z')))

        plt.scatter(Y, Z)
        plt.scatter(U3_Y, U3_magnitude, color='red', s=5)
        plt.xlabel('Spanwise direction [m]')
        plt.ylabel('U3 Deformation [m]')
        plt.title('Deformation along wingspan')
        plt.legend(['Undeformed', 'Deformed'])
        plt.axis('equal')
        plt.savefig('Parts/output/defomred_wing.png')
        plt.show()

        print('Results were processed successfully')
        print('max U3 displacement is: ', max(U3_magnitude), '[m]', 'and max mises stress is: ', max(mises), '[Pa]')


    @action()
    def save_aircraft_configuration(self):
        os.chdir(DIR)
        user_input_list = {"Parameter": "Value",
                           "aircraft_name": self.aircraft_name,
                           "span": self.my_wing.span,
                           "leading_edge_sweep": self.my_wing.leading_edge_sweep,
                           "root_chord": self.my_wing.root_chord,
                           "material_name": self.my_wing.material,
                           "material_density": self.my_wing.material_properties[0],
                           "material_elastic_modulus": self.my_wing.material_properties[1],
                           "material_poisson_ratio": self.my_wing.material_properties[2],
                           "skin_thickness": self.my_wing.skin_thickness,
                           "upper_inner_skin_thickness": self.my_wing.upper_inner_skin_thickness,
                           "upper_outer_skin_thickness": self.my_wing.upper_outer_skin_thickness,
                           "lower_inner_skin_thickness": self.my_wing.lower_inner_skin_thickness,
                           "lower_outer_skin_thickness": self.my_wing.lower_outer_skin_thickness,
                           "spar_thickness": self.my_wing.spar_thickness,
                           "rib_thickness": self.my_wing.rib_thickness,
                           "centre_section_skin_thickness": self.my_wing.centre_section_skin_thickness,
                           "centre_section_spar_thickness": self.my_wing.centre_section_spar_thickness,
                           "centre_section_rib_thickness": self.my_wing.centre_section_rib_thickness}

        filename = f"Parts/output/{user_input_list['aircraft_name']}_configuration.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for key, value in user_input_list.items():
                writer.writerow([key, value])
        print('Custom aircraft configuration was saved successfully')

    @action()
    def open_saved_aircraft_configuration(self):

        class SavedAircraft(Aircraft):
            os.chdir(DIR)

            read_csv = pd.read_csv(self.saved_aircraft_configuration, delimiter=",")
            wing_param = []
            for i in range(len(read_csv) - 1):
                wing_param.append(read_csv.iloc[i + 1, 1])

            @Part
            def wing_from_file(self):
                return Aircraft(span_inp=float(self.wing_param[0]),
                                leading_edge_sweep=float(self.wing_param[1]),
                                root_chord=float(self.wing_param[2]),
                                material=self.wing_param[5],
                                skin_thickness=float(self.wing_param[9]),
                                upper_inner_skin_thickness=float(self.wing_param[10]),
                                upper_outer_skin_thickness=float(self.wing_param[11]),
                                lower_inner_skin_thickness=float(self.wing_param[12]),
                                lower_outer_skin_thickness=float(self.wing_param[13]),
                                spar_thickness=float(self.wing_param[14]),
                                rib_thickness=float(self.wing_param[15]),
                                centre_section_skin_thickness=float(self.wing_param[16]),
                                centre_section_spar_thickness=float(self.wing_param[17]),
                                centre_section_rib_thickness=float(self.wing_param[18]))


        if __name__ == '__main__':
            from parapy.gui import display

            obj = SavedAircraft()
            display(obj)

    @Part
    def step_writer_unified_wing(self):
        return STEPWriter(nodes=[self.my_wing.wing_loft_surf_inner,
                                 self.my_wing.wing_loft_surf_outer,
                                 self.my_wing.my_wingbox.my_spars.front_spar_inner,
                                 self.my_wing.my_wingbox.my_spars.frontspar_outer,
                                 self.my_wing.my_wingbox.my_spars.rearspar_inner,
                                 self.my_wing.my_wingbox.my_spars.rearspar_outer,
                                 self.my_wing.my_wingbox.my_ribs.root_rib,
                                 self.my_wing.my_wingbox.my_ribs.tip_rib,
                                 self.my_wing.my_wingbox.my_ribs.ribs_cut,
                                 self.my_wing.my_wingbox.my_stringers.stringer_upper_inner,
                                 self.my_wing.my_wingbox.my_stringers.stringer_upper_outer,
                                 self.my_wing.my_wingbox.my_stringers.stringer_lower_inner,
                                 self.my_wing.my_wingbox.my_stringers.stringer_lower_outer,
                                 self.my_wing.my_centerpiece.upperskin_centerpiece_loft,
                                 self.my_wing.my_centerpiece.lowerskin_centerpiece_loft,
                                 self.my_wing.my_centerpiece.frontspar_surf_centerpiece,
                                 self.my_wing.my_centerpiece.rearspar_loft_centerpiece,
                                 self.my_wing.my_centerpiece.ribs_cp,
                                 self.my_wing.my_centerpiece.stringer_upper_CP,
                                 self.my_wing.my_centerpiece.stringer_lower_CP,
                                 self.my_wing.transform_mirror_wing_inner,
                                 self.my_wing.transform_mirror_wing_outer,
                                 self.my_wing.my_centerpiece.transform_mirror_CP_upperskin,
                                 self.my_wing.my_centerpiece.transform_mirror_CP_lowerskin,
                                 self.my_wing.my_centerpiece.transform_mirror_CP_frontspar,
                                 self.my_wing.my_centerpiece.transform_mirror_CP_rearspar],
                          default_directory='Parts/output',
                          unit='M',
                          filename="wing.step")
    @Part
    def step_writer_full_assembly(self):
        return STEPWriter(trees=[self.wing],
                          default_directory='Parts/output',
                          unit='M',
                          filename="wing_assembly.step")

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

if __name__ == '__main__':
    from parapy.gui.data import DataPanel

    # DataPanel.POPUP_EXCEPTIONS = False
    # DataPanel.LOG_EXCEPTIONS = False
    obj = Aircraft(label="Aircraft")
    from parapy.gui import display
    display(obj)
