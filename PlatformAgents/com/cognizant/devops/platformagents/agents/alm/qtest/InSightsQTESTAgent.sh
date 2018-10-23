#-------------------------------------------------------------------------------
# Copyright 2017 Cognizant Technology Solutions
#   
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
#-------------------------------------------------------------------------------
#! /bin/sh
# /etc/init.d/InSightsQTESTAgent

### BEGIN INIT INFO
# Provides: Runs a Python script on startup
# Required-Start: BootPython start
# Required-Stop: BootPython stop
# Default-Start: 2 3 4 5
# Default-stop: 0 1 6
# Short-Description: Simple script to run python program at boot
# Description: Runs a python program at boot
### END INIT INFO


#export INSIGHTS_AGENT_HOME=/home/ec2-user/insightsagents
source /etc/profile

case "$1" in
  start)
    if [[ $(ps aux | grep '[a]lm.qtest.QtestAgent' | awk '{print $2}') ]]; then
     echo "InSightsQTESTAgent already running"
    else
     echo "Starting InSightsQTESTAgent"
     cd $INSIGHTS_AGENT_HOME/PlatformAgents/qtest
     python -c "from com.cognizant.devops.platformagents.agents.alm.qtest.QtestAgent import QtestAgent; QtestAgent()" &
    fi
    if [[ $(ps aux | grep '[a]lm.qtest.QtestAgent' | awk '{print $2}') ]]; then
     echo "InSightsQTESTAgent Started Sucessfully"
    else
     echo "InSightsQTESTAgent Failed to Start"
    fi
    ;;
  stop)
    echo "Stopping InSightsQTESTAgent"
    if [[ $(ps aux | grep '[a]lm.qtest.QtestAgent' | awk '{print $2}') ]]; then
     sudo kill -9 $(ps aux | grep '[a]lm.qtest.QtestAgent' | awk '{print $2}')
    else
     echo "InSightsQTESTAgent already in stopped state"
    fi
    if [[ $(ps aux | grep '[a]lm.qtest.QtestAgent' | awk '{print $2}') ]]; then
     echo "InSightsQTESTAgent Failed to Stop"
    else
     echo "InSightsQTESTAgent Stopped"
    fi
    ;;
  restart)
    echo "Restarting InSightsQTESTAgent"
    if [[ $(ps aux | grep '[a]lm.qtest.QtestAgent' | awk '{print $2}') ]]; then
     echo "InSightsQTESTAgent stopping"
     sudo kill -9 $(ps aux | grep '[a]lm.qtest.QtestAgent' | awk '{print $2}')
     echo "InSightsQTESTAgent stopped"
     echo "InSightsQTESTAgent starting"
     cd $INSIGHTS_AGENT_HOME/PlatformAgents/qtest
     python -c "from com.cognizant.devops.platformagents.agents.alm.qtest.QtestAgent import QtestAgent; QtestAgent()" &
     echo "InSightsQTESTAgent started"
    else
     echo "InSightsQTESTAgent already in stopped state"
     echo "InSightsQTESTAgent starting"
     cd $INSIGHTS_AGENT_HOME/PlatformAgents/qtest
     python -c "from com.cognizant.devops.platformagents.agents.alm.qtest.QtestAgent import QtestAgent; QtestAgent()" &
     echo "InSightsQTESTAgent started"
    fi
    ;;
  status)
    echo "Checking the Status of InSightsQTESTAgent"
    if [[ $(ps aux | grep '[a]lm.qtest.QtestAgent' | awk '{print $2}') ]]; then
     echo "InSightsQTESTAgent is running"
    else
     echo "InSightsQTESTAgent is stopped"
    fi
    ;;
  *)
    echo "Usage: /etc/init.d/InSightsQTESTAgent {start|stop|restart|status}"
    exit 1
    ;;
esac
exit 0