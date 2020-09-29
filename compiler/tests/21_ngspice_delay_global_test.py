#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#
import unittest
from testutils import *
import sys,os
sys.path.append(os.getenv("OPENRAM_HOME"))
import globals
from globals import OPTS
from sram_factory import factory
import debug

class timing_sram_test(openram_test):

    def runTest(self):
        config_file = "{}/tests/configs/config".format(os.getenv("OPENRAM_HOME"))
        globals.init_openram(config_file)
        OPTS.spice_name="ngspice"
        OPTS.analytical_delay = False
        OPTS.netlist_only = True

        # This is a hack to reload the characterizer __init__ with the spice version
        from importlib import reload
        import characterizer
        reload(characterizer)
        from characterizer import delay
        from sram_config import sram_config
        OPTS.local_array_size = 8
        OPTS.route_supplies = False
        c = sram_config(word_size=8,
                        num_words=32,
                        num_banks=1)

        c.words_per_row=2
        c.recompute_sizes()
        debug.info(1, "Testing timing for global hierarchical array")
        s = factory.create(module_type="sram", sram_config=c)

        tempspice = OPTS.openram_temp + "temp.sp"
        s.sp_write(tempspice)

        probe_address = "1" * s.s.addr_size
        probe_data = s.s.word_size - 1
        debug.info(1, "Probe address {0} probe data bit {1}".format(probe_address, probe_data))

        corner = (OPTS.process_corners[0], OPTS.supply_voltages[0], OPTS.temperatures[0])
        d = delay(s.s, tempspice, corner)
        import tech
        loads = [tech.spice["dff_in_cap"]*4]
        slews = [tech.spice["rise_time"]*2]
        data, port_data = d.analyze(probe_address, probe_data, slews, loads)
        #Combine info about port into all data
        data.update(port_data[0])

        if OPTS.tech_name == "freepdk45":
            golden_data = {'slew_lh': [0.2592187],
                           'slew_hl': [0.2592187],
                           'delay_lh': [0.2465583],
                           'disabled_write0_power': [0.1924678],
                           'disabled_read0_power': [0.152483],
                           'write0_power': [0.3409064],
                           'disabled_read1_power': [0.1737818],
                           'read0_power': [0.3096708],
                           'read1_power': [0.3107916],
                           'delay_hl': [0.2465583],
                           'write1_power': [0.26915849999999997],
                           'leakage_power': 0.002044307,
                           'min_period': 0.898,
                           'disabled_write1_power': [0.201411]}
        elif OPTS.tech_name == "scn4m_subm":
            golden_data =  {'delay_hl': [1.8435739999999998],
                            'delay_lh': [1.8435739999999998],
                            'disabled_read0_power': [5.917947],
                            'disabled_read1_power': [7.154297],
                            'disabled_write0_power': [7.696351],
                            'disabled_write1_power': [7.999409000000001],
                            'leakage_power': 0.004809726,
                            'min_period': 6.875,
                            'read0_power': [11.833079999999999],
                            'read1_power': [11.99236],
                            'slew_hl': [1.8668490000000002],
                            'slew_lh': [1.8668490000000002],
                            'write0_power': [13.287510000000001],
                            'write1_power': [10.416369999999999]}
        else:
            self.assertTrue(False) # other techs fail

        # Check if no too many or too few results
        self.assertTrue(len(data.keys())==len(golden_data.keys()))
        
        self.assertTrue(self.check_golden_data(data,golden_data,0.25))

        globals.end_openram()

# run the test from the command line
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main(testRunner=debugTestRunner())
