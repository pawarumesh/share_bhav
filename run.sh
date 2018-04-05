#!/bin/bash
if [ -z "$VCAP_APP_PORT" ];
then SERVER_PORT=8080;
else SERVER_PORT="$VCAP_APP_PORT";
fi
python server.py