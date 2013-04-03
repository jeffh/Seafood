"""All low-level tasks that the highlevel module invokes
"""
from bootstrapper.lowlevel.dispatchers import purge_salt, bootstrap
import bootstrapper.lowlevel.osx
import bootstrapper.lowlevel.linux
from bootstrapper.lowlevel.tasks import (
    minion, master, hostname, upload, create_minion_key
)
from bootstrapper.lowlevel.utils import upload_key
