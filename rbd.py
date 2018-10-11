import subprocess
import shutil
import logging
import json
import random

class RBD:
    def __init__(self):
        self.rbdbin = shutil.which('rbd')
        if not self.rbdbin:
            raise Exception("rbd binary not found")

    def info(self, image):
        params = 'info {}'.format(image)
        info = self.runrbd_json(params.split(' '))
        return info
        
    def get_protected_snapshot(self, image):
        src_snap = None
        snaps = self.snap_list(image)
        for snap in snaps:
            snap_spec = "{}@{}".format(image, snap['name'])
            info = self.info(snap_spec)
            if info['protected'] == 'true':
                src_snap = snap['name']
                break
        if not src_snap:
            src_snap = "wagent-{}".format(random.randint(1000,10000))
            self.snap_create(source, src_snap)
            self.snap_protect(source, src_snap)
        return src_snap

    def clone(self, source, dest):
        src_snap = self.get_protected_snapshot(source)
        params = 'clone {}@{} {}'.format(source, src_snap, dest)
        src_info = self.info(source)
        data_pool = src_info.get('data_pool', None)
        if data_pool:
            params += ' --data-pool {}'.format(data_pool)
        out = self.runrbd(params.split(" "))
        return out

    def snap_create(self, image, snapshot):
        params = 'snap create {}@{}'.format(image, snapshot)
        out = self.runrbd(params.split(' '))
        return out

    def snap_list(self, image):
        params = 'snap list {}'.format(image)
        snaps = self.runrbd_json(params.split(' '))
        return snaps
    
    def snap_rollback(self, image, snapshot):
        params = 'snap rollback {}@{}'.format(image, snapshot)
        out = self.runrbd(params.split(' '))
        return out
    
    def snap_remove(self, image, snapshot):
        params = 'snap remove {}@{}'.format(image, snapshot)
        out = self.runrbd(params.split(' '))
        return out

    def snap_protect(self, image, snapshot):
        params = 'snap protect {}@{}'.format(image, snapshot)
        out = self.runrbd(params.split(' '))
        return out

    def snap_unprotect(self, image, snapshot):
        params = 'snap unprotect {}@{}'.format(image, snapshot)
        out = self.runrbd(params.split(' '))
        return out

    def runrbd(self, params):
        cmd = [ self.rbdbin ]
        cmd.extend(params)
        process =  subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode == 0:
            return process.stdout.decode('utf-8')
        else:
            msg = "Error occured during rbd command: '{}'".format(cmd)
            msg += ", returncode: {}".format(process.returncode)
            msg += ", stderr: {}".format(process.stderr)
            raise Exception(msg)

    def runrbd_json(self, params):
        params.extend(['--format', 'json'])
        stdout = self.runrbd(params)
        out = json.loads(stdout)
        return out
