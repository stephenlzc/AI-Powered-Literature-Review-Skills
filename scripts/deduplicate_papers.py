#!/usr/bin/env python3
"""
文献去重工具

功能：
- 基于DOI精确去重
- 基于标题相似度去重
- 基于作者+年份+期刊去重
- 保留高质量版本
"""

from typing import List, Dict, Tuple
from difflib import SequenceMatcher
from collections import defaultdict


def calculate_similarity(str1: str, str2: str) -> float:
    """
    计算两个字符串的相似度
    
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


def extract_author_signature(authors: List, max_authors: int = 3) -> str:
    """
    提取作者签名（用于去重）
    
    Args:
        authors: 作者列表
        max_authors: 最多取前几作者
    
    Returns:
        作者签名字符串
    """
    if not authors:
        return ""
    
    signatures = []
    for author in authors[:max_authors]:
        if isinstance(author, dict):
            name = author.get("name", "")
        else:
            name = str(author)
        
        # 提取姓氏
        surname = name.split()[-1] if " " in name else name
        signatures.append(surname.lower())
    
    return "|".join(signatures)


def calculate_paper_quality_score(paper: Dict) -> float:
    """
    计算文献质量分数
    
    用于决定保留哪个重复版本
    
    Args:
        paper: 文献元数据
    
    Returns:
        质量分数
    """
    score = 0.0
    
    # 有DOI加分
    if paper.get("doi"):
        score += 10
    
    # 被引次数
    citations = paper.get("citation_count", 0)
    if citations > 0:
        score += min(citations / 100, 50)  # 最多50分
    
    # 期刊质量（如果有影响因子信息）
    impact_factor = paper.get("impact_factor", 0)
    if impact_factor > 0:
        score += impact_factor
    
    # 开放获取
    if paper.get("is_oa"):
        score += 5
    
    # 有完整元数据加分
    if paper.get("abstract"):
        score += 5
    if paper.get("volume") and paper.get("issue"):
        score += 3
    
    return score


def deduplicate_papers(
    papers: List[Dict],
    doi_similarity_threshold: float = 1.0,
    title_similarity_threshold: float = 0.85,
    metadata_match_threshold: float = 0.9
) -> Tuple[List[Dict], List[Dict]]:
    """
    文献去重主函数
    
    采用多层去重策略：
    1. DOI精确匹配
    2. 标题相似度匹配
    3. 作者+年份+期刊元数据匹配
    
    Args:
        papers: 文献列表
        doi_similarity_threshold: DOI匹配阈值（默认1.0精确匹配）
        title_similarity_threshold: 标题相似度阈值
        metadata_match_threshold: 元数据匹配阈值
    
    Returns:
        (去重后的文献列表, 被移除的重复文献列表)
    """
    if not papers:
        return [], []
    
    unique_papers = []
    removed_papers = []
    
    # 第一层：DOI去重
    doi_groups = defaultdict(list)
    papers_without_doi = []
    
    for paper in papers:
        doi = normalize_doi(paper.get("doi", ""))
        if doi:
            doi_groups[doi].append(paper)
        else:
            papers_without_doi.append(paper)
    
    # 处理DOI分组，保留质量最高的
    for doi, group in doi_groups.items():
        if len(group) == 1:
            unique_papers.append(group[0])
        else:
            # 保留质量最高的版本
            best_paper = max(group, key=calculate_paper_quality_score)
            unique_papers.append(best_paper)
            removed_papers.extend([p for p in group if p != best_paper])
    
    # 第二层：标题相似度去重（针对没有DOI的文献）
    papers_to_check = papers_without_doi + unique_papers
    unique_papers = []
    
    for paper in papers_to_check:
        is_duplicate = False
        title = paper.get("title", "").lower()
        
        for existing in unique_papers:
            existing_title = existing.get("title", "").lower()
            similarity = calculate_similarity(title, existing_title)
            
            if similarity >= title_similarity_threshold:
                # 标题相似，比较质量，保留高质量的
                if calculate_paper_quality_score(paper) > calculate_paper_quality_score(existing):
                    removed_papers.append(existing)
                    unique_papers.remove(existing)
                    unique_papers.append(paper)
                else:
                    removed_papers.append(paper)
                
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_papers.append(paper)
    
    # 第三层：作者+年份+期刊去重
    papers_to_check = unique_papers
    unique_papers = []
    
    for paper in papers_to_check:
        is_duplicate = False
        
        author_sig = extract_author_signature(paper.get("authors", []))
        year = paper.get("year", "")
        journal = paper.get("journal", "").lower()[:20]  # 取前20字符
        
        paper_signature = f"{author_sig}|{year}|{journal}"
        
        for existing in unique_papers:
            existing_author_sig = extract_author_signature(existing.get("authors", []))
            existing_year = existing.get("year", "")
            existing_journal = existing.get("journal", "").lower()[:20]
            
            existing_signature = f"{existing_author_sig}|{existing_year}|{existing_journal}"
            
            # 计算签名相似度
            sig_similarity = calculate_similarity(paper_signature, existing_signature)
            
            if sig_similarity >= metadata_match_threshold:
                # 可能是同一篇，比较质量
                if calculate_paper_quality_score(paper) > calculate_paper_quality_score(existing):
                    removed_papers.append(existing)
                    unique_papers.remove(existing)
                    unique_papers.append(paper)
                else:
                    removed_papers.append(paper)
                
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_papers.append(paper)
    
    return unique_papers, removed_papers


def find_potential_duplicates(
    papers: List[Dict],
    similarity_threshold: float = 0.7
) -> List[Tuple[Dict, Dict, float]]:
    """
    查找潜在的重复文献对（用于人工审核）
    
    Args:
        papers: 文献列表
        similarity_threshold: 相似度阈值
    
    Returns:
        潜在重复对列表 [(paper1, paper2, similarity), ...]
    """
    potential_duplicates = []
    
    for i, paper1 in enumerate(papers):
        for paper2 in papers[i+1:]:
            # 计算标题相似度
            title_sim = calculate_similarity(
                paper1.get("title", ""),
                paper2.get("title", "")
            )
            
            if title_sim >= similarity_threshold:
                potential_duplicates.append((paper1, paper2, title_sim))
                continue
            
            # 检查DOI
            doi1 = normalize_doi(paper1.get("doi", ""))
            doi2 = normalize_doi(paper2.get("doi", ""))
            
            if doi1 and doi2 and doi1 == doi2:
                potential_duplicates.append((paper1, paper2, 1.0))
    
    # 按相似度排序
    potential_duplicates.sort(key=lambda x: x[2], reverse=True)
    
    return potential_duplicates


def print_deduplication_report(
    original_count: int,
    unique_papers: List[Dict],
    removed_papers: List[Dict]
):
    """
    打印去重报告
    
    Args:
        original_count: 原始文献数量
        unique_papers: 去重后的文献
        removed_papers: 被移除的文献
    """
    print("=" * 70)
    print("文献去重报告")
    print("=" * 70)
    
    print(f"\n原始文献数量: {original_count}")
    print(f"去重后数量: {len(unique_papers)}")
    print(f"移除重复: {len(removed_papers)}")
    print(f"去重率: {len(removed_papers) / original_count * 100:.1f}%")
    
    if removed_papers:
        print("\n被移除的文献:")
        for paper in removed_papers[:10]:  # 只显示前10个
            title = paper.get("title", "Unknown")[:50]
            print(f"  - {title}...")
        
        if len(removed_papers) > 10:
            print(f"  ... 还有 {len(removed_papers) - 10} 篇")


if __name__ == "__main__":
    # 测试示例
    test_papers = [
        {
            "id": "E1",
            "title": "Deep learning for image recognition",
            "authors": [{"name": "Y LeCun"}],
            "year": 2015,
            "journal": "Nature",
            "doi": "10.1038/nature14539",
            "citation_count": 50000
        },
        {
            "id": "E2",  # DOI重复的文献
            "title": "Deep learning",
            "authors": [{"name": "Y LeCun"}],
            "year": 2015,
            "journal": "Nature",
            "doi": "10.1038/nature14539",
            "citation_count": 50000
        },
        {
            "id": "E3",  # 标题相似的文献
            "title": "Deep learning for image recognition: A survey",
            "authors": [{"name": "Y LeCun"}],
            "year": 2015,
            "journal": "Nature",
            "doi": "",
            "citation_count": 100
        },
        {
            "id": "E4",  # 完全不同的文献
            "title": "Attention is all you need",
            "authors": [{"name": "A Vaswani"}],
            "year": 2017,
            "journal": "NIPS",
            "doi": "10.48550/arXiv.1706.03762",
            "citation_count": 80000
        }
    ]
    
    unique, removed = deduplicate_papers(test_papers)
    print_deduplication_report(len(test_papers), unique, removed)
