install:
	install -m0755 daikinctl.py /usr/local/bin/daikinctl
	install -m0644 daikinctl.service /etc/systemd/system/daikinctl.service
