# HEAT PUMP COST BENEFIT ANALYSIS AND EMISSIONS ESTIMATOR

import streamlit as st
import pandas as pd
from helper import generate_df, make_stacked_bar_horiz
from PIL import Image


#__________ set default values______________
#efficiencies and performance coefficients - default values
boiler_heat_eff = 0.88
boiler_hw_eff = 0.88
immersion_hw_eff = 1
#typical heat pump performance:
hp_heat_scop_typ = 3.2
hp_hw_cop_typ = 2.7
#hi heat pump performance
hp_heat_scop_hi = 3.8
hp_hw_cop_hi = 2.8

#Raise in temp (degC) from mains water to hot water AS USED
hw_temp_raise_default = 25

#carbon intensity values taken from SAP 10.2 (dec 2021)
GAS_kgCO2perkWh = 0.21
ELEC_RENEW_kgCO2perkWh = 0
ELEC_AVE_kgCO2perkWh = 0.136

# price cap October 2022 gas and electricity domestic standing and unit charges
gas_stand = 28.0
gas_unit = 10.3
elec_stand = 46.0
elec_unit = 34.0

# efficincy measures to choose from
efficiency_opts = [('Draft proofing and/or door insulation (3%)', 0.03),
                    ('Increased loft insulation (5%)', 0.05),
                    ('Improved window glazing (5%)', 0.05),
                    ('Cavity wall insulation (10%)', 0.1),
                    ('Underfloor insulation (10%)', 0.1),
                    ('Internal or external solid wall insulation (15%)', 0.15),
                    ('Enter a custom heating demand saving', -1.0)]
#____________ Page info________________________________________

about_markdown = 'This app has been developed by UrbanTasker Inc. (urbantasker.com)' 

st.set_page_config(layout="centered", menu_items={'Get Help': None, 'Report a Bug': None, 'About': about_markdown})

#__________write some reference info to the sidebar____________

df_tot = pd.DataFrame([['1', 2100, 7000], ['2', 2750, 9500], 
                        ['3', 3000, 12000], ['4', 3500, 15000],
                        ['5', 4300, 17000]],
                        columns=['House size', 'Electricity (kWh)', 'Gas (kWh)'])
df_tot.set_index('House size', inplace=True)                        

df_hw = pd.DataFrame([['Washing up', 15], ['5 min water-saving shower', 30], ['10 min power shower', 150], ['Bath', 100]],
columns=['Use', 'Hot water used (L)'])
df_hw.set_index('Use', inplace=True)

df_cook = pd.DataFrame([['Gas hob', 0.8], ['Gas grill', 1], ['Gas oven', 1.5]],
columns=['Use', 'Gas consumption per use (kWh)'])
df_cook.set_index('Use', inplace=True)

st.sidebar.header('Reference information')
st.sidebar.subheader('Typical total annual household energy consumption by number of bedrooms')
st.sidebar.table(df_tot.style.format("{:,d}"))
st.sidebar.subheader('Typical amounts of water for different uses')
st.sidebar.table(df_hw)
st.sidebar.subheader('Typical amounts of energy used for cooking with gas appliances')
st.sidebar.table(df_cook.style.format(precision=1))

#___________Main page__________________________________________

st.title('Heat Pump Running Costs and Emissions Estimator')    


message = """
This tool is developed for cost benefit analysis of heatpump vs using the gas furnace alone in Canada.
Please note that using heat pump alone might not be feasible for most of the places in Canada unless ofcourse
heatpump is very high rating in which case cost of installing the heatpump will be prohibitive itself. Therefore,
the tool assumes that with heatpump gas furnace is used as supplemental heating source.
The tool also compares the CO$_2$ emissions for both the setups.
"""
st.write(message)
#st.header('Inputs')
st.markdown("<div id='linkto_top'></div>", unsafe_allow_html=True)
#Now go to main tabs
tab1, tab2, tab3 = st.tabs(["Basic Settings", "Advanced Settings", "Further Information"])

with tab1:
    #_______________basic settings_________________________________________
    st.subheader('1.  Annual energy consumption')

    st.write('Your projected annual energy consumption should be available on your energy bill. If you do not know ' +
    'your annual energy consumption, you can use the typical values for your house size shown in the sidebar to the left.')
    # is_know_annual = st.radio('Do you know your annual energy consumption for electricity and gas?', ['Yes', 'No'])
     
    # if is_know_annual is 'Yes':

    c1, c2, c3 = st.columns(3)        
    with c1:
        province = st.selectbox('Province:', ('Ontario', 'BC'))
    with c2:
        elec_total_kWh = st.number_input('Annual electricity consumption (kWh):', min_value=0, max_value=100000, value=3000, step=100)
    with c3:
        if province == 'Ontario':
            gas_total_kWh = st.number_input("Annual gas consumption (m^3):", min_value=0, max_value=100000, value=12000, step=100)
        else:
            gas_total_kWh = st.number_input("Annual gas consumption (Joules):", min_value=0, max_value=1000, value=100, step=1)


    st.subheader('2.  Hot water usage')
    st.write('How is your hot water heated?  If you have solar thermal panels to heat your hot water, select the source which tops-up the temperature when needed.')
    hw_source = st.radio('Hot water heat source:', ['gas', 'electricity (immersion heater or electric boiler)'])
    is_hw_gas = (hw_source=='gas')

    st.write('How much hot water does your household use in a typical day?  *You can find some reference values in the sidebar to the left to help here.*')
    hw_lday = st.number_input('The UK average is 140 litres per person per day.  Enter the total litres/day here:', 
    min_value=0, max_value=1000, value=350, step=1)

    st.subheader('3.  Cooking')
    st.write('If you cook with gas, we would like to know how much to help calculate the energy used for heating.')
    is_cook_gas = st.checkbox('I cook with mains gas', value=False)

    if is_cook_gas:
        st.write('How much energy do you use cooking with gas *each week*? *You can find some reference values in the sidebar to the left to help here.*')
        gas_cook_kWhweek = st.number_input('A typical household uses between 5 and 12 kWh per week.  Enter total kWh/week here:', 
        min_value=0, max_value=100, value=8, step=1)

    st.subheader('4.  More complex set-ups')       
    
    is_second_heatsource = st.checkbox('I have a secondary heating source in addition to gas central heating', value=False)
    
    if is_second_heatsource:
        opts = ['gas', 'electric', 'other (not included in energy consumption calculations below)']
        second_heatsource_type = st.radio('My secondary heat source is:', opts)
        opts = ['Keep using my secondary heat source', 'Remove the secondary heat source and have the heat pump supply this heat']
        second_heatsource_remains = st.radio('In the heat pump scenario, I would...', opts)
        is_second_heatsource_remains = (second_heatsource_remains == opts[0])
        second_heatsource_kWh = st.number_input('Annual estimated energy usage of the secondary heatsource (kWh).  5% of your gas usage is used as an intial estimate.', min_value=0, max_value=100000, value=int(0.05*gas_total_kWh), step=10)

    # some complex set-ups don't need extra inputs, just explain how to use the existing ones.
    with st.expander('I generate some of my own electricity'):
        st.write('When entering the annual electricity consumption above, only input the annual *imported* electricity. ' +
        'The results below will then only relate to the imported energy and emissions.' +
        ' Heating your home with a heat pump may not use much of your solar-generated electricity due to the energy demand ' +
        'being primarily in the winter when your existing electricity consumption may already use all your generation capacity. '
        'However, your surplus generation capacity in the summer months can be used to heat your hot water with the heat pump.')
        is_free_summer_hw = st.checkbox('Set 4 months of summer hot water use to be provided at no cost in the heat pump scenarios', value=False)

    with st.expander('I use solar thermal panels to heat my hot water'):
        st.write('Typically solar thermal energy does not provide all of your hot water heating needs.  In this case you should reduce the '
        +'hot water usage above to the fraction that will be heated by other sources on an average day (across the whole year).')

    st.subheader('5.  Switching to a heat pump')

    st.write('Some efficiency measures are often implemented prior to or as part of a heat pump installation.' +
    ' Optionally, you can take these into account here.')    
    
    efficiency_boost = 0
    with st.expander('Energy efficiency measures'):         
        st.write('Select the energy efficiency measures to be implemented.' +
        ' Approximate heating demand reduction for each measure is shown in brackets. These are conservative estimates based on average *measured*' +
         ' reductions in heat demand rather than quoted reductions, which includes for example the effect of households choosing more comfortable heating settings' +
         ' once their energy bill reduces. Alternatively you can enter a custom heating demand reduction by selecting the last checkbox.')
        
        #make a checkbox for each efficiency boost we have:
        for (lab, boost) in efficiency_opts:

            is_op = st.checkbox(lab, value=False)
            if is_op:
                if boost < 0: #custom option selected
                    custom_val = st.number_input('Enter percentage saving:', 0.0, 100.0, 20.0, 1.0)
                    efficiency_boost += custom_val/100
                else:
                    efficiency_boost += boost                
        
    st.write('If you can disconnect from gas completely, you may save money by not paying the gas standing charge.  Any gas fireplace, '
    + 'gas hobs, or gas oven would need to be removed and replaced with electric appliances or simply disconnected.')
    is_disconnect_gas = st.checkbox('Disconnect from mains gas in heat pump scenario', value=False)

#____________advanced settings______________________
with tab2:

    st.subheader('1.  Energy prices')

    op1 = 'Use the UK-average domestic energy price cap for direct debit paying customers for the period beginning October 2022'
    op2 = 'Use custom unit and standing charges'

    charge_option = st.radio('Prices to use:',[op1, op2])

    is_two_tier_tariff = False
    #if user selects to input their own energy tariff
    if charge_option == op2:
        c1, c2 = st.columns(2)
        
        with c1:    
            gas_stand = st.number_input('Gas standing charge (p/day):', min_value=0.0, max_value=100.0, value=gas_stand, step=0.01)
            gas_unit = st.number_input('Gas unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=gas_unit, step=0.01)

        with c2:    
            elec_stand = st.number_input('Electricity standing charge (p/day):', min_value=0.0, max_value=100.0, value=elec_stand, step=0.01)        
            elec_unit = st.number_input('Electricity unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=elec_unit, step=0.01)  

        is_two_tier_tariff = st.checkbox('Add off-peak electricity tariff (e.g. like Economy7)')

        if is_two_tier_tariff:
            st.write('In the heat pump scenarios we assume that the average energy consumed per off-peak tariff hour by heating is two-thirds that used in the' +
            ' average peak-tariff hour. We also assume all of the hot water heating is performed in off-peak hours (unless using solar power) and none of the cooking.')

            elec_unit2 = st.number_input('Off-peak electricity unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=18.0, step=0.01)  
            second_tariff_hours = st.slider('Number of hours of off-peak tariff per day:', 0, 10, 7, 1)
            pc_elec_second_tariff = st.slider('Percentage of electricity consumption (excluding heat pump) in off-peak hours:', 0, 100, 40, 1)
            pc_elec_second_tariff /= 100
        
    st.subheader('2.  Device performance')
    st.write('Results are calculated for both a typical and a high-performance heat pump installation.  '
    + ' The heat pump system performance is described by the seasonal coefficient of performance (SCOP).')
    c1, c2, c3 = st.columns([3, 3, 4])
    
    #TODO: could potentially include immersion heating efficiency here
    with c1:
        st.write('_Average boiler efficiency_')
        boiler_heat_eff = st.number_input('When space heating:', min_value=0.0, max_value=1.00, value=boiler_heat_eff, step=0.01, key='boiler1')
        boiler_hw_eff = st.number_input('When hot water heating:', min_value=0.0, max_value=1.00, value=boiler_hw_eff, step=0.01, key='boiler2')
    with c2:
        st.write('*Typical heat pump SCOP*')
        hp_heat_scop_typ = st.number_input('When space heating:', min_value=0.1, max_value=10.0, value=hp_heat_scop_typ, step=0.1, key='typ1')
        hp_hw_cop_typ = st.number_input('When hot water heating:', min_value=0.1, max_value=10.0, value=hp_hw_cop_typ, step=0.1, key='typ2')
    with c3:
        st.write('*High-performance heat pump SCOP*')
        hp_heat_scop_hi = st.number_input('When space heating:', min_value=0.1, max_value=10.0, value=hp_heat_scop_hi, step=0.1, key='hi1')
        hp_hw_cop_hi = st.number_input('When hot water heating:', min_value=0.1, max_value=10.0, value=hp_hw_cop_hi, step=0.1, key='hi2')

    st.subheader('3.  Hot Water Temperature')
    st.write('Typical mains cold water may be at 15$^{\circ}$C, while a comfortable shower temperature is 37-41$^{\circ}$C.  The gas boiler '
    + 'will supply hot water hotter than this, which is then mixed with cold water, but the total energy used per litre is similar to providing '
    +'water at this temperature.')
    hw_temp_raise = st.number_input('Cold and hot water temperature difference (degrees C):', min_value=1, max_value=100, step=1, 
    help='The typical difference in temperature between mains water and hot water as used.', value=hw_temp_raise_default)

with tab3:
    #____________ Further Information____________________________
    st.subheader('1.  Carbon intensity')
    st.write("We use standard values for carbon intensity of different energy sources as set in the Standard Assessment Procedure (SAP) 10.2, "
    +"released December 2021.  These values only consider the CO$_2$ equivalent emissions associated per unit of energy, not the embedded emissions of the "
    + "energy generation and transmission infrastructure.  These values are: ")
    costs_table = pd.DataFrame([['Mains Gas', GAS_kgCO2perkWh], ['Electricity (grid average)', ELEC_AVE_kgCO2perkWh],
    ['Electricity (renewable only)', ELEC_RENEW_kgCO2perkWh]], columns=['Energy Source', 'CO2 Equivalent Emissions (kgCO2/kWh)'])
    costs_table.set_index('Energy Source', inplace=True)
    st.table(costs_table)

    st.subheader('2.  Other approximations and considerations')
    st.markdown(
    """
    It would not be possible to put together a perfectly accurate, but simple calculator comparing energy usage with and without a heat pump.
    This calculator necessarily gives only an indicative comparison, but in the majority of cases it should be representative when used correctly.
    Some examples as to why this calculator may be slightly inaccurate include:
    1. Switching from a boiler to a heat pump may change your heat demand independently of any energy saving measures you implement, for example you may save energy by overshooting the set temperature less, or you may have a different set temperature at night.
    2. Atypical annual variation in heating demand will result in different heat pump performance, as will weather conditions different from the UK average.
    3. Switching from a combi boiler to a heat pump will require you to install a hot water storage tank, which will impact the efficiency of heating hot water - some heat will be lost while storing the water, but less will be lost while waiting for the water to heat up on demand.
    4. Switching from gas to electric cooking (if you select gas cooking and disconnect from mains gas options) will change the energy demand of your cooking - electric is typically more efficient.       
    """
    )

is_submit1 = st.button(label='Update results')
result_container = st.container()

#leave some whitespace before adding the footer...
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.markdown("This tool is a project of <a href='https://urbantasker.com'>UrbanTasker</a>.", unsafe_allow_html=True)

st.markdown("<a href='#linkto_top'>^ Back to top ^</a>", unsafe_allow_html=True)


#don't proceed until Update results has been pressed
if not is_submit1:
    st.stop()

#_______________Results calculation______________________
#prepare some variables

#calculate hot water kWh/L
GAS_HW_kWhperL = 4200 * hw_temp_raise/(3600 * 1000 * boiler_hw_eff)
IMMERSION_HW_kWhperL = 4200 * hw_temp_raise/(3600 * 1000 * immersion_hw_eff)

#_____________first do the current case____________________
if is_two_tier_tariff:
    elec_unit_eff = (pc_elec_second_tariff*elec_unit2) + (1 - pc_elec_second_tariff)*elec_unit
else:
    elec_unit_eff = elec_unit

costs_by_type = [['Current', 'Gas standing', gas_stand*3.65],
                ['Current', 'Gas unit',  gas_total_kWh * gas_unit/100],
                ['Current', 'Elec.  standing', elec_stand*3.65],
                ['Current', 'Elec.  unit', elec_total_kWh * elec_unit_eff/100]] 
            
costs_total = (gas_stand + elec_stand)*3.65 + gas_total_kWh * gas_unit/100 + elec_total_kWh * elec_unit_eff/100

# hot water energy demand
if is_hw_gas:
    gas_hw_kWh = hw_lday * 365 * GAS_HW_kWhperL
    elec_hw_kWh = 0
else:
    gas_hw_kWh = 0
    elec_hw_kWh = hw_lday * 365 * IMMERSION_HW_kWhperL

#cooking demand - only done if gas
if is_cook_gas:
    gas_cook_kWh = gas_cook_kWhweek * 52
else:
    gas_cook_kWh = 0

#gas heating is remainder after hot water and cooking removed
gas_heat_kWh = gas_total_kWh - gas_hw_kWh - gas_cook_kWh

#see if there's any electric heating in addition:
if is_second_heatsource:
    if second_heatsource_type=='electric':
        elec_heat_kWh = second_heatsource_kWh
    else:
        elec_heat_kWh = 0    
    # elif second_heatsource_type=='other':
    #     other_total_kWh = second_heatsource_kWh
else:
    elec_heat_kWh = 0

#electric other is remainder after heating and hw removed
elec_other_kWh = elec_total_kWh-elec_heat_kWh-elec_hw_kWh

#if other electricity is now negative, assume user has overestimated either 
# their electric hw usage or electric heating - whichever the greater.
#reduce to bring other electricity to zero.
if elec_other_kWh < 0:
    if elec_hw_kWh > elec_heat_kWh:
        elec_hw_kWh += elec_other_kWh
    else: 
        elec_heat_kWh += elec_other_kWh

    elec_other_kWh = 0

#select carbon intensity of electricity
if is_elec_renewable:
    elec_kgCO2perkWh = ELEC_RENEW_kgCO2perkWh
else:
    elec_kgCO2perkWh = ELEC_AVE_kgCO2perkWh

#current energy usage table
energy_usage = [['Current', 'Heating', gas_heat_kWh+elec_heat_kWh, gas_heat_kWh*GAS_kgCO2perkWh+elec_heat_kWh*elec_kgCO2perkWh],
            ['Current', 'Hot water', gas_hw_kWh+elec_hw_kWh, gas_hw_kWh*GAS_kgCO2perkWh + elec_hw_kWh*elec_kgCO2perkWh],
            ['Current', 'Cooking', gas_cook_kWh, gas_cook_kWh*GAS_kgCO2perkWh],
            ['Current', 'Other Elec.', elec_other_kWh, elec_other_kWh*elec_kgCO2perkWh]]                

energy_total = gas_total_kWh + elec_total_kWh
emissions_total = sum([gas_heat_kWh*GAS_kgCO2perkWh, gas_hw_kWh*GAS_kgCO2perkWh, gas_cook_kWh*GAS_kgCO2perkWh, elec_total_kWh*elec_kgCO2perkWh])

#___________now do the future/heat pump case_____________


def do_heat_pump_case(install_type, gas_heat_kWh, elec_heat_kWh, gas_hw_kWh, elec_hw_kWh, gas_cook_kWh):
    """
    install type either 'Typical' or 'Hi-performance'
    """

    #set heat pump performance coefficients to hi or typical:
    if install_type == 'Hi-performance':
        hp_heat_scop = hp_heat_scop_hi
        hp_hw_cop = hp_hw_cop_hi
    else:
        hp_heat_scop = hp_heat_scop_typ
        hp_hw_cop = hp_hw_cop_typ

    #calculate future heating energy - dependent upon second heat source (if any)
    if not is_second_heatsource:
        elec_heat_kWh = (1 - efficiency_boost) * gas_heat_kWh * boiler_heat_eff/hp_heat_scop
        gas_heat_kWh = 0
    else:
        if is_second_heatsource_remains:
            if second_heatsource_type=='gas':
                elec_heat_kWh = (1 - efficiency_boost) * (gas_heat_kWh - second_heatsource_kWh) * boiler_heat_eff/hp_heat_scop
                gas_heat_kWh = second_heatsource_kWh
            elif second_heatsource_type=='electric':
                elec_heat_kWh = second_heatsource_kWh + (1 - efficiency_boost) * gas_heat_kWh * boiler_heat_eff/hp_heat_scop
                gas_heat_kWh = 0
        else:
            if second_heatsource_type=='electric':
                elec_heat_kWh = (1 - efficiency_boost) * (gas_heat_kWh * boiler_heat_eff + second_heatsource_kWh)/hp_heat_scop
                gas_heat_kWh = 0
            elif second_heatsource_type=='gas': #same as the no second heatsource case, as we assume same efficiency as boiler
                elec_heat_kWh = (1 - efficiency_boost) * gas_heat_kWh * boiler_heat_eff/hp_heat_scop
                gas_heat_kWh = 0
            else:#other second heatsource, assume gas boiler efficiency, but not included in gas_heat_kWh
                elec_heat_kWh = (1 - efficiency_boost) * (gas_heat_kWh + second_heatsource_kWh) * boiler_heat_eff/hp_heat_scop
                gas_heat_kWh = 0

    #hot water
    if is_hw_gas:
        elec_hw_kWh = gas_hw_kWh * boiler_heat_eff/hp_hw_cop
    else:
        elec_hw_kWh = elec_hw_kWh * immersion_hw_eff/hp_hw_cop

    #gas cooking energy
    if is_cook_gas:
        if is_disconnect_gas:
            emissions_cook = gas_cook_kWh * elec_kgCO2perkWh
            elec_cook_kWh = gas_cook_kWh
            gas_cook_kWh = 0   
        else:
            emissions_cook = gas_cook_kWh * GAS_kgCO2perkWh
            elec_cook_kWh = 0
    else:
        emissions_cook = 0   
        gas_cook_kWh = 0 #redundant, for clarity
        elec_cook_kWh = 0 

    #totals
    elec_total_kWh = elec_other_kWh + elec_heat_kWh + elec_hw_kWh + elec_cook_kWh
    gas_total_kWh = gas_heat_kWh + gas_cook_kWh

    #new energy consumption and emissions table
    case_name = install_type + ' HP Install'
    energy_usage = [[case_name, 'Heating', gas_heat_kWh+elec_heat_kWh, gas_heat_kWh*GAS_kgCO2perkWh+elec_heat_kWh*elec_kgCO2perkWh],
                [case_name, 'Hot water', elec_hw_kWh, elec_hw_kWh*elec_kgCO2perkWh],
                [case_name, 'Cooking', gas_cook_kWh+elec_cook_kWh, emissions_cook],
                [case_name, 'Other Elec.', elec_other_kWh, elec_other_kWh*elec_kgCO2perkWh]]   

    energy_total = elec_heat_kWh + elec_hw_kWh + elec_cook_kWh  + elec_other_kWh + gas_heat_kWh + gas_cook_kWh
    emissions_total = sum([elec_heat_kWh*elec_kgCO2perkWh, gas_heat_kWh*GAS_kgCO2perkWh, elec_hw_kWh*elec_kgCO2perkWh, emissions_cook, elec_other_kWh*elec_kgCO2perkWh])

    #update costs

    #don't include gas standing charge if disconnecting from gas
    if is_disconnect_gas:
        gas_stand_total = 0
    else:
        gas_stand_total = gas_stand*3.65

    if is_two_tier_tariff:
        #TODO: correct this!!!!
        #this pc of heating in second tariff (second_tariff_hours limited to 10)
        pc_heat_second_tariff = (2/3)*second_tariff_hours/((2/3)*10 + 14)
        #all of hot water in second tariff (or free in summer solar)
        #none of cooking in second tariff
        #same pc of other elec in second tariff as original scenario

        if is_free_summer_hw: #those with solar panels can get free hot water for 4 months
            elec_unit_total_cost = elec_heat_kWh * (pc_heat_second_tariff*elec_unit2 + (1-pc_heat_second_tariff)*elec_unit) + \
                elec_hw_kWh*(2/3)*elec_unit2 + elec_cook_kWh*elec_unit + elec_other_kWh*elec_unit_eff
        else:
            elec_unit_total_cost = elec_heat_kWh * (pc_heat_second_tariff*elec_unit2 + (1-pc_heat_second_tariff)*elec_unit) + \
                elec_hw_kWh*elec_unit2 + elec_cook_kWh*elec_unit + elec_other_kWh*elec_unit_eff
        elec_unit_total_cost /= 100
    else:
        if is_free_summer_hw: #those with solar panels can get free hot water for 4 months
            elec_unit_total_cost = (elec_total_kWh - elec_hw_kWh/3)*elec_unit/100
        else:
            elec_unit_total_cost = elec_total_kWh*elec_unit/100

    costs_by_type = [[case_name, 'Gas standing', gas_stand_total],
                    [case_name, 'Gas unit',  gas_total_kWh*gas_unit/100],
                    [case_name, 'Elec.  standing', elec_stand*3.65],
                    [case_name, 'Elec.  unit', elec_unit_total_cost]] 
    
    costs_total = sum([gas_stand_total, gas_total_kWh*gas_unit/100, elec_stand*3.65, elec_unit_total_cost])

    return energy_usage, costs_by_type, energy_total, emissions_total, costs_total

energy_usage_typ, costs_by_type_typ, energy_total_typ, emissions_total_typ, costs_total_typ = \
do_heat_pump_case('Typical', gas_heat_kWh, elec_heat_kWh, gas_hw_kWh, elec_hw_kWh, gas_cook_kWh)

energy_usage_hi, costs_by_type_hi, energy_total_hi, emissions_total_hi, costs_total_hi = \
do_heat_pump_case('Hi-performance', gas_heat_kWh, elec_heat_kWh, gas_hw_kWh, elec_hw_kWh, gas_cook_kWh)

#if no gas heating, just delete cooking data entries (index 2):
if not is_cook_gas:
    energy_usage.pop(2)
    energy_usage_hi.pop(2)
    energy_usage_typ.pop(2)

#_______________Present results_________________________

with result_container:
    st.header('Results')
    st.write('The impact of installing a heat pump (and any other changes entered above) on your annual energy **costs**, '
    +'**CO$_2$ emissions** and **energy usage** are summarized below, for both a typical installation and a high-performing one.' +
    '  Please remember that these are only estimates and no estimate can be perfect.  '
    + 'You can find '
    + 'more information on the assumptions that have gone into generating these estimates on the *Further Information* tab.')

    with st.expander('Tell me more about high-performance installations'):
        st.write(
            """
            High-performance installations typically include design features such as:
            - A low operating flow temperature (e.g. 35$^\circ$C), utilising larger radiators if necessary
            - Flow controls designed to minimising cycling of the heat pump (regular switching on and off)
            - Weather compensation control 
            - Many other aspects of the system designed and installed to best practice 
            """
            )

    #calculate key values to show...
    df_costs = generate_df(costs_by_type, [costs_by_type_typ, costs_by_type_hi], ['Costs (£)'])
    df_energy = generate_df(energy_usage, [energy_usage_typ, energy_usage_hi], ['Energy (kWh)', 'Emissions (kg of CO2)'])

    #present costs, energy consumed and emissions side-by-side
    change_str2 = lambda v : '+' if v > 0 else '-'

    st.subheader('1. Annual Energy Costs')

    st.write('The costs of energy are changing rapidly at the moment in the UK, so the cost of energy may be significantly'
    + ' different by the time you have a heat pump installed.  To give the simplest, like-for-like comparison, '
    + 'we use a constant price of energy for the whole year based on the October 2022 domestic energy price cap (even though this is set to change for many in April 2023).'
    + '  These costs should only be used comparatively between the two cases and may be quite different from your energy bill in previous years.  '
    + '  You can edit the price of energy used in the *Advanced Settings* tab at the top of the page.')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Current', f"£{costs_total:,.0f}")
    with c2:
        dcost = -100*(costs_total - costs_total_typ)/costs_total
        st.metric('Typical HP Install', f"£{costs_total_typ:,.0f}", 
        delta=f"{change_str2(dcost)}£{abs(costs_total - costs_total_typ):,.0f} ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')
    with c3:
        dcost = -100*(costs_total - costs_total_hi)/costs_total
        st.metric('Hi-performance HP Install', f"£{costs_total_hi:,.0f}", 
        delta=f"{change_str2(dcost)} £{abs(costs_total - costs_total_hi):,.0f} ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')

    bars = make_stacked_bar_horiz(df_costs, 'Costs (£)', 1)
    st.altair_chart(bars, use_container_width=True)

    st.subheader('2. Annual Emissions')
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Current', f"{emissions_total:,.0f} kg CO2")
    with c2:
        dcost = 100*(emissions_total_typ - emissions_total)/emissions_total
        st.metric('Typical HP Install', f"{emissions_total_typ:,.0f} kg CO2", 
        delta=f"{change_str2(dcost)} {abs(emissions_total_typ - emissions_total):,.0f} kg CO2 ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')
    with c3:
        dcost = 100*(emissions_total_hi - emissions_total)/emissions_total
        st.metric('Hi-performance HP Install', f"{emissions_total_hi:,.0f} kg CO2", 
        delta=f"{change_str2(dcost)} {abs(emissions_total_hi - emissions_total):,.0f} kg CO2 ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')

    bars = make_stacked_bar_horiz(df_energy, 'Emissions (kg of CO2)')
    st.altair_chart(bars, use_container_width=True)

    st.subheader('3. Annual Energy Usage')
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Current', f"{energy_total:,.0f} kWh")
    with c2:
        dcost = 100*(energy_total_typ - energy_total)/energy_total
        st.metric('Typical HP Install', f"{energy_total_typ:,.0f} kWh", 
        delta=f"{change_str2(dcost)} {abs(energy_total_typ - energy_total):,.0f} kWh ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')
    with c3:
        dcost = 100*(energy_total_hi - energy_total)/energy_total
        st.metric('Hi-performance HP Install', f"{energy_total_hi:,.0f} kWh", 
        delta=f"{change_str2(dcost)} {abs(energy_total_hi - energy_total):,.0f} kWh ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')

    bars = make_stacked_bar_horiz(df_energy, 'Energy (kWh)')
    st.altair_chart(bars, use_container_width=True)

    st.write('If you found this tool helpful - please share!')
