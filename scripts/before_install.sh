#!/bin/bash

# Cause entire deployment to fail if supervisor fails
set -euo pipefail

# NYC Council Councilmatic deploys on two different servers: staging and Councilmatic. For this reason, we need not differentiate between two repos. 
mkdir -p /home/datamade/nyc-council-councilmatic

# Decrypt blackbox-encrypted files 
cd /opt/codedeploy-agent/deployment-root/$DEPLOYMENT_GROUP_ID/$DEPLOYMENT_ID/deployment-archive/ && chown -R datamade.datamade . && sudo -H -u datamade blackbox_postdeploy