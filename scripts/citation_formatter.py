#!/usr/bin/env python3
"""
引用格式化工具（增强版）

支持：
- GB/T 7714-2015 格式
- BibTeX 格式（含 Better BibTeX）
- 自动语言检测
- 多种文献类型
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class CitationFormat:
    """引用格式配置"""
    style: str  # gb7714, bibtex, apa, mla
    language: str  # zh, en, auto
    include_doi: bool = True
    include_url: bool = False


class CitationFormatter:
    """
    增强版引用格式化器
    
    支持多种引用格式和文献类型
    """
    
    # 文献类型标识映射
    TYPE_MAP = {
        "journal": "J",
        "book": "M",
        "conference": "C",
        "thesis": "D",
        "report": "R",
        "patent": "P",
        "standard": "S",
        "online": "EB",
        "preprint": "Preprint"
    }
    
    def __init__(self, config: Optional[CitationFormat] = None):
        """
        初始化格式化器
        
        Args:
            config: 格式配置
        """
        self.config = config or CitationFormat(style="gb7714", language="auto")
    
    def format(self, paper: Dict, index: str) -> str:
        """
        格式化单篇文献
        
        Args:
            paper: 文献元数据字典
            index: 文献编号（如 C1, E1）
        
        Returns:
            格式化后的引用字符串
        """
        # 检测语言
        lang = self._detect_language(paper)
        
        # 根据格式类型选择格式化方法
        if self.config.style == "gb7714":
            return self._format_gb7714(paper, index, lang)
        elif self.config.style == "bibtex":
            return self._format_bibtex(paper, index, lang)
        elif self.config.style == "apa":
            return self._format_apa(paper, index, lang)
        else:
            return self._format_gb7714(paper, index, lang)
    
    def _detect_language(self, paper: Dict) -> str:
        """检测文献语言"""
        if self.config.language != "auto":
            return self.config.language
        
        title = paper.get("title", "")
        # 简单检测中文字符
        if any('\u4e00' <= char <= '\u9fff' for char in title):
            return "zh"
        return "en"
    
    def _format_gb7714(self, paper: Dict, index: str, lang: str) -> str:
        """
        格式化为 GB/T 7714-2015 格式
        """
        paper_type = paper.get("type", "journal")
        type_code = self.TYPE_MAP.get(paper_type, "J")
        
        if lang == "zh":
            return self._format_gb7714_zh(paper, index, type_code)
        else:
            return self._format_gb7714_en(paper, index, type_code)
    
    def _format_gb7714_zh(self, paper: Dict, index: str, type_code: str) -> str:
        """GB/T 7714-2015 中文格式"""
        authors = self._format_authors_zh(paper.get("authors", []))
        title = paper.get("title", "")
        journal = paper.get("journal", "")
        year = paper.get("year", "")
        volume = paper.get("volume", "")
        issue = paper.get("issue", "")
        pages = paper.get("pages", "")
        doi = paper.get("doi", "")
        
        # 构建引用
        citation = f"[{index}] {authors}. {title}[{type_code}]. {journal}"
        
        if year:
            citation += f", {year}"
        if volume:
            citation += f", {volume}"
            if issue:
                citation += f"({issue})"
        if pages:
            citation += f": {pages}"
        
        citation += "."
        
        if doi and self.config.include_doi:
            citation += f" DOI:{doi}."
        
        return citation
    
    def _format_gb7714_en(self, paper: Dict, index: str, type_code: str) -> str:
        """GB/T 7714-2015 英文格式"""
        authors = self._format_authors_en(paper.get("authors", []))
        title = paper.get("title", "")
        journal = paper.get("journal", "")
        year = paper.get("year", "")
        volume = paper.get("volume", "")
        issue = paper.get("issue", "")
        pages = paper.get("pages", "")
        doi = paper.get("doi", "")
        
        # 构建引用
        citation = f"[{index}] {authors}. {title}[{type_code}]. {journal}"
        
        if year:
            citation += f", {year}"
        if volume:
            if issue:
                citation += f", {volume}({issue})"
            else:
                citation += f", {volume}"
        if pages:
            citation += f": {pages}"
        
        citation += "."
        
        if doi and self.config.include_doi:
            citation += f" DOI:{doi}."
        
        return citation
    
    def _format_authors_zh(self, authors: List) -> str:
        """格式化中文作者"""
        if not authors:
            return "佚名"
        
        # 处理字符串格式的作者
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",")]
        
        # 取前3位作者
        if len(authors) <= 3:
            return ", ".join(authors)
        else:
            return ", ".join(authors[:3]) + ", 等"
    
    def _format_authors_en(self, authors: List) -> str:
        """格式化英文作者"""
        if not authors:
            return "Anonymous"
        
        # 处理字符串格式的作者
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",")]
        
        formatted = []
        for author in authors:
            if isinstance(author, dict):
                name = author.get("name", "")
            else:
                name = str(author)
            
            # 处理姓名格式
            parts = name.strip().split()
            if len(parts) >= 2:
                # 假设最后一部分是姓
                surname = parts[-1]
                initials = "".join([p[0] + "." for p in parts[:-1] if p])
                formatted.append(f"{surname} {initials}".strip())
            else:
                formatted.append(name)
        
        # 取前3位作者
        if len(formatted) <= 3:
            return ", ".join(formatted)
        else:
            return ", ".join(formatted[:3]) + ", et al."
    
    def _format_bibtex(self, paper: Dict, index: str, lang: str) -> str:
        """
        格式化为 BibTeX 格式
        
        使用 Better BibTeX 风格的引用密钥
        """
        # 生成引用密钥
        cite_key = self._generate_cite_key(paper)
        
        # 确定条目类型
        paper_type = paper.get("type", "journal")
        bibtex_type = self._get_bibtex_type(paper_type)
        
        # 构建BibTeX条目
        lines = [f"@{bibtex_type}{{{cite_key}},"]
        
        # 添加字段
        fields = self._build_bibtex_fields(paper, lang)
        for key, value in fields.items():
            if value:
                lines.append(f"  {key} = {{{value}}},")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_cite_key(self, paper: Dict) -> str:
        """
        生成 Better BibTeX 风格的引用密钥
        
        格式: AuthorYearTitle (如 LeCun2015Deep)
        """
        authors = paper.get("authors", [])
        year = paper.get("year", "")
        title = paper.get("title", "")
        
        # 获取第一作者姓氏
        if authors:
            if isinstance(authors[0], dict):
                first_author = authors[0].get("name", "")
            else:
                first_author = str(authors[0])
            
            # 提取姓氏
            surname = first_author.split()[-1] if " " in first_author else first_author
            surname = re.sub(r'[^\w]', '', surname)
        else:
            surname = "Unknown"
        
        # 提取标题关键词
        title_words = re.findall(r'\w+', title)
        title_part = "".join([w.capitalize() for w in title_words[:3] if len(w) > 3])
        
        return f"{surname}{year}{title_part}" if year else f"{surname}{title_part}"
    
    def _get_bibtex_type(self, paper_type: str) -> str:
        """转换为BibTeX条目类型"""
        mapping = {
            "journal": "article",
            "book": "book",
            "conference": "inproceedings",
            "thesis": "phdthesis",
            "report": "techreport",
            "preprint": "unpublished"
        }
        return mapping.get(paper_type, "misc")
    
    def _build_bibtex_fields(self, paper: Dict, lang: str) -> Dict[str, str]:
        """构建BibTeX字段"""
        fields = {}
        
        # 作者
        authors = paper.get("authors", [])
        if authors:
            if isinstance(authors[0], dict):
                author_list = [a.get("name", "") for a in authors]
            else:
                author_list = authors
            fields["author"] = " and ".join(author_list)
        
        # 标题
        fields["title"] = paper.get("title", "")
        
        # 期刊/会议
        if paper.get("type") == "journal":
            fields["journal"] = paper.get("journal", "")
        elif paper.get("type") == "conference":
            fields["booktitle"] = paper.get("journal", "")
        
        # 年份
        if paper.get("year"):
            fields["year"] = str(paper["year"])
        
        # 卷号、期号、页码
        if paper.get("volume"):
            fields["volume"] = paper["volume"]
        if paper.get("issue"):
            fields["number"] = paper["issue"]
        if paper.get("pages"):
            fields["pages"] = paper["pages"]
        
        # DOI
        if paper.get("doi") and self.config.include_doi:
            fields["doi"] = paper["doi"]
        
        # 摘要
        if paper.get("abstract"):
            fields["abstract"] = paper["abstract"]
        
        return fields
    
    def _format_apa(self, paper: Dict, index: str, lang: str) -> str:
        """APA格式（简化版）"""
        authors = self._format_authors_en(paper.get("authors", []))
        year = paper.get("year", "n.d.")
        title = paper.get("title", "")
        journal = paper.get("journal", "")
        
        citation = f"{authors} ({year}). {title}. {journal}"
        
        if paper.get("volume"):
            citation += f", {paper['volume']}"
            if paper.get("issue"):
                citation += f"({paper['issue']})"
        
        if paper.get("pages"):
            citation += f", {paper['pages']}"
        
        citation += "."
        
        if paper.get("doi"):
            citation += f" https://doi.org/{paper['doi']}"
        
        return citation
    
    def format_list(self, papers: List[Dict], prefix: str = "") -> List[str]:
        """
        格式化文献列表
        
        Args:
            papers: 文献元数据列表
            prefix: 编号前缀（如 C、E）
        
        Returns:
            格式化后的引用列表
        """
        citations = []
        for i, paper in enumerate(papers, 1):
            index = f"{prefix}{i}" if prefix else str(i)
            citation = self.format(paper, index)
            citations.append(citation)
        return citations
    
    def format_bibliography(self, papers_zh: List[Dict], papers_en: List[Dict]) -> str:
        """
        格式化完整的参考文献列表（分中英文）
        
        Args:
            papers_zh: 中文文献列表
            papers_en: 英文文献列表
        
        Returns:
            完整的参考文献字符串
        """
        lines = ["## 参考文献", ""]
        
        # 中文文献
        if papers_zh:
            lines.append("### 中文文献")
            lines.append("")
            for i, paper in enumerate(papers_zh, 1):
                citation = self.format(paper, f"C{i}")
                lines.append(citation)
            lines.append("")
        
        # 英文文献
        if papers_en:
            lines.append("### 英文文献")
            lines.append("")
            for i, paper in enumerate(papers_en, 1):
                citation = self.format(paper, f"E{i}")
                lines.append(citation)
            lines.append("")
        
        return "\n".join(lines)


# 便捷的函数接口
def format_citation(paper: Dict, index: str, style: str = "gb7714", lang: str = "auto") -> str:
    """
    便捷函数：格式化单篇文献
    
    Args:
        paper: 文献元数据
        index: 编号
        style: 格式（gb7714/bibtex/apa）
        lang: 语言
    
    Returns:
        格式化后的引用
    """
    config = CitationFormat(style=style, language=lang)
    formatter = CitationFormatter(config)
    return formatter.format(paper, index)


def format_reference_list(papers: List[Dict], prefix: str = "", style: str = "gb7714") -> List[str]:
    """
    便捷函数：格式化文献列表
    
    Args:
        papers: 文献列表
        prefix: 编号前缀
        style: 格式
    
    Returns:
        格式化后的引用列表
    """
    config = CitationFormat(style=style, language="auto")
    formatter = CitationFormatter(config)
    return formatter.format_list(papers, prefix)


if __name__ == "__main__":
    # 测试示例
    test_papers = [
        {
            "title": "基于深度学习的图像识别研究",
            "authors": ["张三", "李四", "王五"],
            "journal": "计算机学报",
            "year": 2023,
            "volume": "46",
            "issue": "5",
            "pages": "1023-1035",
            "doi": "10.xxxx",
            "type": "journal"
        },
        {
            "title": "Deep learning for image recognition",
            "authors": ["John Smith", "Alice Johnson", "Bob Williams", "Carol Brown"],
            "journal": "Nature",
            "year": 2023,
            "volume": "123",
            "issue": "4",
            "pages": "567-580",
            "doi": "10.xxxx",
            "type": "journal"
        }
    ]
    
    formatter = CitationFormatter()
    
    print("=== GB/T 7714-2015 格式 ===\n")
    for i, paper in enumerate(test_papers, 1):
        lang = "zh" if i == 1 else "en"
        prefix = "C" if i == 1 else "E"
        print(formatter.format(paper, f"{prefix}1"))
        print()
    
    print("\n=== BibTeX 格式 ===\n")
    config = CitationFormat(style="bibtex", language="auto")
    bibtex_formatter = CitationFormatter(config)
    for i, paper in enumerate(test_papers, 1):
        print(bibtex_formatter.format(paper, str(i)))
        print()
