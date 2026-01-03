import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import safe_earth
from safe_earth.data.climate.era5 import ERA5Var
import safe_earth.metrics.fairness as fairness
import pandas as pd
import numpy as np
import pickle
import time
import pdb
import platform

resolution = '240x121'
lead_times = [np.timedelta64(x, 'h') for x in range(12, 241, 12)]

variables_precip = [ERA5Var('total_precipitation_6hr', name='P6'), ERA5Var('total_precipitation_24hr', name='P24')]
variables_precip_fuxi = [ERA5Var('total_precipitation_6hr', name='P6'), ERA5Var('total_precipitation_24hr_from_6hr', name='P24')]
models_precip = ['graphcast', 'fuxi']
variables_other = [ERA5Var('2m_temperature', name='T2M'), ERA5Var('10m_u_component_of_wind', name='U1OM'), ERA5Var('10m_v_component_of_wind', name='V1OM')]
models_other = ['graphcast', 'pangu', 'fuxi']

era5 = safe_earth.data.climate.era5.get_era5(resolution, variables=variables_precip+variables_other)

# convert precip unit from m to mm
era5['P6'].values = era5['P6'].values * 1000
era5['P6'].attrs['units'] = 'mm'
era5['P24'].values = era5['P24'].values * 1000
era5['P24'].attrs['units'] = 'mm'

for model in models_precip:
    print(f'===== ON PRECIP MODEL: {model} =====', flush=True)

    print('about to load model pred data', flush=True)

    if model == 'fuxi':
        preds = safe_earth.data.climate.wb2.get_wb2_preds(model, resolution, lead_times, variables=variables_precip_fuxi)
    else:
        preds = safe_earth.data.climate.wb2.get_wb2_preds(model, resolution, lead_times, variables=variables_precip)

        # graphcast preds also need to be converted m -> mm
        preds['P6'] = preds['P6'] * 1000
        preds['P24'] = preds['P24'] * 1000

    print('about to run losses', flush=True)

    loss_gdf = safe_earth.metrics.losses.climate_weighted_l2(
        data=preds, 
        ground_truth=era5, 
        lon_dim='longitude', 
        lat_dim='latitude',
        lead_time_dim='prediction_timedelta'
    )

    print('about to run errors', flush=True)

    attributes = 'all'
    strata_metrics = safe_earth.metrics.errors.stratified_rmse(
        loss_gdf,
        loss_metrics=['weighted_l2'],
        attributes=attributes,
        added_cols={'model': model}
    )

    print('saving stratified errors', flush=True)

    with open(f'outputs/additional_vars/{model}_precip_errors.pkl', 'wb') as f:
        pickle.dump(strata_metrics, f)

    print('moving onto fairness', flush=True)

    fairness_metrics = fairness.measure_fairness(strata_metrics, funcs=[fairness.greatest_abs_diff, fairness.variance])

    print('saving fairness results', flush=True)

    with open(f'outputs/additional_vars/{model}_precip_fairness.pkl', 'wb') as f:
        pickle.dump(fairness_metrics, f)

print('precipitation completed successfully!', flush=True)

# for model in models_other:
#     print(f'===== ON TEMP/WIND VAR MODEL: {model} =====', flush=True)

#     print('about to load model pred data', flush=True)

#     preds = safe_earth.data.climate.wb2.get_wb2_preds(model, resolution, lead_times, variables=variables_other)

#     print('about to run losses', flush=True)

#     loss_gdf = safe_earth.metrics.losses.climate_weighted_l2(
#         data=preds, 
#         ground_truth=era5, 
#         lon_dim='longitude', 
#         lat_dim='latitude',
#         lead_time_dim='prediction_timedelta'
#     )

#     print('about to run errors', flush=True)

#     attributes = 'all'
#     strata_metrics = safe_earth.metrics.errors.stratified_rmse(
#         loss_gdf,
#         loss_metrics=['weighted_l2'],
#         attributes=attributes,
#         added_cols={'model': model}
#     )

#     print('saving stratified errors', flush=True)

#     with open(f'outputs/additional_vars/{model}_t2m_wind_errors.pkl', 'wb') as f:
#         pickle.dump(strata_metrics, f)

#     print('moving onto fairness', flush=True)

#     fairness_metrics = fairness.measure_fairness(strata_metrics, funcs=[fairness.greatest_abs_diff, fairness.variance])

#     print('saving fairness results', flush=True)

#     with open(f'outputs/additional_vars/{model}_t2m_wind_fairness.pkl', 'wb') as f:
#         pickle.dump(fairness_metrics, f)

# print('temp/wind completed successfully!', flush=True)
