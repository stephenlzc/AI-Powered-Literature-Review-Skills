#!/usr/bin/env python3
"""
统一数据模型定义

提供标准化的Paper、Author等数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum


class PaperType(Enum):
    """文献类型"""
    JOURNAL = "journal"
    CONFERENCE = "conference"
    PREPRINT = "preprint"
    BOOK = "book"
    THESIS = "thesis"
    REPORT = "report"
    PATENT = "patent"


class VerificationStatus(Enum):
    """验证状态"""
    PENDING = "pending"
    VERIFIED = "verified"
    SINGLE_SOURCE = "single_source"
    PREPRINT = "preprint"
    RETRACTED = "retracted"
    NOT_FOUND = "not_found"
    METADATA_MISMATCH = "metadata_mismatch"


@dataclass
class Author:
    """作者信息"""
    given_name: str = ""
    family_name: str = ""
    full_name: str = ""
    affiliation: str = ""
    orcid: str = ""
    
    def __post_init__(self):
        if not self.full_name and (self.given_name or self.family_name):
            self.full_name = f"{self.given_name} {self.family_name}".strip()
    
    def format_for_citation(self, lang: str = "en") -> str:
        """格式化为引用格式"""
        if lang == "zh":
            return self.full_name
        else:
            # 英文：姓, 名首字母
            if self.family_name and self.given_name:
                initials = "".join([p[0] + "." for p in self.given_name.split() if p])
                return f"{self.family_name} {initials}".strip()
            return self.full_name


@dataclass
class Venue:
    """发表 venue（期刊/会议）信息"""
    name: str = ""
    type: str = ""  # journal, conference, preprint
    publisher: str = ""
    issn: str = ""
    e_issn: str = ""
    impact_factor: float = 0.0
    quartile: str = ""  # Q1, Q2, Q3, Q4


@dataclass
class Paper:
    """
    统一文献数据模型
    
    支持多数据库的统一数据结构
    """
    # 标识
    id: str = ""  # 内部ID (E1, C1, etc.)
    paper_id: str = ""  # 源数据库ID
    doi: str = ""
    pmid: str = ""
    arxiv_id: str = ""
    
    # 基本元数据
    title: str = ""
    authors: List[Author] = field(default_factory=list)
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    
    # 发表信息
    venue: Venue = field(default_factory=Venue)
    year: Optional[int] = None
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publication_date: str = ""
    
    # 类型和语言
    paper_type: PaperType = PaperType.JOURNAL
    language: Literal["zh", "en", "other"] = "en"
    
    # 质量和指标
    citation_count: int = 0
    reference_count: int = 0
    influential_citation_count: int = 0
    
    # 开放获取
    is_oa: bool = False
    oa_status: str = ""  # gold, green, bronze, hybrid, closed
    oa_url: str = ""
    license: str = ""
    
    # PDF
    pdf_url: str = ""
    pdf_path: str = ""
    pdf_downloaded: bool = False
    
    # 验证
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_source: str = ""
    verification_date: Optional[datetime] = None
    
    # 来源
    source_db: str = ""  # cnki, semantic_scholar, pubmed, etc.
    source_url: str = ""
    
    # 引用
    cite_key: str = ""  # BibTeX引用密钥
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """后处理，自动设置语言等"""
        if not self.language and self.title:
            # 简单检测语言
            if any('\u4e00' <= char <= '\u9fff' for char in self.title):
                self.language = "zh"
            else:
                self.language = "en"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "doi": self.doi,
            "pmid": self.pmid,
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": [
                {
                    "given_name": a.given_name,
                    "family_name": a.family_name,
                    "full_name": a.full_name,
                    "affiliation": a.affiliation,
                    "orcid": a.orcid
                }
                for a in self.authors
            ],
            "abstract": self.abstract,
            "keywords": self.keywords,
            "venue": {
                "name": self.venue.name,
                "type": self.venue.type,
                "publisher": self.venue.publisher,
                "impact_factor": self.venue.impact_factor,
                "quartile": self.venue.quartile
            },
            "year": self.year,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "paper_type": self.paper_type.value,
            "language": self.language,
            "citation_count": self.citation_count,
            "is_oa": self.is_oa,
            "oa_status": self.oa_status,
            "pdf_url": self.pdf_url,
            "verification_status": self.verification_status.value,
            "source_db": self.source_db,
            "cite_key": self.cite_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Paper":
        """从字典创建"""
        authors = [
            Author(
                given_name=a.get("given_name", ""),
                family_name=a.get("family_name", ""),
                full_name=a.get("full_name", ""),
                affiliation=a.get("affiliation", ""),
                orcid=a.get("orcid", "")
            )
            for a in data.get("authors", [])
        ]
        
        venue_data = data.get("venue", {})
        venue = Venue(
            name=venue_data.get("name", ""),
            type=venue_data.get("type", ""),
            publisher=venue_data.get("publisher", ""),
            impact_factor=venue_data.get("impact_factor", 0.0),
            quartile=venue_data.get("quartile", "")
        )
        
        return cls(
            id=data.get("id", ""),
            paper_id=data.get("paper_id", ""),
            doi=data.get("doi", ""),
            pmid=data.get("pmid", ""),
            arxiv_id=data.get("arxiv_id", ""),
            title=data.get("title", ""),
            authors=authors,
            abstract=data.get("abstract", ""),
            keywords=data.get("keywords", []),
            venue=venue,
            year=data.get("year"),
            volume=data.get("volume", ""),
            issue=data.get("issue", ""),
            pages=data.get("pages", ""),
            paper_type=PaperType(data.get("paper_type", "journal")),
            language=data.get("language", "en"),
            citation_count=data.get("citation_count", 0),
            is_oa=data.get("is_oa", False),
            pdf_url=data.get("pdf_url", ""),
            verification_status=VerificationStatus(data.get("verification_status", "pending")),
            source_db=data.get("source_db", ""),
            cite_key=data.get("cite_key", "")
        )
    
    def get_first_author_surname(self) -> str:
        """获取第一作者姓氏"""
        if self.authors:
            return self.authors[0].family_name or self.authors[0].full_name.split()[-1]
        return "Unknown"
    
    def generate_cite_key(self) -> str:
        """生成BibTeX引用密钥"""
        if self.cite_key:
            return self.cite_key
        
        author = self.get_first_author_surname()
        year = self.year or "XXXX"
        
        # 提取标题前几个词
        title_words = self.title.split()[:3]
        title_part = "".join([w.capitalize() for w in title_words if w.isalnum()])
        
        self.cite_key = f"{author}{year}{title_part[:10]}"
        return self.cite_key


@dataclass
class PaperCollection:
    """文献集合"""
    papers: List[Paper] = field(default_factory=list)
    session_id: str = ""
    query: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_paper(self, paper: Paper):
        """添加文献"""
        self.papers.append(paper)
    
    def get_by_id(self, paper_id: str) -> Optional[Paper]:
        """通过ID获取文献"""
        for paper in self.papers:
            if paper.id == paper_id or paper.paper_id == paper_id:
                return paper
        return None
    
    def get_by_doi(self, doi: str) -> Optional[Paper]:
        """通过DOI获取文献"""
        for paper in self.papers:
            if paper.doi == doi:
                return paper
        return None
    
    def filter_by_status(self, status: VerificationStatus) -> List[Paper]:
        """按验证状态筛选"""
        return [p for p in self.papers if p.verification_status == status]
    
    def filter_by_year(self, start: int, end: int) -> List[Paper]:
        """按年份筛选"""
        return [p for p in self.papers if p.year and start <= p.year <= end]
    
    def filter_by_language(self, lang: str) -> List[Paper]:
        """按语言筛选"""
        return [p for p in self.papers if p.language == lang]
    
    def to_dict_list(self) -> List[Dict]:
        """转换为字典列表"""
        return [p.to_dict() for p in self.papers]
    
    def save_to_json(self, filepath: str):
        """保存为JSON"""
        import json
        data = {
            "session_id": self.session_id,
            "query": self.query,
            "created_at": self.created_at.isoformat(),
            "papers": self.to_dict_list()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_json(cls, filepath: str) -> "PaperCollection":
        """从JSON加载"""
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        collection = cls(
            session_id=data.get("session_id", ""),
            query=data.get("query", ""),
            created_at=datetime.fromisoformat(data.get("created_at"))
        )
        
        for paper_data in data.get("papers", []):
            collection.add_paper(Paper.from_dict(paper_data))
        
        return collection
