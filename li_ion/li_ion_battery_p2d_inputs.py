# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 14:27:54 2018

@author: dkorff
"""

import numpy as np
#import cantera as ct

class Inputs():
    # These flags specify whether to include each element (anode, separator,
    #   cathode) in the simulation:
    flag_anode = 1
    flag_sep = 1
    flag_cathode = 1
    
    n_comps = flag_anode + flag_sep + flag_cathode
    
    # Number of discretized volumes in the y-direction:
    npoints_anode = 5*flag_anode
    npoints_cathode = 5*flag_cathode
    npoints_elyte = 3*flag_sep
    
    # Flag to allow re-equilibration between charge/discharge
    flag_re_equil = 1
    
    # These flags specify whether to plot various data
    plot_profiles_flag = 1
    plot_potential_profiles = 1*plot_profiles_flag  # Plots potential profiles
    plot_electrode_profiles = 1*plot_profiles_flag  # Plots solid phase mole fraction profiles
    plot_elyte_profiles = 1*plot_profiles_flag      # Plots concentration of Li+ in elyte phase
    plot_cap_flag = 0       # Plots dis/charge capacity curves
    
    # Options for plots
    
    # phi_time sets the options for the potential plot. 0 will plot a charge/
    #   discharge profile on a single axes. 1 will plot potential over time
    #   including the re-equilibration step (assuming re-equilibration is
    #   turned on).
    phi_time = 0*plot_potential_profiles

    # The C-rate is the rate of charge/discharge - how many charges/discharges
    #   can be carried out in 1 hour? This sets the current density:
    C_rate = 1
    
    # Set number of charge/discharge cycles to run
    n_cycles = 1
    
    # Flag to determine whether to use a constant dr or constant dv 
    #   discretization of the electrode particles
    particle_method = 'dr'
    
    # Simulation temperature (or initial temperature)
    T = 300  # [K]

    # Set initial SOC to generalize both electrode initial lithiation
    # Fully charged = anode fully lithiated, cathode fully de-lithiated.
    # Range of value is from 0 to 1.
    SOC_0 = 0.03

    # Number of "shells" in anode particle:
    nshells_anode = 5
    n_shells_cathode = 5

    "Cantera and CTI file info:"
#    ctifile = 'lithium_ion_battery_ideal_LCO.cti'
#    ctifile = 'lithium_ion_battery_updated.cti'
    ctifile = 'lithium_ion_battery_mod.cti'
    anode_phase = 'anode'
    cathode_phase = 'cathode'
    metal_phase = 'electron'
    elyte_phase = 'electrolyte'
    anode_surf_phase = 'edge_anode_electrolyte'
    cathode_surf_phase = 'edge_cathode_electrolyte'

    Li_species_anode = 'Li[anode]'
    Vac_species_anode = 'V[anode]'
    Li_species_cathode = 'Li[cathode]'
    Vac_species_cathode = 'V[cathode]'
    
    Li_species_elyte = 'Li+[elyt]'

    Phi_anode_init = 0.0
    Phi_elyte_init = 2.5
    Delta_Phi_init = 4.0

    # Cutoff Values for lithiation and delithiation of anode:
    Li_an_min = 0.005; Li_an_max = 1 - Li_an_min
    Li_cat_min = 0.005; Li_cat_max = 1 - Li_cat_min

    "Anode geometry and transport"
    # Microstructure
    eps_solid_an = 0.6  # Graphite volume fraction [-]
    tau_an = 1.6        # Tortuosity - assume equal values for carbon and elyte [-]
    r_p_an = 5e-6       # Average pore radius [m]
    d_part_an = 5e-6    # Average particle diameter for graphite [m]
    overlap_an = 0.4    # Percentage of anode particle overlapping with other
                        #   anode particles.  Reduces total anode/elyte
                        #   surface area.
    H_an = 25e-6        # Anode thickness [m]

    # Other Parameters
    C_dl_an = 1.5e-2    # Double-layer capacitance [F/m^2]
    sigma_an = 75.0     # Bulk anode electrical conductivity [S/m]

    D_Li_an = 7.5e-16   # Bulk diffusion coefficient for Li in graphite [m^2/s]
    D_Li_an_el = np.array([1e-12, 1e-12, 1e-10, 3e-11])

    "Electrolyte geometry and transport"
    # Separator thickness [m]
    H_elyte = 25e-6
    # Elyte species bulk diffusion coefficients [m^2/s]
    D_Li_elyte = np.array([1e-12, 1e-12, 1e-10, 3e-11])
    z_k_elyte = np.array([0., 0., 1., -1.])

    eps_elyte_sep = 0.5 # Separator electrolyte volume fraction
    tau_sep = 1.6       # Tortuosity of separator
    sigma_sep = 50.0    # Bulk ionic conductivity of separator [S/m]

    "Cathode geometry and transport"
    # Microstructure:
    eps_solid_ca = 0.5  # LiCoO2 volume fraction [-]
    tau_ca = 1.6        # Tortuosity - assume equal values for LiCoO2 and elyte [-]
    r_p_ca = 5e-6       # Average pore radius [m]
    d_part_ca = 5e-6    # Average particle diameter for LiCoO2 [m]
    overlap_ca = 0.4    # Percentage of anode particle overlapping with other
                        #   anode particles.  Reduces total anode/elyte
                        #   surface area.
    H_ca = 25e-6        # Cathode thickness [m]

    # Other parameters:
    C_dl_ca = 1.5e-2    # Double-layer capacitance [F/m^2]
    sigma_ca = 7.50     # Bulk cathode electrical conductivity [S/m]
    D_Li_ca = 7.5e-16   # Bulk diffusion coefficient for Li in LiCoO2 [m^2/s]
    D_Li_cat_el = np.array([1e-12, 1e-12, 1e-10, 3e-11])
    
print("Runner check")

#if __name__ == "__main__":
#    exec(open("li_ion_battery_p2d_init.py").read())
#    exec(open("li_ion_battery_p2d_model.py").read())
