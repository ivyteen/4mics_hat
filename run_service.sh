#!/bin/bash

MOUNT_DIR="/media/pi"
LS_CMD="ls /dev/sd[a-g][1-9]"
WIFI_SET_FILE_PATH="/media/pi/wifi-set"

RAMDISK_PATH="/mnt/ramdisk"
WPA_CONF_PATH="$RAMDISK_PATH/wpa_psk.conf"


RUN="/home/pi/4mics_hat/magiceco_pixels.py"
ERROR_IND="/home/pi/4mics_hat/error_indicator.py"


function usbDiskMount() {
	local retval
	if mountpoint -q $MOUNT_DIR; then
		#echo "$MOUNT_DIR is already been mounted, start the code."
		retval=0
	else
		#echo "Not Mounted, Try to mount."
		declare -a LS_OUTPUT;
		LS_OUTPUT=($($LS_CMD))
		if [ ${#LS_OUTPUT[@]} -ne 1 ]; then
			#echo "Two or more USB disk is connected"
			#echo "Remain Only 1"
			# ERROR indication with LED
			retval=1
		else
		
			sudo mount ${LS_OUTPUT[0]} $MOUNT_DIR
			if [ $? -eq 0 ]; then
				#echo "Disk Mounted"
				retval=0
			else
				#echo "Disk not Mounted"
				retval=2
				# ERROR indication with LED
			fi
		fi
	fi

	#Check if the model file is in the disk
		
	if [ $retval -eq 0 ]; then
		if [ ! -e $WIFI_SET_FILE_PATH ]; then
			retval=3
		fi
	fi

	echo $retval
}

function ramdiskMount() {
	if [ ! -e $RAMDISK_PATH ]; then
		sudo mkdir $RAMDISK_PATH
	fi

	sudo mount -t tmpfs -o size=1K tmpfs $RAMDISK_PATH

}


if [ ! -e $MOUNT_DIR ]; then
	sudo mkdir $MOUNT_DIR
fi


retval=$(usbDiskMount)


if [ $retval -eq 0 ]; then

	ramdiskMount

	SET=$(seq 0 1)
	
	for i in $SET
	do
		read line
		if [ $i -eq 0 ]; then
			SSID=$line
		else
			PW=$line
		fi
		
	done < $WIFI_SET_FILE_PATH

	sudo wpa_passphrase $SSID $PW > $WPA_CONF_PATH
	sudo ifconfig wlan0 up
	sudo wpa_supplicant -B -iwlan0 -c$WPA_CONF_PATH -Dnl80211,wext
	if [ $? -ne 0 ]; then
		retval=4
		/usr/bin/python3 $ERROR_IND $retval

	else
		sudo dhclient wlan0
		/usr/bin/python3 $RUN
	fi


else
	echo $retval
	/usr/bin/python3 $ERROR_IND $retval
fi
