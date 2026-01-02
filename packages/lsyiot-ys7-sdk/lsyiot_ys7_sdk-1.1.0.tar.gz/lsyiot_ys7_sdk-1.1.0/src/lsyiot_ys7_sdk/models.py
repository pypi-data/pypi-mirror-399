"""
萤石云API响应实体类
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List


@dataclass
class AccessToken:
    """AccessToken信息"""

    access_token: str
    """访问令牌"""

    expire_time: int
    """过期时间，精确到毫秒"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {"accessToken": self.access_token, "expireTime": self.expire_time}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessToken":
        """从字典创建实例"""
        return cls(
            access_token=data.get("accessToken", ""),
            expire_time=data.get("expireTime", 0),
        )


@dataclass
class PresetIndex:
    """预置点信息"""

    index: int
    """预置点序号，C6设备是1-12，该参数需要开发者自行保存"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {"index": self.index}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PresetIndex":
        """从字典创建实例"""
        return cls(index=data.get("index", 0))


@dataclass
class CaptureResult:
    """设备抓拍结果"""

    pic_url: str
    """抓拍后的图片路径，图片保存有效期为2小时"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {"picUrl": self.pic_url}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaptureResult":
        """从字典创建实例"""
        return cls(pic_url=data.get("picUrl", ""))


@dataclass
class DeviceCapacity:
    """设备能力集"""

    support_cloud: Optional[str] = None
    """是否支持云存储，1表示支持"""

    support_talk: Optional[str] = None
    """是否支持语音对讲，1表示支持"""

    support_ptz: Optional[str] = None
    """是否支持云台控制，1表示支持"""

    ptz_preset: Optional[str] = None
    """是否支持预置点，1表示支持"""

    support_capture: Optional[str] = None
    """是否支持抓图，1表示支持"""

    support_encrypt: Optional[str] = None
    """是否支持加密，1表示支持"""

    support_wifi: Optional[str] = None
    """是否支持WiFi，1表示支持"""

    support_defence: Optional[str] = None
    """是否支持布撤防，1表示支持"""

    ptz_center_mirror: Optional[str] = None
    """是否支持中心镜像，1表示支持"""

    ptz_top_bottom: Optional[str] = None
    """是否支持上下镜像，1表示支持"""

    ptz_left_right: Optional[str] = None
    """是否支持左右镜像，1表示支持"""

    support_intelligent_track: Optional[str] = None
    """是否支持智能追踪，1表示支持"""

    support_privacy: Optional[str] = None
    """是否支持隐私遮蔽，1表示支持"""

    support_upgrade: Optional[str] = None
    """是否支持升级，1表示支持"""

    support_disk: Optional[str] = None
    """是否支持磁盘，1表示支持"""

    support_alarm_voice: Optional[str] = None
    """是否支持告警声音，1表示支持"""

    support_modify_pwd: Optional[str] = None
    """是否支持修改密码，1表示支持"""

    _raw_data: Optional[Dict[str, Any]] = None
    """原始数据，包含所有能力集字段"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        if self._raw_data:
            return self._raw_data
        result = {}
        if self.support_cloud is not None:
            result["support_cloud"] = self.support_cloud
        if self.support_talk is not None:
            result["support_talk"] = self.support_talk
        if self.support_ptz is not None:
            result["support_ptz"] = self.support_ptz
        if self.ptz_preset is not None:
            result["ptz_preset"] = self.ptz_preset
        if self.support_capture is not None:
            result["support_capture"] = self.support_capture
        if self.support_encrypt is not None:
            result["support_encrypt"] = self.support_encrypt
        if self.support_wifi is not None:
            result["support_wifi"] = self.support_wifi
        if self.support_defence is not None:
            result["support_defence"] = self.support_defence
        if self.ptz_center_mirror is not None:
            result["ptz_center_mirror"] = self.ptz_center_mirror
        if self.ptz_top_bottom is not None:
            result["ptz_top_bottom"] = self.ptz_top_bottom
        if self.ptz_left_right is not None:
            result["ptz_left_right"] = self.ptz_left_right
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceCapacity":
        """从字典创建实例"""
        return cls(
            support_cloud=data.get("support_cloud"),
            support_talk=data.get("support_talk"),
            support_ptz=data.get("support_ptz"),
            ptz_preset=data.get("ptz_preset"),
            support_capture=data.get("support_capture"),
            support_encrypt=data.get("support_encrypt"),
            support_wifi=data.get("support_wifi"),
            support_defence=data.get("support_defence"),
            ptz_center_mirror=data.get("ptz_center_mirror"),
            ptz_top_bottom=data.get("ptz_top_bottom"),
            ptz_left_right=data.get("ptz_left_right"),
            support_intelligent_track=data.get("support_intelligent_track"),
            support_privacy=data.get("support_privacy"),
            support_upgrade=data.get("support_upgrade"),
            support_disk=data.get("support_disk"),
            support_alarm_voice=data.get("support_alarm_voice"),
            support_modify_pwd=data.get("support_modify_pwd"),
            _raw_data=data,
        )


@dataclass
class LiveAddress:
    """播放地址信息"""

    id: str
    """地址ID"""

    url: str
    """直播/回放地址"""

    expire_time: Optional[str] = None
    """直播地址有效期"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {"id": self.id, "url": self.url}
        if self.expire_time is not None:
            result["expireTime"] = self.expire_time
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LiveAddress":
        """从字典创建实例"""
        return cls(
            id=data.get("id", ""),
            url=data.get("url", ""),
            expire_time=data.get("expireTime"),
        )


@dataclass
class StreamAddress:
    """直播流播放地址"""

    address: str
    """播放地址"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {"address": self.address}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamAddress":
        """从字典创建实例"""
        return cls(address=data.get("address", ""))


@dataclass
class DeviceInfo:
    """设备信息"""

    device_serial: str
    """设备序列号"""

    device_name: str
    """设备名称"""

    model: str
    """设备型号"""

    status: int
    """在线状态：0-不在线，1-在线"""

    defence: int
    """布撤防状态"""

    is_encrypt: int
    """是否加密：0-不加密，1-加密"""

    alarm_sound_mode: int
    """告警声音模式：0-短叫，1-长叫，2-静音"""

    offline_notify: int
    """设备下线是否通知：0-不通知，1-通知"""

    category: str
    """设备大类"""

    local_name: Optional[str] = None
    """设备上报名称"""

    parent_category: Optional[str] = None
    """设备二级类目"""

    update_time: Optional[int] = None
    """修改时间"""

    net_type: Optional[str] = None
    """网络类型，如wire(有线)"""

    signal: Optional[str] = None
    """信号强度(%)"""

    risk_level: Optional[int] = None
    """设备风险安全等级，0-安全"""

    net_address: Optional[str] = None
    """设备IP地址"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "deviceSerial": self.device_serial,
            "deviceName": self.device_name,
            "model": self.model,
            "status": self.status,
            "defence": self.defence,
            "isEncrypt": self.is_encrypt,
            "alarmSoundMode": self.alarm_sound_mode,
            "offlineNotify": self.offline_notify,
            "category": self.category,
        }
        if self.local_name is not None:
            result["localName"] = self.local_name
        if self.parent_category is not None:
            result["parentCategory"] = self.parent_category
        if self.update_time is not None:
            result["updateTime"] = self.update_time
        if self.net_type is not None:
            result["netType"] = self.net_type
        if self.signal is not None:
            result["signal"] = self.signal
        if self.risk_level is not None:
            result["riskLevel"] = self.risk_level
        if self.net_address is not None:
            result["netAddress"] = self.net_address
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceInfo":
        """从字典创建实例"""
        return cls(
            device_serial=data.get("deviceSerial", ""),
            device_name=data.get("deviceName", ""),
            model=data.get("model", ""),
            status=data.get("status", 0),
            defence=data.get("defence", 0),
            is_encrypt=data.get("isEncrypt", 0),
            alarm_sound_mode=data.get("alarmSoundMode", 0),
            offline_notify=data.get("offlineNotify", 0),
            category=data.get("category", ""),
            local_name=data.get("localName"),
            parent_category=data.get("parentCategory"),
            update_time=data.get("updateTime"),
            net_type=data.get("netType"),
            signal=data.get("signal"),
            risk_level=data.get("riskLevel"),
            net_address=data.get("netAddress"),
        )


@dataclass
class DeviceConnectionInfo:
    """设备连接信息"""

    sub_serial: str
    """设备序列号"""

    local_ip: str
    """设备局域网IP地址"""

    nat_ip: str
    """设备外网地址"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "subSerial": self.sub_serial,
            "localIp": self.local_ip,
            "natIp": self.nat_ip,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceConnectionInfo":
        """从字典创建实例"""
        return cls(
            sub_serial=data.get("subSerial", ""),
            local_ip=data.get("localIp", ""),
            nat_ip=data.get("natIp", ""),
        )


@dataclass
class DeviceStatus:
    """设备状态信息"""

    privacy_status: int
    """隐私状态：0-关闭，1-打开，-1-初始值，2-不支持，-2-设备没有上报或不支持"""

    pir_status: int
    """红外状态：1-启用，0-禁用，-1-初始值，2-不支持，-2-设备没有上报或不支持"""

    alarm_sound_mode: int
    """告警声音模式：0-短叫，1-长叫，2-静音，3-自定义语音，-1-设备没有上报或不支持"""

    battry_status: int
    """电池电量(1-100%)，-1表示设备没有上报或不支持"""

    lock_signal: int
    """门锁和网关间的无线信号(%)，-1表示设备没有上报或不支持"""

    disk_num: int
    """挂载的sd硬盘数量，-1表示设备没有上报或不支持"""

    disk_state: str
    """sd硬盘状态：0-正常，1-存储介质错，2-未格式化，3-正在格式化"""

    cloud_status: int
    """云存储状态：-2-不支持，-1-未开通，0-未激活，1-激活，2-过期"""

    nvr_disk_num: int
    """NVR上挂载的硬盘数量：-1-设备没有上报或不支持，-2-未关联"""

    nvr_disk_state: str
    """NVR上挂载的硬盘状态"""

    cloud_type: Optional[int] = None
    """云存储类型"""

    net_address: Optional[str] = None
    """设备IP地址"""

    signal: Optional[int] = None
    """设备信号强度(0-100)，-1表示设备未上报或不支持"""

    wake_up_status: Optional[int] = None
    """唤醒状态：0-正常，1-休眠"""

    cloud_channel_list: Optional[List[Dict[str, Any]]] = None
    """设备通道号和设备侧云存储上报开关状态"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "privacyStatus": self.privacy_status,
            "pirStatus": self.pir_status,
            "alarmSoundMode": self.alarm_sound_mode,
            "battryStatus": self.battry_status,
            "lockSignal": self.lock_signal,
            "diskNum": self.disk_num,
            "diskState": self.disk_state,
            "cloudStatus": self.cloud_status,
            "nvrDiskNum": self.nvr_disk_num,
            "nvrDiskState": self.nvr_disk_state,
        }
        if self.cloud_type is not None:
            result["cloudType"] = self.cloud_type
        if self.net_address is not None:
            result["netAddress"] = self.net_address
        if self.signal is not None:
            result["signal"] = self.signal
        if self.wake_up_status is not None:
            result["wakeUpStatus"] = self.wake_up_status
        if self.cloud_channel_list is not None:
            result["cloudChannelList"] = self.cloud_channel_list
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceStatus":
        """从字典创建实例"""
        return cls(
            privacy_status=data.get("privacyStatus", -2),
            pir_status=data.get("pirStatus", -2),
            alarm_sound_mode=data.get("alarmSoundMode", -1),
            battry_status=data.get("battryStatus", -1),
            lock_signal=data.get("lockSignal", -1),
            disk_num=data.get("diskNum", -1),
            disk_state=data.get("diskState", ""),
            cloud_status=data.get("cloudStatus", -2),
            nvr_disk_num=data.get("nvrDiskNum", -1),
            nvr_disk_state=data.get("nvrDiskState", ""),
            cloud_type=data.get("cloudType"),
            net_address=data.get("netAddress"),
            signal=data.get("signal"),
            wake_up_status=data.get("wakeUpStatus"),
            cloud_channel_list=data.get("cloudChannelList"),
        )


@dataclass
class Device:
    """设备信息"""

    id: Optional[str] = None
    """条目索引"""

    device_serial: Optional[str] = None
    """设备序列号"""

    device_name: Optional[str] = None
    """设备名称"""

    device_type: Optional[str] = None
    """设备型号"""

    status: Optional[int] = None
    """设备在线状态，1-在线；0-离线"""

    defence: Optional[int] = None
    """布撤防状态"""

    device_version: Optional[str] = None
    """固件版本号"""

    add_time: Optional[int] = None
    """用户添加时间"""

    update_time: Optional[int] = None
    """设备最后更新时间"""

    parent_category: Optional[str] = None
    """设备二级类目名称"""

    risk_level: Optional[int] = None
    """设备风险安全等级，0-安全；大于0，有风险，风险越高，值越大"""

    net_address: Optional[str] = None
    """设备IP地址"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        if self.id is not None:
            result["id"] = self.id
        if self.device_serial is not None:
            result["deviceSerial"] = self.device_serial
        if self.device_name is not None:
            result["deviceName"] = self.device_name
        if self.device_type is not None:
            result["deviceType"] = self.device_type
        if self.status is not None:
            result["status"] = self.status
        if self.defence is not None:
            result["defence"] = self.defence
        if self.device_version is not None:
            result["deviceVersion"] = self.device_version
        if self.add_time is not None:
            result["addTime"] = self.add_time
        if self.update_time is not None:
            result["updateTime"] = self.update_time
        if self.parent_category is not None:
            result["parentCategory"] = self.parent_category
        if self.risk_level is not None:
            result["riskLevel"] = self.risk_level
        if self.net_address is not None:
            result["netAddress"] = self.net_address
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Device":
        """从字典创建实例"""
        return cls(
            id=data.get("id"),
            device_serial=data.get("deviceSerial"),
            device_name=data.get("deviceName"),
            device_type=data.get("deviceType"),
            status=data.get("status"),
            defence=data.get("defence"),
            device_version=data.get("deviceVersion"),
            add_time=data.get("addTime"),
            update_time=data.get("updateTime"),
            parent_category=data.get("parentCategory"),
            risk_level=data.get("riskLevel"),
            net_address=data.get("netAddress"),
        )


@dataclass
class PageInfo:
    """分页信息"""

    total: int
    """数据总数"""

    size: int
    """分页大小"""

    page: int
    """分页页码"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {"total": self.total, "size": self.size, "page": self.page}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PageInfo":
        """从字典创建实例"""
        return cls(
            total=data.get("total", 0),
            size=data.get("size", 0),
            page=data.get("page", 0),
        )


@dataclass
class DeviceListResult:
    """设备列表结果"""

    devices: List[Device]
    """设备列表"""

    page: PageInfo
    """分页信息"""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "data": [device.to_dict() for device in self.devices],
            "page": self.page.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceListResult":
        """从字典创建实例"""
        devices_data = data.get("data", [])
        devices = [Device.from_dict(device) for device in devices_data]
        page = PageInfo.from_dict(data.get("page", {}))
        return cls(devices=devices, page=page)
