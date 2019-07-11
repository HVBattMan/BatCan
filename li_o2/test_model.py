"""
Author:
Amy LeBar (20 August 2018)
Li-O2 Battery Model:
This model examines the reactions taking place within the carbon-based
cathode of a Li-O2 battery. Electrolyte = 1 M LiTFSI in TEGDME
"""

# Load any needed modules
import numpy as np
import cantera as ct

import sys
sys.path.append('../')

from functions.diffusion_coeffs import dst as dst
from functions.diffusion_coeffs import cst as cst

def LiO2_func(t,SV,params,objs,geom,ptr,SVptr):
    print('t =',t)

    # Pull phases out of 'objs' inside function
    gas = objs['gas']
    cath_b = objs['cath_b']
    elyte = objs['elyte']
    oxide = objs['oxide']
    inter = objs['inter']
    air_elyte = objs['air_elyte']
    Li_b = objs['Li_b']
    Li_s = objs['Li_s']

    dSVdt = np.zeros_like(SV)

    # Pull parameters out of 'params' inside function
    i_ext = params['i_ext']
    T = params['T']
    Ny_cath = params['Ny_cath']
    dyInv_cath = params['dyInv_cath']
    Ny_sep = params['Ny_sep']
    dyInv_sep = params['dyInv_sep']
    A_int = params['A_int']
    C_dl = params['C_dl']
    E_carb_inv = params['E_carb_inv']
    E_sep_inv = params['E_sep_inv']
    Zk_elyte = params['Zk_elyte']
    R_sep = params['R_sep']
    SV_single_cath = params['SV_single_cath']
    SV_single_sep = params['SV_single_sep']

    W_elyte = elyte.molecular_weights

    " ======================================== CATHODE ======================================== "
    " --- Pre-loop --- "
    # Set potentials and concentrations for 'next'
    cath_b.electric_potential = 0
    elyte.electric_potential = SV[SVptr['phi']]
    elyte.TDY = T, sum(SV[SVptr['elyte']]), SV[SVptr['elyte']]
    Yk_next = elyte.Y
    Xk_next = elyte.X
    Ck_elyte_next = elyte.concentrations
#    Yk_next = SV[SVptr['elyte']]
#    Xk_next = Yk_next * sum(W_elyte) / W_elyte
    inter.coverages = SV[SVptr['theta']]
    phi_elyte_next = elyte.electric_potential

    # Mass transport and ionic current at air/elyte BC
    Nk_top = air_elyte.get_net_production_rates(elyte)
    i_io_top = 0

    Nk_bot = np.zeros_like(Nk_top)

    # Initialize SV pointer offset
    SV_move = 0

    for j in np.arange(Ny_cath - 1):
        phi_elyte_this = phi_elyte_next
        phi_elyte_next = SV[SVptr['phi']+SV_move+SV_single_cath]
        Xk_this = Xk_next
        Ck_elyte_this = Ck_elyte_next
        elyte.TDY = T, sum(SV[SVptr['elyte']+SV_move+SV_single_cath]), SV[SVptr['elyte']+SV_move+SV_single_cath]
        Yk_next = elyte.Y
        Xk_next = elyte.X
        Ck_elyte_next = elyte.concentrations
#        Yk_next = SV[SVptr['elyte']+SV_move+SV_single_cath]
#        Xk_next = Yk_next * sum(W_elyte) / W_elyte
#
        # Mass transport and ionic current
        u_k = np.zeros_like(Yk_next)

        Ck_elyte_int = 0.5*(Ck_elyte_this + Ck_elyte_next)

        if params['transport'] == 'cst':
            Dk_elyte = cst(Ck_elyte_int,objs,params)[0]
            Dk_elyte_mig = cst(Ck_elyte_int,objs,params)[1]
        if params['transport'] == 'dst':
            Dk_elyte = dst(Ck_elyte_int,params)[0]
            Dk_elyte_mig = dst(Ck_elyte_int,params)[1]

        u_k = Dk_elyte / (ct.gas_constant * T)
        Xk_int = 0.5 * (Xk_this + Xk_next)

        Nk_bot = - u_k * Ck_elyte_int * (((ct.gas_constant * T) / Xk_int) * (Xk_next - Xk_this) * dyInv_cath \
                 + Zk_elyte * ct.faraday * (phi_elyte_next - phi_elyte_this) * dyInv_cath)

        i_io_bot = ct.faraday * sum(Zk_elyte * Nk_bot)

        elyte.TDY = T, sum(SV[SVptr['elyte']+SV_move]), SV[SVptr['elyte']+SV_move]
        # Calculate Faradaic current
        i_far = inter.get_net_production_rates(cath_b) * ct.faraday

        # Calculate change in double layer potential
        i_dl = (i_io_top - i_io_bot) * dyInv_cath + i_far*A_int          # double layer current
        dSVdt[SVptr['phi']+SV_move] = i_dl / (C_dl*A_int)

        # Calculate change in electrolyte concentrations
        sdot_int = inter.get_net_production_rates(elyte) * A_int
        sdot_dl = np.zeros_like(sdot_int)
        sdot_dl[ptr['Li+']] = -i_dl / (ct.faraday * Zk_elyte[ptr['Li+']])
        dSVdt[SVptr['elyte']+SV_move] = ((Nk_top - Nk_bot) * dyInv_cath \
                                        + (sdot_int + sdot_dl)) * W_elyte * E_carb_inv

        # Calculate change in surface coverages
        dSVdt[SVptr['theta']+SV_move] = inter.get_net_production_rates(inter) / inter.site_density

        # Set next 'top' flux and ionic current as current 'bottom'
        Nk_top = Nk_bot
        i_io_top = i_io_bot

        SV_move = SV_move + SV_single_cath                               # new SV offset value

        # Set potentials and concentrations for 'next' node
        cath_b.electric_potential = 0
        elyte.TDY = T, sum(SV[SVptr['elyte']+SV_move]), SV[SVptr['elyte']+SV_move]
        coverages = SV[SVptr['theta']+SV_move]/sum(SV[SVptr['theta']+SV_move])
        print(coverages)
        inter.coverages = coverages#SV[SVptr['theta']+SV_move]
        elyte.electric_potential = phi_elyte_next

    " --- Post-loop --- "
    # Set previous 'next' as current 'this'

    # Read out reaction terms, before setting electrolyte object state to that
    #   of the first separator node:

    # Calculate Faradaic current
    i_far = inter.get_net_production_rates(cath_b) * ct.faraday
    # Production rate of electrolyte species:
    sdot_int = inter.get_net_production_rates(elyte) * A_int
    # Production rate of surface species:
    sdot_surf = inter.get_net_production_rates(inter)

    phi_elyte_this = phi_elyte_next
    Xk_this = Xk_next

    elyte.TDY = T, sum(SV[SVptr['sep_elyte']]), SV[SVptr['sep_elyte']]
    Xk_next = elyte.X
    print(Xk_this,Xk_next)
    Xk_int = 0.5 * (Xk_this + Xk_next)

    elyte.TDY = T, sum(SV[SVptr['elyte']+SV_move]), SV[SVptr['elyte']+SV_move]

    # Molar transport and ionic current at separator BC
    i_io_bot = i_ext

    Ck_elyte = elyte.concentrations
    C_elyte = sum(Ck_elyte)

    if params['transport'] == 'cst':
        Dk_elyte = cst(Ck_elyte,objs,params)[0]
        Dk_elyte_mig = cst(Ck_elyte,objs,params)[1]
    if params['transport'] == 'dst':
        Dk_elyte = dst(Ck_elyte,params)[0]
        Dk_elyte_mig = dst(Ck_elyte,params)[1]

    u_k = Dk_elyte / (ct.gas_constant * T)

    """phi_elyte_next = phi_elyte_this - (i_io_bot + ct.faraday*ct.gas_constant*T*C_elyte \
                    * sum(Zk_elyte*u_k*(Xk_next - Xk_this) * dyInv_cath)) \
                    / (ct.faraday**2 *dyInv_cath * sum(Zk_elyte**2 * u_k * Ck_elyte))"""

    dyInv = 0.5*(dyInv_cath + dyInv_sep)
    phi_elyte_next = phi_elyte_this - (i_io_bot/dyInv + ct.faraday*ct.gas_constant*T*sum(u_k*Ck_elyte*Zk_elyte*(Xk_next - Xk_this)/Xk_int))/(ct.faraday**2*sum(u_k*Ck_elyte*Zk_elyte**2))

    print('phi =',phi_elyte_next)

    Nk_bot = - u_k * Ck_elyte * (((ct.gas_constant * T) / Xk_int) * (Xk_next - Xk_this) * dyInv \
            + Zk_elyte * ct.faraday * (phi_elyte_next - phi_elyte_this) * dyInv)

    i_io_bot_check = ct.faraday * sum(Zk_elyte * Nk_bot)
    print('i_io_check = ',i_io_bot_check,' i_ext = ',i_ext)
#    Nk_bot = np.zeros(elyte.n_species)
#    Nk_bot[ptr['Li+']] = i_io_bot / (ct.faraday * Zk_elyte[ptr['Li+']])



    # Calculate change in double layer potential
    i_dl = (i_io_top - i_io_bot) * dyInv_cath + i_far*A_int              # double layer current
    dSVdt[SVptr['phi']+SV_move] = i_dl / (C_dl*A_int)

    # Calculate change in electrolyte concentrations
    sdot_dl = np.zeros_like(sdot_int)
    sdot_dl[ptr['Li+']] = -i_dl / (ct.faraday * Zk_elyte[ptr['Li+']])
    dSVdt[SVptr['elyte']+SV_move] = ((Nk_top - Nk_bot) * dyInv_cath + \
                                    (sdot_int + sdot_dl)) * W_elyte * E_carb_inv

    # Calculate change in surface coverages
    dSVdt[SVptr['theta']+SV_move] = sdot_surf/ inter.site_density

    # Set states in last cathode node
    """cath_b.electric_potential = 0
    elyte.electric_potential = SV[SVptr['phi']+SV_move]
    inter.coverages = SV[SVptr['theta']+SV_move]
    elyte.electric_potential = phi_elyte_next"""

    " ======================================== SEPARATOR ======================================== "
    # Initialize SV pointer offset for separator
#    SV_move = 0
#
#    " --- Pre-loop --- "
#    elyte.TDY = T, sum(SV[SVptr['sep_elyte']]), SV[SVptr['sep_elyte']]
#    Yk_next = elyte.Y
#    Xk_next = elyte.X
#    phi_elyte_next = elyte.electric_potential
#
#    for j in np.arange(Ny_sep - 1):
#        Nk_top = Nk_bot
#        phi_elyte_this = phi_elyte_next
#        elyte.TDY = T, sum(SV[SVptr['sep_elyte']+SV_move]), SV[SVptr['sep_elyte']+SV_move]
#        Xk_this = Xk_next
#        Yk_next = elyte.Y
#        Xk_next = elyte.X
#        #Yk_next = SV[SVptr['sep_elyte']+SV_move+SV_single_sep]
#        #Xk_next = Yk_next * sum(W_elyte) / W_elyte
#
#        Ck_elyte = elyte.concentrations
#        C_elyte = sum(Ck_elyte)
#        i_io_top = ct.faraday * sum(Zk_elyte * Nk_top)
#
#        if params['transport'] == 'cst':
#            Dk_elyte = cst(Ck_elyte,objs,params)[0]
#            Dk_elyte_mig = cst(Ck_elyte,objs,params)[1]
#        if params['transport'] == 'dst':
#            Dk_elyte = dst(Ck_elyte,params)[0]
#            Dk_elyte_mig = dst(Ck_elyte,params)[1]
#
#        Ck_elyte = elyte.concentrations
#        u_k = np.zeros_like(Yk_next)
#        u_k = Dk_elyte / (ct.gas_constant * T)
#        Xk_int = 0.5 * (Xk_this + Xk_next)
#
#        phi_elyte_next = phi_elyte_this - (i_io_top + ct.faraday*ct.gas_constant*T*C_elyte \
#                        * sum(Zk_elyte*u_k*(Xk_next - Xk_this)*dyInv_sep)) \
#                        / (ct.faraday**2*dyInv_sep * sum(Zk_elyte**2 * u_k * Ck_elyte))
#
#        #phi_elyte_next = phi_elyte_this + R_sep * params['i_ext'] / Ny_sep
#
#        print('Ck =',Ck_elyte)
#
#        Nk_bot = - u_k * Ck_elyte * ((ct.gas_constant * T) / Xk_int * (Xk_next - Xk_this) * dyInv_sep \
#                + Zk_elyte * ct.faraday * (phi_elyte_next - phi_elyte_this) * dyInv_sep)
##        Nk_bot = i_ext / ct.faraday
#
#        # Calculate change in electrolyte concentrations
#        dSVdt[SVptr['sep_elyte']+SV_move] = (Nk_top - Nk_bot) * dyInv_sep * E_sep_inv
#        print('N_bot =',Nk_bot)
#
#        # Set potentials and concentrations
#        elyte.TDY = T, sum(SV[SVptr['sep_elyte']+SV_move]), SV[SVptr['sep_elyte']+SV_move]
#        elyte.electric_potential = phi_elyte_next
#
#        # New SV offset value
#        SV_move = SV_move + SV_single_sep
#
#    " --- Post-loop --- "
#    # Set next 'top' flux as current 'bottom'
#    Nk_top = Nk_bot
#
#    # Set lithium anode potential
#    Li_b.electric_potential = elyte.electric_potential - SV[SVptr['sep_phi']+SV_move]
#
#    # Transport and potential at anode BC
#    Nk_bot = Li_s.get_net_production_rates(elyte)
#
#    # Calculate double layer potential between separator and anode
#    i_far = Li_s.get_net_production_rates(elyte)[ptr['Li+']] * ct.faraday
#    i_dl = i_ext - i_far
#    dSVdt[SVptr['sep_phi']+SV_move] = i_dl / (C_dl) #* A_int)
#
#    # Calculate change in electrolyte concentrations
#    dSVdt[SVptr['sep_elyte']+SV_move] = (Nk_top - Nk_bot) * dyInv_sep * E_sep_inv

    return dSVdt
