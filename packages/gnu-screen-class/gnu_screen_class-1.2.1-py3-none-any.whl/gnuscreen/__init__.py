import datetime
import importlib.metadata
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Iterable, Optional

_EXE = '/usr/bin/screen'
_CACHE = {}

gnuscreen_logger = logging.getLogger(__name__)

__version__ = importlib.metadata.version('gnu-screen-class')


@dataclass
class GnuScreen:
    id: int
    name: str
    launched: datetime.datetime
    attached: bool

    @property
    def exists(self) -> bool:
        """Return true if screen with 'name' exists"""
        try:
            os.kill(self.id, 0)
            return True
        except OSError as e:
            if e.errno == 3:
                return False
            raise

    def execute(self, cmds: Iterable[str]) -> None:
        """Execute commands on screen"""
        if isinstance(cmds,str):
            raise ValueError("Pass tuple or list of strings, not a string")
        bcmd = ['/usr/bin/screen', '-S', str(self.id), '-X', 'exec', '.!!', 'echo']
        bcmd.extend(cmds)
        subprocess.run(bcmd, check=True)

    def close(self):
        """Close screen"""
        cmd = ('/usr/bin/screen', '-S', str(self.id), '-X', 'kill')
        subprocess.run(cmd, check=True)
        gnuscreen_logger.debug(f'Set {cmd}')

    @staticmethod
    def query(name: str) -> Optional['GnuScreen']:
        """Get existing screen if it exists""" 
        if (gs := _CACHE.get(name)) is not None:
            gnuscreen_logger.info(f'existing {name}')
            return gs
        gnuscreen_logger.debug('refreshing cache')
        GnuScreen.list()  # refresh cache
        if gnuscreen_logger.isEnabledFor(logging.DEBUG):
            for k, v in _CACHE.items():
                gnuscreen_logger.debug(f'{k} = {v}')
        return _CACHE.get(name)

    @staticmethod
    def get(name: str) -> 'GnuScreen':
        """Get existing screen or create new one"""
        if (gs := GnuScreen.query(name)) is None:
            subprocess.run((_EXE, '-S', name, '-m', '-d'), stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                           start_new_session=True, check=True)
            return GnuScreen.query(name)
        else:
            return gs

    @staticmethod
    def list() -> Iterable['GnuScreen']:
        """List existing screens"""
        global _CACHE
        current = {}
        cp = subprocess.run((_EXE, '-ls'), stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, check=False)
        for line in cp.stdout.split('\n'):
            gnuscreen_logger.debug(line)
            parts = line.split('.')
            if len(parts) == 2 and parts[0][0] == '\t':
                id = int(parts[0])
                data = parts[1].split('(')
                name = data[0].strip()
                dt = data[1].split(')')[0]
                launched = datetime.datetime.strptime(dt, '%m/%d/%Y %I:%M:%S %p')
                attached = 'Attached' in data[2]
                current[name] = GnuScreen(id, name, launched, attached)
                gnuscreen_logger.debug(f'id {id} {name} {launched}')
        _CACHE = current
        return current.values()
