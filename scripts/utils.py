#!/usr/bin/env python3
"""
工具函数集合

提供速率限制、重试机制、相似度计算等通用功能
"""

import time
import asyncio
import functools
from typing import Callable, Any, Optional
from difflib import SequenceMatcher


class RateLimiter:
    """
    速率限制器
    
    基于令牌桶算法的速率限制实现
    """
    
    def __init__(self, rate: float = 1.0, burst: int = 5):
        """
        初始化速率限制器
        
        Args:
            rate: 每秒允许的请求数
            burst: 突发容量
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """获取令牌"""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens < 1:
                # 需要等待
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class RetryPolicy:
    """
    重试策略
    
    实现指数退避重试机制
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_exceptions: tuple = (Exception,)
    ):
        """
        初始化重试策略
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟（秒）
            max_delay: 最大延迟（秒）
            exponential_base: 指数基数
            retryable_exceptions: 可重试的异常类型
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行带重试的函数
        
        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数
        
        Returns:
            函数执行结果
        
        Raises:
            最后一次重试的异常
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except self.retryable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                else:
                    print(f"All {self.max_retries} attempts failed.")
        
        raise last_exception


def rate_limited(rate: float = 1.0):
    """
    速率限制装饰器
    
    Args:
        rate: 每秒允许的调用次数
    
    Example:
        @rate_limited(rate=3.0)  # 每秒最多3次调用
        async def fetch_data():
            pass
    """
    limiter = RateLimiter(rate=rate)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with limiter:
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    retryable_exceptions: tuple = (Exception,)
):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟
        retryable_exceptions: 可重试的异常
    
    Example:
        @with_retry(max_retries=5, base_delay=2.0)
        async def api_call():
            pass
    """
    policy = RetryPolicy(
        max_retries=max_retries,
        base_delay=base_delay,
        retryable_exceptions=retryable_exceptions
    )
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await policy.execute(func, *args, **kwargs)
        return wrapper
    return decorator


def calculate_similarity(str1: str, str2: str) -> float:
    """
    计算两个字符串的相似度
    
    使用SequenceMatcher算法
    
    Args:
        str1: 第一个字符串
        str2: 第二个字符串
    
    Returns:
        相似度（0.0 - 1.0）
    """
    if not str1 or not str2:
        return 0.0
    
    # 标准化处理
    s1 = str1.lower().strip()
    s2 = str2.lower().strip()
    
    return SequenceMatcher(None, s1, s2).ratio()


def normalize_doi(doi: str) -> str:
    """
    标准化DOI
    
    移除前缀，统一格式
    
    Args:
        doi: 原始DOI
    
    Returns:
        标准化后的DOI
    """
    if not doi:
        return ""
    
    # 移除URL前缀
    doi = doi.replace("https://doi.org/", "")
    doi = doi.replace("http://doi.org/", "")
    doi = doi.replace("doi.org/", "")
    doi = doi.replace("DOI:", "")
    doi = doi.replace("doi:", "")
    
    return doi.strip().lower()


def format_author_name(name: str, lang: str = "en") -> str:
    """
    格式化作者姓名
    
    Args:
        name: 原始姓名
        lang: 语言（zh/en）
    
    Returns:
        格式化后的姓名
    """
    name = name.strip()
    
    if lang == "zh":
        # 中文姓名保持原样
        return name
    else:
        # 英文姓名：处理各种格式
        parts = name.split()
        if len(parts) >= 2:
            # 假设最后一个是姓
            surname = parts[-1]
            given = " ".join(parts[:-1])
            initials = "".join([p[0] + "." for p in given.split() if p])
            return f"{surname} {initials}".strip()
        return name


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


class ProgressTracker:
    """
    进度追踪器
    """
    
    def __init__(self, total: int, desc: str = "Processing"):
        """
        初始化进度追踪器
        
        Args:
            total: 总任务数
            desc: 描述
        """
        self.total = total
        self.current = 0
        self.desc = desc
        self.start_time = time.time()
    
    def update(self, n: int = 1):
        """更新进度"""
        self.current += n
        self._print_progress()
    
    def _print_progress(self):
        """打印进度"""
        if self.total == 0:
            return
        
        percent = self.current / self.total * 100
        elapsed = time.time() - self.start_time
        
        if self.current > 0:
            eta = elapsed / self.current * (self.total - self.current)
            eta_str = f"ETA: {eta:.0f}s"
        else:
            eta_str = "ETA: --"
        
        print(f"\r{self.desc}: {self.current}/{self.total} ({percent:.1f}%) {eta_str}", end="", flush=True)
    
    def finish(self):
        """完成"""
        self.current = self.total
        self._print_progress()
        print()  # 换行


# 数据库速率限制配置
DATABASE_RATE_LIMITS = {
    "semantic_scholar": 100 / 300,  # 100 per 5 minutes
    "pubmed": 3.0,  # 3 per second
    "crossref": 1.0,  # 1 per second (polite)
    "arxiv": 1.0,  # 1 per second
    "openalex": 10.0,  # 10 per second
    "ieee": 0.5,  # 慢一些
    "cnki": 0.2,  # 人工操作，非常慢
}


def get_rate_limit(database: str) -> float:
    """
    获取数据库的速率限制
    
    Args:
        database: 数据库名称
    
    Returns:
        每秒请求数
    """
    return DATABASE_RATE_LIMITS.get(database.lower(), 1.0)
