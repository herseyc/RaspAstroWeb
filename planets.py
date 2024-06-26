#########################################################
# Plot a map of the Solar System                        #
# Output planets.png in static/                         #
#########################################################
import numpy
from datetime import datetime
from raspastroinfo import AstroData
import matplotlib as mpl
import matplotlib.pyplot as plt
from gps3 import agps3
from rasp_calc_func import *
from config import *
from get_gps import *
import time


gps_data_tuple = get_gps_data()

gpsfixtype = gps_data_tuple[0]
gpslatdms = gps_data_tuple[1]
gpslondms = gps_data_tuple[2]
gpsaltitude = gps_data_tuple[3]
gpslatitude = gps_data_tuple[4]
gpslongitude = gps_data_tuple[5]
gps_data = gps_data_tuple[6]

planets = AstroData(obslat=gps_data[1], obslon=gps_data[2], obslev=gps_data[3], obshorizon=MY_HORIZON)

planets.sun_info()

planets.planet_info()

# Set up a dictionary of values used to generate the plots
# Size is just a way I set the size of the different objects it is not
# a reference to actual size, but just a way to illustrate the size of
# the smallest planet (Mercury) to the largest planet (Jupiter)
planet_dict = {
    "Mercury": {
        "distance": planets.mercury['sun_distance'],
        "hlon": convert_dms_to_dd(planets.mercury['hlon']),
        "hlat": convert_dms_to_dd(planets.mercury['hlat']),
        "size": 2,
        "color": "brown",
    },
    "Venus": {
        "distance": planets.venus['sun_distance'],
        "hlon": convert_dms_to_dd(planets.venus['hlon']),
        "hlat": convert_dms_to_dd(planets.venus['hlat']),
        "size": 4,
        "color": "orange",
    },
    "Earth": {
        "distance": 1,
        "hlon": convert_dms_to_dd(planets.sun_data['earth_hlon']),
        "hlat": convert_dms_to_dd(planets.sun_data['earth_hlat']),
        "size": 4,
        "color": "green",
    },
    "Mars": {
        "distance": planets.mars['sun_distance'],
        "hlon": convert_dms_to_dd(planets.mars['hlon']),
        "hlat": convert_dms_to_dd(planets.mars['hlat']),
        "size": 4,
        "color": "red",
    },
    "Jupiter": {
        "distance": planets.jupiter['sun_distance'],
        "hlon": convert_dms_to_dd(planets.jupiter['hlon']),
        "hlat": convert_dms_to_dd(planets.jupiter['hlat']),
        "size": 12,
        "color": "purple",
    },
    "Saturn": {
        "distance": planets.saturn['sun_distance'],
        "hlon": convert_dms_to_dd(planets.saturn['hlon']),
        "hlat": convert_dms_to_dd(planets.saturn['hlat']),
        "size": 10,
        "color": "olive",
    },
    "Uranus": {
        "distance": planets.uranus['sun_distance'],
        "hlon": convert_dms_to_dd(planets.uranus['hlon']),
        "hlat": convert_dms_to_dd(planets.uranus['hlat']),
        "size": 8,
        "color": "cyan",
    },
    "Neptune": {
        "distance": planets.neptune['sun_distance'],
        "hlon": convert_dms_to_dd(planets.neptune['hlon']),
        "hlat": convert_dms_to_dd(planets.neptune['hlat']),
        "size": 8,
        "color": "blue",
    },
    "Pluto": {
        "distance": planets.pluto['sun_distance'],
        "hlon": convert_dms_to_dd(planets.pluto['hlon']),
        "hlat": convert_dms_to_dd(planets.pluto['hlat']),
        "size": 1,
        "color": "gray",
    },
}

#print(planet_dict)

# Time for text label
time_generated = datetime.utcnow()

mpl.rcParams['xtick.color'] = 'white'
fig = plt.figure(figsize=(15,15), facecolor='black')
#ax = fig.add_subplot(projection='hammer', fc='black')
ax = fig.add_subplot(projection='polar', fc='black')
ax.set_theta_zero_location("SE")
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.grid(False)
# Display time generated
ax.text(-45,33, f"Generated {time_generated} UTC", fontdict={"fontsize": "medium", "color": "white", "family": "monospace", "fontweight": "bold"})

ax.plot(0, 0, marker='o', markersize=20, color="yellow", label="Sun")
for key in planet_dict:
    ax.plot(numpy.deg2rad(planet_dict[key]['hlon']), planet_dict[key]['distance']+1, marker='o', markersize=planet_dict[key]['size'], color=planet_dict[key]['color'], label=key)
    #ax.plot(planet_dict[key]['hlon'], planet_dict[key]['hlat'], marker='o', markersize=planet_dict[key]['size'], color=planet_dict[key]['color'], label=key)

ax.legend()
plt.savefig(INSTALLDIR + '/static/planets.png', bbox_inches='tight')


