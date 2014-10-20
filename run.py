

import logging
import logging.config
#logging.config.fileConfig("logging.conf")

from webui import webui
from database.sqlite.sqlite import *

# config = {
WeeklyDb = WeeklySqliteDB()

# }

# make some test
test_main()

# start the main server
webui.main(WeeklyDb = WeeklyDb)        # ** kargs

