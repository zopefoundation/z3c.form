import os

PREFER_Z3C_PT = os.environ.get("PREFER_Z3C_PT", 'false').lower() in \
                ('y', 'yes', 't', 'true', 'on', '1')

