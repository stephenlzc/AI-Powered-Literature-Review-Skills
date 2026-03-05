#!/usr/bin/env python3
"""
路径配置管理器

支持：
- 从环境变量加载配置
- 从配置文件加载
- 动态路径解析
- 变量替换
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Union
from dataclasses import dataclass


@dataclass
class PathConfig:
    """
    路径配置类
    
    所有路径都支持：
    1. 环境变量替换: ${VAR_NAME} 或 ${VAR_NAME:-default}
    2. 模板变量替换: {base_dir}, {sessions_dir}, {session_id}
    """
    
    # 基础路径
    base_output_dir: Path
    sessions_dir: Path
    cache_dir: Path
    temp_dir: Path
    
    # 子目录结构
    pdfs_dir: Path
    metadata_dir: Path
    checkpoints_dir: Path
    results_dir: Path
    
    @classmethod
    def from_env(cls, env_prefix: str = "LIT_SURVEY") -> "PathConfig":
        """
        从环境变量加载配置
        
        Args:
            env_prefix: 环境变量前缀，默认为 "LIT_SURVEY"
        
        Returns:
            PathConfig实例
        """
        # 基础路径
        base_dir = Path(
            os.getenv(f"{env_prefix}_BASE_DIR", "./literature-survey-output")
        ).resolve()
        
        sessions_dir = Path(
            os.getenv(f"{env_prefix}_SESSIONS_DIR", base_dir / "sessions")
        )
        cache_dir = Path(
            os.getenv(f"{env_prefix}_CACHE_DIR", base_dir / ".cache")
        )
        temp_dir = Path(
            os.getenv(f"{env_prefix}_TEMP_DIR", base_dir / ".temp")
        )
        
        return cls(
            base_output_dir=base_dir,
            sessions_dir=sessions_dir,
            cache_dir=cache_dir,
            temp_dir=temp_dir,
            pdfs_dir=sessions_dir / "pdfs",
            metadata_dir=sessions_dir / "metadata",
            checkpoints_dir=sessions_dir / "checkpoints",
            results_dir=sessions_dir / "results"
        )
    
    @classmethod
    def from_config_file(cls, config_path: Union[str, Path]) -> "PathConfig":
        """从配置文件加载"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        if config_path.suffix in ['.yaml', '.yml']:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        paths = data.get("paths", {})
        base_dir_str = paths.get("base_dir", "./literature-survey-output")
        base_dir = Path(cls._expand_env_vars(base_dir_str)).resolve()
        
        return cls(
            base_output_dir=base_dir,
            sessions_dir=cls._resolve_path(paths.get("sessions_dir"), base_dir / "sessions", base_dir),
            cache_dir=cls._resolve_path(paths.get("cache_dir"), base_dir / ".cache", base_dir),
            temp_dir=cls._resolve_path(paths.get("temp_dir"), base_dir / ".temp", base_dir),
            pdfs_dir=cls._resolve_path(paths.get("pdfs_dir"), base_dir / "sessions" / "pdfs", base_dir),
            metadata_dir=cls._resolve_path(paths.get("metadata_dir"), base_dir / "sessions" / "metadata", base_dir),
            checkpoints_dir=cls._resolve_path(paths.get("checkpoints_dir"), base_dir / "sessions" / "checkpoints", base_dir),
            results_dir=cls._resolve_path(paths.get("results_dir"), base_dir / "sessions" / "results", base_dir)
        )
    
    @staticmethod
    def _expand_env_vars(value: str) -> str:
        """展开环境变量，支持 ${VAR} 和 ${VAR:-default} 语法"""
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_expr = match.group(1)
            if ':-' in var_expr:
                var_name, default = var_expr.split(':-', 1)
                return os.getenv(var_name, default)
            else:
                return os.getenv(var_expr, '')
        
        return re.sub(pattern, replace_var, value)
    
    @staticmethod
    def _resolve_path(path_value, default_path: Path, base_dir: Path) -> Path:
        """解析路径值"""
        if path_value is None:
            return default_path
        
        expanded = PathConfig._expand_env_vars(str(path_value))
        expanded = expanded.replace("{base_dir}", str(base_dir))
        return Path(expanded)
    
    def ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.sessions_dir,
            self.cache_dir,
            self.temp_dir,
            self.pdfs_dir,
            self.metadata_dir,
            self.checkpoints_dir,
            self.results_dir
        ]
        
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_session_dir(self, session_id: str) -> Path:
        """获取特定会话的目录"""
        return self.sessions_dir / session_id
    
    def resolve_path(self, path_template: str, session_id: Optional[str] = None) -> Path:
        """
        解析路径模板
        
        支持的特殊变量：
        - {base_dir}: 基础输出目录
        - {sessions_dir}: 会话目录
        - {session_id}: 当前会话ID
        - {cache_dir}: 缓存目录
        - {temp_dir}: 临时目录
        """
        resolved = self._expand_env_vars(path_template)
        
        replacements = {
            "{base_dir}": str(self.base_output_dir),
            "{sessions_dir}": str(self.sessions_dir),
            "{cache_dir}": str(self.cache_dir),
            "{temp_dir}": str(self.temp_dir),
            "{pdfs_dir}": str(self.pdfs_dir),
            "{metadata_dir}": str(self.metadata_dir),
            "{checkpoints_dir}": str(self.checkpoints_dir),
            "{results_dir}": str(self.results_dir),
        }
        
        if session_id:
            replacements["{session_id}"] = session_id
        
        for old, new in replacements.items():
            resolved = resolved.replace(old, new)
        
        return Path(resolved)
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            "base_output_dir": str(self.base_output_dir),
            "sessions_dir": str(self.sessions_dir),
            "cache_dir": str(self.cache_dir),
            "temp_dir": str(self.temp_dir),
            "pdfs_dir": str(self.pdfs_dir),
            "metadata_dir": str(self.metadata_dir),
            "checkpoints_dir": str(self.checkpoints_dir),
            "results_dir": str(self.results_dir),
        }


class RuntimePathResolver:
    """运行时路径解析器"""
    
    def __init__(self, config: PathConfig, session_id: Optional[str] = None):
        self.config = config
        self.session_id = session_id
    
    def resolve(self, template: str) -> Path:
        """解析路径模板"""
        return self.config.resolve_path(template, self.session_id)
    
    def get_output_path(self, filename: str, subdir: Optional[str] = None) -> Path:
        """获取输出文件路径"""
        if self.session_id:
            base = self.config.get_session_dir(self.session_id)
        else:
            base = self.config.results_dir
        
        if subdir:
            path = base / subdir / filename
        else:
            path = base / filename
        
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


def get_default_path_config() -> PathConfig:
    """获取默认路径配置"""
    return PathConfig.from_env()


def setup_paths(config: Optional[PathConfig] = None) -> PathConfig:
    """设置路径配置并创建必要的目录"""
    if config is None:
        config = PathConfig.from_env()
    
    config.ensure_directories()
    return config


if __name__ == "__main__":
    print("Testing PathConfig...")
    config = PathConfig.from_env()
    print("\nPaths from environment:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
    config.ensure_directories()
    print("\nDirectories created successfully!")
