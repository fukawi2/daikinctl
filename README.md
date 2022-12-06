# daikinctl

## About

Simple daemon script to monitor temperatures (inside and outside) of a Daikin air-conditioner unit.

If temperatures exceed thresholds (too hot or too cold), the script will turn the air conditioner on.

Once the temperatures recover to within desired thresholds, the unit will be turned off.

This allows a wider range of acceptable temperatures, without having to run the air conditioner all the time.

## Install

Run `make install` or manually install the .py and .service files as desired. Don't forget to update the path
to `daikinctl` in the service file if you put it someone other than `/usr/local/bin/daikinctl`

## Usage

Requires 2 arguments:

    ./daikinctl <Hostname or IP of Airconditioner Wifi Module> <Friendly Name of Unit>

Temperature thresholds are defined at the top of the script:

    MIN_TEMP_INSIDE=14
    MAX_TEMP_INSIDE=26
    MIN_TEMP_OUTSIDE=5
    MAX_TEMP_OUTSIDE=26

## Credits

- Reverse engineering of the HTTP protocol thanks to https://github.com/ael-code/daikin-control
