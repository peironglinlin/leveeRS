# leveeRS
Python scripts for data processing and analyses of our levee project.

## 1_process_data.py
Processing USGS urban data from 1938 to 2005 on two scales, county and levee-protected floodplains.

## 2_Fig1c_and_Fig1d.py
Draw the urban expansion of national counties and national levee-protected floodplains in the 10 years before and after the year of levee completion year. This code was also used to generate FigS5, but on individual state or watershed, not the national scale anymore. This code was also used to generate FigS10, the difference is the time span selection.

## 3_calc_watershed.py
Calculate the e value in each watershed.

## 4_calc_state.py
Calculate the e value in each state.

## 5_calc_cons_year.py
Calculate the e value based on the levee construction year.

## 6_Fig3.py
Draw the temporal dynamics of the levee effect in the US. This code was also used to generate FigS9, but we removed the locations with high saturation of urban areas in the protected floodplains throughout the entire time series.

## 7_FigS2.py
Draw the histograms of the levee and dam construction completion years in the contiguous US.

## 8_FigS3.py
Draw raw urban expansion curves of a selected county.

## 9_FigS4.py
Draw the net effect of levee construction on floodplain urban expansion.

## Processed_data_for_Fig1c_and_Fig1d.csv
Processed data for drawing Fig1c and Fig1d. This data contains three columns, the first column is the label for the x axis (urban expansion time series before and after the levee construction year T0), and the second and third columns are the values for the y axis (the urban area in the levee-protected floodplains and that in the counties).


## COMID_systemID_intersection.csv
Spatial correspondence between the levee-protected floodplain and the county.
