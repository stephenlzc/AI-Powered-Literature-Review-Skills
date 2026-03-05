#!/usr/bin/env python3
"""
引用验证工具

功能：
- DOI验证
- Crossref/Semantic Scholar查询验证
- 预印本检查（arXiv→期刊版本）
- 撤稿检测
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class VerificationStatus(Enum):
    """验证状态"""
    VERIFIED = "verified"           # 多源确认
    SINGLE_SOURCE = "single_source" # 单源确认
    PREPRINT = "preprint"           # 预印本
    RETRACTED = "retracted"         # 已撤稿
    NOT_FOUND = "not_found"         # 未找到
    METADATA_MISMATCH = "metadata_mismatch"  # 元数据不一致
    PENDING = "pending"             # 待验证


@dataclass
class VerificationResult:
    """验证结果"""
    paper_id: str
    status: VerificationStatus
    confidence: float  # 置信度 0.0-1.0
    message: str
    verified_metadata: Dict
    verification_source: str
    checks: Dict
    timestamp: datetime


class ReferenceVerifier:
    """
    引用验证器
    
    防止幻觉引用，确保文献真实性
    """
    
    def __init__(self, email: str = "user@example.com"):
        """
        初始化验证器
        
        Args:
            email: 用于OpenAlex等API的礼貌请求
        """
        self.email = email
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": f"LiteratureSurvey/2.0 (mailto:{self.email})"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def verify_paper(self, paper: Dict) -> VerificationResult:
        """
        验证单篇文献
        
        Args:
            paper: 文献元数据
        
        Returns:
            验证结果
        """
        paper_id = paper.get("id", "unknown")
        
        # 1. 如果有DOI，优先DOI验证
        if paper.get("doi"):
            result = await self._verify_by_doi(paper)
            if result.status in [VerificationStatus.VERIFIED, VerificationStatus.SINGLE_SOURCE]:
                return result
        
        # 2. 通过标题+作者搜索验证
        result = await self._verify_by_metadata(paper)
        if result.status != VerificationStatus.NOT_FOUND:
            return result
        
        # 3. 标记为未找到
        return VerificationResult(
            paper_id=paper_id,
            status=VerificationStatus.NOT_FOUND,
            confidence=0.0,
            message="Unable to verify paper in any source",
            verified_metadata={},
            verification_source="",
            checks={},
            timestamp=datetime.now()
        )
    
    async def verify_papers(self, papers: List[Dict]) -> List[VerificationResult]:
        """
        批量验证文献
        
        Args:
            papers: 文献列表
        
        Returns:
            验证结果列表
        """
        tasks = [self.verify_paper(paper) for paper in papers]
        return await asyncio.gather(*tasks)
    
    async def _verify_by_doi(self, paper: Dict) -> VerificationResult:
        """通过DOI验证"""
        doi = paper.get("doi", "").strip()
        paper_id = paper.get("id", "unknown")
        
        # 尝试Crossref
        try:
            crossref_result = await self._query_crossref(doi)
            if crossref_result.get("status") == "ok":
                metadata = crossref_result.get("message", {})
                
                # 比对元数据
                match_score = self._compare_metadata(paper, metadata)
                
                if match_score > 0.8:
                    return VerificationResult(
                        paper_id=paper_id,
                        status=VerificationStatus.VERIFIED,
                        confidence=match_score,
                        message="Verified via Crossref DOI",
                        verified_metadata=self._extract_crossref_metadata(metadata),
                        verification_source="crossref",
                        checks={"doi_resolved": True, "metadata_match": True},
                        timestamp=datetime.now()
                    )
                else:
                    return VerificationResult(
                        paper_id=paper_id,
                        status=VerificationStatus.METADATA_MISMATCH,
                        confidence=match_score,
                        message="DOI resolved but metadata mismatch",
                        verified_metadata=self._extract_crossref_metadata(metadata),
                        verification_source="crossref",
                        checks={"doi_resolved": True, "metadata_match": False},
                        timestamp=datetime.now()
                    )
        except Exception as e:
            pass  # 继续尝试其他源
        
        # 尝试Semantic Scholar
        try:
            ss_result = await self._query_semantic_scholar(doi=doi)
            if ss_result:
                return VerificationResult(
                    paper_id=paper_id,
                    status=VerificationStatus.SINGLE_SOURCE,
                    confidence=0.7,
                    message="Verified via Semantic Scholar",
                    verified_metadata=self._extract_ss_metadata(ss_result),
                    verification_source="semantic_scholar",
                    checks={"doi_resolved": True},
                    timestamp=datetime.now()
                )
        except Exception:
            pass
        
        return VerificationResult(
            paper_id=paper_id,
            status=VerificationStatus.NOT_FOUND,
            confidence=0.0,
            message="DOI not found in any verification source",
            verified_metadata={},
            verification_source="",
            checks={"doi_resolved": False},
            timestamp=datetime.now()
        )
    
    async def _verify_by_metadata(self, paper: Dict) -> VerificationResult:
        """通过标题+作者元数据验证"""
        title = paper.get("title", "")
        authors = paper.get("authors", [])
        paper_id = paper.get("id", "unknown")
        
        # 在Semantic Scholar中搜索
        try:
            ss_result = await self._query_semantic_scholar(title=title)
            if ss_result:
                # 比对作者
                if self._match_authors(authors, ss_result.get("authors", [])):
                    return VerificationResult(
                        paper_id=paper_id,
                        status=VerificationStatus.SINGLE_SOURCE,
                        confidence=0.6,
                        message="Verified via Semantic Scholar metadata search",
                        verified_metadata=self._extract_ss_metadata(ss_result),
                        verification_source="semantic_scholar",
                        checks={"title_match": True, "author_match": True},
                        timestamp=datetime.now()
                    )
        except Exception:
            pass
        
        return VerificationResult(
            paper_id=paper_id,
            status=VerificationStatus.NOT_FOUND,
            confidence=0.0,
            message="Unable to verify via metadata search",
            verified_metadata={},
            verification_source="",
            checks={},
            timestamp=datetime.now()
        )
    
    async def _query_crossref(self, doi: str) -> Dict:
        """查询Crossref API"""
        url = f"https://api.crossref.org/works/{doi}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                return {"status": "not_found"}
            else:
                response.raise_for_status()
    
    async def _query_semantic_scholar(self, doi: str = "", title: str = "") -> Optional[Dict]:
        """查询Semantic Scholar API"""
        if doi:
            url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
        elif title:
            url = f"https://api.semanticscholar.org/graph/v1/paper/search"
            params = {"query": title, "fields": "title,authors,year", "limit": 1}
        else:
            return None
        
        try:
            if doi:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            else:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("data"):
                            return data["data"][0]
        except Exception:
            pass
        
        return None
    
    async def check_preprint(self, paper: Dict) -> Dict:
        """
        检查是否为预印本，并查找发表版本
        
        Returns:
            {"is_preprint": bool, "published_version": Dict or None}
        """
        source_db = paper.get("source_db", "").lower()
        title = paper.get("title", "")
        
        # 检查是否为预印本来源
        preprint_sources = ["arxiv", "biorxiv", "medrxiv", "ssrn"]
        is_preprint = any(src in source_db for src in preprint_sources)
        
        if not is_preprint:
            return {"is_preprint": False, "published_version": None}
        
        # 尝试查找发表版本
        try:
            # 在Semantic Scholar中搜索
            ss_result = await self._query_semantic_scholar(title=title)
            if ss_result:
                venue = ss_result.get("venue", "")
                # 如果找到了期刊名称，说明有发表版本
                if venue and venue not in ["arXiv", "bioRxiv", "medRxiv"]:
                    return {
                        "is_preprint": True,
                        "published_version": self._extract_ss_metadata(ss_result)
                    }
        except Exception:
            pass
        
        return {"is_preprint": True, "published_version": None}
    
    async def check_retraction(self, paper: Dict) -> Dict:
        """
        检查是否被撤稿
        
        Returns:
            {"is_retracted": bool, "retraction_info": Dict}
        """
        doi = paper.get("doi", "")
        
        # 尝试Crossref的撤稿信息
        try:
            if doi:
                result = await self._query_crossref(doi)
                message = result.get("message", {})
                
                # 检查撤稿标记
                if message.get("is-retracted"):
                    return {
                        "is_retracted": True,
                        "retraction_info": {
                            "source": "crossref",
                            "date": message.get("retraction-date"),
                            "reason": "See Crossref record for details"
                        }
                    }
        except Exception:
            pass
        
        return {"is_retracted": False, "retraction_info": {}}
    
    def _compare_metadata(self, paper: Dict, crossref_metadata: Dict) -> float:
        """比对元数据相似度"""
        scores = []
        
        # 标题比对
        paper_title = paper.get("title", "").lower()
        cr_title = crossref_metadata.get("title", [""])[0].lower() if isinstance(
            crossref_metadata.get("title"), list) else str(crossref_metadata.get("title", "")).lower()
        
        if paper_title and cr_title:
            title_score = self._string_similarity(paper_title, cr_title)
            scores.append(title_score)
        
        # 作者比对
        paper_authors = paper.get("authors", [])
        cr_authors = crossref_metadata.get("author", [])
        if paper_authors and cr_authors:
            author_score = self._match_authors_score(paper_authors, cr_authors)
            scores.append(author_score)
        
        # 年份比对
        paper_year = paper.get("year")
        cr_year = crossref_metadata.get("published-print", {}).get("date-parts", [[0]])[0][0]
        if paper_year and cr_year:
            year_score = 1.0 if str(paper_year) == str(cr_year) else 0.0
            scores.append(year_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """计算字符串相似度"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1, s2).ratio()
    
    def _match_authors(self, authors1: List, authors2: List) -> bool:
        """比对作者列表"""
        score = self._match_authors_score(authors1, authors2)
        return score > 0.5
    
    def _match_authors_score(self, authors1: List, authors2: List) -> float:
        """计算作者匹配分数"""
        if not authors1 or not authors2:
            return 0.0
        
        # 提取姓氏进行比较
        surnames1 = set()
        for a in authors1[:3]:  # 只比较前3位
            if isinstance(a, dict):
                name = a.get("name", "")
            else:
                name = str(a)
            surnames1.add(name.split()[-1].lower())
        
        surnames2 = set()
        for a in authors2[:3]:
            if isinstance(a, dict):
                family = a.get("family", "")
            else:
                family = str(a).split()[-1]
            surnames2.add(family.lower())
        
        # 计算Jaccard相似度
        intersection = surnames1 & surnames2
        union = surnames1 | surnames2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _extract_crossref_metadata(self, message: Dict) -> Dict:
        """从Crossref响应提取元数据"""
        authors = []
        for author in message.get("author", []):
            authors.append({
                "given": author.get("given", ""),
                "family": author.get("family", ""),
                "affiliation": [a.get("name", "") for a in author.get("affiliation", [])]
            })
        
        return {
            "title": message.get("title", [""])[0] if isinstance(message.get("title"), list) else message.get("title", ""),
            "authors": authors,
            "journal": message.get("container-title", [""])[0] if isinstance(message.get("container-title"), list) else "",
            "year": message.get("published-print", {}).get("date-parts", [[None]])[0][0],
            "volume": message.get("volume", ""),
            "issue": message.get("issue", ""),
            "pages": message.get("page", ""),
            "doi": message.get("DOI", ""),
            "publisher": message.get("publisher", "")
        }
    
    def _extract_ss_metadata(self, data: Dict) -> Dict:
        """从Semantic Scholar响应提取元数据"""
        return {
            "title": data.get("title", ""),
            "authors": [{"name": a.get("name", "")} for a in data.get("authors", [])],
            "journal": data.get("venue", ""),
            "year": data.get("year"),
            "doi": data.get("externalIds", {}).get("DOI", ""),
            "citation_count": data.get("citationCount", 0)
        }


def print_verification_report(results: List[VerificationResult]):
    """打印验证报告"""
    print("=" * 70)
    print("引用验证报告")
    print("=" * 70)
    
    # 统计
    status_counts = {}
    for r in results:
        status_counts[r.status.value] = status_counts.get(r.status.value, 0) + 1
    
    print("\n验证统计：")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
    # 详细结果
    print("\n详细结果：")
    for result in results:
        status_symbol = {
            VerificationStatus.VERIFIED: "✓",
            VerificationStatus.SINGLE_SOURCE: "~",
            VerificationStatus.PREPRINT: "P",
            VerificationStatus.RETRACTED: "✗",
            VerificationStatus.NOT_FOUND: "?",
            VerificationStatus.METADATA_MISMATCH: "!"
        }.get(result.status, " ")
        
        print(f"\n  [{status_symbol}] {result.paper_id}")
        print(f"      Status: {result.status.value}")
        print(f"      Confidence: {result.confidence:.2f}")
        print(f"      Source: {result.verification_source}")
        print(f"      Message: {result.message}")


if __name__ == "__main__":
    # 测试示例
    test_papers = [
        {
            "id": "E1",
            "title": "Attention is all you need",
            "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}],
            "doi": "10.48550/arXiv.1706.03762",
            "year": 2017
        },
        {
            "id": "E2",
            "title": "A non-existent paper title",
            "authors": [{"name": "Fake Author"}],
            "doi": "10.0000/fake.doi.12345"
        }
    ]
    
    async def main():
        async with ReferenceVerifier() as verifier:
            results = await verifier.verify_papers(test_papers)
            print_verification_report(results)
    
    asyncio.run(main())
