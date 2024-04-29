#!/bin/bash

# This script is used by scalingo each time the application
# is deployed.
# For review apps, if a first-deploy hook is defined, then
# that first deploy hook will override this post deploy hook.

echo "Entering post deploy hook"
make update
echo "Completed post deploy hook"
