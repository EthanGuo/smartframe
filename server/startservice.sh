#!/bin/bash


EXE_MODE="--start"


show_usage()
{
    echo "Usage: $0 [action]"
    echo "commands:"
    echo "    $0 [--start]/<--stop> - Start/Stop services,'--start' can be omitted."
    exit 0
}

launch_webserver()
{
    echo "launch web server on gunicorn"
    MONGODB_URI=mongodb://localhost:27017 gunicorn -k "geventwebsocket.gunicorn.workers.GeventWebSocketWorker" --workers=2 --bind=:8080 app:app --pid /tmp/smart-web.pid --daemon --log-syslog --access-logfile ./server.log
}

launch_workserver()
{
    echo "launch smart works server"
    MONGODB_URI=mongodb://localhost:27017 celery worker --app=smartserver.v1.worker:worker --pid=/tmp/smart-worker.pid --detach --logfile ./worker.log
}

launch_periodicserver()
{
    echo "launch smart periodic server"
    MONGODB_URI=mongodb://localhost:27017 celery beat --app=smartserver.v1.worker:worker --pid=/tmp/smart-periodictask.pid --detach --logfile ./beat.log
}

stop_server()
{
    echo "Kill service $1. Please wait..."
    kill -9 `ps aux | grep $1 | grep -v grep | awk '{print $2}'` > /dev/null 2>&1
}


if [ $# -ge 1 ] ; then
    for arg in "$@"
    do
        if [ "$arg"x = "-h"x -o "$arg"x = "--help"x ]; then
            show_usage
        elif [ "$arg"x = "-s"x -o "$arg"x = "--start"x ]; then
            EXE_MODE="--start"
        elif [ "$arg"x = "-t"x -o "$arg"x = "--stop"x ]; then
            EXE_MODE="--stop"
        fi
    done
fi


if [ "$EXE_MODE" = "--start" ]; then
    echo "Start services. Please wait..."
    launch_webserver && launch_workserver && launch_periodicserver
    exit 0
elif [ "$EXE_MODE"x = "--stop"x ]; then
    echo "Stop services. Please wait..."
    stop_server gunicorn
    stop_server celery
    rm /tmp/smart-*.pid > /dev/null 2>&1
    exit 0
fi
