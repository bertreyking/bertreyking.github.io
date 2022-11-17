
#!/bin/bash

#def_clean_logs_evevts
events_logs="/var/log/applogs_cleanup-$HOSTNAME-`date +%Y-%m%d-%H%M`.txt"

#def_cmp_app_logs_dir
log_dir="/logs/appsdir/applogs"
log_bk="/logs/appsdir/bk"

#collect_logssize
logsize=$(du -sh $log_dir | awk '$1=($1-G) {print $1}' | cut -d '.' -f 1)

#def_clean_env
a=75

function clean_logs {

	if [ $logsize -gt $a ];
	then
        find $log_dir -name "*.log" -exec mv {} $log_bk \;
        tar -zcvPf applogs-$HOSTNAME-`date +%Y-%m%d-%H%M`.tar.gz $log_bk && mv applogs-*.tar.gz /logs/backup/
        rm -rf $log_bk/*
	else
        du -sh $log_dir | awk '{print $1}'
	fi
}

function report {

	clean_logs
}

report >$events_logs

#def_clean_60d_ago's_logs_file
find /var/log/ -mmin +60 -name applogs_cleanup_*.txt -exec rm {} \;
