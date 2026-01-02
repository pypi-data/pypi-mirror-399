import time
import requests
from typing import Optional, Callable, TypeVar, Any
from enum import IntEnum
from .exceptions import (
    Ys7SdkAccessTokenError,
    Ys7SdkPTZControlError,
    Ys7SdkDeviceCaptureError,
    Ys7SdkDeviceError,
    Ys7SdkLiveStreamError,
    get_err_msg,
)
from .models import (
    AccessToken,
    PresetIndex,
    CaptureResult,
    DeviceCapacity,
    LiveAddress,
    StreamAddress,
    DeviceInfo,
    DeviceConnectionInfo,
    DeviceStatus,
    DeviceListResult,
)


class PTZDirection(IntEnum):
    """云台控制方向枚举"""

    UP = 0  # 上
    DOWN = 1  # 下
    LEFT = 2  # 左
    RIGHT = 3  # 右
    UP_LEFT = 4  # 左上
    DOWN_LEFT = 5  # 左下
    UP_RIGHT = 6  # 右上
    DOWN_RIGHT = 7  # 右下
    ZOOM_IN = 8  # 物理放大
    ZOOM_OUT = 9  # 物理缩小
    FOCUS_NEAR = 10  # 调整近焦距
    FOCUS_FAR = 11  # 调整远焦距
    AUTO = 16  # 自动控制


class PTZSpeed(IntEnum):
    """云台速度枚举"""

    SLOW = 0  # 慢（海康设备不可为0）
    MEDIUM = 1  # 适中
    FAST = 2  # 快


class MirrorCommand(IntEnum):
    """镜像翻转方向枚举"""

    UP_DOWN = 0  # 上下翻转
    LEFT_RIGHT = 1  # 左右翻转
    CENTER = 2  # 中心翻转


class LsyiotYs7API:
    BASE_URL = "https://open.ys7.com/api/lapp"

    # Token 提前刷新时间（秒），在过期前 5 分钟刷新
    TOKEN_REFRESH_MARGIN = 300

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = None
        self.expire_time = None

    def _ensure_access_token(self) -> str:
        """
        确保 access_token 有效，如果无效或即将过期则自动刷新

        Returns:
            str: 有效的 access_token

        Raises:
            Ys7SdkAccessTokenError: 获取token失败时抛出异常
        """
        current_time = int(time.time() * 1000)  # 毫秒时间戳

        # 检查 token 是否存在且未过期（提前 5 分钟刷新）
        if (
            self.access_token
            and self.expire_time
            and current_time < self.expire_time - self.TOKEN_REFRESH_MARGIN * 1000
        ):
            return self.access_token

        # token 不存在或即将过期，重新获取
        self.get_access_token()
        return self.access_token

    def _request_with_token_retry(
        self,
        request_func: Callable[[], dict],
        token_param_updater: Callable[[str], None],
    ) -> dict:
        """
        带 token 自动刷新重试的请求包装器

        如果请求返回 10002 错误码（token过期），自动刷新 token 并重试一次

        Args:
            request_func: 执行请求的函数，返回响应的 JSON dict
            token_param_updater: 更新请求中 token 参数的函数

        Returns:
            dict: API 响应结果
        """
        result = request_func()

        # 检查是否是 token 过期错误 (10002)
        if result.get("code") == "10002":
            # 刷新 token
            self.get_access_token()
            # 更新请求参数中的 token
            token_param_updater(self.access_token)
            # 重试请求
            result = request_func()

        return result

    def get_access_token(self) -> AccessToken:
        """
        获取accessToken

        该接口用于管理员账号根据appKey和secret获取accessToken。
        注意：获取到的accessToken有效期是7天，请在即将过期或者接口报错10002时重新获取。
        每个token具备独立的7天生命周期，请勿频繁调用避免占用过多接口调用次数。
        最佳实践是在本地进行缓存。

        Returns:
            AccessToken: 包含accessToken和expireTime的实体对象

        Raises:
            Ys7SdkAccessTokenError: 获取token失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> result = api.get_access_token()
            >>> print(result.access_token)
            >>> print(result.expire_time)
        """
        url = f"{self.BASE_URL}/token/get"

        data = {"appKey": self.app_key, "appSecret": self.app_secret}

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()

            if result.get("code") == "200":
                token_data = result.get("data", {})
                self.access_token = token_data.get("accessToken")
                self.expire_time = token_data.get("expireTime")
                return AccessToken.from_dict(token_data)
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkAccessTokenError(f"获取accessToken失败: [{error_code}] {error_msg}")

        except Exception as e:
            raise Ys7SdkAccessTokenError(f"网络请求失败: {str(e)}")

    def ptz_start(
        self,
        device_serial: str,
        channel_no: int,
        direction: int,
        speed: int,
        access_token: Optional[str] = None,
    ) -> None:
        """
        开始云台控制

        对设备进行开始云台控制，开始云台控制之后必须先调用停止云台控制接口才能进行其他操作，
        包括其他方向的云台转动。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            channel_no (int): 通道号
            direction (int): 操作命令
                - 0: 上
                - 1: 下
                - 2: 左
                - 3: 右
                - 4: 左上
                - 5: 左下
                - 6: 右上
                - 7: 右下
                - 8: 物理放大
                - 9: 物理缩小
                - 10: 调整近焦距
                - 11: 调整远焦距
                - 16: 自动控制
            speed (int): 云台速度
                - 0: 慢（海康设备参数不可为0）
                - 1: 适中
                - 2: 快
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Raises:
            Ys7SdkPTZControlError: 云台控制失败时抛出异常
            ValueError: 参数校验失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> # 向左转动，速度适中
            >>> api.ptz_start("502608888", 1, PTZDirection.LEFT, PTZSpeed.MEDIUM)
        """
        # 参数校验
        if direction not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16]:
            raise ValueError(f"direction参数无效: {direction}，有效值为0-11和16")
        if speed not in [0, 1, 2]:
            raise ValueError(f"speed参数无效: {speed}，有效值为0、1、2")

        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/ptz/start"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
            "channelNo": channel_no,
            "direction": direction,
            "speed": speed,
        }

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") != "200":
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkPTZControlError(f"云台控制失败: [{error_code}] {error_msg}")

        except Ys7SdkPTZControlError:
            raise
        except Exception as e:
            raise Ys7SdkPTZControlError(f"网络请求失败: {str(e)}")

    def ptz_stop(
        self,
        device_serial: str,
        channel_no: int,
        direction: Optional[int] = None,
        access_token: Optional[str] = None,
    ) -> None:
        """
        停止云台控制

        设备停止云台控制。建议停止云台接口带方向参数。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            channel_no (int): 通道号
            direction (Optional[int]): 操作命令（可选，建议带上）
                - 0: 上
                - 1: 下
                - 2: 左
                - 3: 右
                - 4: 左上
                - 5: 左下
                - 6: 右上
                - 7: 右下
                - 8: 放大
                - 9: 缩小
                - 10: 近焦距
                - 11: 远焦距
                - 16: 自动控制
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Raises:
            Ys7SdkPTZControlError: 云台控制失败时抛出异常
            ValueError: 参数校验失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> # 停止向左转动
            >>> api.ptz_stop("502608888", 1, direction=PTZDirection.LEFT)
        """
        # 参数校验
        if direction is not None and direction not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16]:
            raise ValueError(f"direction参数无效: {direction}，有效值为0-11和16")

        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/ptz/stop"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
            "channelNo": channel_no,
        }

        # direction是可选参数，如果提供则添加到请求中
        if direction is not None:
            data["direction"] = direction

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") != "200":
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkPTZControlError(f"停止云台控制失败: [{error_code}] {error_msg}")

        except Ys7SdkPTZControlError:
            raise
        except Exception as e:
            raise Ys7SdkPTZControlError(f"网络请求失败: {str(e)}")

    def preset_add(
        self,
        device_serial: str,
        channel_no: int,
        access_token: Optional[str] = None,
    ) -> PresetIndex:
        """
        添加预置点

        支持云台控制操作的设备添加预置点，该接口需要设备支持能力集：ptz_preset=1

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            channel_no (int): 通道号
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            PresetIndex: 预置点信息实体

        Raises:
            Ys7SdkPTZControlError: 操作失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> result = api.preset_add("502608888", 1)
            >>> print(f"预置点序号: {result.index}")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/preset/add"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
            "channelNo": channel_no,
        }

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") == "200":
                return PresetIndex.from_dict(result.get("data", {}))
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkPTZControlError(f"添加预置点失败: [{error_code}] {error_msg}")

        except Ys7SdkPTZControlError:
            raise
        except Exception as e:
            raise Ys7SdkPTZControlError(f"网络请求失败: {str(e)}")

    def preset_move(
        self,
        device_serial: str,
        channel_no: int,
        index: int,
        access_token: Optional[str] = None,
    ) -> None:
        """
        调用预置点

        对预置点进行调用控制，使设备移动到指定预置点位置。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            channel_no (int): 通道号
            index (int): 预置点序号，C6设备预置点是1-12
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Raises:
            Ys7SdkPTZControlError: 操作失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> # 调用预置点3
            >>> api.preset_move("502608888", 1, index=3)
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/preset/move"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
            "channelNo": channel_no,
            "index": index,
        }

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") != "200":
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkPTZControlError(f"调用预置点失败: [{error_code}] {error_msg}")

        except Ys7SdkPTZControlError:
            raise
        except Exception as e:
            raise Ys7SdkPTZControlError(f"网络请求失败: {str(e)}")

    def preset_clear(
        self,
        device_serial: str,
        channel_no: int,
        index: int,
        access_token: Optional[str] = None,
    ) -> None:
        """
        清除预置点

        清除指定的预置点。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            channel_no (int): 通道号
            index (int): 预置点序号，C6设备预置点是1-12
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Raises:
            Ys7SdkPTZControlError: 操作失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> # 清除预置点3
            >>> api.preset_clear("502608888", 1, index=3)
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/preset/clear"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
            "channelNo": channel_no,
            "index": index,
        }

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") != "200":
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkPTZControlError(f"清除预置点失败: [{error_code}] {error_msg}")

        except Ys7SdkPTZControlError:
            raise
        except Exception as e:
            raise Ys7SdkPTZControlError(f"网络请求失败: {str(e)}")

    def ptz_mirror(
        self,
        device_serial: str,
        channel_no: int,
        command: int,
        access_token: Optional[str] = None,
    ) -> None:
        """
        镜像翻转

        对设备进行镜像翻转操作（需要设备支持）。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            channel_no (int): 通道号
            command (int): 镜像方向
                - 0: 上下翻转
                - 1: 左右翻转
                - 2: 中心翻转
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Raises:
            Ys7SdkPTZControlError: 操作失败时抛出异常
            ValueError: 参数校验失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> # 中心翻转
            >>> api.ptz_mirror("502608888", 1, MirrorCommand.CENTER)
        """
        # 参数校验
        if command not in [0, 1, 2]:
            raise ValueError(f"command参数无效: {command}，有效值为0（上下）、1（左右）、2（中心）")

        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/ptz/mirror"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
            "channelNo": channel_no,
            "command": command,
        }

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") != "200":
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkPTZControlError(f"镜像翻转失败: [{error_code}] {error_msg}")

        except Ys7SdkPTZControlError:
            raise
        except Exception as e:
            raise Ys7SdkPTZControlError(f"网络请求失败: {str(e)}")

    def capture(
        self,
        device_serial: str,
        channel_no: int,
        quality: Optional[int] = None,
        access_token: Optional[str] = None,
    ) -> CaptureResult:
        """
        设备抓拍图片

        抓拍设备当前画面，该接口仅适用于IPC或者关联IPC的DVR设备。
        该接口并非预览时的截图功能。
        该接口需要设备支持能力集：support_capture=1

        注意：设备抓图能力有限，请勿频繁调用，建议每个摄像头调用的间隔4s以上。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            channel_no (int): 通道号，IPC设备填写1
            quality (Optional[int]): 视频清晰度（此参数不生效）
                - 0: 流畅
                - 1: 高清(720P)
                - 2: 4CIF
                - 3: 1080P
                - 4: 400w
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            CaptureResult: 抓拍结果实体

        Raises:
            Ys7SdkDeviceCaptureError: 抓拍失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> result = api.capture("502608888", 1)
            >>> print(f"图片地址: {result.pic_url}")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/capture"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
            "channelNo": channel_no,
        }

        # quality是可选参数
        if quality is not None:
            data["quality"] = quality

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") == "200":
                return CaptureResult.from_dict(result.get("data", {}))
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkDeviceCaptureError(f"设备抓拍失败: [{error_code}] {error_msg}")

        except Ys7SdkDeviceCaptureError:
            raise
        except Exception as e:
            raise Ys7SdkDeviceCaptureError(f"网络请求失败: {str(e)}")

    def get_device_capacity(
        self,
        device_serial: str,
        access_token: Optional[str] = None,
    ) -> DeviceCapacity:
        """
        获取设备能力集

        根据设备序列号查询设备能力集，了解设备支持的功能。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            DeviceCapacity: 设备能力集实体

        Raises:
            Ys7SdkDeviceError: 操作失败时抛出异常

        Note:
            能力集说明中有的，而返回字段中没有的那些能力默认不支持

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> result = api.get_device_capacity("502608888")
            >>> if result.support_capture == '1':
            ...     print("设备支持抓图")
            >>> if result.ptz_preset == '1':
            ...     print("设备支持预置点")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/capacity"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
        }

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") == "200":
                return DeviceCapacity.from_dict(result.get("data", {}))
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkDeviceError(f"获取设备能力集失败: [{error_code}] {error_msg}")

        except Ys7SdkDeviceError:
            raise
        except Exception as e:
            raise Ys7SdkDeviceError(f"网络请求失败: {str(e)}")

    def get_live_address(
        self,
        device_serial: str,
        channel_no: Optional[int] = None,
        protocol: Optional[int] = None,
        code: Optional[str] = None,
        expire_time: Optional[int] = None,
        type: Optional[int] = None,
        quality: Optional[int] = None,
        start_time: Optional[str] = None,
        stop_time: Optional[str] = None,
        support_h265: Optional[int] = None,
        mute: Optional[int] = None,
        playback_speed: Optional[str] = None,
        gbchannel: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> LiveAddress:
        """
        获取播放地址

        通过设备序列号、通道号获取单台设备的播放地址信息，无法获取永久有效期播放地址。

        Args:
            device_serial (str): 设备序列号，限制最多50个字符
            channel_no (Optional[int]): 通道号，默认为1
            protocol (Optional[int]): 流播放协议
                - 1: ezopen（默认）
                - 2: hls
                - 3: rtmp
                - 4: flv
            code (Optional[str]): ezopen协议地址的设备的视频加密密码
            expire_time (Optional[int]): 过期时长，单位秒；针对hls/rtmp/flv设置有效期，30秒-720天
            type (Optional[int]): 地址类型
                - 1: 预览（默认）
                - 2: 本地录像回放
                - 3: 云存储录像回放
            quality (Optional[int]): 预览视频清晰度（仅针对预览生效）
                - 1: 高清（主码流）
                - 2: 流畅（子码流）
            start_time (Optional[str]): 本地录像/云存储录像回放开始时间，示例：2019-12-01 00:00:00
            stop_time (Optional[str]): 本地录像/云存储录像回放结束时间，示例：2019-12-01 23:59:59
            support_h265 (Optional[int]): 是否要求播放视频为H265编码格式，1-需要，0-不要求
            mute (Optional[int]): 开启静音，1-静音，0-不静音（默认），仅针对RTMP、HTTP-FLV有效
            playback_speed (Optional[str]): 回放倍速，支持-1、0.5、1、2、4、8、16，仅支持protocol=4且type=2或3
            gbchannel (Optional[str]): 国标设备的通道编号，视频通道编号ID
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            LiveAddress: 播放地址实体

        Raises:
            Ys7SdkLiveStreamError: 操作失败时抛出异常

        Note:
            - 云存储开始结束时间必须在同一天
            - 回放仅支持rtmp、ezopen、flv协议
            - 录像回放不支持切换清晰度

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> # 获取HLS直播地址
            >>> result = api.get_live_address("C78957921", channel_no=1, protocol=2)
            >>> print(f"播放地址: {result.url}")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/v2/live/address/get"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
        }

        # 添加可选参数
        if channel_no is not None:
            data["channelNo"] = channel_no
        if protocol is not None:
            data["protocol"] = protocol
        if code is not None:
            data["code"] = code
        if expire_time is not None:
            data["expireTime"] = expire_time
        if type is not None:
            data["type"] = type
        if quality is not None:
            data["quality"] = quality
        if start_time is not None:
            data["startTime"] = start_time
        if stop_time is not None:
            data["stopTime"] = stop_time
        if support_h265 is not None:
            data["supportH265"] = support_h265
        if mute is not None:
            data["mute"] = mute
        if playback_speed is not None:
            data["playbackSpeed"] = playback_speed
        if gbchannel is not None:
            data["gbchannel"] = gbchannel

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") == "200":
                return LiveAddress.from_dict(result.get("data", {}))
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkLiveStreamError(f"获取播放地址失败: [{error_code}] {error_msg}")

        except Ys7SdkLiveStreamError:
            raise
        except Exception as e:
            raise Ys7SdkLiveStreamError(f"网络请求失败: {str(e)}")

    def get_stream_address(
        self,
        stream_id: int,
        protocol: int,
        quality: Optional[int] = None,
        support_h265: Optional[int] = None,
        mute: Optional[int] = None,
        type: Optional[int] = None,
        expire_time: Optional[int] = None,
        access_token: Optional[str] = None,
    ) -> StreamAddress:
        """
        获取直播流播放地址（GET方式）

        通过直播流ID获取播放地址。

        Args:
            stream_id (int): 直播流ID
            protocol (int): 流播放协议
                - 1: hls
                - 2: rtmp
                - 3: flv
            quality (Optional[int]): 视频清晰度（rtmp直推流不生效）
                - 1: 高清（主码流，默认）
                - 2: 流畅（子码流）
            support_h265 (Optional[int]): 是否支持H265编码（rtmp直推流不生效）
                - 0: 不支持（默认）
                - 1: 支持
            mute (Optional[int]): 是否静音（rtmp直推流不生效）
                - 0: 不静音（默认）
                - 1: 静音
            type (Optional[int]): 类型
                - 1: 播放地址（默认）
                - 2: 推流地址（rtmp接入直播流生效）
            expire_time (Optional[int]): 过期时间，单位秒，默认730天，最大730天（rtmp接入直播流生效）
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            StreamAddress: 直播流播放地址实体

        Raises:
            Ys7SdkLiveStreamError: 操作失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> # 获取HLS播放地址
            >>> result = api.get_stream_address(stream_id=787305182210818048, protocol=1)
            >>> print(f"播放地址: {result.address}")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = "https://open.ys7.com/api/service/media/streammanage/stream/address"

        headers = {
            "accessToken": token,
        }

        params = {
            "streamId": stream_id,
            "protocol": protocol,
        }

        # 添加可选参数
        if quality is not None:
            params["quality"] = quality
        if support_h265 is not None:
            params["supportH265"] = support_h265
        if mute is not None:
            params["mute"] = mute
        if type is not None:
            params["type"] = type
        if expire_time is not None:
            params["expireTime"] = expire_time

        try:

            def do_request():
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()

            def update_token(new_token):
                headers["accessToken"] = new_token

            result = self._request_with_token_retry(do_request, update_token)

            meta = result.get("meta", {})
            if meta.get("code") == 200:
                return StreamAddress.from_dict(result.get("data", {}))
            else:
                error_code = str(meta.get("code", "未知"))
                error_msg = meta.get("message", get_err_msg(error_code))
                raise Ys7SdkLiveStreamError(f"获取直播流播放地址失败: [{error_code}] {error_msg}")

        except Ys7SdkLiveStreamError:
            raise
        except Exception as e:
            raise Ys7SdkLiveStreamError(f"网络请求失败: {str(e)}")

    def get_device_info(
        self,
        device_serial: str,
        access_token: Optional[str] = None,
    ) -> DeviceInfo:
        """
        获取单个设备信息

        查询用户下指定设备的基本信息。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            DeviceInfo: 设备信息实体

        Raises:
            Ys7SdkDeviceError: 操作失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> result = api.get_device_info("427734168")
            >>> print(f"设备名称: {result.device_name}")
            >>> print(f"在线状态: {'在线' if result.status == 1 else '离线'}")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/info"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
        }

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") == "200":
                return DeviceInfo.from_dict(result.get("data", {}))
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkDeviceError(f"获取设备信息失败: [{error_code}] {error_msg}")

        except Ys7SdkDeviceError:
            raise
        except Exception as e:
            raise Ys7SdkDeviceError(f"网络请求失败: {str(e)}")

    def get_device_connection_info(
        self,
        device_serial: str,
        access_token: Optional[str] = None,
    ) -> DeviceConnectionInfo:
        """
        获取单个设备连接信息

        查询用户下指定设备的网络连接信息。

        注意：不支持子账号和托管权限。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            DeviceConnectionInfo: 设备连接信息实体

        Raises:
            Ys7SdkDeviceError: 操作失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> result = api.get_device_connection_info("FX3049123")
            >>> print(f"局域网IP: {result.local_ip}")
            >>> print(f"外网IP: {result.nat_ip}")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/connection/info"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
        }

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") == "200":
                return DeviceConnectionInfo.from_dict(result.get("data", {}))
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkDeviceError(f"获取设备连接信息失败: [{error_code}] {error_msg}")

        except Ys7SdkDeviceError:
            raise
        except Exception as e:
            raise Ys7SdkDeviceError(f"网络请求失败: {str(e)}")

    def get_device_status(
        self,
        device_serial: str,
        channel: Optional[int] = None,
        access_token: Optional[str] = None,
    ) -> DeviceStatus:
        """
        获取设备状态信息

        根据序列号通道号获取设备状态信息。

        Args:
            device_serial (str): 设备序列号，存在英文字母的设备序列号，字母需为大写
            channel (Optional[int]): 通道号，默认为1
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            DeviceStatus: 设备状态信息实体

        Raises:
            Ys7SdkDeviceError: 操作失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> result = api.get_device_status("427734168", channel=1)
            >>> print(f"云存储状态: {result.cloud_status}")
            >>> print(f"硬盘数量: {result.disk_num}")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/status/get"

        data = {
            "accessToken": token,
            "deviceSerial": device_serial,
        }

        # channel是可选参数
        if channel is not None:
            data["channel"] = channel

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") == "200":
                return DeviceStatus.from_dict(result.get("data", {}))
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkDeviceError(f"获取设备状态信息失败: [{error_code}] {error_msg}")

        except Ys7SdkDeviceError:
            raise
        except Exception as e:
            raise Ys7SdkDeviceError(f"网络请求失败: {str(e)}")

    def get_device_list(
        self,
        page_start: Optional[int] = None,
        page_size: Optional[int] = None,
        access_token: Optional[str] = None,
    ) -> DeviceListResult:
        """
        分页查询设备列表

        分页查询设备列表。起始页从0开始，不超过400页；每页默认查询数默认为10，不超过50。
        支持子账号查询。可分页查询出授权给子账号的设备，最小授权权限"Permission":"Get" "Resource":"dev:序列号"。
        不支持查询托管设备。

        Args:
            page_start (Optional[int]): 分页页码，起始页从0开始，不超过400页
            page_size (Optional[int]): 分页大小，默认为10，不超过50
            access_token (Optional[str]): accessToken，如果为None则使用实例中缓存的token

        Returns:
            DeviceListResult: 设备列表结果，包含设备列表和分页信息

        Raises:
            Ys7SdkDeviceError: 操作失败时抛出异常

        Example:
            >>> api = LsyiotYs7API(app_key="your_app_key", app_secret="your_app_secret")
            >>> api.get_access_token()
            >>> # 获取第一页，每页10条
            >>> result = api.get_device_list(page_start=0, page_size=10)
            >>> print(f"总数: {result.page.total}")
            >>> for device in result.devices:
            ...     print(f"设备: {device.device_name}, 状态: {'在线' if device.status == 1 else '离线'}")
        """
        # 获取accessToken（自动刷新即将过期的token）
        token = access_token or self._ensure_access_token()

        url = f"{self.BASE_URL}/device/list"

        data = {
            "accessToken": token,
        }

        # 添加可选参数
        if page_start is not None:
            data["pageStart"] = page_start
        if page_size is not None:
            data["pageSize"] = page_size

        try:

            def do_request():
                response = requests.post(url, data=data)
                response.raise_for_status()
                return response.json()

            result = self._request_with_token_retry(
                do_request, lambda new_token: data.update({"accessToken": new_token})
            )

            if result.get("code") == "200":
                return DeviceListResult.from_dict(result)
            else:
                error_code = result.get("code", "未知")
                error_msg = get_err_msg(error_code)
                raise Ys7SdkDeviceError(f"获取设备列表失败: [{error_code}] {error_msg}")

        except Ys7SdkDeviceError:
            raise
        except Exception as e:
            raise Ys7SdkDeviceError(f"网络请求失败: {str(e)}")
