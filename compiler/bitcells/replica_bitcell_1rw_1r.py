# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#
import debug
import bitcell_base
from tech import cell_properties as props
from globals import OPTS


class replica_bitcell_1rw_1r(bitcell_base.bitcell_base):
    """
    A single bit cell which is forced to store a 0.
    This module implements the single memory cell used in the design. It
    is a hand-made cell, so the layout and netlist should be available in
    the technology library. """

    pin_names = [props.bitcell.cell_1rw1r.pin.bl0,
                 props.bitcell.cell_1rw1r.pin.br0,
                 props.bitcell.cell_1rw1r.pin.bl1,
                 props.bitcell.cell_1rw1r.pin.br1,
                 props.bitcell.cell_1rw1r.pin.wl0,
                 props.bitcell.cell_1rw1r.pin.wl1,
                 props.bitcell.cell_1rw1r.pin.vdd,
                 props.bitcell.cell_1rw1r.pin.gnd]
    type_list = ["OUTPUT", "OUTPUT", "OUTPUT", "OUTPUT", "INPUT", "INPUT", "POWER", "GROUND"]
    
    def __init__(self, name, cell_name=None):
        if not cell_name:
            cell_name = OPTS.replica_bitcell_name
        super().__init__(name, cell_name)
        debug.info(2, "Create replica bitcell 1rw+1r object")

    def get_stage_effort(self, load):
        parasitic_delay = 1
        size = 0.5 #This accounts for bitline being drained thought the access TX and internal node
        cin = 3 #Assumes always a minimum sizes inverter. Could be specified in the tech.py file.
        read_port_load = 0.5 #min size NMOS gate load
        return logical_effort.logical_effort('bitline', size, cin, load+read_port_load, parasitic_delay, False)
        
    def input_load(self):
        """Return the relative capacitance of the access transistor gates"""
        
        # FIXME: This applies to bitline capacitances as well.
        # FIXME: sizing is not accurate with the handmade cell. Change once cell widths are fixed.
        access_tx_cin = parameter["6T_access_size"]/drc["minwidth_tx"]
        return 2*access_tx_cin

    def build_graph(self, graph, inst_name, port_nets):
        """Adds edges to graph. Multiport bitcell timing graph is too complex
           to use the add_graph_edges function."""
        pin_dict = {pin:port for pin,port in zip(self.pins, port_nets)}
        pins = props.bitcell.cell_1rw1r.pin
        #Edges hardcoded here. Essentially wl->bl/br for both ports.
        # Port 0 edges
        graph.add_edge(pin_dict[pins.wl0], pin_dict[pins.bl0], self)
        graph.add_edge(pin_dict[pins.wl0], pin_dict[pins.br0], self)
        # Port 1 edges
        graph.add_edge(pin_dict[pins.wl1], pin_dict[pins.bl1], self)
        graph.add_edge(pin_dict[pins.wl1], pin_dict[pins.br1], self)
