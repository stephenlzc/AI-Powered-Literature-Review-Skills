#!/usr/bin/env python3
"""
配置管理器 - 支持环境变量、配置文件和用户输入

特点：
- 支持YAML配置文件
- 环境变量覆盖
- 运行时用户输入
- 动态路径解析
"""

import os
import re
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PathConfig:
    """路径配置"""
    base_dir: str
    output_dir: str
    temp_dir: str
    logs_dir: str
    cache_dir: str
    filenames: Dict[str, str]


class ConfigManager:
    """
    配置管理器
    
    管理应用的配置，支持多级配置覆盖：
    1. 默认配置 (代码中定义)
    2. 配置文件 (config.yaml)
    3. 环境变量
    4. 运行时用户输入 (优先级最高)
    """
    
    # 变量占位符模式: {VAR_NAME}
    VAR_PATTERN = re.compile(r'\{(\w+)\}')
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 env_prefix: str = "LIT_SURVEY"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认查找 ./config.yaml
            env_prefix: 环境变量前缀
        """
        self.env_prefix = env_prefix
        self.config_path = config_path or self._find_config_file()
        self.config: Dict[str, Any] = {}
        self.runtime_vars: Dict[str, str] = {}
        
        # 加载配置
        self._load_defaults()
        self._load_config_file()
        self._load_env_vars()
    
    def _find_config_file(self) -> str:
        """查找配置文件"""
        # 按优先级查找
        possible_paths = [
            "./config.yaml",
            "./config.yml",
            "~/.literature-survey/config.yaml",
            "/etc/literature-survey/config.yaml"
        ]
        
        for path in possible_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                return str(expanded_path)
        
        # 默认使用当前目录
        return "./config.yaml"
    
    def _load_defaults(self):
        """加载默认配置"""
        self.config = {
            "paths": {
                "base_dir": "./sessions/{DATE}_{SESSION_ID}",
                "output_dir": "{base_dir}/output",
                "temp_dir": "{base_dir}/temp",
                "logs_dir": "{base_dir}/logs",
                "cache_dir": "./.cache",
                "filenames": {
                    "keywords": "keywords.json",
                    "search_results": "raw_results.json",
                    "unique_papers": "papers.json",
                    "citations": "citations.json",
                    "outline": "outline.json",
                    "draft": "draft.md",
                    "final": "文献综述_{TOPIC}_{DATE}.md"
                }
            },
            "search": {
                "defaults": {
                    "num_papers": 50,
                    "year_range": 5,
                    "language": "both"
                }
            },
            "llm": {
                "models": {
                    "keyword_extractor": {
                        "provider": "openai",
                        "model": "gpt-4o-mini"
                    },
                    "writer": {
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-20241022"
                    }
                }
            }
        }
    
    def _load_config_file(self):
        """加载配置文件"""
        if not Path(self.config_path).exists():
            print(f"Config file not found: {self.config_path}, using defaults")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
            
            if file_config:
                self._deep_merge(self.config, file_config)
                print(f"Loaded config from: {self.config_path}")
        except Exception as e:
            print(f"Error loading config file: {e}, using defaults")
    
    def _load_env_vars(self):
        """加载环境变量"""
        # API Keys
        api_keys = {
            "OPENAI_API_KEY": ["llm", "api", "openai", "api_key"],
            "ANTHROPIC_API_KEY": ["llm", "api", "anthropic", "api_key"],
            "EXA_API_KEY": ["databases", "exa", "api_key"],
            "SEMANTIC_SCHOLAR_API_KEY": ["databases", "semantic_scholar", "api_key"],
        }
        
        for env_var, config_path in api_keys.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(self.config, config_path, value)
        
        # 自定义环境变量 (LIT_SURVEY_*)
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix + "_"):
                config_key = key[len(self.env_prefix) + 1:].lower()
                self._set_nested_value(self.config, config_key.split("_"), value)
    
    def _deep_merge(self, base: Dict, override: Dict):
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _set_nested_value(self, d: Dict, path: List[str], value: Any):
        """设置嵌套字典值"""
        for key in path[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        d[path[-1]] = value
    
    def _get_nested_value(self, d: Dict, path: str, default: Any = None) -> Any:
        """获取嵌套字典值"""
        keys = path.split(".")
        for key in keys:
            if isinstance(d, dict) and key in d:
                d = d[key]
            else:
                return default
        return d
    
    def set_runtime_var(self, key: str, value: str):
        """
        设置运行时变量
        
        Args:
            key: 变量名
            value: 变量值
        """
        self.runtime_vars[key] = value
    
    def set_runtime_vars(self, vars_dict: Dict[str, str]):
        """批量设置运行时变量"""
        self.runtime_vars.update(vars_dict)
    
    def resolve_path(self, path_template: str, **extra_vars) -> str:
        """
        解析路径模板
        
        支持的变量:
        - {PROJECT_ROOT}: 项目根目录
        - {SESSION_ID}: 会话ID
        - {DATE}: 当前日期 (YYYYMMDD)
        - {TOPIC}: 研究主题（清理为文件名安全格式）
        - 以及配置中定义的其他变量
        
        Args:
            path_template: 路径模板
            **extra_vars: 额外变量
        
        Returns:
            解析后的路径
        """
        # 收集所有可用变量
        vars_dict = {}
        
        # 内置变量
        vars_dict["PROJECT_ROOT"] = str(Path(__file__).parent.parent.absolute())
        vars_dict["DATE"] = datetime.now().strftime("%Y%m%d")
        
        # 运行时变量
        vars_dict.update(self.runtime_vars)
        
        # 额外变量
        vars_dict.update(extra_vars)
        
        # 递归解析（支持变量嵌套）
        max_iterations = 10
        result = path_template
        
        for _ in range(max_iterations):
            new_result = self.VAR_PATTERN.sub(
                lambda m: vars_dict.get(m.group(1), m.group(0)),
                result
            )
            if new_result == result:
                break
            result = new_result
        
        # 清理路径
        result = result.replace("//", "/")
        
        # 如果是相对路径，基于项目根目录解析
        if not result.startswith("/") and not result.startswith("~"):
            result = os.path.join(vars_dict.get("PROJECT_ROOT", "."), result)
        
        # 展开用户目录
        result = os.path.expanduser(result)
        
        return result
    
    def get_path(self, path_name: str, **extra_vars) -> str:
        """
        获取解析后的路径
        
        Args:
            path_name: 路径名称 (如 "base_dir", "output_dir")
            **extra_vars: 额外变量
        
        Returns:
            解析后的绝对路径
        """
        path_template = self._get_nested_value(self.config, f"paths.{path_name}")
        if path_template is None:
            raise ValueError(f"Path '{path_name}' not found in config")
        
        return self.resolve_path(path_template, **extra_vars)
    
    def get_filename(self, filename_key: str, **extra_vars) -> str:
        """
        获取解析后的文件名
        
        Args:
            filename_key: 文件名键 (如 "keywords", "final")
            **extra_vars: 额外变量
        
        Returns:
            解析后的文件名
        """
        filename_template = self._get_nested_value(
            self.config, 
            f"paths.filenames.{filename_key}"
        )
        if filename_template is None:
            raise ValueError(f"Filename '{filename_key}' not found in config")
        
        # 清理TOPIC变量，使其适合作为文件名
        if "TOPIC" in extra_vars:
            topic = extra_vars["TOPIC"]
            # 限制长度，移除非法字符
            topic = re.sub(r'[\\/*?:"<>|]', "_", topic)
            topic = topic[:30]  # 限制长度
            extra_vars["TOPIC"] = topic
        
        return self.resolve_path(filename_template, **extra_vars)
    
    def get_full_path(self, filename_key: str, **extra_vars) -> str:
        """
        获取完整路径（输出目录 + 文件名）
        
        Args:
            filename_key: 文件名键
            **extra_vars: 额外变量
        
        Returns:
            完整的文件路径
        """
        output_dir = self.get_path("output_dir", **extra_vars)
        filename = self.get_filename(filename_key, **extra_vars)
        
        # 如果文件名已经是绝对路径，直接返回
        if filename.startswith("/"):
            return filename
        
        return os.path.join(output_dir, os.path.basename(filename))
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，如 "search.defaults.num_papers"
            default: 默认值
        
        Returns:
            配置值
        """
        return self._get_nested_value(self.config, key_path, default)
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值
        
        Args:
            key_path: 配置键路径
            value: 值
        """
        keys = key_path.split(".")
        self._set_nested_value(self.config, keys, value)
    
    def create_directories(self, **extra_vars):
        """
        创建所有必要的目录
        
        Args:
            **extra_vars: 额外变量用于路径解析
        """
        dirs_to_create = [
            "base_dir",
            "output_dir", 
            "temp_dir",
            "logs_dir",
            "cache_dir"
        ]
        
        for dir_name in dirs_to_create:
            try:
                path = self.get_path(dir_name, **extra_vars)
                Path(path).mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {path}")
            except Exception as e:
                print(f"Warning: Could not create directory {dir_name}: {e}")
    
    def get_llm_config(self, task: str) -> Dict[str, Any]:
        """
        获取LLM配置
        
        Args:
            task: 任务名称 (如 "keyword_extractor", "writer")
        
        Returns:
            LLM配置字典
        """
        config = self.get(f"llm.models.{task}", {})
        
        # 添加API密钥
        provider = config.get("provider")
        if provider:
            api_key = self.get(f"llm.api.{provider}.api_key")
            if api_key:
                config["api_key"] = api_key
        
        return config
    
    def get_database_config(self, db_name: str) -> Dict[str, Any]:
        """
        获取数据库配置
        
        Args:
            db_name: 数据库名称
        
        Returns:
            数据库配置字典
        """
        config = self.get(f"databases.{db_name}", {})
        
        # 解析API密钥中的环境变量
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var, "")
        
        return config
    
    def interactive_setup(self):
        """
        交互式设置
        
        提示用户输入必要的配置
        """
        print("\n=== Literature Survey 配置设置 ===\n")
        
        # 检查API Keys
        api_keys = {
            "OPENAI_API_KEY": "OpenAI API Key (用于GPT-4o等模型)",
            "ANTHROPIC_API_KEY": "Anthropic API Key (用于Claude模型)",
            "EXA_API_KEY": "EXA API Key (用于文献搜索)",
        }
        
        for key, description in api_keys.items():
            current = os.getenv(key)
            if current:
                show = current[:10] + "..." + current[-4:] if len(current) > 20 else current
                print(f"✓ {key}: {show}")
            else:
                print(f"✗ {key}: 未设置 - {description}")
                value = input(f"  请输入 {key} (或直接回车跳过): ").strip()
                if value:
                    os.environ[key] = value
        
        # 输出路径设置
        print("\n--- 输出路径设置 ---")
        current_output = self.get_path("output_dir")
        print(f"当前输出路径: {current_output}")
        new_output = input("请输入新的输出路径 (或直接回车保持默认): ").strip()
        if new_output:
            self.set("paths.output_dir", new_output)
        
        # 会话ID
        session_id = input("\n请输入会话标识 (用于区分不同研究项目): ").strip()
        if session_id:
            self.set_runtime_var("SESSION_ID", session_id)
        
        print("\n✓ 配置完成\n")
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return self.config.copy()
    
    def save(self, filepath: Optional[str] = None):
        """
        保存配置到文件
        
        Args:
            filepath: 文件路径，默认覆盖原配置文件
        """
        path = filepath or self.config_path
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        print(f"Config saved to: {path}")


# 便捷函数
def load_config(config_path: Optional[str] = None,
                session_id: Optional[str] = None,
                topic: Optional[str] = None) -> ConfigManager:
    """
    加载配置
    
    Args:
        config_path: 配置文件路径
        session_id: 会话ID
        topic: 研究主题
    
    Returns:
        ConfigManager实例
    """
    config = ConfigManager(config_path)
    
    if session_id:
        config.set_runtime_var("SESSION_ID", session_id)
    
    if topic:
        config.set_runtime_var("TOPIC", topic)
    
    return config


if __name__ == "__main__":
    # 测试
    config = ConfigManager()
    
    # 设置运行时变量
    config.set_runtime_var("SESSION_ID", "test123")
    config.set_runtime_var("TOPIC", "深度学习医学图像")
    
    print("路径解析测试:")
    print(f"  base_dir: {config.get_path('base_dir')}")
    print(f"  output_dir: {config.get_path('output_dir')}")
    
    print("\n文件名解析测试:")
    print(f"  final: {config.get_filename('final')}")
    print(f"  full_path: {config.get_full_path('final')}")
    
    print("\n配置值测试:")
    print(f"  search.defaults.num_papers: {config.get('search.defaults.num_papers')}")
    
    # 交互式设置
    # config.interactive_setup()
