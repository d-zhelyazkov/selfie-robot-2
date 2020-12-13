import logging as log
import math

import numpy as np
import rx.core as rx
import urllib3
from cv2 import cv2 as cv
from urllib3 import HTTPResponse

import camera
import reactives
from tools import do_random_task

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


class ParamOptimizer(rx.Observer):

    def __init__(self):
        super().__init__()
        camera_api.settings_aemode_put(camera.AEModeValue(camera.AEMode.OFF))

        self.iso = ISOSetting()
        self.ss = SSSetting()

    def on_next(self, processing_result) -> None:
        (_, points) = processing_result
        (blue_points, red_points) = points
        blue_cnt = len(blue_points)
        red_cnt = len(red_points)
        if blue_cnt == 2 and red_cnt == 1:
            return

        if blue_cnt < 2 or red_cnt < 1:
            self.increase_exposure()
        else:
            self.decrease_exposure()

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


class ISOSetting(Setting):

    def __init__(self):
        super().__init__(camera.Setting.ISO)
        self.min_val = int(self.info.values[0])
        self.max_val = int(int(self.info.values[-1]) / 2)

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

    def __init__(self):
        super().__init__(camera.Setting.SHUTTER_SPEED)
        self.min_val = int(self.info.values[0])
        self.max_val = 10 ** (int(math.log10(int(self.info.values[-1]))) - 1)

    @property
    def value(self):
        return int(super().value)

    def increase(self):
        new_ss = 10 ** (int(math.log10(self.value)) - 1)
        new_ss = max(new_ss, self.min_val)
        return self.set(new_ss)

    def decrease(self):
        new_ss = 10 ** (int(math.log10(self.value)) + 1)
        new_ss = min(new_ss, self.max_val)
        return self.set(new_ss)
