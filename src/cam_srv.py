import logging as log
import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import List

import numpy as np
import urllib3
from cv2 import cv2 as cv
from urllib3 import HTTPResponse

import camera
import reactives
import robot_finder
from tools import do_random_task, s2ns

camera_config = camera.Configuration()
camera_config.host = "192.168.137.22:9001/camera"
camera_config.timeout = urllib3.Timeout(connect=1, read=2)

# camera_config.retry = urllib3.Retry(total=5, backoff_factor=0.1)
# camera_config.retry.RETRY_AFTER_STATUS_CODES = list(urllib3.Retry.RETRY_AFTER_STATUS_CODES) + [422]

# camera_config.debug = True
camera_api = camera.DefaultApi(camera.ApiClient(camera_config))
# create an instance of the API class

# camera_api.settings_aecompensation_put(camera.AECompensationValue(-2.0))
# camera_api.settings_aelock_put(camera.AELockValue(True))
# camera_api.settings_aemode_put(camera.AEModeValue(camera.AEMode.OFF))
# camera_api.settings_iso_put(camera.ISOValue(50))
# camera_api.settings_shutterspeed_put(body=camera.ShutterSpeedValue(100000))


images = reactives.Subject(np.ndarray(()))


def image():
    response: HTTPResponse = camera_api.image_get(_preload_content=False)

    np_arr = np.frombuffer(response.data, np.uint8)
    img = cv.imdecode(np_arr, cv.IMREAD_COLOR)
    log.debug("Image size: %s", img.shape[:2])

    images.on_next(img)

    return img


class Setting:
    def __init__(self, setting):
        self.setting = setting
        self.info = camera_api.settings_setting_get(setting)
        self._value = self.info.value
        self.init_val = self.value
        self.last_val = None
        self.backups = list()

    @property
    def value(self):
        # self.info = camera_api.settings_setting_get(self.setting)
        # return self.info.value
        return self._value

    def set(self, new_val):
        curr_val = self.value
        # if new_val in [curr_val, self.last_val]:
        if new_val in [curr_val]:
            return False

        log.info(f"Changing {self.setting} from {curr_val} to {new_val}")
        camera_api.settings_setting_put(
            camera.SettingValue(str(new_val)),
            self.setting
        )
        self.last_val = curr_val
        self._value = new_val
        return True

    def sync(self):
        self.info = camera_api.settings_setting_get(self.setting)
        self._value = self.info.value

    def backup(self):
        if self.backups and self.backups[-1] == self._value:
            return

        log.debug("Backing up %s with value %s", self.setting, self._value)
        self.backups.append(self._value)

    def restore(self):
        if not self.backups:
            log.debug("No backups for %s", self.setting)
            return False

        change = self.set(self.backups.pop())
        if change:
            log.debug("%s restored to %s", self.setting, self._value)
        return change

    def reset(self):
        self.set(self.init_val)
        self.reset_history()

    def reset_history(self):
        self.last_val = None

    def __str__(self):
        return f"{self.setting}: {self.value}; Info: {self.info}"


@dataclass
class SettingsContainer(Setting):
    settings_: List[Setting]

    def __enter__(self):
        log.info(str(self))
        return self

    def reset(self):
        for setting in self.settings_:
            setting.reset()

    def backup(self):
        for setting in self.settings_:
            setting.backup()

    def restore(self):
        change = False
        for setting in self.settings_:
            change |= setting.restore()
        return change

    def __str__(self):
        return "\n".join(map(str, self.settings_))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset()


class ParamOptimizer:

    @staticmethod
    def on_found(_):
        exposure.backup()
        focus.backup()

    @staticmethod
    def on_not_found(case) -> None:
        change = False
        change |= exposure.restore()
        change |= focus.restore()
        if change:
            return

        change = focus.near()
        if change:
            return

        if case == robot_finder.NotFoundCase.FEW_POINTS:
            change = do_random_task([
                exposure.increase,
                exposure.decrease,
                # focus.auto,
            ])
        elif case == robot_finder.NotFoundCase.MANY_POINTS:
            change = do_random_task([
                exposure.decrease,
                # focus.near,
            ])

        if not change:
            do_random_task([
                exposure.increase,
                exposure.decrease,
                # focus.auto,
                # focus.near,
            ])


class Exposure(SettingsContainer):
    def __init__(self):
        # noinspection PyArgumentList
        SettingsContainer.__init__(self, [
            Setting(camera.Setting.AE_MODE),
            ISOSetting(),
            SSSetting(),
        ])

        self.ae, self.iso, self.ss = self.settings_

    def auto(self):
        return self.ae.set(camera.AEMode.ON)

    def increase(self):
        return self.__change([
            self.iso.increase,
            self.ss.decrease,
        ])

    def decrease(self):
        return self.__change([
            self.iso.decrease,
            self.ss.increase,
        ])

    def __change(self, changes):
        self.manual()

        change = False
        for _ in range(3):
            change = do_random_task(changes)
            if change:
                break

        if not change:
            log.warning("Failed to alter exposure...")
        return change

    def manual(self):
        change = self.ae.set(camera.AEMode.OFF)
        if change:
            self.iso.sync()
            self.ss.sync()
        return change

    def backup(self):
        self.iso.backup()
        self.ss.backup()

    def restore(self):
        change = False
        change |= self.manual()
        change |= self.iso.restore()
        change |= self.ss.restore()
        return change

    def reset(self):
        self.auto()


class ISOSetting(Setting):

    def __init__(self, max_val=800):
        super().__init__(camera.Setting.ISO)
        self.min_val = int(self.info.values[0])
        self.max_val = min(
            int(self.info.values[2]),
            max_val,
        )

    @property
    def value(self):
        return int(super().value)

    def increase(self):
        new_iso = self.value * 2
        new_iso = min(new_iso, self.max_val)
        return self.set(new_iso)

    def decrease(self):
        new_iso = int(self.value / 2)
        new_iso = max(new_iso, self.min_val)
        return self.set(new_iso)


class SSSetting(Setting):

    def __init__(self, max_time=s2ns(1 / 100)):
        """
        :param max_time: max shutter speed time in ns
        """
        super().__init__(camera.Setting.SHUTTER_SPEED)
        self.min_time = int(self.info.values[0])
        self.max_time = min(
            10 ** (int(math.log10(int(self.info.values[-1])))),
            int(max_time),
        )

    @property
    def value(self):
        """
        in nanoseconds
        """
        return int(super().value)

    def increase(self):
        new_ss = 10 ** (int(math.log10(self.value)) - 1)
        new_ss = max(new_ss, self.min_time)
        return self.set(new_ss)

    def decrease(self):
        new_ss = 10 ** (int(math.log10(self.value)) + 1)
        new_ss = min(new_ss, self.max_time)
        return self.set(new_ss)


class Focus(SettingsContainer):
    class Mode(Enum):
        AUTO = auto()
        NEAR = auto()

    def __init__(self) -> None:
        super().__init__([
            Setting(camera.Setting.FOCUS_MODE),
            Setting(camera.Setting.FOCUS_DISTANCE),
        ])
        self.mode, self.distance = self.settings_
        self._backup = None
        self._value = None

    def auto(self):
        self._value = Focus.Mode.AUTO
        return self.mode.set(camera.FocusMode.AUTO)

    def near(self):
        change = False
        change |= self.mode.set(camera.FocusMode.MANUAL)
        change |= self.distance.set(self.distance.info.values[-1])
        self._value = Focus.Mode.NEAR
        return change

    def backup(self):
        self._backup = self._value

    def restore(self):
        if self._backup == Focus.Mode.AUTO:
            return self.auto()
        elif self._backup == Focus.Mode.NEAR:
            return self.near()
        else:
            return False

    def reset(self):
        self.auto()


exposure = Exposure()
focus = Focus()


@dataclass
class SettingBackup:
    setting: Setting

    def __enter__(self):
        self.setting.backup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.setting.restore()


def snapshot():
    log.info("Snapshotting...")
    with SettingBackup(exposure), SettingBackup(focus):
        exposure.auto()
        focus.auto()
        snap = image()
    log.info("Snapshot complete!")
    return snap
