#!/bin/bash

settingsfile=`$(cd $(dirname $0));pwd`/CN171/settings.py


case $1 in
        True)
		echo "Settings file is : "$settingsfile
                sed -i 's/DEBUG = .*/DEBUG = True/g' $settingsfile
                case $? in
                        0) echo "set logdebug successfully!";;
                        *) echo "set logdebug failed!";;
                esac
                ;;
        False)
		echo "Settings file is : "$settingsfile
                sed -i 's/DEBUG = .*/DEBUG = False/g' $settingsfile
                case $? in
                        0) echo "set logdebug successfully!";;
                        *) echo "set logdebug failed!";;
                esac
                ;;
        *) echo "Command : sh logdebug.sh True|False" ;;
esac

