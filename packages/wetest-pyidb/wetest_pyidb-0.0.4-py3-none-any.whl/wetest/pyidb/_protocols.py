from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ref: ct2-agent/cmd/idb/cmd/list.go:40:deviceItem
class Device(BaseModel):
    udid: str
    serial: str
    name: str
    market_name: str
    product_version: str
    conn_type: str
    device_id: int


# ref: ct2-agent/cmd/idb/cmd/info.go:87:info
class Info(BaseModel):
    market_name: str = Field(alias="MarketName")
    device_name: str = Field(alias="DeviceName")
    product_version: str = Field(alias="ProductVersion")
    product_type: str = Field(alias="ProductType")
    model_number: str = Field(alias="ModelNumber")
    serial_number: str = Field(alias="SerialNumber")
    cpu_architecture: str = Field(alias="CPUArchitecture")
    product_name: str = Field(alias="ProductName")
    protocol_version: int = Field(alias="ProtocolVersion")
    region_info: str = Field(alias="RegionInfo")
    time_interval_since_1970: float = Field(alias="TimeIntervalSince1970")
    time_zone: str = Field(alias="TimeZone")
    unique_device_id: str = Field(alias="UniqueDeviceID")
    wifi_address: str = Field(alias="WiFiAddress")
    bluetooth_address: str = Field(alias="BluetoothAddress")
    base_band_version: str = Field(alias="BasebandVersion")
    screen_width: int = Field(default=0, alias="ScreenWidth")
    screen_height: int = Field(default=0, alias="ScreenHeight")
    screen_scale_factor: float = Field(default=0, alias="ScreenScaleFactor")
    conn_type: str = Field(default="unknown", alias="ConnType")


# ref: ioskit/services/dvt/instruments/device_info.go:47:processInfo
class ProcessInfo(BaseModel):
    is_application: bool = Field(alias="IsApplication")
    name: str = Field(alias="Name")
    pid: int = Field(alias="Pid")
    real_app_name: str = Field(alias="RealAppName")
    start_date: str = Field(alias="StartDate")
    bundle_id: str = Field(alias="BundleId")
    display_name: str = Field(alias="DisplayName")


class AppInfo(BaseModel):
    application_dsid: int = Field(alias="ApplicationDSID")
    application_type: str = Field(alias="ApplicationType")
    bundle_display_name: str = Field(alias="CFBundleDisplayName")
    bundle_executable: str = Field(alias="CFBundleExecutable")
    bundle_id: str = Field(alias="CFBundleIdentifier")
    bundle_name: str = Field(alias="CFBundleName")
    bundle_short_version: str = Field(alias="CFBundleShortVersionString")
    bundle_version: str = Field(alias="CFBundleVersion")
    container: str = Field(alias="Container")
    entitlements: Dict[str, Any] = Field(alias="Entitlements")
    environment_variables: Dict[str, Any] = Field(alias="EnvironmentVariables")
    minimum_os_version: str = Field(alias="MinimumOSVersion")
    path: str = Field(alias="Path")
    profile_validated: bool = Field(alias="ProfileValidated")
    sb_app_tags: Optional[str] = Field(alias="SBAppTags")
    signer_identity: str = Field(alias="SignerIdentity")
    uid_device_family: List[int] = Field(alias="UIDeviceFamily")
    ui_required_device_capabilities: List[str] = Field(alias="UIRequiredDeviceCapabilities")
    ui_file_sharing_enabled: bool = Field(alias="UIFileSharingEnabled")
