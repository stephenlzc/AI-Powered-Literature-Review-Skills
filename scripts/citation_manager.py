#!/usr/bin/env python3
"""
引用管理器 - 支持交叉引用和多种输出格式

特点：
- 支持GB/T 7714-2015格式
- 支持Word书签交叉引用
- 支持Markdown超链接
- 自动生成唯一ID
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class CitationStyle(Enum):
    """引用格式"""
    GB7714 = "gb7714"
    BIBTEX = "bibtex"
    APA = "apa"
    MLA = "mla"
    IEEE = "ieee"


class CrossRefFormat(Enum):
    """交叉引用格式"""
    BOOKMARK = "bookmark"      # Word书签
    HYPERLINK = "hyperlink"    # 超链接
    BOTH = "both"              # 两者都用
    NONE = "none"              # 不启用


@dataclass
class Author:
    """作者信息"""
    name: str = ""
    given_name: str = ""
    family_name: str = ""
    affiliation: str = ""
    orcid: str = ""
    
    def format_cn(self) -> str:
        """中文格式"""
        return self.name
    
    def format_en_short(self) -> str:
        """英文简写格式 (Smith J)"""
        if self.family_name and self.given_name:
            initials = ''.join([p[0] + '.' for p in self.given_name.split() if p])
            return f"{self.family_name} {initials}".strip()
        return self.name
    
    def format_en_full(self) -> str:
        """英文全格式"""
        if self.family_name and self.given_name:
            return f"{self.given_name} {self.family_name}".strip()
        return self.name


@dataclass
class Paper:
    """文献信息"""
    # 标识
    id: str = ""                    # 内部ID (C1, E1等)
    title: str = ""
    authors: List[Author] = field(default_factory=list)
    
    # 发表信息
    journal: str = ""
    year: int = 0
    volume: str = ""
    issue: str = ""
    pages: str = ""
    
    # 标识符
    doi: str = ""
    pmid: str = ""
    arxiv_id: str = ""
    
    # 元数据
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    language: str = "en"           # zh/en
    paper_type: str = "journal"    # journal/conference/book/thesis
    
    # 链接
    url: str = ""
    pdf_url: str = ""
    
    # 质量指标
    citation_count: int = 0
    impact_factor: float = 0.0
    
    # 附加信息
    notes: str = ""
    
    def get_first_author(self) -> Optional[Author]:
        """获取第一作者"""
        return self.authors[0] if self.authors else None
    
    def get_first_author_surname(self) -> str:
        """获取第一作者姓氏"""
        author = self.get_first_author()
        if author:
            if author.family_name:
                return author.family_name
            # 从name中提取
            parts = author.name.split()
            return parts[-1] if parts else "Unknown"
        return "Unknown"


@dataclass
class Citation:
    """引用实例"""
    paper_id: str
    context: str = ""           # 引用上下文
    page: str = ""              # 页码（如适用）
    note: str = ""              # 附加说明


class CitationManager:
    """
    引用管理器
    
    管理文献的引用编号、格式化和交叉引用
    """
    
    def __init__(self, style: CitationStyle = CitationStyle.GB7714, 
                 cross_ref: CrossRefFormat = CrossRefFormat.BOOKMARK):
        """
        初始化引用管理器
        
        Args:
            style: 引用格式
            cross_ref: 交叉引用格式
        """
        self.style = style
        self.cross_ref = cross_ref
        self.papers: Dict[str, Paper] = {}  # id -> Paper
        self.cn_counter = 0
        self.en_counter = 0
    
    def add_paper(self, paper: Paper, assign_id: bool = True) -> str:
        """
        添加文献
        
        Args:
            paper: 文献对象
            assign_id: 是否自动分配ID
        
        Returns:
            分配的ID
        """
        if assign_id and not paper.id:
            # 根据语言分配ID
            if paper.language == "zh":
                self.cn_counter += 1
                paper.id = f"C{self.cn_counter}"
            else:
                self.en_counter += 1
                paper.id = f"E{self.en_counter}"
        
        self.papers[paper.id] = paper
        return paper.id
    
    def add_papers(self, papers: List[Paper]) -> List[str]:
        """批量添加文献"""
        return [self.add_paper(p) for p in papers]
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        """获取文献"""
        return self.papers.get(paper_id)
    
    def format_citation(self, paper_ids: str or List[str], 
                        format_type: str = "inline") -> str:
        """
        格式化引用
        
        Args:
            paper_ids: 单个ID或ID列表
            format_type: 格式类型
                - inline: 行内引用 [C1] 或 [E1]
                - author_year: 作者-年份 (Smith, 2023)
                - bookmark: Word书签链接
                - link: Markdown链接
        
        Returns:
            格式化后的引用字符串
        """
        if isinstance(paper_ids, str):
            paper_ids = [paper_ids]
        
        if format_type == "inline":
            return self._format_inline(paper_ids)
        elif format_type == "author_year":
            return self._format_author_year(paper_ids)
        elif format_type == "bookmark":
            return self._format_bookmark(paper_ids)
        elif format_type == "link":
            return self._format_link(paper_ids)
        else:
            return self._format_inline(paper_ids)
    
    def _format_inline(self, paper_ids: List[str]) -> str:
        """行内编号格式 [C1,C2] 或 [C1-C3]"""
        if len(paper_ids) == 1:
            return f"[{paper_ids[0]}]"
        
        # 分离中英文
        cn_ids = sorted([p for p in paper_ids if p.startswith('C')])
        en_ids = sorted([p for p in paper_ids if p.startswith('E')])
        
        parts = []
        if cn_ids:
            parts.append(self._compress_ids(cn_ids))
        if en_ids:
            parts.append(self._compress_ids(en_ids))
        
        return '[' + ','.join(parts) + ']'
    
    def _format_author_year(self, paper_ids: List[str]) -> str:
        """作者-年份格式 (Smith et al., 2023)"""
        if len(paper_ids) == 1:
            paper = self.papers.get(paper_ids[0])
            if paper:
                surname = paper.get_first_author_surname()
                return f"({surname}, {paper.year})"
            return f"[{paper_ids[0]}]"
        
        # 多篇引用
        years = []
        for pid in paper_ids:
            paper = self.papers.get(pid)
            if paper:
                years.append(str(paper.year))
        
        if years:
            paper = self.papers.get(paper_ids[0])
            surname = paper.get_first_author_surname() if paper else "et al."
            return f"({surname} et al., {', '.join(years)})"
        
        return self._format_inline(paper_ids)
    
    def _format_bookmark(self, paper_ids: List[str]) -> str:
        """Word书签格式"""
        refs = []
        for pid in paper_ids:
            # Word书签链接格式
            ref = f'<a href="#ref_{pid}">[{pid}]</a>'
            refs.append(ref)
        
        if len(refs) == 1:
            return refs[0]
        return ', '.join(refs)
    
    def _format_link(self, paper_ids: List[str]) -> str:
        """Markdown链接格式"""
        refs = []
        for pid in paper_ids:
            paper = self.papers.get(pid)
            if paper and paper.url:
                ref = f"[[{pid}]]({paper.url})"
            else:
                ref = f"[{pid}]"
            refs.append(ref)
        
        if len(refs) == 1:
            return refs[0]
        return ', '.join(refs)
    
    def _compress_ids(self, ids: List[str]) -> str:
        """压缩连续ID [C1,C2,C3] -> [C1-C3]"""
        if not ids:
            return ""
        
        if len(ids) == 1:
            return ids[0]
        
        # 提取数字
        def extract_num(s):
            return int(re.search(r'\d+', s).group())
        
        nums = [extract_num(i) for i in ids]
        prefix = re.match(r'[A-Za-z]+', ids[0]).group()
        
        # 检查是否连续
        if nums == list(range(nums[0], nums[0] + len(nums))):
            return f"{prefix}{nums[0]}-{prefix}{nums[-1]}"
        
        return ','.join(ids)
    
    def generate_reference_list(self, output_format: str = "markdown") -> str:
        """
        生成参考文献列表
        
        Args:
            output_format: 输出格式 (markdown/html/docx/text)
        
        Returns:
            格式化后的参考文献列表
        """
        # 分离中英文文献
        cn_papers = [(pid, p) for pid, p in self.papers.items() if p.language == 'zh']
        en_papers = [(pid, p) for pid, p in self.papers.items() if p.language == 'en']
        
        # 排序
        cn_papers.sort(key=lambda x: int(re.search(r'\d+', x[0]).group()))
        en_papers.sort(key=lambda x: int(re.search(r'\d+', x[0]).group()))
        
        lines = []
        
        # 中文文献
        if cn_papers:
            if output_format == "markdown":
                lines.append("### 中文文献\n")
            for pid, paper in cn_papers:
                ref = self._format_reference_gb7714_cn(paper, output_format)
                lines.append(ref)
            lines.append("")
        
        # 英文文献
        if en_papers:
            if output_format == "markdown":
                lines.append("### 英文文献\n")
            for pid, paper in en_papers:
                ref = self._format_reference_gb7714_en(paper, output_format)
                lines.append(ref)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_reference_gb7714_cn(self, paper: Paper, output_format: str) -> str:
        """GB/T 7714-2015 中文格式"""
        # 格式化作者
        if len(paper.authors) <= 3:
            author_str = ', '.join([a.format_cn() for a in paper.authors])
        else:
            author_str = ', '.join([a.format_cn() for a in paper.authors[:3]]) + ', 等'
        
        # 类型标识
        type_map = {
            'journal': 'J',
            'conference': 'C',
            'book': 'M',
            'thesis': 'D'
        }
        type_id = type_map.get(paper.paper_type, 'J')
        
        # 基础格式
        ref = f"[{paper.id}] {author_str}. {paper.title}[{type_id}]. {paper.journal}"
        
        if paper.year:
            ref += f", {paper.year}"
        if paper.volume:
            ref += f", {paper.volume}"
            if paper.issue:
                ref += f"({paper.issue})"
        if paper.pages:
            ref += f": {paper.pages}"
        
        ref += "."
        
        if paper.doi:
            ref += f" DOI:{paper.doi}."
        
        # 根据输出格式调整
        if output_format == "html" or output_format == "docx_bookmark":
            # 添加书签锚点
            bookmark = f'<a name="ref_{paper.id}"></a>'
            ref = bookmark + ref
        
        return ref
    
    def _format_reference_gb7714_en(self, paper: Paper, output_format: str) -> str:
        """GB/T 7714-2015 英文格式"""
        # 格式化作者
        if len(paper.authors) <= 3:
            author_str = ', '.join([a.format_en_short() for a in paper.authors])
        else:
            author_str = ', '.join([a.format_en_short() for a in paper.authors[:3]]) + ', et al'
        
        # 类型标识
        type_map = {
            'journal': 'J',
            'conference': 'C',
            'book': 'M',
            'thesis': 'D'
        }
        type_id = type_map.get(paper.paper_type, 'J')
        
        # 基础格式
        ref = f"[{paper.id}] {author_str}. {paper.title}[{type_id}]. {paper.journal}"
        
        if paper.year:
            ref += f", {paper.year}"
        if paper.volume:
            if paper.issue:
                ref += f", {paper.volume}({paper.issue})"
            else:
                ref += f", {paper.volume}"
        if paper.pages:
            ref += f": {paper.pages}"
        
        ref += "."
        
        if paper.doi:
            ref += f" DOI:{paper.doi}."
        
        # 根据输出格式调整
        if output_format == "html" or output_format == "docx_bookmark":
            # 添加书签锚点
            bookmark = f'<a name="ref_{paper.id}"></a>'
            ref = bookmark + ref
        
        return ref
    
    def generate_bibtex(self) -> str:
        """生成BibTeX格式"""
        entries = []
        
        for pid, paper in self.papers.items():
            # 生成引用密钥
            cite_key = self._generate_bibtex_key(paper)
            
            # 类型映射
            type_map = {
                'journal': 'article',
                'conference': 'inproceedings',
                'book': 'book',
                'thesis': 'phdthesis'
            }
            entry_type = type_map.get(paper.paper_type, 'misc')
            
            # 作者
            author_str = ' and '.join([a.format_en_full() for a in paper.authors])
            
            lines = [f"@{entry_type}{{{cite_key}},"]
            lines.append(f"  author = {{{author_str}}},")
            lines.append(f"  title = {{{paper.title}}},")
            
            if paper.paper_type == 'journal':
                lines.append(f"  journal = {{{paper.journal}}},")
            elif paper.paper_type == 'conference':
                lines.append(f"  booktitle = {{{paper.journal}}},")
            
            if paper.year:
                lines.append(f"  year = {{{paper.year}}},")
            if paper.volume:
                lines.append(f"  volume = {{{paper.volume}}},")
            if paper.issue:
                lines.append(f"  number = {{{paper.issue}}},")
            if paper.pages:
                lines.append(f"  pages = {{{paper.pages}}},")
            if paper.doi:
                lines.append(f"  doi = {{{paper.doi}}},")
            
            lines.append("}")
            entries.append('\n'.join(lines))
        
        return '\n\n'.join(entries)
    
    def _generate_bibtex_key(self, paper: Paper) -> str:
        """生成BibTeX引用密钥"""
        surname = paper.get_first_author_surname()
        year = str(paper.year) if paper.year else "XXXX"
        
        # 提取标题关键词
        words = re.findall(r'\w+', paper.title)
        title_part = ''.join([w.capitalize() for w in words[:3] if len(w) > 3])
        
        return f"{surname}{year}{title_part[:15]}"
    
    def export_to_file(self, filepath: str, format_type: str = "markdown"):
        """
        导出到文件
        
        Args:
            filepath: 文件路径
            format_type: 格式类型
        """
        if format_type == "markdown":
            content = self.generate_reference_list("markdown")
        elif format_type == "bibtex":
            content = self.generate_bibtex()
        elif format_type == "json":
            content = json.dumps({
                pid: asdict(p) for pid, p in self.papers.items()
            }, ensure_ascii=False, indent=2)
        else:
            content = self.generate_reference_list(format_type)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        cn_count = sum(1 for p in self.papers.values() if p.language == 'zh')
        en_count = sum(1 for p in self.papers.values() if p.language == 'en')
        
        # 按年份统计
        year_dist = {}
        for p in self.papers.values():
            year = p.year
            if year:
                year_dist[year] = year_dist.get(year, 0) + 1
        
        # 按期刊统计
        journal_dist = {}
        for p in self.papers.values():
            j = p.journal
            if j:
                journal_dist[j] = journal_dist.get(j, 0) + 1
        
        return {
            "total": len(self.papers),
            "chinese": cn_count,
            "english": en_count,
            "year_distribution": year_dist,
            "top_journals": sorted(journal_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        }


# 便捷函数
def create_citation_manager(style: str = "gb7714", 
                            cross_ref: str = "bookmark") -> CitationManager:
    """
    创建引用管理器
    
    Args:
        style: 引用格式 (gb7714/bibtex/apa/mla/ieee)
        cross_ref: 交叉引用格式 (bookmark/hyperlink/both/none)
    
    Returns:
        CitationManager实例
    """
    style_enum = CitationStyle(style.lower())
    cross_ref_enum = CrossRefFormat(cross_ref.lower())
    return CitationManager(style_enum, cross_ref_enum)


if __name__ == "__main__":
    # 测试
    manager = CitationManager()
    
    # 添加测试文献
    paper1 = Paper(
        title="基于深度学习的医学图像诊断研究",
        authors=[Author(name="张三"), Author(name="李四")],
        journal="计算机学报",
        year=2023,
        volume="46",
        issue="5",
        pages="1023-1035",
        doi="10.xxxx",
        language="zh"
    )
    
    paper2 = Paper(
        title="Deep learning for image recognition",
        authors=[
            Author(name="Yann LeCun", given_name="Yann", family_name="LeCun"),
            Author(name="Yoshua Bengio", given_name="Yoshua", family_name="Bengio")
        ],
        journal="Nature",
        year=2015,
        volume="521",
        issue="7553",
        pages="436-444",
        doi="10.1038/nature14539",
        language="en"
    )
    
    manager.add_paper(paper1)
    manager.add_paper(paper2)
    
    print("行内引用:")
    print(f"  单篇: {manager.format_citation('C1')}")
    print(f"  多篇: {manager.format_citation(['C1', 'E1'])}")
    
    print("\n参考文献列表:")
    print(manager.generate_reference_list())
    
    print("\nBibTeX:")
    print(manager.generate_bibtex())
