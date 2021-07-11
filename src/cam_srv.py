import logging as log
import math
from dataclasses import dataclass
from typing import List

import numpy as np
import rx.core as rx
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


images = reactives.Subject()
images.last = np.ndarray(())


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

    def reset(self):
        self.set(self.init_val)
        self.reset_history()

    def reset_history(self):
        self.last_val = None

    def __str__(self):
        return f"{self.setting}: {self.value}; Info: {self.info}"


@dataclass
class SettingsContainer:
    settings_: List[Setting]

    def __enter__(self):
        return self

    def reset(self):
        for setting in self.settings_:
            setting.reset()

    def __str__(self):
        return "\n".join(map(str, self.settings_))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset()


class ParamOptimizer(SettingsContainer, rx.Observer):

    def __init__(self):
        # noinspection PyArgumentList
        SettingsContainer.__init__(self, [
            Setting(camera.Setting.AE_MODE),
            ISOSetting(),
            SSSetting(),
            Focus(),
        ])

        self.ae, self.iso, self.ss, self.focus = self.settings_
        self.ae.set(camera.AEMode.OFF)
        self.focus.near()

        log.info(self.settings_)

    def on_next(self, not_found_case) -> None:

        change = False
        if not_found_case == robot_finder.NotFoundCase.FEW_POINTS:
            change = self.increase_exposure()
        elif not_found_case == robot_finder.NotFoundCase.MANY_POINTS:
            change = self.decrease_exposure()

        if not change:
            do_random_task([
                self.iso.increase,
                self.iso.decrease,
                self.ss.increase,
                self.ss.decrease,
            ])

    def increase_exposure(self):
        if do_random_task([
            self.iso.increase,
            self.ss.decrease,
        ]):
            return True
        else:
            log.warning("Cannot increase exposure...")
            return False

    def decrease_exposure(self):
        if do_random_task([
            self.iso.decrease,
            self.ss.increase,
        ]):
            return True
        else:
            log.warning("Cannot decrease exposure...")
            return False

    def reset(self):
        self.ae.reset()
        self.focus.reset()


class SuggestingParamOptimizer(ParamOptimizer):
    def increase_exposure(self):
        log.info("Suggest exposure increase...")

    def decrease_exposure(self):
        log.info("Suggest exposure decrease...")


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
            max_time,
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

    def __init__(self) -> None:
        super().__init__([
            Setting(camera.Setting.FOCUS_MODE),
            Setting(camera.Setting.FOCUS_DISTANCE),
        ])
        self.mode, self.distance = self.settings_

    def near(self):
        self.mode.set(camera.FocusMode.MANUAL)
        self.distance.set(self.distance.info.values[-1])

    def reset(self):
        self.mode.reset()
