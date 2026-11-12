"""Read-only TB371FC wake capture with hidden Windows child processes."""

import argparse
import ctypes
from datetime import datetime
import json
import msvcrt
import os
from pathlib import Path
import re
import subprocess
import time
import zipfile


CREATE_NO_WINDOW = 0x08000000
WAKE_LINES = re.compile(
    r'R94_|R97_DIAG|R10[478]_|R10x_FORCE|PANEL_DEAD|LCD bias|crc_done|'
    r'nvt_read_fw_history|nvt_ts_(?:suspend|pm_suspend|pm_resume)|'
    r'nvt_check_fw_reset_state|hactive=|DSI PLL|PM: suspend|frame_retired_error'
)
FAILURE = re.compile(r'PREPANEL_FW_FAILED|PREPARE_FAILED|REK_FAILED|PANEL_DEAD|NATIVE_UNBLANK_FAILED')
ANSI = re.compile(r'\x1b\[[0-9;]*m')
BOOT_ID = re.compile(r'^[a-f0-9-]{36}$')
REMOTE_PATH = re.compile(r'^/data/local/tmp/tb-wake-(?:trace|logger)-[a-f0-9-]+$')


def timestamp():
    return datetime.now().astimezone().isoformat(timespec='milliseconds')


def atomic_write(path, data):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)


class Journal:
    def __init__(self, directory):
        self.directory = directory
        self.path = directory / 'wake-current.log'

    def write(self, text):
        if self.path.exists() and self.path.stat().st_size >= 8 * 1024 * 1024:
            archived = self.directory / f'wake-{datetime.now():%Y%m%d-%H%M%S-%f}.log'
            self.path.replace(archived)
            for old in sorted(self.directory.glob('wake-2*.log'))[:-15]:
                old.unlink()
        with self.path.open('a', encoding='utf-8') as log:
            log.write(f'{timestamp()} {text}\n')


class Recorder:
    def __init__(self, config):
        self.config = config
        self.directory = Path(config['log_directory']).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.journal = Journal(self.directory)
        self.boot = ''
        self.remote = ''
        self.remote_sizes = {}
        self.kernel_time = -1.0
        self.kernel_lines = set()
        self.last_snapshot = 0.0
        self.last_dmesg = 0.0
        self.failures = 0
        self.online = None
        self.last_event = ''
        try:
            previous = json.loads((self.directory / 'status.json').read_text(encoding='utf-8'))
            if (BOOT_ID.fullmatch(previous.get('boot_id', '')) and
                    REMOTE_PATH.fullmatch(previous.get('device_log_directory', ''))):
                self.boot = previous['boot_id']
                self.remote = previous['device_log_directory']
        except (OSError, ValueError):
            pass

    def adb(self, arguments, timeout=8):
        try:
            result = subprocess.run(
                [self.config['adb'], '-s', self.config['serial'], *arguments],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=timeout, creationflags=CREATE_NO_WINDOW,
            )
            if result.returncode:
                return None
            return result.stdout.decode('utf-8', errors='replace').replace('\r\n', '\n')
        except (OSError, subprocess.TimeoutExpired):
            return None

    def shell(self, command, timeout=8):
        return self.adb(['shell', '-T', command], timeout)

    def status(self, state, detail=''):
        info = {
            'updated': timestamp(), 'state': state, 'detail': detail,
            'pid': os.getpid(), 'serial': self.config['serial'],
            'boot_id': self.boot, 'device_log_directory': self.remote,
            'last_event': self.last_event,
        }
        atomic_write(self.directory / 'status.json', json.dumps(info, ensure_ascii=False, indent=2).encode('utf-8'))

    def ensure_device_recorder(self):
        candidate = self.remote or self.config.get('existing_device_directory', '')
        if REMOTE_PATH.fullmatch(candidate):
            check = (f'p=$(cat {candidate}/pid 2>/dev/null); '
                     f'test -n "$p" && kill -0 "$p" 2>/dev/null && '
                     f'grep -Fq "{candidate}/record.sh" /proc/"$p"/cmdline && '
                     f'grep -Fq "{self.boot}" {candidate}/wake.log && echo running')
            if (self.shell(check) or '').strip() == 'running':
                self.remote = candidate
                return True

        candidate = f'/data/local/tmp/tb-wake-logger-{self.boot}'
        if self.shell(f'umask 077; mkdir -p {candidate}') is None:
            return False
        script = Path(__file__).with_name('record_on_device.sh')
        if self.adb(['push', str(script), f'{candidate}/record.sh']) is None:
            return False
        if self.shell(f'sh -n {candidate}/record.sh') is None:
            return False
        start = (f'setsid /system/bin/sh {candidate}/record.sh {candidate} 0 '
                 f'</dev/null >{candidate}/recorder-status.log 2>&1 & '
                 f'echo $! >{candidate}/pid')
        if self.shell(start) is None:
            return False
        self.remote = candidate
        self.remote_sizes.clear()
        verify = (f'p=$(cat {candidate}/pid); kill -0 "$p" && '
                  f'grep -Fq "{candidate}/record.sh" /proc/"$p"/cmdline && echo running')
        if (self.shell(verify) or '').strip() != 'running':
            return False
        self.journal.write(f'Device event recorder started at {candidate}')
        return True

    def save_device_logs(self):
        if not self.remote:
            return
        for name in ('wake.log', 'wake.previous.log'):
            size = self.shell(f'wc -c < {self.remote}/{name} 2>/dev/null')
            if size is None or not size.strip().isdigit():
                continue
            size = int(size.strip())
            if self.remote_sizes.get(name) == size:
                continue
            content = self.shell(f'cat {self.remote}/{name}')
            if content is None:
                continue
            suffix = 'previous' if name == 'wake.previous.log' else 'current'
            target = self.directory / f'device-{self.boot}-{suffix}.log'
            atomic_write(target, content.encode('utf-8'))
            self.remote_sizes[name] = size
            if name == 'wake.log':
                self.last_event = content.splitlines()[-1] if content.splitlines() else ''
            for old in sorted(self.directory.glob('device-*.log'), key=lambda p: p.stat().st_mtime)[:-20]:
                old.unlink()

    def snapshot(self):
        if time.monotonic() - self.last_snapshot < 60 or self.failures >= 3:
            return
        self.last_snapshot = time.monotonic()
        self.failures += 1
        name = f'incident-{datetime.now():%Y%m%d-%H%M%S}-{self.boot[:8]}.zip'
        path = self.directory / name
        queries = {
            'kernel.txt': 'dmesg',
            'power.txt': 'dumpsys power',
            'display.txt': 'dumpsys display',
            'input.txt': 'dumpsys input',
        }
        with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for filename, query in queries.items():
                value = self.shell(query, timeout=6)
                if value is not None:
                    archive.writestr(filename, value[:4 * 1024 * 1024])
        self.journal.write(f'Fault evidence saved in {name}')
        for old in sorted(self.directory.glob('incident-*.zip'))[:-8]:
            old.unlink()

    def read_kernel(self):
        query = ("dmesg | grep -Ei 'R94_|R97_DIAG|R10[478]_|R10x_FORCE|PANEL_DEAD|"
                 "LCD bias|crc_done|nvt_read_fw_history|nvt_ts_(suspend|pm_suspend|pm_resume)|"
                 "nvt_check_fw_reset_state|hactive=|DSI PLL|PM: suspend|frame_retired_error'")
        result = self.shell(query)
        if result is None:
            return
        fault = False
        for line in result.splitlines():
            line = ANSI.sub('', line).strip()
            match = re.match(r'^\[\s*(\d+\.\d+)\]', line)
            if not match or not WAKE_LINES.search(line):
                continue
            tick = float(match[1])
            if tick < self.kernel_time or (tick == self.kernel_time and line in self.kernel_lines):
                continue
            if tick > self.kernel_time:
                self.kernel_time = tick
                self.kernel_lines.clear()
            self.kernel_lines.add(line)
            self.journal.write(line)
            fault |= bool(FAILURE.search(line))
        if fault:
            self.snapshot()

    def tick(self):
        boot = (self.shell('cat /proc/sys/kernel/random/boot_id') or '').strip()
        if not BOOT_ID.fullmatch(boot):
            if self.online is not False:
                self.journal.write('Device disconnected; waiting for the same serial')
            self.online = False
            self.status('waiting', 'ADB device is not connected or not authorized')
            return
        if boot != self.boot:
            self.save_device_logs()
            self.boot = boot
            self.remote = ''
            self.remote_sizes.clear()
            self.kernel_time = -1.0
            self.kernel_lines.clear()
            self.failures = 0
            self.journal.write(f'BOOT {boot} {(self.shell("uname -v") or "").strip()}')
        if self.online is not True:
            self.journal.write('Device connected')
        self.online = True
        recording = self.ensure_device_recorder()
        self.save_device_logs()
        if time.monotonic() - self.last_dmesg >= 30:
            self.read_kernel()
            self.last_dmesg = time.monotonic()
        self.status('recording' if recording else 'host-only', '10-second connection checks; kernel capture every 30 seconds')

    def run(self):
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.SetPriorityClass.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
        kernel.SetPriorityClass.restype = ctypes.c_int
        kernel.SetErrorMode(0x0001 | 0x0002 | 0x8000)
        if not kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000):
            self.journal.write(f'Could not set below-normal priority: {ctypes.get_last_error()}')
        self.journal.write('Silent recorder started')
        stop = self.directory / 'stop.request'
        try:
            while not stop.exists():
                try:
                    self.tick()
                except Exception as error:
                    self.journal.write(f'Recorder error {type(error).__name__}: {error}')
                    self.status('retrying', str(error))
                for _ in range(10):
                    if stop.exists():
                        break
                    time.sleep(1)
        finally:
            if self.remote and REMOTE_PATH.fullmatch(self.remote):
                stop_device = (
                    f'p=$(cat {self.remote}/pid 2>/dev/null); '
                    'case "$p" in ""|*[!0-9]*) exit 0;; esac; '
                    f'if grep -Fq "{self.remote}/record.sh" /proc/"$p"/cmdline 2>/dev/null; '
                    'then kill -TERM -- "-$p"; fi'
                )
                self.shell(stop_device)
            self.status('stopped')
            self.journal.write('Silent recorder stopped')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8-sig'))
    directory = Path(config['log_directory'])
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'worker.lock').open('a+b') as lock:
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return
        if os.fstat(lock.fileno()).st_size == 0:
            lock.write(b'0')
            lock.flush()
        Recorder(config).run()


if __name__ == '__main__':
    main()
