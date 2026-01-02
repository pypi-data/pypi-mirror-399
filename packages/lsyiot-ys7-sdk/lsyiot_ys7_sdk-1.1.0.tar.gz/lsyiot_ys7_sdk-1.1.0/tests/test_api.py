"""
LsyiotYs7API 测试用例
使用 pytest 和 mock 模拟 HTTP 请求
"""

import pytest
from unittest.mock import patch, Mock
from lsyiot_ys7_sdk import (
    LsyiotYs7API,
    PTZDirection,
    PTZSpeed,
    MirrorCommand,
    Ys7SdkError,
    Ys7SdkAccessTokenError,
    Ys7SdkPTZControlError,
    Ys7SdkDeviceCaptureError,
    Ys7SdkDeviceError,
    Ys7SdkLiveStreamError,
    AccessToken,
    PresetIndex,
    CaptureResult,
    DeviceCapacity,
    LiveAddress,
    StreamAddress,
    DeviceInfo,
    DeviceConnectionInfo,
    DeviceStatus,
    Device,
    PageInfo,
    DeviceListResult,
)


@pytest.fixture
def api():
    """创建 API 实例"""
    return LsyiotYs7API(app_key="test_app_key", app_secret="test_app_secret")


@pytest.fixture
def api_with_token():
    """创建带有 token 的 API 实例（设置足够长的过期时间）"""
    import time

    api = LsyiotYs7API(app_key="test_app_key", app_secret="test_app_secret")
    api.access_token = "test_access_token"
    # 设置未来的过期时间（当前时间 + 7天），单位毫秒
    api.expire_time = int(time.time() * 1000) + 7 * 24 * 60 * 60 * 1000
    return api


class TestGetAccessToken:
    """测试 get_access_token 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_access_token_success(self, mock_post, api):
        """测试成功获取 accessToken"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {
                "accessToken": "at.test_token_12345",
                "expireTime": 1702800000000,
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api.get_access_token()

        assert isinstance(result, AccessToken)
        assert result.access_token == "at.test_token_12345"
        assert result.expire_time == 1702800000000
        assert api.access_token == "at.test_token_12345"
        assert api.expire_time == 1702800000000

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_access_token_failure(self, mock_post, api):
        """测试获取 accessToken 失败"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "10001",
            "msg": "参数错误",
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Ys7SdkAccessTokenError):
            api.get_access_token()

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_access_token_network_error(self, mock_post, api):
        """测试网络请求失败"""
        import requests

        mock_post.side_effect = requests.RequestException("网络错误")

        with pytest.raises(Ys7SdkAccessTokenError) as exc_info:
            api.get_access_token()
        assert "网络请求失败" in str(exc_info.value)


class TestPTZStart:
    """测试 ptz_start 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_ptz_start_success(self, mock_post, api_with_token):
        """测试云台控制开始成功"""
        mock_response = Mock()
        mock_response.json.return_value = {"code": "200", "msg": "操作成功"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.ptz_start(
            device_serial="TEST123456",
            channel_no=1,
            direction=PTZDirection.LEFT,
            speed=PTZSpeed.MEDIUM,
        )

        assert result is None
        # 验证 POST 请求被调用（可能包含请求参数验证）
        assert mock_post.called

    def test_ptz_start_invalid_direction(self, api_with_token):
        """测试无效的方向参数"""
        with pytest.raises(ValueError) as exc_info:
            api_with_token.ptz_start(
                device_serial="TEST123456",
                channel_no=1,
                direction=99,
                speed=PTZSpeed.MEDIUM,
            )
        assert "direction参数无效" in str(exc_info.value)

    def test_ptz_start_invalid_speed(self, api_with_token):
        """测试无效的速度参数"""
        with pytest.raises(ValueError) as exc_info:
            api_with_token.ptz_start(
                device_serial="TEST123456",
                channel_no=1,
                direction=PTZDirection.LEFT,
                speed=99,
            )
        assert "speed参数无效" in str(exc_info.value)

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_ptz_start_no_token(self, mock_post, api):
        """测试没有 token 时自动获取失败的情况"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "10017",
            "msg": "appKey不存在",
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Ys7SdkAccessTokenError) as exc_info:
            api.ptz_start(
                device_serial="TEST123456",
                channel_no=1,
                direction=PTZDirection.LEFT,
                speed=PTZSpeed.MEDIUM,
            )
        assert "获取accessToken失败" in str(exc_info.value)

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_ptz_start_api_error(self, mock_post, api_with_token):
        """测试 API 返回错误"""
        mock_response = Mock()
        mock_response.json.return_value = {"code": "60000", "msg": "设备不支持云台控制"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Ys7SdkPTZControlError):
            api_with_token.ptz_start(
                device_serial="TEST123456",
                channel_no=1,
                direction=PTZDirection.LEFT,
                speed=PTZSpeed.MEDIUM,
            )


class TestPTZStop:
    """测试 ptz_stop 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_ptz_stop_success(self, mock_post, api_with_token):
        """测试云台控制停止成功"""
        mock_response = Mock()
        mock_response.json.return_value = {"code": "200", "msg": "操作成功"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.ptz_stop(
            device_serial="TEST123456",
            channel_no=1,
            direction=PTZDirection.LEFT,
        )

        assert result is None

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_ptz_stop_without_direction(self, mock_post, api_with_token):
        """测试不带方向参数停止"""
        mock_response = Mock()
        mock_response.json.return_value = {"code": "200", "msg": "操作成功"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.ptz_stop(
            device_serial="TEST123456",
            channel_no=1,
        )

        assert result is None

    def test_ptz_stop_invalid_direction(self, api_with_token):
        """测试无效的方向参数"""
        with pytest.raises(ValueError):
            api_with_token.ptz_stop(
                device_serial="TEST123456",
                channel_no=1,
                direction=99,
            )


class TestPresetAdd:
    """测试 preset_add 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_preset_add_success(self, mock_post, api_with_token):
        """测试添加预置点成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {"index": 3},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.preset_add(
            device_serial="TEST123456",
            channel_no=1,
        )

        assert isinstance(result, PresetIndex)
        assert result.index == 3

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_preset_add_no_token(self, mock_post, api):
        """测试没有 token 时自动获取失败的情况"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "10017",
            "msg": "appKey不存在",
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Ys7SdkAccessTokenError) as exc_info:
            api.preset_add(device_serial="TEST123456", channel_no=1)
        assert "获取accessToken失败" in str(exc_info.value)


class TestPresetMove:
    """测试 preset_move 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_preset_move_success(self, mock_post, api_with_token):
        """测试调用预置点成功"""
        mock_response = Mock()
        mock_response.json.return_value = {"code": "200", "msg": "操作成功"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.preset_move(
            device_serial="TEST123456",
            channel_no=1,
            index=3,
        )

        assert result is None


class TestPresetClear:
    """测试 preset_clear 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_preset_clear_success(self, mock_post, api_with_token):
        """测试清除预置点成功"""
        mock_response = Mock()
        mock_response.json.return_value = {"code": "200", "msg": "操作成功"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.preset_clear(
            device_serial="TEST123456",
            channel_no=1,
            index=3,
        )

        assert result is None


class TestPTZMirror:
    """测试 ptz_mirror 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_ptz_mirror_success(self, mock_post, api_with_token):
        """测试镜像翻转成功"""
        mock_response = Mock()
        mock_response.json.return_value = {"code": "200", "msg": "操作成功"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.ptz_mirror(
            device_serial="TEST123456",
            channel_no=1,
            command=MirrorCommand.CENTER,
        )

        assert result is None

    def test_ptz_mirror_invalid_command(self, api_with_token):
        """测试无效的命令参数"""
        with pytest.raises(ValueError) as exc_info:
            api_with_token.ptz_mirror(
                device_serial="TEST123456",
                channel_no=1,
                command=99,
            )
        assert "command参数无效" in str(exc_info.value)


class TestCapture:
    """测试 capture 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_capture_success(self, mock_post, api_with_token):
        """测试抓拍成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {"picUrl": "https://example.com/image.jpg"},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.capture(
            device_serial="TEST123456",
            channel_no=1,
        )

        assert isinstance(result, CaptureResult)
        assert result.pic_url == "https://example.com/image.jpg"

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_capture_no_token(self, mock_post, api):
        """测试没有 token 时自动获取失败的情况"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "10017",
            "msg": "appKey不存在",
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Ys7SdkAccessTokenError) as exc_info:
            api.capture(device_serial="TEST123456", channel_no=1)
        assert "获取accessToken失败" in str(exc_info.value)

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_capture_with_quality(self, mock_post, api_with_token):
        """测试带清晰度参数抓拍"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {"picUrl": "https://example.com/image_hd.jpg"},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.capture(
            device_serial="TEST123456",
            channel_no=1,
            quality=3,
        )

        assert result.pic_url == "https://example.com/image_hd.jpg"


class TestGetDeviceCapacity:
    """测试 get_device_capacity 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_capacity_success(self, mock_post, api_with_token):
        """测试获取设备能力集成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {
                "support_capture": "1",
                "support_talk": "1",
                "support_ptz": "1",
                "ptz_preset": "1",
                "support_mirror": "0",
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_device_capacity(device_serial="TEST123456")

        assert isinstance(result, DeviceCapacity)
        assert result.support_capture == "1"
        assert result.support_talk == "1"
        assert result.ptz_preset == "1"


class TestGetLiveAddress:
    """测试 get_live_address 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_live_address_success(self, mock_post, api_with_token):
        """测试获取播放地址成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {
                "url": "https://hls.example.com/live/test.m3u8",
                "expireTime": "2024-12-31 23:59:59",
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_live_address(
            device_serial="TEST123456",
            channel_no=1,
            protocol=2,
        )

        assert isinstance(result, LiveAddress)
        assert "hls.example.com" in result.url

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_live_address_with_all_params(self, mock_post, api_with_token):
        """测试带全部参数获取播放地址"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {
                "url": "ezopen://open.ys7.com/test/1.live",
                "expireTime": "2024-12-31 23:59:59",
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_live_address(
            device_serial="TEST123456",
            channel_no=1,
            protocol=1,
            quality=1,
            type=1,
        )

        assert isinstance(result, LiveAddress)


class TestGetStreamAddress:
    """测试 get_stream_address 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.get")
    def test_get_stream_address_success(self, mock_get, api_with_token):
        """测试获取直播流地址成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "meta": {"code": 200, "message": "操作成功"},
            "data": {
                "address": "https://hls.example.com/stream/test.m3u8",
            },
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = api_with_token.get_stream_address(
            stream_id=787305182210818048,
            protocol=1,
        )

        assert isinstance(result, StreamAddress)
        assert "hls.example.com" in result.address

    @patch("lsyiot_ys7_sdk.api.requests.get")
    def test_get_stream_address_api_error(self, mock_get, api_with_token):
        """测试 API 返回错误"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "meta": {"code": 10001, "message": "参数错误"},
            "data": None,
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with pytest.raises(Ys7SdkLiveStreamError) as exc_info:
            api_with_token.get_stream_address(
                stream_id=787305182210818048,
                protocol=1,
            )
        assert "获取直播流播放地址失败" in str(exc_info.value)


class TestGetDeviceInfo:
    """测试 get_device_info 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_info_success(self, mock_post, api_with_token):
        """测试获取设备信息成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {
                "deviceSerial": "TEST123456",
                "deviceName": "测试设备",
                "localName": "本地设备名称",
                "model": "CS-C6CN",
                "status": 1,
                "defence": 0,
                "isEncrypt": 0,
                "alarmSoundMode": 0,
                "offlineNotify": 1,
                "category": "IPC",
                "parentCategory": "camera",
                "netType": "wire",
                "signal": "100",
                "riskLevel": 0,
                "netAddress": "192.168.1.100",
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_device_info(device_serial="TEST123456")

        assert isinstance(result, DeviceInfo)
        assert result.device_serial == "TEST123456"
        assert result.device_name == "测试设备"
        assert result.status == 1
        assert result.model == "CS-C6CN"


class TestGetDeviceConnectionInfo:
    """测试 get_device_connection_info 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_connection_info_success(self, mock_post, api_with_token):
        """测试获取设备连接信息成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {
                "subSerial": "TEST123456",
                "localIp": "192.168.1.100",
                "natIp": "220.112.33.44",
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_device_connection_info(device_serial="TEST123456")

        assert isinstance(result, DeviceConnectionInfo)
        assert result.sub_serial == "TEST123456"
        assert result.local_ip == "192.168.1.100"
        assert result.nat_ip == "220.112.33.44"


class TestGetDeviceStatus:
    """测试 get_device_status 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_status_success(self, mock_post, api_with_token):
        """测试获取设备状态成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {
                "privacyStatus": 0,
                "pirStatus": 1,
                "alarmSoundMode": 0,
                "battryStatus": 80,
                "lockSignal": 90,
                "diskNum": 1,
                "diskState": "正常",
                "cloudStatus": 1,
                "nvrDiskNum": 0,
                "nvrDiskState": "",
                "netAddress": "192.168.1.100",
                "signal": 85,
                "wakeUpStatus": 0,
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_device_status(
            device_serial="TEST123456",
            channel=1,
        )

        assert isinstance(result, DeviceStatus)
        assert result.disk_num == 1
        assert result.cloud_status == 1
        assert result.battry_status == 80
        assert result.signal == 85

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_status_without_channel(self, mock_post, api_with_token):
        """测试不带通道号获取设备状态"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": {
                "diskNum": 1,
                "cloudStatus": -1,
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_device_status(device_serial="TEST123456")

        assert isinstance(result, DeviceStatus)


class TestEnums:
    """测试枚举类"""

    def test_ptz_direction_values(self):
        """测试云台方向枚举值"""
        assert PTZDirection.UP == 0
        assert PTZDirection.DOWN == 1
        assert PTZDirection.LEFT == 2
        assert PTZDirection.RIGHT == 3
        assert PTZDirection.ZOOM_IN == 8
        assert PTZDirection.ZOOM_OUT == 9
        assert PTZDirection.AUTO == 16

    def test_ptz_speed_values(self):
        """测试云台速度枚举值"""
        assert PTZSpeed.SLOW == 0
        assert PTZSpeed.MEDIUM == 1
        assert PTZSpeed.FAST == 2

    def test_mirror_command_values(self):
        """测试镜像命令枚举值"""
        assert MirrorCommand.UP_DOWN == 0
        assert MirrorCommand.LEFT_RIGHT == 1
        assert MirrorCommand.CENTER == 2


class TestExceptionHierarchy:
    """测试异常继承层次结构"""

    def test_all_exceptions_inherit_from_base(self):
        """测试所有SDK异常都继承自Ys7SdkError"""
        assert issubclass(Ys7SdkAccessTokenError, Ys7SdkError)
        assert issubclass(Ys7SdkPTZControlError, Ys7SdkError)
        assert issubclass(Ys7SdkDeviceCaptureError, Ys7SdkError)
        assert issubclass(Ys7SdkDeviceError, Ys7SdkError)
        assert issubclass(Ys7SdkLiveStreamError, Ys7SdkError)

    def test_base_exception_inherits_from_exception(self):
        """测试基础异常继承自Exception"""
        assert issubclass(Ys7SdkError, Exception)

    def test_catch_all_sdk_errors(self):
        """测试可以用基类捕获所有SDK异常"""
        # 测试Ys7SdkAccessTokenError
        try:
            raise Ys7SdkAccessTokenError("token error")
        except Ys7SdkError as e:
            assert "token error" in str(e)

        # 测试Ys7SdkPTZControlError
        try:
            raise Ys7SdkPTZControlError("ptz error")
        except Ys7SdkError as e:
            assert "ptz error" in str(e)

        # 测试Ys7SdkDeviceError
        try:
            raise Ys7SdkDeviceError("device error")
        except Ys7SdkError as e:
            assert "device error" in str(e)

        # 测试Ys7SdkLiveStreamError
        try:
            raise Ys7SdkLiveStreamError("stream error")
        except Ys7SdkError as e:
            assert "stream error" in str(e)


class TestEntityToDict:
    """测试实体类的 to_dict 方法"""

    def test_access_token_to_dict(self):
        """测试 AccessToken 的 to_dict 方法"""
        token = AccessToken(access_token="test_token", expire_time=1234567890)
        result = token.to_dict()

        assert result["accessToken"] == "test_token"
        assert result["expireTime"] == 1234567890

    def test_preset_index_to_dict(self):
        """测试 PresetIndex 的 to_dict 方法"""
        preset = PresetIndex(index=5)
        result = preset.to_dict()

        assert result["index"] == 5

    def test_capture_result_to_dict(self):
        """测试 CaptureResult 的 to_dict 方法"""
        capture = CaptureResult(pic_url="https://example.com/image.jpg")
        result = capture.to_dict()

        assert result["picUrl"] == "https://example.com/image.jpg"

    def test_device_info_to_dict(self):
        """测试 DeviceInfo 的 to_dict 方法"""
        info = DeviceInfo(
            device_serial="TEST123",
            device_name="测试设备",
            local_name="本地名称",
            model="CS-C6CN",
            status=1,
            defence=0,
            is_encrypt=0,
            alarm_sound_mode=0,
            offline_notify=1,
            category="IPC",
            parent_category="camera",
            net_type="wire",
            signal="100",
            risk_level=0,
            net_address="192.168.1.100",
        )
        result = info.to_dict()

        assert result["deviceSerial"] == "TEST123"
        assert result["deviceName"] == "测试设备"
        assert result["status"] == 1


class TestGetDeviceList:
    """测试 get_device_list 方法"""

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_list_success(self, mock_post, api_with_token):
        """测试获取设备列表成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": [
                {
                    "id": "004368108f1444459901a063969a6c03",
                    "deviceSerial": "TEST123456",
                    "deviceName": "测试摄像头1",
                    "deviceType": "CS-C6CN",
                    "status": 1,
                    "defence": 0,
                    "deviceVersion": "V5.3.0 build 210101",
                    "addTime": 1693806032741,
                    "updateTime": 1693806032741,
                    "parentCategory": "IPC",
                    "riskLevel": 0,
                    "netAddress": "192.168.1.100",
                },
                {
                    "id": "004368108f1444459901a063969a6c04",
                    "deviceSerial": "TEST123457",
                    "deviceName": "测试摄像头2",
                    "deviceType": "CS-C3W",
                    "status": 0,
                    "defence": 1,
                    "deviceVersion": "V5.2.0 build 200801",
                    "addTime": 1693806032742,
                    "updateTime": 1693806032742,
                    "parentCategory": "IPC",
                    "riskLevel": 0,
                    "netAddress": None,
                },
            ],
            "page": {"total": 2, "size": 10, "page": 0},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_device_list(page_start=0, page_size=10)

        assert isinstance(result, DeviceListResult)
        assert len(result.devices) == 2
        assert isinstance(result.page, PageInfo)
        assert result.page.total == 2
        assert result.page.size == 10
        assert result.page.page == 0

        # 验证第一个设备
        device1 = result.devices[0]
        assert isinstance(device1, Device)
        assert device1.device_serial == "TEST123456"
        assert device1.device_name == "测试摄像头1"
        assert device1.status == 1
        assert device1.device_version == "V5.3.0 build 210101"

        # 验证第二个设备
        device2 = result.devices[1]
        assert device2.device_serial == "TEST123457"
        assert device2.status == 0

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_list_default_params(self, mock_post, api_with_token):
        """测试不带参数获取设备列表"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": [],
            "page": {"total": 0, "size": 10, "page": 0},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_device_list()

        assert isinstance(result, DeviceListResult)
        assert len(result.devices) == 0
        assert result.page.total == 0

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_list_large_page(self, mock_post, api_with_token):
        """测试大量设备分页"""
        # 模拟400页数据
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "200",
            "msg": "操作成功",
            "data": [
                {
                    "id": f"id_{i}",
                    "deviceSerial": f"DEVICE{i:06d}",
                    "deviceName": f"设备{i}",
                    "deviceType": "CS-C6CN",
                    "status": i % 2,
                    "defence": 0,
                    "deviceVersion": "V5.3.0",
                    "addTime": 1693806032000 + i,
                    "updateTime": 1693806032000 + i,
                    "parentCategory": "IPC",
                    "riskLevel": 0,
                    "netAddress": f"192.168.1.{i % 255}",
                }
                for i in range(50)
            ],
            "page": {"total": 20000, "size": 50, "page": 10},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = api_with_token.get_device_list(page_start=10, page_size=50)

        assert len(result.devices) == 50
        assert result.page.total == 20000
        assert result.page.page == 10

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_list_no_token(self, mock_post, api):
        """测试没有 token 时自动获取失败的情况"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "10017",
            "msg": "appKey不存在",
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Ys7SdkAccessTokenError) as exc_info:
            api.get_device_list()
        assert "获取accessToken失败" in str(exc_info.value)

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_list_api_error(self, mock_post, api_with_token):
        """测试 API 返回非 10002 错误"""
        mock_response = Mock()
        # 使用 10005 错误码（而不是 10002，因为 10002 会触发自动重试）
        mock_response.json.return_value = {"code": "10005", "msg": "appKey被冻结"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Ys7SdkDeviceError) as exc_info:
            api_with_token.get_device_list()
        assert "获取设备列表失败" in str(exc_info.value)

    @patch("lsyiot_ys7_sdk.api.requests.post")
    def test_get_device_list_token_expired_retry(self, mock_post, api_with_token):
        """测试 token 过期时自动刷新并重试"""
        # 第一次调用返回 10002（token 过期），触发 token 刷新
        # 刷新 token 的请求成功，第三次调用（重试）返回成功
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            if call_count[0] == 1:
                # 第一次调用 get_device_list，返回 10002
                mock_response.json.return_value = {"code": "10002", "msg": "accessToken过期"}
            elif call_count[0] == 2:
                # 刷新 token，返回成功
                mock_response.json.return_value = {
                    "code": "200",
                    "msg": "操作成功",
                    "data": {
                        "accessToken": "new_access_token",
                        "expireTime": 9999999999999,
                    },
                }
            else:
                # 重试 get_device_list，返回成功
                mock_response.json.return_value = {
                    "code": "200",
                    "msg": "操作成功",
                    "data": [],
                    "page": {"total": 0, "size": 10, "page": 0},
                }
            return mock_response

        mock_post.side_effect = side_effect

        result = api_with_token.get_device_list()

        assert result.page.total == 0
        assert api_with_token.access_token == "new_access_token"
        assert call_count[0] == 3  # 确认调用了 3 次


class TestDeviceEntity:
    """测试 Device 实体类"""

    def test_device_to_dict(self):
        """测试 Device 的 to_dict 方法"""
        device = Device(
            id="test_id",
            device_serial="TEST123",
            device_name="测试设备",
            device_type="CS-C6CN",
            status=1,
            defence=0,
            device_version="V5.3.0",
            add_time=1693806032741,
            update_time=1693806032741,
            parent_category="IPC",
            risk_level=0,
            net_address="192.168.1.100",
        )
        result = device.to_dict()

        assert result["id"] == "test_id"
        assert result["deviceSerial"] == "TEST123"
        assert result["deviceName"] == "测试设备"
        assert result["status"] == 1

    def test_page_info_to_dict(self):
        """测试 PageInfo 的 to_dict 方法"""
        page = PageInfo(total=100, size=10, page=5)
        result = page.to_dict()

        assert result["total"] == 100
        assert result["size"] == 10
        assert result["page"] == 5

    def test_device_list_result_to_dict(self):
        """测试 DeviceListResult 的 to_dict 方法"""
        devices = [
            Device(device_serial="TEST1", device_name="设备1", status=1),
            Device(device_serial="TEST2", device_name="设备2", status=0),
        ]
        page = PageInfo(total=2, size=10, page=0)
        result = DeviceListResult(devices=devices, page=page)

        result_dict = result.to_dict()
        assert len(result_dict["data"]) == 2
        assert result_dict["page"]["total"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
