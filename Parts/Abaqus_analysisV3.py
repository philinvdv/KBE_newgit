from parapy.lib.abaqus.primitive.feature import SurfaceInteraction
from parapy.mesh.core.groups import FaceGroup, EdgeGroup
from parapy.mesh.salome.controls import FixedNumber, Quad
from parapy.mesh.salome.main import Mesh
from parapy.lib.abaqus.primitive.load import CLoad, DLoad, Dsload
from parapy.lib.abaqus.adaptor import Adaptor
from parapy.lib.abaqus.primitive.component import Dynamic, Step, Static
from parapy.lib.abaqus.primitive.material import \
    Density, ElasticIsotropic, Material
from parapy.lib.abaqus.primitive.output import FieldOutput, HistoryOutput
from parapy.lib.abaqus.primitive.section import ShellSectionProperties
from parapy.lib.abaqus.writer import Writer
from parapy.mesh import Controls, Groups
from parapy.core import *
from parapy.geom import *
import numpy as np
from parapy.core.validate import *

#import MyAssinmnetV2
from Parts.Meshing import MeshingFunc
#from MyAssinmnetV2 import Aircraft
#from Parts.Wing_Class import Wing_me
#import Wing_Class

class AbaqusINPwriter(GeomBase):
    # n_mesh_points = Input(30)
    path = Input()
    mesh_element_length = Input(0.2, validator=GT(0, msg="Mesh element length cannot be smaller than " "{validator.limit}!"))
    density = Input(1000., validator=GT(0, msg="Material density cannot be smaller than " "{validator.limit}!"))
    elastic_modulus = Input(1e9, validator=GT(0, msg="Elastic modulus cannot be smaller than " "{validator.limit}!"))
    poisson_ratio = Input(0.3)
    skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    spar_thickness = Input(0.01, validator=GT(0, msg="Spar thickness cannot be smaller than " "{validator.limit}!"))
    rib_thickness = Input(0.005, validator=GT(0, msg="Rib thickness cannot be smaller than " "{validator.limit}!"))
    load_factor = Input(2.5)
    aircraft_mass = Input(10000, validator=GT(0, msg="Aircraft mass cannot be smaller than " "{validator.limit}!"))
    span = Input(10, validator=GT(0, msg="Wing span cannot be smaller than " "{validator.limit}!"))
    width_centerpiece = Input(3, validator=GT(0, msg="Centre section width cannot be smaller than " "{validator.limit}!"))
    # number_of_engines = Input(1)
    engine_position = Input([4, 8])
    engine_mass = Input(1000, validator=GE(0, msg="Engine cannot be smaller than " "{validator.limit}!"))
    Gravity = 9.81

    @Attribute
    def aircraft(self):
        return self.path

    @Attribute
    def material(self):
        material_behaviours = [Density(self.density), ElasticIsotropic(self.elastic_modulus, self.poisson_ratio)]
        material_properties = Material(name="test_material-2",
                        behaviours=material_behaviours)
        return material_properties


# below are all the parts that make up the wing box

    #All the skins:
    @Part
    def upper_skin(self):
        return Fused(shape_in=self.aircraft.my_skins.fused_inner_upperskin_and_flanges,
                     tool=self.aircraft.my_skins.fused_outer_upperskin_and_flanges,
                             hidden=False)

    @Part
    def lower_skin(self):
        return Fused(shape_in=self.aircraft.my_skins.fused_inner_lowerskin_and_flanges,
                     tool=self.aircraft.my_skins.fused_outer_lowerskin_and_flanges,
                             hidden=False)

    # All the spars:
    @Part
    def front_spar(self):
        return Fused(shape_in=self.aircraft.my_spars.front_spar_inner,
                     tool=self.aircraft.my_spars.frontspar_outer,
                             hidden=False)

    @Part
    def rear_spar(self):
        return Fused(shape_in=self.aircraft.my_spars.rearspar_inner,
                     tool=self.aircraft.my_spars.rearspar_outer,
                             hidden=False)



    @Part
    def meshed_upper_skin(self):
        return MeshingFunc(part_class=self.upper_skin,
                           groups=[FaceGroup(shape=self.upper_skin.faces)] +
                                  [EdgeGroup(shape=self.upper_skin.edges)] +
                                  [FaceGroup(shape=[self.upper_skin.faces[0], self.upper_skin.faces[3]])] +
                                  [FaceGroup(shape=self.upper_skin.faces[idx]) for idx in range(len(self.upper_skin.faces))] +
                                  [EdgeGroup(shape=self.upper_skin.edges[idy]) for idy in range(len(self.upper_skin.edges))],
                           mesh_element_length=self.mesh_element_length)
    @Part
    def meshed_lower_skin(self):
        return MeshingFunc(part_class=self.lower_skin,
                           groups=[FaceGroup(shape=self.lower_skin.faces)] +
                                  [EdgeGroup(shape=self.lower_skin.edges)] +
                                  [FaceGroup(shape=[self.lower_skin.faces[0], self.lower_skin.faces[3]])] +
                                  [FaceGroup(shape=self.lower_skin.faces[idx]) for idx in range(len(self.lower_skin.faces))] +
                                  [EdgeGroup(shape=self.lower_skin.edges[idy]) for idy in range(len(self.lower_skin.edges))],
                           mesh_element_length=self.mesh_element_length)
    @Part
    def meshed_front_spar(self):
        return MeshingFunc(part_class=self.front_spar,
                           groups=[FaceGroup(shape=self.front_spar.faces)] +
                                  [EdgeGroup(shape=self.front_spar.edges)] +
                                  [FaceGroup(shape=self.front_spar.faces[idx]) for idx in range(len(self.front_spar.faces))] +
                                  [EdgeGroup(shape=self.front_spar.edges[idy]) for idy in range(len(self.front_spar.edges))],
                           mesh_element_length=self.mesh_element_length)
    @Part
    def meshed_rear_spar(self):
        return MeshingFunc(part_class=self.rear_spar,
                           groups=[FaceGroup(shape=self.rear_spar.faces)] +
                                  [EdgeGroup(shape=self.rear_spar.edges)] +
                                  [FaceGroup(shape=self.rear_spar.faces[idx]) for idx in range(len(self.rear_spar.faces))] +
                                  [EdgeGroup(shape=self.rear_spar.edges[idy]) for idy in range(len(self.rear_spar.edges))],
                           mesh_element_length=self.mesh_element_length)

    @Attribute
    def skin_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.skin_thickness)

    @Attribute
    def spar_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.spar_thickness)

    @Attribute
    def rib_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.rib_thickness)


# Adaptor to write the inp file

    @Attribute
    def my_abaqus_adaptor(self):
        my_obj = Adaptor()

        # First part: upper skin
        my_obj.process_2d_part(self.upper_skin,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_upper_skin.mesh.subgrid[0], self.skin_material_properties)],
        preferred_name=f"Upper_Skin"
        )
        # Second part: lower skin
        my_obj.process_2d_part(self.lower_skin,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_lower_skin.mesh.subgrid[0], self.skin_material_properties)],
        preferred_name=f"lower_Skin"
        )
        # Third part: front spar
        my_obj.process_2d_part(self.front_spar,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_front_spar.mesh.subgrid[0], self.spar_material_properties)],
        preferred_name=f"front_spar"
        )
        # Forth part: rear spar
        my_obj.process_2d_part(self.rear_spar,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_rear_spar.mesh.subgrid[0], self.spar_material_properties)],
        preferred_name=f"rear_spar"
        )

        #U=upper
        #L=lower
        #I=inner
        #O=outer
        #F=front
        #R=rear

        # Connection between upper skin flange and inner rear spar
        UIR_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[1]),
                                                               "SPOS")

        UIF_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[2]),
                                                               "SPOS")

        UOR_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[4]),
                                                               "SPOS")

        UOF_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[5]),
                                                               "SPOS")

        LIR_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[1]),
                                                               "SPOS")

        LIF_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[2]),
                                                               "SPOS")

        LOR_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[4]),
                                                               "SPOS")

        LOF_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[5]),
                                                               "SPOS")

        UIR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0].edges[0]))

        LIR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0].edges[2]))

        UOR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[1]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[1].edges[0]))

        LOR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[1]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[1].edges[2]))

        UIF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0].edges[0]))

        LIF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0].edges[2]))

        UOF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[1]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[1].edges[0]))

        LOF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[1]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[1].edges[2]))
        #Upper connections
        my_obj.process_tie(UIR_skin_tie, UIR_spar_tie, "Surface to Surface")
        my_obj.process_tie(UOR_skin_tie, UOR_spar_tie, "Surface to Surface")
        my_obj.process_tie(UIF_skin_tie, UIF_spar_tie, "Surface to Surface")
        my_obj.process_tie(UOF_skin_tie, UOF_spar_tie, "Surface to Surface")
        #Lower connections
        my_obj.process_tie(LIR_skin_tie, LIR_spar_tie, "Surface to Surface")
        my_obj.process_tie(LOR_skin_tie, LOR_spar_tie, "Surface to Surface")
        my_obj.process_tie(LIF_skin_tie, LIF_spar_tie, "Surface to Surface")
        my_obj.process_tie(LOF_skin_tie, LOF_spar_tie, "Surface to Surface")


        # boundary conditions
        my_obj.process_boundary_condition(self.upper_skin, self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[0].edges[1]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)
        my_obj.process_boundary_condition(self.lower_skin, self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[0].edges[1]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)
        my_obj.process_boundary_condition(self.front_spar, self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0].edges[1]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)
        my_obj.process_boundary_condition(self.rear_spar, self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0].edges[1]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)

        # Engine as point masses
        # for n in range(len(self.engine_position)):
        #     pairs = [(self.lower_skin, node) for node in self.engine_mass_nodes[n]]
        #     my_obj.process_point_mass(pairs, self.engine_mass, preferred_name=f"engine_{n}_point_mass")


        return my_obj

    @Attribute
    def engine_mass_nodes(self):
        nodes_per_engine = []
        nodes_of_all_engines = []
        for n in range(len(self.engine_position)):
            for i in range(len(self.spanwise_nodes[1])):
                if abs(self.engine_position[n] - self.spanwise_nodes[1][i][1]) <= self.mesh_element_length:
                    nodes_per_engine.append(self.spanwise_nodes[1][i])
                else:
                    continue
            nodes_of_all_engines.append(nodes_per_engine)
            nodes_per_engine = []
        return nodes_of_all_engines

    @Attribute
    def spanwise_nodes(self):
        upper_surface_nodes_y_coord = []
        lower_surface_nodes_y_coord = []

        for i in range(len(self.meshed_upper_skin.mesh.subgrid[2].nodes)):
            upper_surface_nodes_y_coord.append(self.meshed_upper_skin.mesh.subgrid[2].nodes[i])
            lower_surface_nodes_y_coord.append(self.meshed_lower_skin.mesh.subgrid[2].nodes[i])
        upper_surface_nodes_y_coord.sort(key=lambda x: x[1])
        lower_surface_nodes_y_coord.sort(key=lambda x: x[1])
        return [upper_surface_nodes_y_coord, lower_surface_nodes_y_coord]


    @Attribute
    def loads(self):

        n_sections = round((0.5*self.span - self.width_centerpiece)/self.mesh_element_length)
        span_sections = np.linspace(self.spanwise_nodes[0][0][1],
                                    self.spanwise_nodes[0][-1][1],
                                    n_sections)
        node_sets = []
        node_per_section = []
        for s in range(len(span_sections)-1):
            for i in range(len(self.spanwise_nodes[0])):
                if (self.spanwise_nodes[0][i][1] <= span_sections[s+1] and self.spanwise_nodes[0][i][1] >= span_sections[s]):
                    node_per_section.append(self.spanwise_nodes[0][i])
                else:
                    continue
            node_sets.append(node_per_section)
            node_per_section = []

        F_total = 0.5 * self.aircraft_mass * self.load_factor * self.Gravity
        F_y = []
        F_num = 0
        n_x_nodes = []
        n_y_nodes = []
        for i in range(len(span_sections)):
            F_num = F_num + (1 - (span_sections[i] / span_sections[-1]))
        F_0 = F_total / F_num
        for i in range(len(span_sections)):
            F_y.append(F_0 * (1 - (span_sections[i] / span_sections[-1])))

        for i in range(len(node_sets)):
            n_x_nodes.append(len(node_sets[i]))

        F_x = [m/n for m, n in zip(F_y, n_x_nodes)]

        node_lift_load = []
        for i in range(len(node_sets)):
            node_set = self.my_abaqus_adaptor.add_set(node_sets[i], part=self.upper_skin, preferred_name="loadpoints")
            # cload.append(CLoad(nodes=[], node_sets=[node_set], F3=F_x[i]))
            node_lift_load.append(CLoad(nodes=[], node_sets=[node_set], F3=F_y[i]))
            # element_load.append(DLoad(elements=[], element_sets=[node_set], load_type='P', magnitude=F_y[i]))

        node_engine_load = []
        for n in range(len(self.engine_position)):
            engine_node_set = self.my_abaqus_adaptor.add_set(self.engine_mass_nodes[n], part=self.lower_skin, preferred_name=f"engine_{n}_mass")
            node_engine_load.append(CLoad(nodes=[], node_sets=[engine_node_set], F3=-self.engine_mass*self.Gravity))

        return [node_lift_load, node_engine_load], [span_sections, node_per_section, node_sets, n_x_nodes, F_total, F_0, F_y, F_x, F_num]


    # @Attribute
    # def force_lines(self):
    #     lines = []
    #     for i in range(len(self.loads[1])):
    #         lines.append([LineSegment(Point(0, self.loads[1][i], 0),
    #                                   Point(0, self.loads[1][i], 0.0005*self.loads[7][i]))])
    #     return lines



    @property
    def my_outputs(self):
        return [FieldOutput(name="field-output"), HistoryOutput(name="history-output")]


    @property
    def my_step(self):
        return Step(name="analysis1",
                    linear=True,
                    step_options=[Static(time_period=1.,
                                         minimum_time_increment=1e-15,
                                         maximum_time_increment=0.1,
                                         initial_time_increment=0.01)],
                    loads=self.loads[0][0] + self.loads[0][1],
                    boundary_conditions=[],
                    outputs=self.my_outputs,
                    interactions=[])

    @Attribute
    def my_inp_writer(self):
        return Writer(adaptor=self.my_abaqus_adaptor, steps=[self.my_step])



if __name__ == '__main__':
    from parapy.gui import display

    my_obj = AbaqusINPwriter()
    my_obj.my_inp_writer.write('output//wing_box.inp')
    display(my_obj)
