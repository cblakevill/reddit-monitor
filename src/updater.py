import re
import requests
import json
import time
import calendar
from PyQt5.QtCore import (
    QThread,
    QMutex,
    QWaitCondition
)
from PyQt5 import QtCore
from config_manager import ConfigManager


class Updater:
    def __init__(self, config_man: ConfigManager):
        self._config_man = config_man
        self.updater_task = UpdaterTask(self._config_man.properties['refresh_rate'])
        self._t_last_updated = self._config_man.properties['last_updated']

    def start(self):
        self.updater_task.start()

    def set_refresh_rate(self, rate):
        self._config_man.set('refresh_rate', rate)
        self.updater_task.refresh_rate = rate
        self.updater_task.cond.wakeAll()

    def update(self):
        if len(self._config_man.properties['subreddits']) == 0:
            raise UpdaterException

        subs = '+'.join(self._config_man.properties['subreddits'])

        headers = {"User-Agent": "reddit-notifier by /u/cblakevill"}
        try:
            response = requests.get("https://www.reddit.com/r/" + subs + "/new.json?limit=10", headers=headers)
        except requests.exceptions.RequestException:
            raise UpdaterException

        if response.status_code != 200:
            raise UpdaterException

        values = json.loads(response.text)

        new_threads = self._filter_threads(values['data']['children'])

        self._t_last_updated = calendar.timegm(time.gmtime())
        self._config_man.set('last_updated', self._t_last_updated)

        return new_threads

    def _filter_threads(self, threads):
        filtered_threads = []

        if len(self._config_man.properties['filter_phrases']) == 0:
            for thread in threads:
                if thread['data']['created_utc'] > self._t_last_updated:
                        filtered_threads.insert(0, thread['data'])
        else:
            phrase_list = []
            for phrase in self._config_man.properties['filter_phrases']:
                phrase_list.append(re.escape(phrase))
            pattern = '|'.join(phrase_list)
            for thread in threads:
                if thread['data']['created_utc'] > self._t_last_updated:
                    match = re.search(pattern, thread['data']['title'], re.IGNORECASE)
                    if self._config_man.properties['filter_mode'] == 'exclude':
                        if not match:
                            filtered_threads.insert(0, thread['data'])
                    else:
                        if match:
                            filtered_threads.insert(0, thread['data'])

        return filtered_threads


class UpdaterTask(QThread):
    update = QtCore.pyqtSignal()

    def __init__(self, refresh_rate):
        super(UpdaterTask, self).__init__(None)
        self.refresh_rate = refresh_rate
        self.mutex = QMutex()
        self.cond = QWaitCondition()

    def run(self):
        while True:
            self.mutex.lock()
            while not self.cond.wait(self.mutex, self.refresh_rate * 1000):
                self.update.emit()
            self.mutex.unlock()


class UpdaterException(Exception):
    pass
