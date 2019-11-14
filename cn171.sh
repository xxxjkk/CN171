#!/bin/bash

logfile="/applog/CN171/cn171run.log"
starttime=`date +"%Y-%m-%d %H:%M:%S"`

case $1 in
        start)
                source /app/CN171/venv/bin/activate
                echo "$starttime  Start CN171...................." >> $logfile
                python3 manage.py runserver 0.0.0.0:8001 >> $logfile 2>&1 &
                endtime=`date +"%Y-%m-%d %H:%M:%S"`
                case $? in
                        0) echo "$endtime  CN171 start successfully!" >> $logfile;;
                        *) echo "$endtime  CN171 stop failed!" >> $logfile;;
                esac
                ;;
        stop)
                echo "$starttime  Stop CN171...................." >> $logfile
                ps -ef |grep "python3 manage.py runserver" |grep -v grep |awk '{print $2}' |xargs -I {} kill -9 {}
                endtime=`date +"%Y-%m-%d %H:%M:%S"`
                case $? in
                        0) echo "$endtime  CN171 stop successfully!" >> $logfile;;
                        *) echo "$endtime  CN171 stop failed!" >> $logfile;;
                esac
                ;;
        status)
                echo "------------$starttime  CN171 Process------------"
                ps -ef |grep "python3 manage.py runserver" |grep -v grep
                ;;
        *)
                echo "Command : sh cn171.sh start|stop|status"
                ;;
esac
