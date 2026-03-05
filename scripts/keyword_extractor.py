#!/usr/bin/env python3
"""
关键词提取与扩展工具（增强版）

功能：
- 从标题提取中英文关键词
- 学科领域模板（CS、医学、经济等）
- 同义词扩展
- 生成多数据库检索表达式
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re


@dataclass
class KeywordSet:
    """关键词集合"""
    zh: List[str]
    en: List[str]
    zh_expanded: Dict[str, List[str]]
    en_expanded: Dict[str, List[str]]


@dataclass
class QuerySet:
    """检索表达式集合"""
    cnki: str
    pubmed: str
    semantic_scholar: str
    ieee: str
    arxiv: str


class KeywordExtractor:
    """
    增强版关键词提取器
    
    支持学科领域模板和LLM辅助提取
    """
    
    # 学科领域模板
    DOMAIN_TEMPLATES = {
        "computer_science": {
            "method_keywords": ["algorithm", "model", "approach", "method", "framework"],
            "domain_keywords": ["AI", "machine learning", "deep learning", "neural network"],
            "task_keywords": ["classification", "detection", "segmentation", "prediction"],
            "data_keywords": ["image", "text", "video", "sensor data"]
        },
        "medicine": {
            "method_keywords": ["clinical trial", "cohort study", "meta-analysis", "RCT"],
            "domain_keywords": ["diagnosis", "treatment", "prognosis", "prevention"],
            "task_keywords": ["screening", "imaging", "biomarker", "therapy"],
            "data_keywords": ["EMR", "imaging", "genomic", "patient data"]
        },
        "economics": {
            "method_keywords": ["econometric", "modeling", "analysis", "estimation"],
            "domain_keywords": ["market", "policy", "finance", "development"],
            "task_keywords": ["forecasting", "evaluation", "optimization"],
            "data_keywords": ["panel data", "time series", "survey"]
        },
        "education": {
            "method_keywords": ["experiment", "survey", "interview", "observation"],
            "domain_keywords": ["learning", "teaching", "curriculum", "assessment"],
            "task_keywords": ["evaluation", "intervention", "design"],
            "data_keywords": ["test scores", "questionnaire", "behavioral data"]
        }
    }
    
    # 术语映射库（扩展版）
    TERM_MAPPINGS = {
        # 计算机科学 - 深度学习
        "深度学习": {
            "en": ["deep learning", "deep neural network", "DNN"],
            "synonyms_zh": ["深度神经网络", "深层学习", "深度机器学习"],
            "synonyms_en": ["neural network", "representation learning", "hierarchical learning"]
        },
        "机器学习": {
            "en": ["machine learning", "ML"],
            "synonyms_zh": ["自动学习", "统计学习", "机器学习算法"],
            "synonyms_en": ["statistical learning", "automated learning", "computational learning"]
        },
        "人工智能": {
            "en": ["artificial intelligence", "AI"],
            "synonyms_zh": ["智能系统", "机器智能", "智能计算"],
            "synonyms_en": ["intelligent systems", "computational intelligence", "machine intelligence"]
        },
        "图像识别": {
            "en": ["image recognition", "image classification"],
            "synonyms_zh": ["图像分类", "视觉识别", "图像检测"],
            "synonyms_en": ["visual recognition", "computer vision", "image analysis", "pattern recognition"]
        },
        "自然语言处理": {
            "en": ["natural language processing", "NLP"],
            "synonyms_zh": ["自然语言理解", "计算语言学", "文本处理"],
            "synonyms_en": ["computational linguistics", "text mining", "language technology", "text processing"]
        },
        "卷积神经网络": {
            "en": ["convolutional neural network", "CNN"],
            "synonyms_zh": ["卷积网络", "ConvNet", "CNN模型"],
            "synonyms_en": ["convnet", "deep convolutional network", "ConvNets"]
        },
        "Transformer": {
            "en": ["transformer", "attention mechanism"],
            "synonyms_zh": ["自注意力", "注意力机制", "Transformer模型"],
            "synonyms_en": ["self-attention", "attention-based model", "attention network"]
        },
        "大语言模型": {
            "en": ["large language model", "LLM"],
            "synonyms_zh": ["大规模语言模型", "预训练语言模型", "基础模型"],
            "synonyms_en": ["foundation model", "pretrained language model", "GPT", "LLMs"]
        },
        "生成式AI": {
            "en": ["generative AI", "generative artificial intelligence"],
            "synonyms_zh": ["生成式人工智能", "AIGC", "生成模型"],
            "synonyms_en": ["AIGC", "generative model", "generative modeling"]
        },
        # 医学
        "癌症": {
            "en": ["cancer", "carcinoma", "tumor"],
            "synonyms_zh": ["肿瘤", "恶性肿瘤", "癌变"],
            "synonyms_en": ["neoplasm", "malignancy", "oncology", "malignant tumor"]
        },
        "基因": {
            "en": ["gene", "genetic"],
            "synonyms_zh": ["遗传", "基因组", "基因序列"],
            "synonyms_en": ["genome", "DNA", "genetics", "genomic"]
        },
        "诊断": {
            "en": ["diagnosis", "diagnostic"],
            "synonyms_zh": ["检测", "筛查", "识别"],
            "synonyms_en": ["detection", "screening", "identification", "diagnostics"]
        },
        "医学图像": {
            "en": ["medical imaging", "medical image"],
            "synonyms_zh": ["医学影像", "医疗图像", "临床图像"],
            "synonyms_en": ["clinical imaging", "biomedical imaging", "radiology"]
        },
        # 教育学
        "在线教育": {
            "en": ["online education", "e-learning"],
            "synonyms_zh": ["网络教育", "远程教育", "互联网教育"],
            "synonyms_en": ["distance learning", "web-based learning", "virtual learning", "online learning"]
        },
        # 经济学
        "数字经济": {
            "en": ["digital economy", "digital transformation"],
            "synonyms_zh": ["数字化转型", "互联网经济", "平台经济"],
            "synonyms_en": ["internet economy", "platform economy", "digitalization"]
        }
    }
    
    def __init__(self, domain: str = ""):
        """
        初始化提取器
        
        Args:
            domain: 学科领域（computer_science, medicine, economics, education）
        """
        self.domain = domain
        self.domain_template = self.DOMAIN_TEMPLATES.get(domain, {})
    
    def extract_keywords(self, title: str, abstract: str = "") -> KeywordSet:
        """
        从标题和摘要提取关键词
        
        Args:
            title: 论文标题
            abstract: 摘要（可选，用于增强提取）
        
        Returns:
            KeywordSet对象
        """
        text = title + " " + abstract
        
        keywords_zh = []
        keywords_en = []
        
        # 尝试匹配已知术语
        for term_zh, mappings in self.TERM_MAPPINGS.items():
            if term_zh.lower() in text.lower():
                keywords_zh.append(term_zh)
                keywords_en.extend(mappings['en'])
        
        # 如果没有匹配到，使用标题分词
        if not keywords_zh:
            # 简单分词（中文按字符，英文按空格）
            zh_words = self._extract_chinese_words(title)
            keywords_zh = zh_words[:5] if zh_words else [title]
        
        if not keywords_en:
            en_words = self._extract_english_words(title)
            keywords_en = en_words[:5] if en_words else [title]
        
        # 去重
        keywords_zh = list(dict.fromkeys(keywords_zh))
        keywords_en = list(dict.fromkeys(keywords_en))
        
        # 扩展同义词
        zh_expanded = self._expand_zh_keywords(keywords_zh)
        en_expanded = self._expand_en_keywords(keywords_en)
        
        return KeywordSet(
            zh=keywords_zh,
            en=keywords_en,
            zh_expanded=zh_expanded,
            en_expanded=en_expanded
        )
    
    def _extract_chinese_words(self, text: str) -> List[str]:
        """提取中文词语"""
        # 简单实现：按常见模式提取
        words = []
        # 这里可以使用jieba等分词库
        # 简化处理：返回常见技术词汇
        common_terms = ["学习", "网络", "模型", "算法", "识别", "分类", "检测", "分析"]
        for term in common_terms:
            if term in text:
                words.append(term)
        return words
    
    def _extract_english_words(self, text: str) -> List[str]:
        """提取英文词语"""
        # 提取英文单词
        english_words = re.findall(r'[a-zA-Z]+', text)
        # 过滤常见停用词
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or', 'based'}
        return [w for w in english_words if w.lower() not in stopwords and len(w) > 3]
    
    def _expand_zh_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """扩展中文关键词同义词"""
        expanded = {}
        for kw in keywords:
            if kw in self.TERM_MAPPINGS:
                mapping = self.TERM_MAPPINGS[kw]
                expanded[kw] = mapping['synonyms_zh']
            else:
                expanded[kw] = []
        return expanded
    
    def _expand_en_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """扩展英文关键词同义词"""
        expanded = {}
        for kw in keywords:
            # 查找对应的英文关键词映射
            found = False
            for term_zh, mapping in self.TERM_MAPPINGS.items():
                if kw.lower() in [e.lower() for e in mapping['en']]:
                    expanded[kw] = mapping['synonyms_en']
                    found = True
                    break
            if not found:
                expanded[kw] = []
        return expanded
    
    def generate_search_queries(self, keyword_set: KeywordSet) -> QuerySet:
        """
        生成多数据库检索表达式
        
        Args:
            keyword_set: 关键词集合
        
        Returns:
            QuerySet对象
        """
        return QuerySet(
            cnki=self._build_cnki_query(keyword_set),
            pubmed=self._build_pubmed_query(keyword_set),
            semantic_scholar=self._build_semantic_scholar_query(keyword_set),
            ieee=self._build_ieee_query(keyword_set),
            arxiv=self._build_arxiv_query(keyword_set)
        )
    
    def _build_cnki_query(self, keyword_set: KeywordSet) -> str:
        """构建CNKI检索式"""
        zh_terms = keyword_set.zh
        zh_expanded = keyword_set.zh_expanded
        
        query_parts = []
        for term in zh_terms:
            synonyms = zh_expanded.get(term, [])
            if synonyms:
                all_terms = [term] + synonyms[:2]  # 最多3个同义词
                query_parts.append("+".join(all_terms))
            else:
                query_parts.append(term)
        
        # 使用主题字段(SU)和AND连接
        if len(query_parts) > 1:
            return "*".join([f"SU=({p})" for p in query_parts])
        return f"SU=({query_parts[0]})" if query_parts else ""
    
    def _build_pubmed_query(self, keyword_set: KeywordSet) -> str:
        """构建PubMed检索式"""
        en_terms = keyword_set.en
        en_expanded = keyword_set.en_expanded
        
        query_parts = []
        for term in en_terms:
            synonyms = en_expanded.get(term, [])
            if synonyms:
                all_terms = [f'"{term}"'] + [f'"{s}"' for s in synonyms[:2]]
                query_parts.append(f"({' OR '.join(all_terms)})")
            else:
                query_parts.append(f'"{term}"')
        
        if len(query_parts) > 1:
            query = " AND ".join(query_parts)
        else:
            query = query_parts[0] if query_parts else ""
        
        # 添加字段限制
        return f"({query}[Title/Abstract])"
    
    def _build_semantic_scholar_query(self, keyword_set: KeywordSet) -> str:
        """构建Semantic Scholar检索式"""
        en_terms = keyword_set.en
        en_expanded = keyword_set.en_expanded
        
        query_parts = []
        for term in en_terms:
            synonyms = en_expanded.get(term, [])
            if synonyms:
                all_terms = [f'"{term}"'] + [f'"{s}"' for s in synonyms[:2]]
                query_parts.append(f"({' OR '.join(all_terms)})")
            else:
                query_parts.append(f'"{term}"')
        
        if len(query_parts) > 1:
            return " AND ".join(query_parts)
        return query_parts[0] if query_parts else ""
    
    def _build_ieee_query(self, keyword_set: KeywordSet) -> str:
        """构建IEEE Xplore检索式"""
        # IEEE使用类似的布尔逻辑
        return self._build_semantic_scholar_query(keyword_set)
    
    def _build_arxiv_query(self, keyword_set: KeywordSet) -> str:
        """构建arXiv检索式"""
        # arXiv使用类似的布尔逻辑
        return self._build_semantic_scholar_query(keyword_set)
    
    def analyze(self, title: str, abstract: str = "", domain: str = "") -> Dict:
        """
        全面分析论文标题
        
        Args:
            title: 论文标题
            abstract: 摘要（可选）
            domain: 学科领域（可选，覆盖初始化时设置的领域）
        
        Returns:
            完整的分析报告
        """
        if domain:
            self.domain = domain
            self.domain_template = self.DOMAIN_TEMPLATES.get(domain, {})
        
        keyword_set = self.extract_keywords(title, abstract)
        queries = self.generate_search_queries(keyword_set)
        
        return {
            "title": title,
            "domain": self.domain,
            "keywords": {
                "zh": keyword_set.zh,
                "en": keyword_set.en,
                "zh_expanded": keyword_set.zh_expanded,
                "en_expanded": keyword_set.en_expanded
            },
            "search_queries": {
                "cnki": queries.cnki,
                "pubmed": queries.pubmed,
                "semantic_scholar": queries.semantic_scholar,
                "ieee": queries.ieee,
                "arxiv": queries.arxiv
            },
            "recommendations": self._generate_recommendations(keyword_set)
        }
    
    def _generate_recommendations(self, keyword_set: KeywordSet) -> List[str]:
        """生成检索建议"""
        recommendations = []
        
        if len(keyword_set.zh) < 3:
            recommendations.append("建议增加更多中文关键词以提高检索召回率")
        
        if len(keyword_set.en) < 3:
            recommendations.append("建议增加更多英文关键词以提高检索召回率")
        
        if not any(kw in ["综述", "review", "survey"] for kw in keyword_set.zh + keyword_set.en):
            recommendations.append("可考虑添加'review'或'综述'关键词查找相关综述文章")
        
        return recommendations


def print_analysis_report(report: Dict):
    """打印分析报告"""
    print(f"论文标题：{report['title']}")
    if report['domain']:
        print(f"学科领域：{report['domain']}")
    print()
    
    print("中文关键词：")
    for i, kw in enumerate(report['keywords']['zh'], 1):
        synonyms = report['keywords']['zh_expanded'].get(kw, [])
        print(f"  {i}. {kw}")
        if synonyms:
            print(f"     同义词：{' / '.join(synonyms)}")
    
    print("\n英文关键词：")
    for i, kw in enumerate(report['keywords']['en'], 1):
        synonyms = report['keywords']['en_expanded'].get(kw, [])
        print(f"  {i}. {kw}")
        if synonyms:
            print(f"     Synonyms: {' / '.join(synonyms)}")
    
    print("\n检索表达式：")
    for db, query in report['search_queries'].items():
        print(f"\n  {db.upper()}:")
        print(f"    {query}")
    
    if report['recommendations']:
        print("\n建议：")
        for rec in report['recommendations']:
            print(f"  • {rec}")


if __name__ == "__main__":
    # 测试示例
    test_cases = [
        {
            "title": "基于深度学习的医学图像诊断研究",
            "abstract": "",
            "domain": "medicine"
        },
        {
            "title": "Transformer模型在自然语言处理中的应用",
            "abstract": "",
            "domain": "computer_science"
        },
        {
            "title": "在线教育平台用户行为分析研究",
            "abstract": "",
            "domain": "education"
        }
    ]
    
    extractor = KeywordExtractor()
    
    for case in test_cases:
        print("=" * 70)
        print()
        report = extractor.analyze(case['title'], case['abstract'], case['domain'])
        print_analysis_report(report)
        print()
