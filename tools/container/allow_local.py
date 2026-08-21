"""Print the command a human can use to allow framework runners locally."""

import os

if os.name == "nt":
    print('$env:AGENT_FRAMEWORK_ALLOW_LOCAL="1"')
else:
    print('export AGENT_FRAMEWORK_ALLOW_LOCAL="1"')
