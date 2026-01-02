import os
from pathlib import Path
from threading import Lock
import pathspec
from typing import Optional

# FileMonitor removed - agent reads fresh from filesystem each call
# Ignore rules are loaded once at startup; restart to pick up changes

DEFAULT_EXCLUDES = [
    '.git', '.auto-coder', 'node_modules', '.mvn', '.idea',
    '__pycache__', '.venv', 'venv', 'dist', 'build', '.gradle',".next"
]


class IgnoreFileManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, project_root: Optional[str] = None):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(IgnoreFileManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, project_root: Optional[str] = None):
        if self._initialized:
            return
        self._initialized = True
        self._spec = None
        self._ignore_file_path = None
        self._project_root = project_root if project_root is not None else os.getcwd()
        self._load_ignore_spec()

    def _load_ignore_spec(self):
        """加载忽略规则文件并解析规则"""
        ignore_patterns = []
        project_root = Path(self._project_root)

        ignore_file_paths = [
            project_root / '.autocoderignore',
            project_root / '.auto-coder' / '.autocoderignore'
        ]

        for ignore_file in ignore_file_paths:
            if ignore_file.is_file():
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    ignore_patterns = f.read().splitlines()
                self._ignore_file_path = str(ignore_file)
                break

        # 添加默认排除目录
        ignore_patterns.extend(DEFAULT_EXCLUDES)

        self._spec = pathspec.PathSpec.from_lines('gitwildmatch', ignore_patterns)

    def should_ignore(self, path: str) -> bool:
        """判断指定路径是否应该被忽略"""
        rel_path = os.path.relpath(path, self._project_root)
        # 标准化分隔符
        rel_path = rel_path.replace(os.sep, '/')
        return self._spec.match_file(rel_path)


# 对外提供的单例管理器
_ignore_manager = None

def should_ignore(path: str, project_root: Optional[str] = None) -> bool:
    """判断指定路径是否应该被忽略"""
    global _ignore_manager
    if _ignore_manager is None:
        _ignore_manager = IgnoreFileManager(project_root=project_root)
    return _ignore_manager.should_ignore(path)
