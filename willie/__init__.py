# coding=utf8
"""
__init__.py - Willie Init Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2012, Edward Powell, http://embolalia.net
Copyright © 2012, Elad Alfassa <elad@fedoraproject.org>

Licensed under the Eiffel Forum License 2.

http://willie.dftba.net/
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import time
import traceback
import signal

__version__ = '5.2.0-git'


def run(config, daemon=False):
    import willie.bot as bot
    import willie.web as web
    import willie.logger
    from willie.tools import stderr
    delay = 20
    # Inject ca_certs from config to web for SSL validation of web requests
    if not os.path.isfile(config.core.ca_certs):
        deb_certs = '/etc/ssl/certs/ca-certificates.crt'
        if not os.path.isfile(deb_certs):
            stderr('Could not open CA certificates file. SSL will not '
                   'work properly.')
        else:
            config.core.ca_certs = deb_certs
            config.save()
            stderr('CA cert location unconfigured or invalid, but they were '
                   'found elsewhere. This location will be used in the future.')
    web.ca_certs = config.core.ca_certs

    def signal_handler(sig, frame):
        if sig == signal.SIGUSR1 or sig == signal.SIGTERM:
            stderr('Got quit signal, shutting down.')
            p.quit('Closing')
    while True:
        try:
            p = bot.Willie(config, daemon=daemon)
            if hasattr(signal, 'SIGUSR1'):
                signal.signal(signal.SIGUSR1, signal_handler)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, signal_handler)
            willie.logger.setup_logging(p)
            p.run(config.core.host, int(config.core.port))
        except KeyboardInterrupt:
            break
        except Exception:
            trace = traceback.format_exc()
            try:
                stderr(trace)
            except:
                pass
            logfile = open(os.path.join(config.core.logdir, 'exceptions.log'), 'a')
            logfile.write('Critical exception in core')
            logfile.write(trace)
            logfile.write('----------------------------------------\n\n')
            logfile.close()
            os.unlink(config.core.pid_file_path)
            os._exit(1)

        if not isinstance(delay, int):
            break
        if p.hasquit:
            break
        stderr('Warning: Disconnected. Reconnecting in %s seconds...' % delay)
        time.sleep(delay)
    os.unlink(config.core.pid_file_path)
    os._exit(0)
