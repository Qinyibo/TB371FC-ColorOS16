import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from monitor_24h import Ring,metadata,reasons_for,cleanup_command

class MonitorTests(unittest.TestCase):
    def test_cleanup_has_no_embedded_null(self):
        command=cleanup_command('12345')
        self.assertNotIn(chr(0),command)
        self.assertIn(r"\000",command)
        with self.assertRaises(ValueError):cleanup_command('12;exit')
    def test_ring_freeze_survives_wrap(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);ring=Ring(root/'ring',chunk=8,slots=3)
            for value in [b'first---',b'second--',b'third---']:ring.write(value)
            ring.freeze(root/'evidence');before={p.name:p.read_bytes() for p in (root/'evidence').glob('*.log')}
            for _ in range(8):ring.write(b'NEW-----')
            ring.close()
            self.assertEqual(before,{p.name:p.read_bytes() for p in (root/'evidence').glob('*.log')})
            self.assertEqual(len(list((root/'ring').glob('*.log'))),3)
    def test_real_transition_triggers(self):
        self.assertEqual(reasons_for(b'ActivityManager: Process com.android.systemui (pid 3079) has died: pers',None,None),['systemui_process_died'])
        self.assertEqual(reasons_for(b'Process com.example.game (pid 12) has died',None,None),[])
        self.assertEqual(reasons_for(None,'BOOT=A failed=1','BOOT=A failed=0'),['touch_failed'])
        self.assertEqual(reasons_for(None,'BOOT=A failed=1','BOOT=A failed=1'),[])
        self.assertEqual(reasons_for(None,'BOOT=B failed=0','BOOT=A failed=0'),['device_boot_changed'])
    def test_status_reader_lock_does_not_stop_recording(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'status.json';metadata(path,{'bytes':1})
            with patch.object(Path,'replace',side_effect=PermissionError('Windows reader')):metadata(path,{'bytes':2})
            self.assertEqual(json.loads(path.read_text())['bytes'],1)
            metadata(path,{'bytes':3});self.assertEqual(json.loads(path.read_text())['bytes'],3)
if __name__=='__main__':unittest.main()
