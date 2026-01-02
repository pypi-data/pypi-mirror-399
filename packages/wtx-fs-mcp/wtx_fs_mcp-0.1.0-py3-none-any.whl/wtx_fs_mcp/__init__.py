"""
FastMCP wtx fs mcp.

Run from the repository root:
    uv run main.py
"""
import shutil
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("wtx_fs_mcp", json_response=True)

def check_fs(source: str, destination: str) -> tuple[Path, Path] | None:
    src_path = Path(source).expanduser().resolve()
    dst_path = Path(destination).expanduser().resolve()

    # 防止源目录被目标目录覆盖
    if dst_path.exists():
        if src_path.samefile(dst_path):
            return None

    # 确保目标父目录存在
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    return src_path, dst_path

# Add an addition tool
@mcp.tool()
def move(source: str, destination: str) -> bool:
    """
        将 source 移动到 destination 位置。
        destination 父目录不存在时会自动创建。
        成功返回 True，失败返回 False。
    """
    try:
        fs_result =  check_fs(source, destination)

        if fs_result is None:
            return False

        src_path, dst_path = fs_result

        # 执行移动
        shutil.move(str(src_path), str(dst_path))
        return True
    except Exception:
        return False


# Add an addition tool
@mcp.tool()
def copy(source: str, destination: str) -> bool:
    """
        将 source 目录复制到 destination 位置。
        destination 父目录不存在时会自动创建。
        成功返回 True，失败返回 False。
    """
    try:
        fs_result =  check_fs(source, destination)

        if fs_result is None:
            return False

        src_path, dst_path = fs_result

        # 执行移动
        shutil.copy(str(src_path), str(dst_path))
        return True
    except Exception:
        return False

def main() -> None:
    mcp.run(transport="stdio")
