#! /usr/bin/env python
# -*- coding: utf-8 -*-


import subprocess
import traceback
from time import sleep, time

from com.dtmilano.android.viewclient import ViewClient


def loop_until(func, seconds=15, nofail=False):
    """
    Helper method for try-until behaviour
    """
    start = time()
    firstrun = True
    while True:
        try:
            print("Looping " + str(func))
            ret = func(firstrun=firstrun)
            if ret != "continue":
                break
        except Exception:
            traceback.print_exc()
            if (time() - start) > seconds:
                if nofail:
                    return
                else:
                    raise
        if (time() - start) > seconds:
            return
        sleep(0.5)
        firstrun = False


class AdbException(Exception):
    pass


class AndroidViewBase:
    def __init__(self, chromecast_name, connect_ip=None):
        self.chromecast_name = chromecast_name
        self.connect_ip = connect_ip

    def main(self, *args, **kwargs):
        started = subprocess.check_output(["adb", "devices"]).decode('utf8')
        print(started)
        if 'daemon not running' in started:
            sleep(5)
        if self.connect_ip:
            print('Connecting to adb device {}...'.format(self.connect_ip))
            connect_stdout = (subprocess.check_output(["adb", "connect", self.connect_ip])
                              .decode('utf8'))
            print(connect_stdout)
            if 'already connected' not in connect_stdout:
                sleep(2)

        devices_out = subprocess.check_output(["adb", "devices"]).decode('utf8')
        if devices_out.split('\n')[1].strip() == '':
            raise AdbException('No devices connected')

        kwargs1 = {"verbose": False, "ignoresecuredevice": False, "ignoreversioncheck": False}
        device, serialno = ViewClient.connectToDeviceOrExit(**kwargs1)

        kwargs2 = {
            "forceviewserveruse": False,
            "startviewserver": True,
            "autodump": False,
            "ignoreuiautomatorkilled": True,
            "compresseddump": True,
            "useuiautomatorhelper": False,
            "debug": {},
        }
        self.vc = ViewClient(device, serialno, **kwargs2)
        self.vc.device.shell("input keyevent KEYCODE_WAKEUP")
        self.vc.device.shell("input keyevent KEYCODE_WAKEUP")

        self.run(*args, **kwargs)

        self.vc.device.shell("input keyevent KEYCODE_HOME")
        self.vc.device.shell("input keyevent KEYCODE_SLEEP")

    def run(self, *args, **kwargs):
        """
        Override this to get a basic script running, with the screen woken and
        going to sleep after finished,
        """
        raise NotImplementedError()
