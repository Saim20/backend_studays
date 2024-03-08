# import imp
# import os
# import sys


# sys.path.insert(0, os.path.dirname(__file__))

# wsgi = imp.load_source('wsgi', 'app.py')
# application = wsgi.app

import os
import sys
from importlib import util

# Insert the directory of this file into the first position of sys.path
# to ensure it has priority over other paths during module import.
sys.path.insert(0, os.path.dirname(__file__))

# Dynamically load the module specified by the path
spec = util.spec_from_file_location("wsgi", os.path.join(os.path.dirname(__file__), 'app.py'))
wsgi = util.module_from_spec(spec)
spec.loader.exec_module(wsgi)

# Assign the application object from the loaded module
application = wsgi.app