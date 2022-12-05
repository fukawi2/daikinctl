#!/usr/bin/env python3

import sys
import urllib.request
import csv
import time

# Turn on if one of these temperatures goes below these values
MIN_TEMP_INSIDE=12
MIN_TEMP_OUTSIDE=3
# Turn on if one of these temperatures goes above these values
MAX_TEMP_INSIDE=26
MAX_TEMP_OUTSIDE=28

# How long to sleep between checks of the unit temps
SLEEP_TIME=60

# Minimum time delta between sending commands to the unit to avoid flapping.
CMD_TIME_DELTA=300

# The HTTP server returns the aircon modes as integers; map them to string
# values using this dict.
UNIT_MODES = {
  "1": "AUTO",
  "2": "DRY",
  "3": "COOLING",
  "4": "HEATING",
  "6": "FAN",
}

# For readability of the script, these constants can be used as aguments to
# the setPowerState() function
POWER_ON=True
POWER_OFF=False

def mkApiCall(path, getQuery = None):
  """
  Send a HTTP GET to the aircon unit, retrieve the response and convert the CSV string of key-values to a dict
  for easier handling in other parts of the script. For example, the HTTP server returns a string that looks like:
    ret=OK,htemp=15.0,hhum=55,otemp=11.0,err=0,cmpfreq=0,mompow=1
  Which we will convert to a dict like:
    dict = {'ret': 'OK', 'htemp': '15.0', 'hhum': '55', 'otemp': '11.0', 'err': '0', 'cmpfreq': '0', 'mompow': '1'}
  """
  url = f"http://{ipAddress}{path}"
  if getQuery:
    url = url + "?" + urllib.parse.urlencode(getQuery)

  try:
    response = urllib.request.urlopen(url).read().decode("utf-8")
  except:
    quit(f"Unable to communicate with host {ipAddress}")    

  # Convert the CSV string of k=v strings to a dict
  kvData = {}
  for kv in response.split(","):
    (key, value) = kv.split("=")
    kvData[key] = value

  # Make sure we got an "OK" response from the unit
  if "ret" in kvData and kvData["ret"] == "OK":
    return kvData
  return None



def getMinimumParameters():
  """
  Sending control messages to the unit only requires a limited range of keys in the query string, but we have to
  specify at least those values. So we keep the last response of control data from the unit and use that to build
  the "minimum" list of parameters to send back, adjusting the one(s) we want to change.
  """
  global ctrlResponse
  minimumParameters = {}
  for key in ctrlResponse:
    if key in [ "pow", "mode", "stemp", "shum", "f_rate", "f_dir" ]:
      minimumParameters[key] = ctrlResponse[key]
  return minimumParameters



def setPowerState(pwrStateOn):
  global lastCmdEpoch
  secondsSinceLastCmd = time.time() - lastCmdEpoch
  if secondsSinceLastCmd < CMD_TIME_DELTA:
    print(f"Aborting sending command because last command was sent {secondsSinceLastCmd} seconds ago")
    return

  getQuery = getMinimumParameters()
  getQuery["pow"] = "1" if pwrStateOn else "0"
  result = mkApiCall("/aircon/set_control_info", getQuery)
  lastCmdEpoch = time.time()

###############################################################################

ipAddress=sys.argv[1]
lastCmdEpoch = 0
ctrlResponse = None

if not ipAddress:
  quit("Usage: daikinctl <ip of aircon>")

while True:
  envData = mkApiCall("/aircon/get_sensor_info")
  unitData = mkApiCall("/aircon/get_control_info")
  ctrlResponse = unitData

  if unitData['mode'] in UNIT_MODES:
    pwrMode = UNIT_MODES[unitData['mode']]
  else:
    pwrMode = f"UNKNOWN ({unitData['mode']})"

  if unitData["pow"] == "1":
    unitIsOn = True
    pwrState = f"ON in mode {pwrMode} and set to {unitData['stemp']} degrees"
  else:
    unitIsOn = False
    pwrState = f"OFF"

  tempOutside = float(envData["otemp"])
  tempInside = float(envData["htemp"])
  print(f"Unit is powered {pwrState}")
  print(f"Outside Temp: {envData['otemp']}")
  print(f"Inside Temp: {envData['htemp']}")

  if unitIsOn:
    if tempOutside > MAX_TEMP_OUTSIDE or tempInside > MAX_TEMP_INSIDE:
      # Still too hot - do not turn off
      True
    elif tempOutside < MIN_TEMP_OUTSIDE or tempInside < MIN_TEMP_INSIDE:
      # Still too hot - do not turn off
      True
    else:
      print("All temps are acceptable; Turning unit off.")
      setPowerState(POWER_OFF)
      time.sleep(1)
      continue
  else:
    if tempOutside > MAX_TEMP_OUTSIDE or tempInside > MAX_TEMP_INSIDE:
      # It's too hot - turn on unit on
      print("It's too hot! Turning unit on.")
      setPowerState(POWER_ON)
      time.sleep(1)
      continue
    elif tempOutside < MIN_TEMP_OUTSIDE or tempInside < MIN_TEMP_INSIDE:
      # It's too cold - turn on unit on
      print("It's too cold! Turning unit on.")
      setPowerState(POWER_ON)
      time.sleep(1)
      continue

  time.sleep(SLEEP_TIME)