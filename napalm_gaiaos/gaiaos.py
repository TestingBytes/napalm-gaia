import logging
import re
import socket
import napalm
from napalm.base.base import NetworkDriver
from napalm.base.exceptions import ConnectionException, SessionLockedException, \
                                   MergeConfigException, ReplaceConfigException,\
                                   CommandErrorException


class GaiaOSDriver(NetworkDriver):
    def __init__(self, hostname,
            username='',
            password='',
            secret='',
            timeout=10,
            optional_args=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.expert_password = secret
        self.timeout = timeout
        self.optional_args = optional_args
        self.config_mode = 'clish'

    def open(self):
        device_type = 'checkpoint_gaia'
        self.device = self._netmiko_open(device_type, netmiko_optional_args=self.optional_args)

    def close(self):
        self._netmiko_close()
    
    def cli(self, commands: list) -> dict:
        output = {}
        try:
            if isinstance(commands, list):
                for cmd in commands:
                    output[cmd] = self.device.send_command(cmd)
            else:
                raise TypeError(
                    'Expected <class \'list\'> not a {}'.format(
                        type(commands)
                        )
                    )
            return output
        except (socket.error, EOFError) as e:
            raise ConnectionClosedException(str(e))
    
    def get_users(self) -> dict:
        username_regex = (
            r'^([A-z0-9_-]{1,32})\s+(\d+)\s+(\d+)\s+([/A-z0-9_-]{1,})\s+'
            r'([./A-z0-9_-]{1,})\s+((?:[\/A-z0-9_-]+\s?)+[\/A-z0-9_-])\s+'
            r'((?:[\/A-z0-9_-]+\s?)+[\/A-z0-9_-]).+?$'
        )
        users = {}
        command = 'show users'
        output = self.device.send_command(command)
        for match in re.finditer(username_regex, output, re.M):
            users[match.group(1)] = {
                'uid': match.group(2),
                'gid': match.group(3),
                'homedir': match.group(4),
                'shell': match.group(5),
                'name': match.group(6),
                'privileges': match.group(7),
            }
        return users

    def get_arp_table(self, vrf=''):
        """
                Get arp table information.
                Return a list of dictionaries having the following set of keys:
                    * interface (string)
                    * mac (string)
                    * ip (string)
                    * age (float)
                For example::
                    [
                        {
                            'interface' : 'eth0',
                            'mac'       : '5c:5e:ab:da:3c:f0',
                            'ip'        : '172.17.17.1',
                            'age'       : 0.0
                        },
                        {
                            'interface': 'eth0',
                            'mac'       : '66:0e:94:96:e0:ff',
                            'ip'        : '172.17.17.2',
                            'age'       : 0.0
                        }
                    ]
                """
        arptable_regex = ()
        commands = 'ip -statistics show'



    def get_config(self, retrieve='all', full=False):
        pass

    def get_facts(self):
        pass

    def get_interfaces(self):
        pass

    def get_interfaces_ip(self):
        pass

    def func(self):
        return 'im a Dummy'

    def _enter_expert_mode(self) -> bool:
        # --->enter func to verify new expert prompt
        output = self.device.send_command_timing('expert')
        if 'Enter expert password:' in output:
            output += self.device.send_command_timing(self.expert_password)
        else:
            return False
        return True

    def _exit_expert_mode(self) -> bool:
        # --->enter func to verify leave - check for clish prompt
        if self.config_mode == 'expert':
            self.device.send_command('exit')
        else:
            return False
        return True

if __name__ == '__main__':
    pass
