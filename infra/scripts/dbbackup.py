#!/usr/bin/python
###########################################################
#
# This python script is used for mysql database backup
# using mysqldump utility.
#
###########################################################

# Import required python libraries
import os
import time
import datetime

# list of databases and its users to backup.
backups = [ 
  {
    'host': 'localhost',
    'name': 'vron',
    'user': 'vron',
    'password': '89Kio3PAwFjnBsdZ91'
  },
]

BACKUP_PATH = '/backup/vron/'

# Getting current datetime to create seprate backup folder like "12012013-071334".
DATETIME = time.strftime('%m%d%Y-%H%M%S')

TODAYBACKUPPATH = BACKUP_PATH + DATETIME

# Checking if backup folder already exists or not. If not exists will create it.
if not os.path.exists( TODAYBACKUPPATH ):
    os.makedirs( TODAYBACKUPPATH )

for db in backups:
  dumpcmd = "mysqldump -u " + db['user'] + " -p" + db['password'] + " " + db['name'] + " > " + TODAYBACKUPPATH + "/" + db['name'] + ".sql"
  os.system(dumpcmd)