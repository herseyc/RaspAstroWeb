#!/usr/bin/env python3 
from flask import Flask, render_template
from raspissinfo import ISSData
from raspastroinfo import AstroData
from gps3 import agps3
import time
import math
from datetime import datetime, timedelta, timezone
import folium
from rasp_calc_func import *
import time
import requests
import numpy
import matplotlib as mpl
import matplotlib.pyplot as plt
from config import *
from get_gps import *
import pgeocode
from pyzipcode import ZipCodeDatabase 
from timezonefinder import TimezoneFinder

import sys
sys.dont_write_bytecode = True

app = Flask(__name__)

#Moon Images
moon_image = {
    "Waxing": {
        "New Moon": "NewMoon",
        "Crescent": "WaxingCrescent",
        "Gibbous": "WaxingGibbous",
        "First Quarter": "FirstQuarter",
        "Full Moon": "FullMoon",
    },
    "Waning": {
        "Full Moon": "FullMoon",
        "Crescent": "WaningCrescent",
        "Gibbous": "WaningGibbous",
        "Last Quarter": "LastQuarter",
        "New Moon": "NewMoon",
    },
}
        


@app.route('/')
def index():
    # Observer informaiton
    current_utctime = datetime.utcnow()
    current_datetime = time_to_human(to_local(current_utctime))

    # function from get_gps.py to poll GPS or GPS config
    gps_data_tuple = get_gps_data()

    gpsfixtype = gps_data_tuple[0]
    gpslatdms = gps_data_tuple[1]
    gpslondms = gps_data_tuple[2]
    gpsaltitude = gps_data_tuple[3]
    gpslatitude = gps_data_tuple[4]
    gpslongitude = gps_data_tuple[5]
    gps_data = gps_data_tuple[6]

    # Create map with observer's location
    obsm = folium.Map(location=[gpslatitude, gpslongitude], zoom_start=5)
    obsm.get_root().width = "450"
    obsm.get_root().height = "250px"
    obsm.get_root().render()
    folium.Marker(location=[gpslatitude, gpslongitude] , popup=f"Observer Location", icon=folium.Icon(color='blue', icon='user')).add_to(obsm)
    obsiframe = obsm.get_root()._repr_html_()


    # Sun/Moon/Planet/Information
    # AstroData from GPS
    astro = {}
    astro = AstroData(obslat=gps_data[1], obslon=gps_data[2], obslev=gps_data[3], obshorizon=MY_HORIZON)
    gps_data.append(astro.obs.horizon)

    # Moon Information
    astro.moon_data = {}
    astro.obs.horizon = "-0:34"
    astro.obs.pressure = 0
    astro.moon_info()

    # Convert Moon event times to human readable local time
    astro.moon_data['next_full_moon'] = time_to_human(to_local(astro.moon_data['next_full_moon'].datetime()))
    astro.moon_data['next_new_moon'] = time_to_human(to_local(astro.moon_data['next_new_moon'].datetime()))

    # Is Moon Rising or Setting
    astro.moon_data['rising_sign'] = rising_or_setting(next_transit_time=astro.moon_data['next_moon_transit'])

    # Convert Moon next transit/set/rise time to human readable local time
    astro.moon_data['next_moon_transit'] = time_to_human(to_local(astro.moon_data['next_moon_transit'].datetime()))
    astro.moon_data['next_moonset'] = time_to_human(to_local(astro.moon_data['next_moonset'].datetime()))
    astro.moon_data['next_moonrise'] = time_to_human(to_local(astro.moon_data['next_moonrise'].datetime()))

    # Sun Information
    astro.sun_data = {}
    astro.obs.horizon = "-0:34"
    astro.obs.pressure = 0
    astro.sun_info()

    # Convert Sun event times to human readable local time
    astro.sun_data['next_sunset'] = time_to_human(to_local(astro.sun_data['next_sunset'].datetime()))
    astro.sun_data['next_sunrise'] = time_to_human(to_local(astro.sun_data['next_sunrise'].datetime()))
    astro.sun_data['next_solstice'] = time_to_human(to_local(astro.sun_data['next_solstice'].datetime()))
    astro.sun_data['next_equinox'] = time_to_human(to_local(astro.sun_data['next_equinox'].datetime()))

    # Is Sun Rising or Setting
    astro.sun_data['rising_sign'] = rising_or_setting(next_transit_time=astro.sun_data['next_sun_transit'])

    # Convert Sun next transit  time to human readable local time
    astro.sun_data['next_sun_transit'] = time_to_human(to_local(astro.sun_data['next_sun_transit'].datetime()))

    # Get Deep Sky Custom Object Info
    # A list of XEphem formated data in config.py
    #set dict for results
    custom_deepsky = {}
    for edbobject in CUSTOM_OBJECTS:
        astro.object_data = {}
        astro.object_info(catalog=edbobject)
        object_name = astro.object_data['name'].split("|")
        astro.object_data['alt'] = round(math.degrees(astro.object_data['alt']), 1)
        astro.object_data['az'] = round(math.degrees(astro.object_data['az']), 1)
        astro.object_data['rising_sign'] = rising_or_setting(next_transit_time=astro.object_data['next_transit'])

        # Convert Deep Sky object next transit times to human readable local time
        astro.object_data['next_transit'] = time_to_human(to_local(astro.object_data['next_transit'].datetime()))
        custom_deepsky[object_name[0]] = astro.object_data 

    # Get Planet Info
    astro.mercury = {}
    astro.venus = {}
    astro.mars = {}
    astro.jupiter = {}
    astro.saturn = {}
    astro.uranus = {}
    astro.neptune = {}
    astro.pluto = {}

    astro.planet_info()

    #Determine if planets are rizing or setting
    astro.mercury['rising_sign'] = rising_or_setting(next_transit_time=astro.mercury['next_transit'])
    astro.venus['rising_sign'] = rising_or_setting(next_transit_time=astro.venus['next_transit'])
    astro.mars['rising_sign'] = rising_or_setting(next_transit_time=astro.mars['next_transit'])
    astro.jupiter['rising_sign'] = rising_or_setting(next_transit_time=astro.jupiter['next_transit'])
    astro.saturn['rising_sign'] = rising_or_setting(next_transit_time=astro.saturn['next_transit'])
    astro.uranus['rising_sign'] = rising_or_setting(next_transit_time=astro.uranus['next_transit'])
    astro.neptune['rising_sign'] = rising_or_setting(next_transit_time=astro.neptune['next_transit'])
    astro.pluto['rising_sign'] = rising_or_setting(next_transit_time=astro.pluto['next_transit'])

    # Convert planet next transit times to human readable local time
    astro.mercury['next_transit'] = time_to_human(to_local(astro.mercury['next_transit'].datetime()))
    astro.venus['next_transit'] = time_to_human(to_local(astro.venus['next_transit'].datetime()))
    astro.mars['next_transit'] = time_to_human(to_local(astro.mars['next_transit'].datetime()))
    astro.jupiter['next_transit'] = time_to_human(to_local(astro.jupiter['next_transit'].datetime()))
    astro.saturn['next_transit'] = time_to_human(to_local(astro.saturn['next_transit'].datetime()))
    astro.uranus['next_transit'] = time_to_human(to_local(astro.uranus['next_transit'].datetime()))
    astro.neptune['next_transit'] = time_to_human(to_local(astro.neptune['next_transit'].datetime()))
    astro.pluto['next_transit'] = time_to_human(to_local(astro.pluto['next_transit'].datetime()))

    # Messier Objects
    messier_objs = {}
    messier_list = []
    messier_file = "./xephemcat/Messier.edb"
    with open(messier_file) as lines:
        for obj in lines:
            if not obj.strip().startswith("#"):
                messier_list.append(obj)

    for messier_obj in messier_list:
        astro.object_data = {}
        astro.object_info(catalog=messier_obj)
        messier_object_name = astro.object_data['name'].split("|")
        astro.object_data['alt'] = round(math.degrees(astro.object_data['alt']), 1)
        astro.object_data['az'] = round(math.degrees(astro.object_data['az']), 1)
        # Is the object rising or setting
        astro.object_data['rising_sign'] = rising_or_setting(next_transit_time=astro.object_data['next_transit'])

        # Convert times to human readable local time
        astro.object_data['next_transit'] = time_to_human(to_local(astro.object_data['next_transit'].datetime()))
        messier_objs[messier_object_name[0]] = astro.object_data 

    # Get Polaris Info
    astro.polaris_data = {}
    astro.polaris_info()

    # Generate Polar Align Image
    phourangle = numpy.deg2rad(astro.polaris_data['phourangle'])
    mpl.rcParams['xtick.color'] = 'white'
    fig = plt.figure(facecolor='black')
    ax = fig.add_subplot(projection='polar', fc='black')
    # Flip it around since polar scope image is inverted
    ax.set_theta_zero_location("S")
    ax.set_yticklabels([])
    ax.text(0,0, "NCP", fontdict={"fontsize": "medium", "color": "white", "family": "monospace", "fontweight": "bold"})
    ax.plot(phourangle, 1, marker='o', markersize=10.2, color='red', label='Polaris')
    plt.savefig('./static/polarisalign.png', bbox_inches='tight')
    astro.polaris_data['phourangle'] = int(astro.polaris_data['phourangle'])
    # Convert polaris next transit time to human readable local time
    astro.polaris_data['next_transit'] = time_to_human(to_local(astro.polaris_data['next_transit'].datetime()))
    astro.polaris_data['hourangle'] = round(astro.polaris_data['phourangle'] * 0.0667, 1)

    return render_template('raspastrostatus.html', datetime=current_datetime,  gpsdata=gps_data, gpslatdec=f"{gpslatitude:.2f}", gpslondec=f"{gpslongitude:.2f}", obsiframe=obsiframe, obssidereal=astro.sidereal, moon=astro.moon_data, moonimage=moon_image, sun=astro.sun_data, mercury=astro.mercury, venus=astro.venus, mars=astro.mars, jupiter=astro.jupiter, saturn=astro.saturn, uranus=astro.uranus, neptune=astro.neptune, pluto=astro.pluto, polaris=astro.polaris_data, deepsky=custom_deepsky, messier=messier_objs)

# INDI Info from INDI Web Manager API
@app.route('/indi')
def indi():
    indi_current = {}
    driver_list = []
    # Pull AstroData for local host name
    astrohost = get_hostname()
    if USE_INDI:
        indi_status = requests.get(f"{INDIWEBMANAGER_API_ENDPOINT}/api/server/status")
        indi_status_data = indi_status.json()
        indi_current['status'] = indi_status_data[0]['status']
        indi_current['active_profile'] = indi_status_data[0]['active_profile']
        if indi_current['status']:
           driver_status = requests.get(f"{INDIWEBMANAGER_API_ENDPOINT}/api/server/drivers")
           driver_status_data = driver_status.json()

           for driver in driver_status_data:
               driver_list.append(driver['name'])
        else:
           driver_list = ["None"]
    else:
        indi_current['status'] = "Not Used"
        driver_list = ["None"]

    return render_template('indi_iframe.html', indicurrent=indi_current, driverlist=driver_list, astrohost=astrohost)

# Display the ISS information
@app.route('/iss')
def iss():
    current_datetime = time_to_human(to_local(datetime.utcnow()))
    current_utctime = datetime.utcnow()

    # Get observer GPS data
    gps_data_tuple = get_gps_data()

    gpsfixtype = gps_data_tuple[0]
    gpslatdms = gps_data_tuple[1]
    gpslondms = gps_data_tuple[2]
    gpsaltitude = gps_data_tuple[3]
    gpslatitude = gps_data_tuple[4]
    gpslongitude = gps_data_tuple[5]
    gps_data = gps_data_tuple[6]

    # ISS Information
    iss = ISSData(obslat=gps_data[1], obslon=gps_data[2], obslev=gps_data[3], obshorizon=MY_HORIZON)
    days = PASSDAYS
    iss.iss_passes(duration=days)
    iss_local = []
    iss_current = {}
    for i in iss.iss_next_passes:
        if not i['eclipsed'] and i['sun_alt'] < 0:
            iss_local.append({
                         "aos": time_to_human(to_local(i['aos'].datetime())), 
                         "los": time_to_human(to_local(i['los'].datetime())), 
                         "alt_max": round(math.degrees(i['alt_max'])),
                         "azs": round(math.degrees(i['azs'])),
                         "constellation": i['constellation'][1],
                         })

    iss_current['geolat'] = iss.iss_telemetry.sublat
    iss_current['geolong'] = iss.iss_telemetry.sublong
    iss_current['a_ra'] = iss.iss_telemetry.a_ra
    iss_current['a_dec'] = iss.iss_telemetry.a_dec
    iss_current['alt'] = iss.iss_telemetry.alt
    iss_current['range'] = meters_to_miles(iss.iss_telemetry.range)
    iss_current['range_velocity'] = round(meters_to_miles(iss.iss_telemetry.range_velocity * 3600), 2) 
    iss_current['elevation_miles'] = meters_to_miles(iss.iss_telemetry.elevation)

    lat_dd = convert_dms_to_dd(iss_current['geolat'])
    lon_dd = convert_dms_to_dd(iss_current['geolong'])

    # Create map with observer location, iss location, and plot past/future path
    m = folium.Map()
    m.get_root().width = "500"
    m.get_root().height = "300px"
    folium.Marker(location=[gpslatitude, gpslongitude] , popup=f"Observer Location", icon=folium.Icon(color='blue', icon='user')).add_to(m)
    folium.Marker(location=[lat_dd, lon_dd], popup=f"ISS Current Location at {current_datetime}", icon=folium.Icon(color='green', prefix='fa', icon='rocket')).add_to(m)

    # Display ISS previous path
    path_points = 120
    seconds_between_points = 30
    delta = current_utctime - timedelta(seconds=seconds_between_points)
    while path_points > 0:
        isspath = ISSData(obslat=gps_data[1], obslon=gps_data[2], obslev=gps_data[3], obsepoch=delta)
        delta = delta - timedelta(seconds=seconds_between_points)
        folium.CircleMarker(location=[convert_dms_to_dd(isspath.iss_telemetry.sublat), convert_dms_to_dd(isspath.iss_telemetry.sublong)], radius=1, fill_color="#ECFFDC", fill=True, color="#ECFFDC").add_to(m)
        path_points -= 1

    # Display ISS future path
    # TODO: Need to figure out how to keep path from wrapping back on
    # itself when it crosses edge of map.
    path_points = 90
    delta = current_utctime + timedelta(seconds=seconds_between_points)
    while path_points > 0:
        isspath = ISSData(obslat=gps_data[1], obslon=gps_data[2], obslev=gps_data[3], obsepoch=delta)
        delta = delta + timedelta(seconds=seconds_between_points)
        folium.CircleMarker(location=[convert_dms_to_dd(isspath.iss_telemetry.sublat), convert_dms_to_dd(isspath.iss_telemetry.sublong)], radius=1, fill_color="#BEBEBE", fill=True, color="#BEBEBE").add_to(m)
        path_points -= 1

    m.get_root().render()
    iframe = m.get_root()._repr_html_()

    return render_template('iss_iframe.html', datetime=current_datetime, iframe=iframe, isscurrent = iss_current, iss_pass_list=iss_local, duration=days)

#Sun statistics
@app.route('/sun')
def sun():
    current_datetime = time_to_human(to_local(datetime.utcnow()))

    gps_data_tuple = get_gps_data()

    gpsfixtype = gps_data_tuple[0]
    gpslatdms = gps_data_tuple[1]
    gpslondms = gps_data_tuple[2]
    gpsaltitude = gps_data_tuple[3]
    gpslatitude = gps_data_tuple[4]
    gpslongitude = gps_data_tuple[5]
    gps_data = gps_data_tuple[6]

    sol = AstroData(obslat=gps_data[1], obslon=gps_data[2], obslev=gps_data[3], obshorizon=MY_HORIZON)

    # Current Sun Information
    sol.sun_data = {}
    sol.obs.date = datetime.utcnow()
    sol.obs.horizon = "-0:34"
    sol.obs.pressure = 0
    sol.sun_info()

    # Convert Sun event times to human readable local time
    sol.sun_data['next_sunset'] = time_to_human(to_local(sol.sun_data['next_sunset'].datetime()))
    sol.sun_data['next_sunrise'] = time_to_human(to_local(sol.sun_data['next_sunrise'].datetime()))
    sol.sun_data['next_solstice'] = time_to_human(to_local(sol.sun_data['next_solstice'].datetime()))
    sol.sun_data['next_equinox'] = time_to_human(to_local(sol.sun_data['next_equinox'].datetime()))

    # Is Sun Rising or Setting
    sol.sun_data['rising_sign'] = rising_or_setting(next_transit_time=sol.sun_data['next_sun_transit'])

    # Convert Sun next transit  time to human readable local time
    sol.sun_data['next_sun_transit'] = time_to_human(to_local(sol.sun_data['next_sun_transit'].datetime()))
    
    # Save current sun data
    currentsundata = sol.sun_data

    # number of days to compute
    numdays = 10
    day = 0

    #Get local time offset (timezone)
    timeoffset = datetime.now() - datetime.utcnow()
    timeoffsetsec = int(round(timeoffset.total_seconds() / 3600))
    #Set time to today at midnight
    today_midnight = datetime.now().replace(hour=0, minute=0)
    #convert today at midnight to UTC
    utc_datetime = today_midnight - timeoffset

    # Set up dictionaries to store data
    sun = {}

    while day < numdays:
       sundate = utc_datetime + timedelta(days=day)
       sol.sun_data = {}

       display_date = sundate.strftime("%m/%d/%Y")
       sol.obs.date = sundate
       sol.obs.horizon = "-0:34"
       sol.obs.pressure = 0
       sol.sun_info()

       # Next Sun Rise and Sun Set
       local_human_next_sunrise = time_to_human(to_local(sol.sun_data['next_sunrise'].datetime())).split()
       local_human_next_sunset = time_to_human(to_local(sol.sun_data['next_sunset'].datetime())).split()
       local_human_next_transit = time_to_human(to_local(sol.sun_data['next_sun_transit'].datetime())).split()
       #Compute the length of the day
       day_length = sol.sun_data['next_sunset'].datetime()- sol.sun_data['next_sunrise'].datetime() 
       display_day = str(day_length).split(":")

       # Next Astronomical Twilight
       sol.obs.horizon = "-18"
       sol.obs.pressure = 0
       # Astronomical Twilight is calculated using the center of the Sun
       sol.sun_info(usecenter=True)

       local_human_astronomical_twilight = time_to_human(to_local(sol.sun_data['next_sunset'].datetime())).split()
       local_human_astronomical_day = time_to_human(to_local(sol.sun_data['next_sunrise'].datetime())).split()
   
       sun[display_date] = { 
               "Sunrise": local_human_next_sunrise[1] + " " + local_human_next_sunrise[2] + " " + local_human_next_sunrise[3], 
               "Sunset": local_human_next_sunset[1] + " " + local_human_next_sunset[2] + " " + local_human_next_sunset[3], 
               "SunTransit": local_human_next_transit[1] + " " + local_human_next_transit[2] + " " + local_human_next_transit[3], 
               "AstronomicalTwilight": local_human_astronomical_twilight[1] + " " + local_human_astronomical_twilight[2] + " " + local_human_astronomical_twilight[3], 
               "AstronomicalDay": local_human_astronomical_day[1] + " " + local_human_astronomical_day[2] + " " + local_human_astronomical_day[3], 
               "DayLengthHours": display_day[0], 
               "DayLengthMinutes": display_day[1],
               "DayLengthSeconds": int(round(float(display_day[2]), 0)),
        }

       day = day+1

    return render_template('sun_stats.html', datetime=current_datetime,  currentsun=currentsundata, sunstats=sun, numdays=numdays)

@app.route('/moon')
def moon():
    current_datetime = time_to_human(to_local(datetime.utcnow()))

    gps_data_tuple = get_gps_data()

    gpsfixtype = gps_data_tuple[0]
    gpslatdms = gps_data_tuple[1]
    gpslondms = gps_data_tuple[2]
    gpsaltitude = gps_data_tuple[3]
    gpslatitude = gps_data_tuple[4]
    gpslongitude = gps_data_tuple[5]
    gps_data = gps_data_tuple[6]

    luna = AstroData(obslat=gps_data[1], obslon=gps_data[2], obslev=gps_data[3], obshorizon=MY_HORIZON)

    # Current Moon Information
    luna.moon_data = {}
    luna.obs.horizon = "-0:34"
    luna.obs.pressure = 0
    luna.obs.date = datetime.utcnow()
    luna.moon_info()

    # Convert Moon event times to human readable local time
    luna.moon_data['next_full_moon'] = time_to_human(to_local(luna.moon_data['next_full_moon'].datetime()))
    luna.moon_data['next_new_moon'] = time_to_human(to_local(luna.moon_data['next_new_moon'].datetime()))

    # Is Moon Rising or Setting
    luna.moon_data['rising_sign'] = rising_or_setting(next_transit_time=luna.moon_data['next_moon_transit'])

    # Convert Moon next transit/set/rise time to human readable local time
    luna.moon_data['next_moon_transit'] = time_to_human(to_local(luna.moon_data['next_moon_transit'].datetime()))
    luna.moon_data['next_moonset'] = time_to_human(to_local(luna.moon_data['next_moonset'].datetime()))
    luna.moon_data['next_moonrise'] = time_to_human(to_local(luna.moon_data['next_moonrise'].datetime()))

    currentmoondata = luna.moon_data


    # number of days to compute
    numdays = 30
    day = 0

    #Get local time offset
    timeoffset = datetime.now() - datetime.utcnow()
    timeoffsetsec = int(round(timeoffset.total_seconds() / 3600))
    #print(timeoffsetsec)

    #Set time to today at midnight
    today_midnight = datetime.now().replace(hour=0, minute=0)
    #print(today_midnight)

    #convert today at midnight to UTC
    utc_datetime = today_midnight - timeoffset
    #print(utc_datetime)

    #Set up dictionaries to store data
    moon = {}

    while day < numdays:
       moondate = utc_datetime + timedelta(days=day)
       luna.moon_data =  {}

       display_date = moondate.strftime("%m/%d/%Y")


       luna.obs.date = moondate
       luna.obs.horizon = "-0:34"
       luna.obs.pressure = 0
       luna.moon_info()


       local_human_next_moonrise = time_to_human(to_local(luna.moon_data['next_moonrise'].datetime())).split()

       #Figure out if Moon rise is on different day (no rise on current day)
       d_day = display_date.split("/")
       md_day = local_human_next_moonrise[0].split("/")

       if int(d_day[1]) != int(md_day[1]):
           get_next_moonset_date = moondate
           moonrise_display = "-"
       else:
           get_next_moonset_date = luna.moon_data['next_moonrise'].datetime()
           moonrise_display = local_human_next_moonrise[1] + " " + local_human_next_moonrise[2] + " " + local_human_next_moonrise[3]

       luna.obs.date = get_next_moonset_date
       luna.moon_info()

       local_human_next_moonset = time_to_human(to_local(luna.moon_data['next_moonset'].datetime()))
       moonset_split = time_to_human(to_local(luna.moon_data['next_moonset'].datetime())).split()

       # Only dipslay set date if day is different
       if local_human_next_moonrise[0] == moonset_split[0]:
           moonset_display = moonset_split[1] + " " + moonset_split[2] + " " + moonset_split[3] 
       else: 
           moonset_display = local_human_next_moonset


       moon[display_date] = { 
               "Moonrise": moonrise_display,
               "Moonset": moonset_display,
               "Phase": luna.moon_data['moon_quarter'],
               "PhaseName": luna.moon_data['moon_phase_name'],
               "PhasePercent": luna.moon_data['moon_phase_percent'],
               "PhaseIcon": luna.moon_data['moon_phase_emoji'],
       }

       day = day+1

    return render_template('moon_stats.html', datetime=current_datetime, currentmoon=currentmoondata, moonimage=moon_image, moonstats=moon, numdays=numdays)

@app.route('/moon/zip/<zipcode>')
def moon_zip(zipcode):

    current_datetime = time_to_human(to_local(datetime.utcnow()))

    # Get lat/lon from zipcode
    zcode = str(zipcode)

    nomi = pgeocode.Nominatim("us")
    zipquery = nomi.query_postal_code(zcode)
    ziplat = convert_dd_to_dms(zipquery["latitude"])
    ziplon = convert_dd_to_dms(zipquery["longitude"])

    #Get Timezone from ziplat/ziplon
    tzobj = TimezoneFinder()
    tzone = tzobj.timezone_at(lat=zipquery["latitude"], lng=zipquery["longitude"])

    ## luna = AstroData(obslat=gps_data[1], obslon=gps_data[2], obslev=gps_data[3], obshorizon=MY_HORIZON)
    luna = AstroData(obslat=ziplat, obslon=ziplon, obslev=0, obshorizon=MY_HORIZON)

    # Current Moon Information
    luna.moon_data = {}
    luna.obs.horizon = "-0:34"
    luna.obs.pressure = 0
    luna.obs.date = datetime.utcnow()
    luna.moon_info()

    # Convert Moon event times to human readable local time
    luna.moon_data['next_full_moon'] = time_to_human(to_timezone(luna.moon_data['next_full_moon'].datetime(), tzone))
    luna.moon_data['next_new_moon'] = time_to_human(to_timezone(luna.moon_data['next_new_moon'].datetime(), tzone))

    # Is Moon Rising or Setting
    luna.moon_data['rising_sign'] = rising_or_setting(next_transit_time=luna.moon_data['next_moon_transit'])

    # Convert Moon next transit/set/rise time to human readable local time
    luna.moon_data['next_moon_transit'] = time_to_human(to_timezone(luna.moon_data['next_moon_transit'].datetime(), tzone))
    luna.moon_data['next_moonset'] = time_to_human(to_timezone(luna.moon_data['next_moonset'].datetime(), tzone))
    luna.moon_data['next_moonrise'] = time_to_human(to_timezone(luna.moon_data['next_moonrise'].datetime(), tzone))

    currentmoondata = luna.moon_data


    # number of days to compute
    numdays = 30
    day = 0

    #Get local time offset
    timeoffset = datetime.now() - datetime.utcnow()
    timeoffsetsec = int(round(timeoffset.total_seconds() / 3600))
    #print(timeoffsetsec)

    #Set time to today at midnight
    today_midnight = datetime.now().replace(hour=0, minute=0)
    #print(today_midnight)

    #convert today at midnight to UTC
    utc_datetime = today_midnight - timeoffset
    #print(utc_datetime)

    #Set up dictionaries to store data
    moon = {}

    while day < numdays:
       moondate = utc_datetime + timedelta(days=day)
       luna.moon_data =  {}

       display_date = moondate.strftime("%m/%d/%Y")


       luna.obs.date = moondate
       luna.obs.horizon = "-0:34"
       luna.obs.pressure = 0
       luna.moon_info()


       local_human_next_moonrise = time_to_human(to_timezone(luna.moon_data['next_moonrise'].datetime(), tzone)).split()

       #Figure out if Moon rise is on different day (no rise on current day)
       d_day = display_date.split("/")
       md_day = local_human_next_moonrise[0].split("/")

       if int(d_day[1]) != int(md_day[1]):
           get_next_moonset_date = moondate
           moonrise_display = "-"
       else:
           get_next_moonset_date = luna.moon_data['next_moonrise'].datetime()
           moonrise_display = local_human_next_moonrise[1] + " " + local_human_next_moonrise[2] + " " + local_human_next_moonrise[3]

       luna.obs.date = get_next_moonset_date
       luna.moon_info()

       local_human_next_moonset = time_to_human(to_timezone(luna.moon_data['next_moonset'].datetime(), tzone))
       moonset_split = time_to_human(to_timezone(luna.moon_data['next_moonset'].datetime(), tzone)).split()

       # Only dipslay set date if day is different
       if local_human_next_moonrise[0] == moonset_split[0]:
           moonset_display = moonset_split[1] + " " + moonset_split[2] + " " + moonset_split[3] 
       else: 
           moonset_display = local_human_next_moonset


       moon[display_date] = { 
               "Moonrise": moonrise_display,
               "Moonset": moonset_display,
               "Phase": luna.moon_data['moon_quarter'],
               "PhaseName": luna.moon_data['moon_phase_name'],
               "PhasePercent": luna.moon_data['moon_phase_percent'],
               "PhaseIcon": luna.moon_data['moon_phase_emoji'],
       }

       day = day+1

    return render_template('moon_stats_zip.html', zipquery=zipquery, zipcode=zcode, ziplat=ziplat, ziplon=ziplon, datetime=current_datetime, currentmoon=currentmoondata, moonimage=moon_image, moonstats=moon, numdays=numdays)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=WEBPORT)
