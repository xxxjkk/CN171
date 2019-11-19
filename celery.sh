#!/bin/bash

export C_FORCE_ROOT="true"
source /app/CN171/venv/bin/activate

beatlogfile="/applog/CN171/celery/beat.log"
workerlogfile="/applog/CN171/celery/worker.log"
starttime=`date +"%Y-%m-%d %H:%M:%S"`

#默认日志级别为info，可在命令中设置
loglevel=info
if [ x"$3" != x ];then
	if [ $3 == "debug" ];then
		loglevel=$3
	fi
fi

case $1 in
	worker)
		case $2 in
			start)
				echo "$starttime  Start Celery Worker...................."
				echo "$starttime  Start Celery Worker...................." >> $workerlogfile
				#启动worker，默认启动与CPU核数相同的线程数，可用参数-c指worker定线程
				python3 manage.py celery multi start worker -A CN171 -l $loglevel --pidfile=/var/run/celery/%n.pid --logfile=/applog/CN171/celery/%n%I.log
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker start successfully!"
							echo "$endtime  Celery Worker start successfully!" >> $workerlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker start failed!"
							echo "$endtime  Celery Worker start failed!" >> $workerlogfile
							;;
				esac
				;;
			stop)
				echo "$starttime  Stop Celery Worker....................."
				echo "$starttime  Stop Celery Worker....................." >> $workerlogfile
				#关闭worker
				ps auxww|grep "celery worker"|grep -v grep|awk '{print $2}'|xargs kill -9
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker stop successfully!"
							echo "$endtime  Celery Worker stop successfully!" >> $workerlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker stop failed!"
							echo "$endtime  Celery Worker stop failed!" >> $workerlogfile
							;;
				esac
				;;
			restart)
				echo "$starttime  Restart Celery Worker.................."
				echo "$starttime  Restart Celery Worker.................." >> $workerlogfile
				#重启worker，默认启动与CPU核数相同的线程数，可用参数-c指worker定线程数
				python3 manage.py celery multi restart worker -A CN171 -l $loglevel --pidfile=/var/run/celery/%n.pid --logfile=/applog/CN171/celery/%n%I.log
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker restart successfully!"
							echo "$endtime  Celery Worker restart successfully!" >> $workerlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker restart failed!"
							echo "$endtime  Celery Worker restart failed!" >> $workerlogfile
							;;
				esac
				;;
			status)
				#查询worker
				echo "------------$starttime  Celery Worker Process------------"
				ps auxww|grep "celery worker"|grep -v grep
				;;
			*) 
				echo "Command : sh celery.sh  worker|beat|all  start|stop|status|restart  [debug]" 
				;;
		esac
		;;
	beat)
        case $2 in
			start)
				echo "$starttime  Start Celery Beat...................."
				echo "$starttime  Start Celery Beat...................." >> $beatlogfile
				#启动beat
				python3 manage.py celery beat -A CN171 -l $loglevel --pidfile="/var/run/celery/celerybeat.pid" >> $beatlogfile 2>&1 &
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat start successfully!"
							echo "$endtime  Celery Beat start successfully!" >> $beatlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat start failed!"
							echo "$endtime  Celery Beat start failed!" >> $beatlogfile
							;;
				esac
				;;
			stop)
				echo "$starttime  Stop Celery Beat....................."
				echo "$starttime  Stop Celery Beat....................." >> $beatlogfile
				#关闭beat
				ps auxww|grep "celery beat"|grep -v grep|awk '{print $2}'|xargs kill -9
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat stop successfully!"
							echo "$endtime  Celery Beat stop successfully!" >> $beatlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat stop failed!"
							echo "$endtime  Celery Beat stop failed!" >> $beatlogfile
							;;
				esac
				;;
			restart)
				echo "$starttime  Restart Celery Beat.................."
				echo "$starttime  Restart Celery Beat.................." >> $beatlogfile
				#重启beat
				ps auxww|grep "celery beat"|grep -v grep|awk '{print $2}'|xargs kill -9 && python3 manage.py celery beat -A CN171 -l $loglevel --pidfile="/var/run/celery/celerybeat.pid" >> $beatlogfile 2>&1 &
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat restart successfully!"
							echo "$endtime  Celery Beat restart successfully!" >> $beatlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat restart failed!"
							echo "$endtime  Celery Beat restart failed!" >> $beatlogfile
							;;
				esac
				;;
			status)
				#查询beat
				echo "------------$starttime  Celery Beat Process------------"
				ps auxww|grep "celery beat"|grep -v grep
				;;
			*) 
				echo "Command : sh celery.sh  worker|beat|all  start|stop|status|restart  [debug]" 
				;;
		esac
		;;
	all)
		case $2 in
			start)
				echo "$starttime  Start Celery Beat&Worker...................."
				echo "$starttime  Start Celery Worker...................." >> $workerlogfile
				echo "$starttime  Start Celery Beat...................." >> $beatlogfile
				
				#启动worker，默认启动与CPU核数相同的线程数，可用参数-c指worker定线程
				python3 manage.py celery multi start worker -A CN171 -l $loglevel --pidfile=/var/run/celery/%n.pid --logfile=/applog/CN171/celery/%n%I.log
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker start successfully!"
							echo "$endtime  Celery Worker start successfully!" >> $workerlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker start failed!"
							echo "$endtime  Celery Worker start failed!" >> $workerlogfile
							;;
				esac
				
				#启动beat
				python3 manage.py celery beat -A CN171 -l $loglevel --pidfile="/var/run/celery/celerybeat.pid" >> $beatlogfile 2>&1 &
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat start successfully!"
							echo "$endtime  Celery Beat start successfully!" >> $beatlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat start failed!"
							echo "$endtime  Celery Beat start failed!" >> $beatlogfile
							;;
				esac
				;;
			stop)
				echo "$starttime  Stop Celery Beat&Worker....................."
				echo "$starttime  Stop Celery Worker....................." >> $workerlogfile
				echo "$starttime  Stop Celery Beat....................." >> $beatlogfile
				
				
				#关闭worker
				ps auxww|grep "celery worker"|grep -v grep|awk '{print $2}'|xargs kill -9
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker stop successfully!"
							echo "$endtime  Celery Worker stop successfully!" >> $workerlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker stop failed!"
							echo "$endtime  Celery Worker stop failed!" >> $workerlogfile
							;;
				esac
				
				#关闭beat
				ps auxww|grep "celery beat"|grep -v grep|awk '{print $2}'|xargs kill -9
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat stop successfully!"
							echo "$endtime  Celery Beat stop successfully!" >> $beatlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat stop failed!"
							echo "$endtime  Celery Beat stop failed!" >> $beatlogfile
							;;
				esac
				;;
			restart)
				echo "$starttime  Restart Celery Beat&Worker.................."
				echo "$starttime  Restart Celery Beat&Worker.................." >> $beatlogfile
				#重启worker，默认启动与CPU核数相同的线程数，可用参数-c指worker定线程数
				python3 manage.py celery multi restart worker -A CN171 -l $loglevel --pidfile=/var/run/celery/%n.pid --logfile=/applog/CN171/celery/%n%I.log
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker restart successfully!"
							echo "$endtime  Celery Worker restart successfully!" >> $workerlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Worker restart failed!"
							echo "$endtime  Celery Worker restart failed!" >> $workerlogfile
							;;
				esac
				
				#重启beat
				ps auxww|grep "celery beat"|grep -v grep|awk '{print $2}'|xargs kill -9 && python3 manage.py celery beat -A CN171 -l $loglevel --pidfile="/var/run/celery/celerybeat.pid" >> $beatlogfile 2>&1 &
				case $? in
						0) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat restart successfully!"
							echo "$endtime  Celery Beat restart successfully!" >> $beatlogfile
							;;
						*) 
							endtime=`date +"%Y-%m-%d %H:%M:%S"`
							echo "$endtime  Celery Beat restart failed!"
							echo "$endtime  Celery Beat restart failed!" >> $beatlogfile
							;;
				esac
				;;
			status)
				#查询beat
				echo "------------$starttime  Celery Beat Process------------"
				ps -ef|grep "celery beat"|grep -v grep
				#查询worker
				echo "------------$starttime  Celery Worker Process------------"
				ps -ef|grep "celery worker"|grep -v grep
				;;
			*) 
				echo "Command : sh celery.sh  worker|beat|all  start|stop|status|restart  [debug]" 
				;;
		esac
		;;
	*) 
		echo "Command : sh celery.sh  worker|beat|all  start|stop|status|restart  [debug]" 
		;;
esac
