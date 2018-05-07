import json
import os


class ConfigManager:

    default_properties = {
                'subreddits': [],
                'refresh_rate': 300,
                'filter_mode': 'include',
                'filter_phrases': [],
                'notification_sound_path': "",
                'sound_notify': 0,
                'popup_notify': 0,
                'last_updated': 0
            }

    def __init__(self, fp):
        self._config_path = fp
        self.properties = self.default_properties

        if os.path.exists(fp):
            properties = json.load(fp=open(fp, "r"))
            if self._valid_settings(properties):
                self.properties = properties

    def save(self):
        json.dump(fp=open(self._config_path, "w"), obj=self.properties)

    def set(self, property, val):
        self.properties[property] = val

    def _valid_settings(self, properties):
        if not all(p in properties for p in self.default_properties):
            return False

        # TODO: rest of the validation

        return True


