#!/usr/bin/env python3
"""
Zotero同步工具

功能：
- 导出为BibTeX格式
- 导出为RIS格式
- 导出为CSL JSON格式
- 生成导入指令
"""

from typing import List, Dict
from pathlib import Path
import json


def format_bibtex(paper: Dict, include_abstract: bool = True) -> str:
    """
    格式化为BibTeX条目
    
    Args:
        paper: 文献元数据
        include_abstract: 是否包含摘要
    
    Returns:
        BibTeX字符串
    """
    # 生成引用密钥
    cite_key = generate_cite_key(paper)
    
    # 确定条目类型
    paper_type = paper.get("type", "journal")
    entry_type = {
        "journal": "article",
        "book": "book",
        "conference": "inproceedings",
        "thesis": "phdthesis",
        "report": "techreport",
        "preprint": "unpublished"
    }.get(paper_type, "misc")
    
    lines = [f"@{entry_type}{{{cite_key}},"]
    
    # 作者
    authors = paper.get("authors", [])
    if authors:
        if isinstance(authors[0], dict):
            author_list = [a.get("name", "") for a in authors]
        else:
            author_list = authors
        lines.append(f"  author = {{{' and '.join(author_list)}}},")
    
    # 标题
    if paper.get("title"):
        lines.append(f"  title = {{{paper['title']}}},")
    
    # 期刊/会议
    if paper_type == "journal" and paper.get("journal"):
        lines.append(f"  journal = {{{paper['journal']}}},")
    elif paper_type == "conference" and paper.get("journal"):
        lines.append(f"  booktitle = {{{paper['journal']}}},")
    
    # 年份
    if paper.get("year"):
        lines.append(f"  year = {{{paper['year']}}},")
    
    # 卷号、期号、页码
    if paper.get("volume"):
        lines.append(f"  volume = {{{paper['volume']}}},")
    if paper.get("issue"):
        lines.append(f"  number = {{{paper['issue']}}},")
    if paper.get("pages"):
        lines.append(f"  pages = {{{paper['pages']}}},")
    
    # DOI
    if paper.get("doi"):
        lines.append(f"  doi = {{{paper['doi']}}},")
    
    # URL
    if paper.get("url"):
        lines.append(f"  url = {{{paper['url']}}},")
    
    # 摘要
    if include_abstract and paper.get("abstract"):
        # 处理摘要中的特殊字符
        abstract = paper['abstract'].replace('{', '{{').replace('}', '}}')
        lines.append(f"  abstract = {{{abstract}}},")
    
    lines.append("}")
    
    return "\n".join(lines)


def format_ris(paper: Dict) -> str:
    """
    格式化为RIS格式
    
    Args:
        paper: 文献元数据
    
    Returns:
        RIS字符串
    """
    lines = []
    
    # 文献类型
    paper_type = paper.get("type", "journal")
    type_map = {
        "journal": "JOUR",
        "book": "BOOK",
        "conference": "CONF",
        "thesis": "THES",
        "report": "RPRT"
    }
    lines.append(f"TY  - {type_map.get(paper_type, 'JOUR')}")
    
    # 标题
    if paper.get("title"):
        lines.append(f"TI  - {paper['title']}")
    
    # 作者
    authors = paper.get("authors", [])
    for author in authors:
        if isinstance(author, dict):
            name = author.get("name", "")
        else:
            name = str(author)
        lines.append(f"AU  - {name}")
    
    # 期刊
    if paper.get("journal"):
        lines.append(f"JO  - {paper['journal']}")
        lines.append(f"T2  - {paper['journal']}")
    
    # 年份
    if paper.get("year"):
        lines.append(f"PY  - {paper['year']}")
        lines.append(f"DA  - {paper['year']}")
    
    # 卷号、期号
    if paper.get("volume"):
        lines.append(f"VL  - {paper['volume']}")
    if paper.get("issue"):
        lines.append(f"IS  - {paper['issue']}")
    
    # 页码
    if paper.get("pages"):
        lines.append(f"SP  - {paper['pages']}")
    
    # DOI
    if paper.get("doi"):
        lines.append(f"DO  - {paper['doi']}")
    
    # URL
    if paper.get("url"):
        lines.append(f"UR  - {paper['url']}")
    
    # 摘要
    if paper.get("abstract"):
        # RIS格式中摘要可能跨多行
        abstract = paper['abstract']
        lines.append(f"AB  - {abstract}")
    
    lines.append("ER  - ")
    
    return "\n".join(lines)


def format_csl_json(paper: Dict) -> Dict:
    """
    格式化为CSL JSON格式
    
    Args:
        paper: 文献元数据
    
    Returns:
        CSL JSON字典
    """
    csl = {
        "id": paper.get("id", ""),
        "type": paper.get("type", "article-journal")
    }
    
    # 标题
    if paper.get("title"):
        csl["title"] = paper["title"]
    
    # 作者
    authors = paper.get("authors", [])
    csl["author"] = []
    for author in authors:
        if isinstance(author, dict):
            name = author.get("name", "")
        else:
            name = str(author)
        
        parts = name.split()
        if len(parts) > 1:
            csl["author"].append({
                "family": parts[-1],
                "given": " ".join(parts[:-1])
            })
        else:
            csl["author"].append({"family": name})
    
    # 容器（期刊/会议）
    if paper.get("journal"):
        csl["container-title"] = paper["journal"]
    
    # 日期
    if paper.get("year"):
        csl["issued"] = {"date-parts": [[paper["year"]]]}
    
    # 卷号、期号
    if paper.get("volume"):
        csl["volume"] = paper["volume"]
    if paper.get("issue"):
        csl["issue"] = paper["issue"]
    
    # 页码
    if paper.get("pages"):
        csl["page"] = paper["pages"]
    
    # DOI
    if paper.get("doi"):
        csl["DOI"] = paper["doi"]
    
    # URL
    if paper.get("url"):
        csl["URL"] = paper["url"]
    
    # 摘要
    if paper.get("abstract"):
        csl["abstract"] = paper["abstract"]
    
    return csl


def generate_cite_key(paper: Dict) -> str:
    """
    生成BibTeX引用密钥
    
    Args:
        paper: 文献元数据
    
    Returns:
        引用密钥
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
        
        surname = first_author.split()[-1] if " " in first_author else first_author
        surname = "".join(c for c in surname if c.isalnum())
    else:
        surname = "Unknown"
    
    # 提取标题关键词
    import re
    title_words = re.findall(r'\w+', title)
    title_part = "".join([w.capitalize() for w in title_words[:3] if len(w) > 3])
    
    return f"{surname}{year}{title_part[:15]}"


def export_to_zotero(
    papers: List[Dict],
    output_dir: str = "./zotero_export",
    formats: List[str] = ["bibtex"]
) -> Dict[str, str]:
    """
    导出文献到多种格式（供Zotero导入）
    
    Args:
        papers: 文献列表
        output_dir: 输出目录
        formats: 导出格式列表 ["bibtex", "ris", "csl_json"]
    
    Returns:
        导出的文件路径字典
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    exported_files = {}
    
    # BibTeX格式
    if "bibtex" in formats:
        bibtex_content = []
        for paper in papers:
            bibtex_content.append(format_bibtex(paper))
            bibtex_content.append("")  # 空行分隔
        
        bibtex_file = output_path / "references.bib"
        bibtex_file.write_text("\n".join(bibtex_content), encoding='utf-8')
        exported_files["bibtex"] = str(bibtex_file)
    
    # RIS格式
    if "ris" in formats:
        ris_content = []
        for paper in papers:
            ris_content.append(format_ris(paper))
            ris_content.append("")  # 空行分隔
        
        ris_file = output_path / "references.ris"
        ris_file.write_text("\n".join(ris_content), encoding='utf-8')
        exported_files["ris"] = str(ris_file)
    
    # CSL JSON格式
    if "csl_json" in formats:
        csl_data = [format_csl_json(paper) for paper in papers]
        
        csl_file = output_path / "references.json"
        csl_file.write_text(
            json.dumps(csl_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        exported_files["csl_json"] = str(csl_file)
    
    return exported_files


def generate_import_instructions(exported_files: Dict[str, str]) -> str:
    """
    生成Zotero导入说明
    
    Args:
        exported_files: 导出的文件路径
    
    Returns:
        导入说明文本
    """
    instructions = """
# Zotero 导入指南

## 导出的文件

"""
    
    for format_name, file_path in exported_files.items():
        instructions += f"- {format_name}: `{file_path}`\n"
    
    instructions += """
## 导入步骤

### 方法1: 使用 BibTeX 文件导入（推荐）

1. 打开 Zotero 桌面应用
2. 选择要导入的文件夹（或新建文件夹）
3. 点击菜单：文件 → 导入...
4. 选择导出的 `references.bib` 文件
5. 选择 "BibTeX" 作为导入格式
6. 点击确定完成导入

### 方法2: 使用 RIS 文件导入

1. 打开 Zotero 桌面应用
2. 选择要导入的文件夹
3. 点击菜单：文件 → 导入...
4. 选择导出的 `references.ris` 文件
5. 选择 "Reference Manager (RIS)" 作为导入格式
6. 点击确定完成导入

### 方法3: 使用 Zotero Connector 浏览器插件

1. 安装 Zotero Connector 浏览器插件
2. 访问文献的 DOI 链接
3. 点击浏览器工具栏的 Zotero 图标
4. 文献将自动保存到 Zotero

## 导入后的整理建议

1. **添加标签**: 为导入的文献添加主题标签，便于分类检索
2. **检查元数据**: 验证导入的元数据是否完整（标题、作者、期刊、DOI等）
3. **下载PDF**: 使用 Zotero 的 "找到可用的PDF" 功能自动下载全文
4. **添加笔记**: 为重要文献添加阅读笔记和研究想法

## 常见问题

**Q: 导入后作者姓名显示不正确？**
A: 检查BibTeX文件中的 `author` 字段格式，确保使用 `and` 分隔多个作者。

**Q: 中文文献导入后格式有问题？**
A: 在Zotero中设置正确的语言字段（zh-CN），并确保使用支持中文的CSL样式。

**Q: 如何批量更新文献的引用密钥？**
A: 使用 Zotero 的 Better BibTeX 插件可以自动生成和管理引用密钥。
"""
    
    return instructions


if __name__ == "__main__":
    # 测试示例
    test_papers = [
        {
            "id": "E1",
            "title": "Deep learning for image recognition",
            "authors": [{"name": "Yann LeCun"}, {"name": "Yoshua Bengio"}],
            "journal": "Nature",
            "year": 2015,
            "volume": "521",
            "issue": "7553",
            "pages": "436-444",
            "doi": "10.1038/nature14539",
            "type": "journal",
            "abstract": "Deep learning allows computational models..."
        },
        {
            "id": "E2",
            "title": "Attention is all you need",
            "authors": [{"name": "Ashish Vaswani"}],
            "journal": "Advances in Neural Information Processing Systems",
            "year": 2017,
            "doi": "10.48550/arXiv.1706.03762",
            "type": "conference"
        }
    ]
    
    # 导出
    exported = export_to_zotero(
        test_papers,
        output_dir="./test_export",
        formats=["bibtex", "ris", "csl_json"]
    )
    
    # 生成导入说明
    instructions = generate_import_instructions(exported)
    print(instructions)
    
    # 显示BibTeX示例
    print("\n" + "=" * 70)
    print("BibTeX 示例:")
    print("=" * 70)
    print(format_bibtex(test_papers[0]))
