import logging
import socket
import subprocess
import time
from pathlib import Path
from typing import Callable, List, Optional, TypeVar, Union

import packaging.version
from pydantic import TypeAdapter

from ._protocols import AppInfo, Device, Info, ProcessInfo
from ._utils import get_idb
from .exceptions import IdbError

IOS15 = packaging.version.parse("15.0.0")
IOS17 = packaging.version.parse("17.0.0")

XCTEST_APP = {
    "com.facebook.WebDriverAgentRunner.xctrunner": [8100],  # WDA 只有一个端口
    "com.wetest.wda-scrcpy.xctrunner": [21343, 21344],  # SCRCPY 有控制端口和视频端口
}

T = TypeVar("T")
logger = logging.getLogger(__name__)


class Idb:
    def __init__(self, udid: str = "", idb_path: str = "", tunnel_port: str = "8082", timeout: float = 5):
        self._udid = udid
        self.idb_path = get_idb(idb_path)
        self.tunnel_port = tunnel_port
        self.timeout = timeout

        self._tunnel_process: Optional[subprocess.Popen] = None

    # 析构函数
    # 用于在程序退出时自动关闭tunnel
    def __del__(self):
        self.tunnel_stop()

    def __repr__(self):
        return f"idb(udid={self.udid}, idb_path={self.idb_path}, tunnel_port={self.tunnel_port}, timeout={self.timeout}, version={self.version})"

    # 拦截所有的属性访问，包括属性不存在的情况
    # 高频属性访问场景有明显性能损耗
    # 用于在iOS>17.0.0版本下拉起tunnel
    def __getattribute__(self, name: str):
        # 避免递归调用，只处理 ps 和 launch app 两类需要挂载镜像和tunnel的情况
        if name in ["ps", "launch", "kill"]:
            # 挂载镜像
            self.mount_developer_image()
            # tunnel start
            ios_version = packaging.version.parse(self.info().product_version)
            if ios_version >= IOS17:
                self.tunnel_start()
                logger.info(f"iOS version {ios_version} start tunnel")
        return super().__getattribute__(name)

    # 处理属性不存在的情况
    def __getattr__(self, name: str):
        # 忽略 pytest 对 __bases__ __tests__ 的访问
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        error_msg = f"pyidb: {name} not found, please wait for the next version to support"
        logger.exception(error_msg)
        raise AttributeError(error_msg)

    @property
    def udid(self):
        # 如果udid为空，尝试获取一个udid，就不再区分通用指令是否需要-u参数
        # ref: ioskit/tunnel/utils.go:GetDevice2
        if self._udid:
            return self._udid
        devices = self.list()
        if devices:
            self._udid = devices[0].udid
        return self._udid

    @udid.setter
    def udid(self, udid: str):
        self._udid = udid

    @property
    def version(self) -> str:
        """
        获取 idb 版本
        Returns:
            str: idb 版本
        """
        ver = self._exec_cmd(["version"], json_parse=False)
        ver = ver.strip("Version:").strip()
        return ver

    @staticmethod
    def _tunneld(tunnel_port: str) -> bool:
        # 检查tunnel端口是否正在被监听
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("127.0.0.1", int(tunnel_port)))
            sock.close()
            logger.debug(f"Port {tunnel_port} is {'open' if result == 0 else 'closed'}")
            return result == 0
        except Exception:
            logger.exception(f"Error checking port {tunnel_port}")
            return False

    def _exec_cmd(
        self, cmd: List[str], parser: Callable[[str], T] = lambda x: x, json_parse: bool = True
    ) -> Union[T, str]:
        """
        execute idb commands

        Args:
            cmd (List[str]): idb commands
            json_parse (bool, optional): 是否以 json 格式解析 command 输出. Defaults to True.

        Returns:
            T: json解析后的结果
            str: 未解析的原始字符串
        """
        idb_path = [self.idb_path]
        cmd = idb_path + cmd + ["--json"] if json_parse else idb_path + cmd

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
        output = result.stdout
        if result.returncode != 0:
            logger.exception(f"{cmd} failed with return code {result.returncode}")
            raise IdbError(cmd, result.returncode, result.stdout)
        if json_parse:
            return parser(output)
        return output

    # ***********************************************************
    # idb commands
    # ***********************************************************

    def list(self) -> List[Device]:
        return self._exec_cmd(["list"], parser=lambda x: TypeAdapter(List[Device]).validate_json(x))

    def info(self, udid: str = "") -> Info:
        target_udid = udid if udid else self.udid

        def info_parser(info_data):
            info_data = Info.model_validate_json(info_data)
            devices = self.list()
            for device in devices:
                if device.udid == target_udid:
                    info_data.conn_type = device.conn_type
                    break
            return info_data

        return self._exec_cmd(["-u", target_udid, "info"], parser=info_parser)

    def tunnel_start(self) -> bool:
        # 非阻塞执行tunnel start
        if Idb._tunneld(self.tunnel_port):
            logger.debug(f"tunnel has started on port {self.tunnel_port}")
            return True
        self._tunnel_process = subprocess.Popen(
            [self.idb_path, "tunnel", "start", "-P", self.tunnel_port],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if Idb._tunneld(self.tunnel_port):
                logger.debug(f"tunnel has started on port {self.tunnel_port}")
                return True
            time.sleep(0.5)

        # 超时未启动，结束tunnel进程，避免僵尸进程
        self.tunnel_stop(self.timeout)
        return Idb._tunneld(self.tunnel_port)

    def tunnel_stop(self) -> bool:
        if self._tunnel_process:
            try:
                self._tunnel_process.terminate()
                self._tunnel_process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self._tunnel_process.kill()
            except Exception:
                logger.exception("Failed to stop tunnel process")
            self._tunnel_process = None
        return not Idb._tunneld(self.tunnel_port)

    def ps(self, bundle_id: str = "", udid: str = "") -> Union[ProcessInfo, List[ProcessInfo]]:
        """
        获取进程列表

        Args:
            udid (str, optional): 指定设备udid, 默认为当前设备
            bundle_id (str, optional): 指定bundle_id, 默认为空，返回所有进程

        Returns:
            List[ProcessInfo]: 所有进程列表。如果 bundle_id 不为空, 返回指定 bundle_id 的进程列表, 如果不存在, 返回空列表
        """
        cmd = ["-u", udid if udid else self.udid, "ps", "--all"]
        ios_version = packaging.version.parse(self.info(udid).product_version)
        if ios_version >= IOS17:
            cmd += ["-P", self.tunnel_port]
        processes = self._exec_cmd(cmd, parser=lambda x: TypeAdapter(List[ProcessInfo]).validate_json(x))
        if bundle_id:
            for p in processes:
                if p.bundle_id == bundle_id:
                    return p
            else:
                return []
        return processes

    def applist(self, bundle_id: str = "", udid: str = "") -> Union[AppInfo, List[AppInfo]]:
        """
        读取设备应用列表

        Args:
            bundle_id (str, optional): 指定bundle_id, 默认为空，返回所有应用
            udid (str, optional): 指定设备udid, 默认为当前设备

        Returns:
            List[AppInfo]: 所有应用列表。如果 bundle_id 不为空, 返回指定 bundle_id 的应用列表, 如果不存在, 返回空列表
        """
        apps = self._exec_cmd(
            ["-u", udid if udid else self.udid, "applist"], parser=lambda x: TypeAdapter(List[AppInfo]).validate_json(x)
        )
        if bundle_id:
            for app in apps:
                if bundle_id == app.bundle_id:
                    return app
            else:
                return None
        return apps

    def launch(self, bundle_id: str, skip_running: bool = False, udid: str = "") -> Union[ProcessInfo]:
        """
        拉起 app
        Args:
            bundle_id (str): app bundle_id
            skip_running (bool, optional): 是否跳过已经运行的 app, 默认为 False
            udid (str, optional): 指定设备udid, 默认为当前设备
        Returns:
            List[Dict[str, str]]: app 进程列表, 如果拉起失败, 返回空列表
        """
        if bundle_id in XCTEST_APP.keys():
            return self._launch_xctest(bundle_id, skip_running, udid)

        ios_version = packaging.version.parse(self.info(udid).product_version)
        cmd = ["-u", udid if udid else self.udid, "launch", bundle_id]
        if skip_running:
            cmd += ["-s"]
        if ios_version >= IOS17:
            cmd += ["-P", self.tunnel_port]
        self._exec_cmd(cmd, json_parse=False)
        return self.ps(bundle_id=bundle_id)

    def _launch_xctest(self, bundle_id: str, skip_running: bool = False, udid: str = "") -> ProcessInfo:
        """
        拉起 xctest 类 app

        Args:
            udid (str, optional): 指定设备udid, 默认为当前设备

        Returns:
            ProcessInfo: xctest 类 app 进程信息, 如果拉起失败, 返回空
        """
        from wetest.osplatform import ios_conn

        # ios15+ 启动企业版本wda。15-17，直接launch，>=17，启动tunnel
        # ios14- 必须用开发者版本，且必须为开发者证书，使用 xctest-B 启动
        # ref: https://iwiki.woa.com/p/4013894043
        if not skip_running and self.ps(bundle_id=bundle_id):
            self.kill(bundle_id, udid)
        ios_version = packaging.version.parse(self.info(udid).product_version)

        cmd = ["-u", udid if udid else self.udid]
        if ios_version >= IOS17:
            cmd += ["launch", bundle_id, "-P", self.tunnel_port]
        elif ios_version >= IOS15:
            cmd += ["launch", bundle_id]
        else:
            cmd += ["xctest", "-B", bundle_id]
        self._exec_cmd(cmd, json_parse=False)

        # 添加端口检查，确保端口启动成功
        for port in XCTEST_APP[bundle_id]:
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    with ios_conn(udid if udid else self.udid, port):
                        logger.debug(f"Port {port} available for {bundle_id}")
                        break
                except Exception:
                    time.sleep(0.1)
            else:
                logger.exception(f"Failed to launch xctest app {bundle_id}, port {port} not available")
                raise IdbError(f"Failed to launch xctest app {bundle_id}, port {port} not available")
        return self.ps(bundle_id=bundle_id)

    def mount_developer_image(self, udid: str = "") -> bool:
        """
        挂载开发者镜像

        Args:
            udid (str, optional): 指定设备udid, 默认为当前设备

        Returns:
            bool: 挂载成功，返回 True, 否则返回 False
        """
        self._exec_cmd(["-u", udid if udid else self.udid, "developer"], json_parse=False)
        # 等待2秒，确保镜像挂载成功，避免立刻执行 -l 命令出现报错，new mounter failed EOF
        time.sleep(2)
        result = self._exec_cmd(["-u", udid if udid else self.udid, "developer", "-l"], json_parse=False)
        return result != ""

    def kill(self, bundle_id: str, udid: str = "") -> bool:
        """
        kill app 进程

        Args:
            bundle_id (str): app bundle_id
            udid (str, optional): 指定设备udid, 默认为当前设备

        Raises:
            IdbError: 如果 app 进程不存在, 抛出 IdbError 异常： "failed with return code 1: Error: ProcessNotFound"

        Returns:
            bool: app 进程不存在, 返回 True, 否则返回 False
        """
        ios_version = packaging.version.parse(self.info(udid).product_version)
        cmd = ["-u", udid if udid else self.udid, "kill", bundle_id]
        if ios_version >= IOS17:
            cmd += ["-P", self.tunnel_port]
        self._exec_cmd(cmd, json_parse=False)
        return len(self.ps(bundle_id=bundle_id)) == 0

    def reboot(self, udid: str = ""):
        """
        重启手机
        Args:
            udid (str, optional): 指定设备udid, 默认为当前设备
        """
        self._exec_cmd(["-u", udid if udid else self.udid, "reboot", "--wait"], json_parse=False)

    def appinfo(self, bundle_id: str, udid: str = "") -> AppInfo:
        """
        获取 app 信息
        Args:
            bundle_id (str): app bundle_id
            udid (str, optional): 指定设备udid, 默认为当前设备

        Raises:
            IdbError: 如果 app 不存在, 抛出 IdbError 异常： Error: get 'bundle_id' info failed: NotFound

        Returns:
            AppInfo: app 信息
        """
        return self._exec_cmd(
            ["-u", udid if udid else self.udid, "appinfo", bundle_id], parser=AppInfo.model_validate_json
        )

    def install(self, app_path: str, mode: str = "v2", udid: str = ""):
        """
        安装 app
        Args:
            app_path (str): app 路径
            mode (str, optional): 安装模式, 默认为 v2
            udid (str, optional): 指定设备udid, 默认为当前设备
        """
        if not Path(app_path).exists():
            raise FileNotFoundError(f"App {app_path} not found")

        # 保留安装进度条
        cmd = [
            self.idb_path,
            "-u",
            udid if udid else self.udid,
            "install",
            app_path,
            "--v1" if mode == "v1" else "--v2",
        ]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # 行缓冲
        )

        output_lines = []
        try:
            # 实时读取输出
            for line in iter(process.stdout.readline, ""):
                if line:
                    logger.debug(line.rstrip())  # 实时打印
                    output_lines.append(line)

            # 等待进程结束
            return_code = process.wait()

            if return_code != 0:
                full_output = "".join(output_lines)
                logger.exception(f"{cmd} failed with return code {return_code}")
                raise IdbError(cmd, return_code, full_output)

            return "".join(output_lines)

        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            raise
        finally:
            if process.stdout:
                process.stdout.close()

    def uninstall(self, bundle_id: str, udid: str = "") -> bool:
        """
        卸载 app
        Args:
            bundle_id (str): app bundle_id
            udid (str, optional): 指定设备udid, 默认为当前设备
        Returns:
            bool: 卸载成功，返回 True, 否则返回 False
        """
        self._exec_cmd(["-u", udid if udid else self.udid, "uninstall", bundle_id], json_parse=False)
        return not self.applist(bundle_id)
