
import streamlit as st
import numpy as np

from scripts._profet import EnergyDemand
from scripts._utils import Plotting
from scripts._energy_coverage import EnergyCoverage
from scripts._costs import Costs
from scripts._ghetool import GheTool
from scripts._utils import hour_to_month

def early_phase():
    st.title("Energibehov")
    st.header("PROFet")
    st.caption("Foreløpig begrenset til Trondheimsklima")
    energy_demand = EnergyDemand()
    demand_array, selected_array = energy_demand.get_thermal_arrays_from_input()
    Plotting().hourly_plot(demand_array, selected_array, Plotting().FOREST_GREEN)
    Plotting().hourly_plot(np.sort(demand_array)[::-1], selected_array, Plotting().FOREST_GREEN)
    st.markdown("---")
    #--
    st.header("Kjølebehov")
    annual_cooling_demand = st.number_input("Legg inn årlig kjølebehov [kWh]", min_value=0, value=0, step=1000)
    cooling_effect = st.number_input("Legg inn kjøleeffekt [kW]", min_value=0, value=0, step=100)
    cooling_per_month = annual_cooling_demand * np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
    months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]
    Plotting().xy_plot(months, months[0], months[-1], "Måneder", cooling_per_month, 0, max(cooling_per_month) + max(cooling_per_month)/10, "Kjølebehov [kwh]", Plotting().GRASS_GREEN)
    #--
    st.header("Dekningsgrad")
    energy_coverage = EnergyCoverage(demand_array)
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad [%]", min_value=50, value=90, max_value=100, step=2)    
    energy_coverage._coverage_calculation()
    Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Grunnvarmedekning", "Spisslast", Plotting().FOREST_GREEN, Plotting().SUN_YELLOW)
    #--
    st.header("Årsvarmefaktor")
    energy_coverage.COP = st.number_input("Velg COP", min_value=1.0, value=3.5, max_value=5.0, step=0.2)
    energy_coverage._geoenergy_cop_calculation()
    Plotting().hourly_triple_stack_plot(energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, 
    energy_coverage.non_covered_arr, "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_GREEN, Plotting().SUN_YELLOW)
    Plotting().hourly_triple_stack_plot(np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], 
    np.sort(energy_coverage.non_covered_arr)[::-1], "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_GREEN, Plotting().SUN_YELLOW)
    st.markdown("---")
    #--
    st.header("Oppsummert")
    st.write(f"Totalt energibehov {int(round(np.sum(demand_array),0))} kWh")
    st.write(f"Dekkes av grunnvarmeanlegget {int(round(np.sum(energy_coverage.covered_arr),0))} kWh")
    st.write(f"- Kompressor {int(round(np.sum(energy_coverage.gshp_compressor_arr),0))} kWh")
    st.write(f"- Levert fra brønn(er) {int(round(np.sum(energy_coverage.gshp_delivered_arr),0))} kWh")
    st.write(f"Spisslast {int(round(np.sum(energy_coverage.non_covered_arr),0))} kWh")
    st.write(f"Varmpumpestørrelse {int(round(energy_coverage.heat_pump_size,0))} kW")
    st.markdown("---")
    #--
    st.title("Brønnpark")
    simulation_obj = GheTool()
    simulation_obj.monthly_load_heating = hour_to_month(energy_coverage.gshp_delivered_arr)
    simulation_obj.monthly_load_cooling = cooling_per_month
    simulation_obj.peak_heating = energy_coverage.heat_pump_size
    simulation_obj.peak_cooling = cooling_effect
    well_guess = int(round(np.sum(energy_coverage.gshp_delivered_arr)/80/300,2))
    st.markdown(f"Estimert ca. **{well_guess}** brønner a 300 m ")
    with st.form("Inndata"):
        c1, c2 = st.columns(2)
        with c1:
            simulation_obj.K_S = st.number_input("Varmledningsevne", min_value=1.0, value=3.5, max_value=10.0, step=1.0) 
            simulation_obj.T_G = st.number_input("Uforstyrret temperatur", min_value=1.0, value=8.0, max_value=20.0, step=1.0)
            simulation_obj.R_B = st.number_input("Målt borehullsmotstand", min_value=0.0, value=0.08, max_value=2.0, step=0.01) + 0.02
            simulation_obj.N_1= st.number_input("Antall brønner (X)", value=1, step=1) 
            simulation_obj.N_2= st.number_input("Antall brønner (Y)", value=1, step=1) 
        with c2:
            H = st.number_input("Brønndybde [m]", min_value=100, value=300, max_value=500, step=10)
            GWT = st.number_input("Grunnvannsstand [m]", min_value=0, value=5, max_value=100, step=1)
            simulation_obj.H = H - GWT
            simulation_obj.B = st.number_input("Avstand mellom brønner", min_value=1, value=15, max_value=30, step=1)
            simulation_obj.RADIUS = st.number_input("Brønndiameter [mm]", min_value = 80, value=115, max_value=300, step=1) / 2000
        st.form_submit_button("Kjør simulering")
        simulation_obj._run_simulation()

    #st.title("Kostnader")
    #st.caption("Under arbeid")
    #tab1, tab2 = st.tabs(["Direkte kjøp", "Lånefinansiert"])
    #with tab1:
    #    costs_operation = Costs(meters)
    #    costs_operation._calculate_monthly_costs(demand_array, energy_coverage.gshp_compressor_arr, energy_coverage.non_covered_arr, costs_operation.INVESTMENT)
    #    costs_operation._show_operation_costs(costs_operation.INVESTMENT)
        #costs.operation_show_after()
        #costs.plot("Driftskostnad")
        #costs.profitibality_operation()
    #with tab2:
    #    costs_operation_and_investment = Costs(meters)
    #    costs_operation_and_investment._calculate_monthly_costs(demand_array, energy_coverage.gshp_compressor_arr, energy_coverage.non_covered_arr, 0)
    #    costs_operation_and_investment._show_operation_costs(0)
        #costs.operation_and_investment_show()
        #costs.plot("Totalkostnad")
        #costs.profitibality_operation_and_investment()
    