#!/usr/bin/env python3
"""
会话管理工具

功能：
- 会话创建和恢复
- 进度保存和检查点
- 中断续传支持
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class SessionCheckpoint:
    """检查点数据"""
    phase: int
    phase_name: str
    timestamp: str
    data: Dict[str, Any]
    version: str = "1.0"


@dataclass
class SessionMetadata:
    """会话元数据"""
    session_id: str
    query: str
    created_at: str
    updated_at: str
    status: str  # running, completed, interrupted, failed
    completed_phases: List[int]
    current_phase: int


class SessionManager:
    """
    会话管理器
    
    管理文献调研会话的生命周期，支持中断续传
    """
    
    def __init__(self, session_id: Optional[str] = None, base_dir: str = "./sessions"):
        """
        初始化会话管理器
        
        Args:
            session_id: 会话ID（如不指定则自动生成）
            base_dir: 会话基础目录
        """
        self.session_id = session_id or self._generate_session_id()
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / self.session_id
        self.checkpoint_dir = self.session_dir / "checkpoints"
        self.results_dir = self.session_dir / "results"
        
        # 确保目录存在
        self._ensure_directories()
        
        # 会话元数据
        self.metadata: Optional[SessionMetadata] = None
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        short_uuid = uuid.uuid4().hex[:8]
        return f"{timestamp}_{short_uuid}"
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
    
    def create_session(self, query: str) -> SessionMetadata:
        """
        创建新会话
        
        Args:
            query: 研究查询/标题
        
        Returns:
            会话元数据
        """
        now = datetime.now().isoformat()
        
        self.metadata = SessionMetadata(
            session_id=self.session_id,
            query=query,
            created_at=now,
            updated_at=now,
            status="running",
            completed_phases=[],
            current_phase=0
        )
        
        # 保存元数据
        self._save_metadata()
        
        # 创建会话日志
        self._create_session_log()
        
        return self.metadata
    
    def load_session(self) -> Optional[SessionMetadata]:
        """
        加载已有会话
        
        Returns:
            会话元数据，如果不存在则返回None
        """
        metadata_file = self.session_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.metadata = SessionMetadata(**data)
        return self.metadata
    
    def _save_metadata(self):
        """保存会话元数据"""
        if self.metadata:
            metadata_file = self.session_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.metadata), f, ensure_ascii=False, indent=2)
    
    def _create_session_log(self):
        """创建会话日志文件"""
        log_file = self.session_dir / "session_log.md"
        
        log_content = f"""# Session Log

**Session ID**: {self.session_id}  
**Query**: {self.metadata.query}  
**Created**: {self.metadata.created_at}  
**Status**: {self.metadata.status}

## Progress

| Phase | Name | Status | Time |
|-------|------|--------|------|
| 0 | Session Log | ✅ Completed | {self.metadata.created_at} |
| 1 | Query Analysis | ⏳ Pending | - |
| 2 | Parallel Search | ⏳ Pending | - |
| 3 | Deduplication | ⏳ Pending | - |
| 4 | Verification | ⏳ Pending | - |
| 5 | PDF Management | ⏳ Pending | - |
| 6 | Citation Export | ⏳ Pending | - |
| 7 | Synthesis | ⏳ Pending | - |

## Notes

"""
        
        log_file.write_text(log_content, encoding='utf-8')
    
    def save_checkpoint(self, phase: int, phase_name: str, data: Dict[str, Any]):
        """
        保存检查点
        
        Args:
            phase: 阶段编号
            phase_name: 阶段名称
            data: 阶段数据
        """
        checkpoint = SessionCheckpoint(
            phase=phase,
            phase_name=phase_name,
            timestamp=datetime.now().isoformat(),
            data=data
        )
        
        # 保存检查点文件
        checkpoint_file = self.checkpoint_dir / f"checkpoint_p{phase}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(checkpoint), f, ensure_ascii=False, indent=2)
        
        # 更新元数据
        if self.metadata:
            if phase not in self.metadata.completed_phases:
                self.metadata.completed_phases.append(phase)
            self.metadata.current_phase = phase
            self.metadata.updated_at = datetime.now().isoformat()
            self._save_metadata()
        
        # 更新日志
        self._update_log(phase, phase_name, "Completed")
        
        print(f"✓ Checkpoint saved: Phase {phase} - {phase_name}")
    
    def load_checkpoint(self, phase: int) -> Optional[SessionCheckpoint]:
        """
        加载检查点
        
        Args:
            phase: 阶段编号
        
        Returns:
            检查点数据，如果不存在则返回None
        """
        checkpoint_file = self.checkpoint_dir / f"checkpoint_p{phase}.json"
        
        if not checkpoint_file.exists():
            return None
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return SessionCheckpoint(**data)
    
    def get_last_completed_phase(self) -> int:
        """
        获取最后完成的阶段
        
        Returns:
            最后完成的阶段编号，如果没有则返回-1
        """
        if self.metadata and self.metadata.completed_phases:
            return max(self.metadata.completed_phases)
        
        # 检查文件系统
        phases = []
        for checkpoint_file in self.checkpoint_dir.glob("checkpoint_p*.json"):
            try:
                phase_num = int(checkpoint_file.stem.split("_p")[1])
                phases.append(phase_num)
            except (IndexError, ValueError):
                continue
        
        return max(phases) if phases else -1
    
    def _update_log(self, phase: int, phase_name: str, status: str):
        """更新会话日志"""
        log_file = self.session_dir / "session_log.md"
        
        if not log_file.exists():
            return
        
        content = log_file.read_text(encoding='utf-8')
        
        # 更新进度表
        # 简单替换，实际使用中可能需要更复杂的逻辑
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        old_status = f"| {phase} | {phase_name} | ⏳ Pending | - |"
        new_status = f"| {phase} | {phase_name} | ✅ {status} | {timestamp} |"
        
        content = content.replace(old_status, new_status)
        
        log_file.write_text(content, encoding='utf-8')
    
    def log_message(self, message: str, level: str = "INFO"):
        """
        记录日志消息
        
        Args:
            message: 消息内容
            level: 日志级别（INFO, WARNING, ERROR）
        """
        log_file = self.session_dir / "session_log.md"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n**[{timestamp}] [{level}]** {message}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def save_results(self, filename: str, data: Any, format: str = "json"):
        """
        保存结果文件
        
        Args:
            filename: 文件名（不含扩展名）
            data: 数据
            format: 格式（json, txt, md）
        """
        result_file = self.results_dir / f"{filename}.{format}"
        
        if format == "json":
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            result_file.write_text(str(data), encoding='utf-8')
    
    def complete_session(self, success: bool = True):
        """
        完成会话
        
        Args:
            success: 是否成功完成
        """
        if self.metadata:
            self.metadata.status = "completed" if success else "failed"
            self.metadata.updated_at = datetime.now().isoformat()
            self._save_metadata()
        
        status_str = "successfully" if success else "with errors"
        self.log_message(f"Session completed {status_str}", "INFO")
    
    def interrupt_session(self, reason: str = ""):
        """
        中断会话
        
        Args:
            reason: 中断原因
        """
        if self.metadata:
            self.metadata.status = "interrupted"
            self.metadata.updated_at = datetime.now().isoformat()
            self._save_metadata()
        
        self.log_message(f"Session interrupted: {reason}", "WARNING")


def create_resumable_session(
    query: str,
    session_id: Optional[str] = None,
    base_dir: str = "./sessions"
) -> tuple:
    """
    便捷函数：创建或恢复可恢复会话
    
    Args:
        query: 研究查询
        session_id: 指定会话ID（恢复现有会话）
        base_dir: 基础目录
    
    Returns:
        (SessionManager, SessionMetadata) 元组
    """
    manager = SessionManager(session_id=session_id, base_dir=base_dir)
    
    # 尝试加载现有会话
    metadata = manager.load_session()
    
    if metadata:
        print(f"Resuming existing session: {manager.session_id}")
        last_phase = manager.get_last_completed_phase()
        if last_phase >= 0:
            print(f"Last completed phase: {last_phase}")
    else:
        # 创建新会话
        metadata = manager.create_session(query)
        print(f"Created new session: {manager.session_id}")
    
    return manager, metadata


if __name__ == "__main__":
    # 测试示例
    print("=" * 70)
    print("Session Manager Test")
    print("=" * 70)
    
    # 创建新会话
    manager, metadata = create_resumable_session(
        query="基于深度学习的医学图像诊断研究"
    )
    
    print(f"\nSession ID: {metadata.session_id}")
    print(f"Query: {metadata.query}")
    print(f"Status: {metadata.status}")
    
    # 模拟保存检查点
    manager.save_checkpoint(
        phase=1,
        phase_name="Query Analysis",
        data={
            "keywords_zh": ["深度学习", "医学图像"],
            "keywords_en": ["deep learning", "medical imaging"],
            "search_queries": {
                "cnki": "SU=('深度学习'+'神经网络')*('医学图像'+'医学影像')",
                "pubmed": "(\"deep learning\"[Title/Abstract]) AND (\"medical imaging\"[Title/Abstract])"
            }
        }
    )
    
    # 模拟保存检查结果
    manager.save_checkpoint(
        phase=2,
        phase_name="Parallel Search",
        data={
            "total_found": 156,
            "cnki_results": 45,
            "semantic_scholar_results": 67,
            "pubmed_results": 44
        }
    )
    
    # 完成会话
    manager.complete_session(success=True)
    
    print("\n" + "=" * 70)
    print("Session completed!")
    print(f"Session directory: {manager.session_dir}")
