import logging
import platform
import shutil
import subprocess
from pathlib import Path

import requests

# idb 下载链接
DARWIN_URL = "https://ct-1303240315.cos.ap-guangzhou.myqcloud.com/releases/idb/latest/darwin/idb"
LINUX_ARM64_URL = "https://ct-1303240315.cos.ap-guangzhou.myqcloud.com/releases/idb/latest/linux-arm64/idb"
LINUX_X86_URL = "https://ct-1303240315.cos.ap-guangzhou.myqcloud.com/releases/idb/latest/linux-amd64/idb"
WINDOWS_URL = "https://ct-1303240315.cos.ap-guangzhou.myqcloud.com/releases/idb/latest/windows/idb.exe"

logger = logging.getLogger(__name__)


def get_idb(idb_path) -> str:
    """获取 idb 路径，如果未找到则下载安装

    Args:
        idb_path: 指定的 idb 路径，可选

    Returns:
        str: idb 可执行文件的完整路径
    """
    # 如果指定了文件路径且存在，直接返回
    if idb_path and Path(idb_path).is_file():
        logger.info("idb path: %s", idb_path)
        return idb_path

    # 获取系统信息
    system = platform.system()
    exe_name = "idb.exe" if system == "Windows" else "idb"

    # 1. 首先在 PATH 中查找
    idb_in_path = shutil.which(exe_name)
    if idb_in_path:
        logger.info("idb path: %s", idb_in_path)
        return idb_in_path

    # 2. 如果 PATH 中没有找到，尝试默认路径
    # pathlib 的推荐用法
    # https://docs.python.org/zh-cn/3.13/library/pathlib.html
    default_dir = Path.home() / "localdevices" / "idb"
    default_path = default_dir / exe_name

    if default_path.exists():
        logger.info("idb path: %s", default_path)
        return str(default_path)

    # 3. 都没有找到，下载安装
    default_dir.mkdir(parents=True, exist_ok=True)

    download_urls = {
        "Windows": WINDOWS_URL,
        "Darwin": DARWIN_URL,
        "Linux": {"arm64": LINUX_ARM64_URL, "x86": LINUX_X86_URL},
    }

    url = download_urls.get(system)
    if not url:
        raise RuntimeError(f"Unsupported operating system: {system}")
    if system == "Linux":
        arch = platform.machine()
        if arch.lower() in ("x86_64", "amd64"):
            url = url["x86"]
        elif arch.lower() in ("aarch64", "arm64"):
            url = url["arm64"]
        else:
            raise RuntimeError(f"Unsupported architecture: {arch}")

    download_file(url, str(default_path))

    # 在类 Unix 系统上设置执行权限
    if system != "Windows":
        default_path.chmod(default_path.stat().st_mode | 0o755)
    if system == "Darwin":
        subprocess.run(["xattr", "-d", "com.apple.quarantine", str(default_path)])

    logger.info("idb path: %s", default_path)
    return str(default_path)


def download_file(url, local_path):
    # 发送 GET 请求并设置流模式
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 检查请求是否成功

    # 以二进制写入模式打开本地文件
    with open(local_path, "wb") as f:
        # 分块写入文件
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
