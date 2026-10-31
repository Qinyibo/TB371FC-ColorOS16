"""Run while the failed device is still connected, before force-rebooting."""
from pathlib import Path
from datetime import datetime
import argparse
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--serial',required=True)
args=parser.parse_args()
out=Path(__file__).resolve().parent/('capture-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
commands={
 'identity': ['shell','date; uname -a; cat /proc/uptime; cat /proc/sys/kernel/random/boot_id; getprop ro.boot.bootreason'],
 'wake-state': ['shell', "su -c 'cat /sys/module/nt36xxx/parameters/r94_wake_state; cat /sys/module/nt36xxx_fw_update/parameters/r94_fw_cache_hits; cat /sys/module/nt36xxx_fw_update/parameters/r94_fw_file_requests; cat /proc/gesture_control; cat /sys/power/suspend_stats/*; cat /sys/class/backlight/panel0-backlight/brightness; cat /sys/class/backlight/panel0-backlight/actual_brightness'"],
 'power':['shell','dumpsys power'],
 'display':['shell','dumpsys display'],
 'input':['shell','dumpsys input'],
 'kernel':['shell',"su -c 'dmesg'"],
 'logcat':['logcat','-b','all','-d','-v','threadtime'],
 'pstore':['shell',"su -c 'ls -l /sys/fs/pstore; cat /sys/fs/pstore/*'"],
}
for name,cmd in commands.items():
    try:
        r=subprocess.run(['adb','-s',args.serial]+cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
        data=r.stdout+b'\nEXIT_CODE='+str(r.returncode).encode()+b'\n'
    except subprocess.TimeoutExpired as e:
        data=(e.stdout or b'')+b'\nCAPTURE_COMMAND_TIMED_OUT\n'
    (out/(name+'.txt')).write_bytes(data)
    print(name,flush=True)
print(out)
