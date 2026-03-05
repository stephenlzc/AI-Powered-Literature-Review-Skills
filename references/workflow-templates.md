# 工作流模板参考

提供不同场景下的文献调研工作流配置模板。

---

## 快速检索模板

**适用场景**：快速了解一个新领域，获取核心文献

**预期耗时**：15-30分钟

**预期文献量**：20-30篇

### Phase 配置

| Phase | 启用 | 配置 |
|-------|------|------|
| 0 Session Log | ✅ | 基础日志 |
| 1 Query Analysis | ✅ | 简化关键词提取 |
| 2 Parallel Search | ✅ | 2-3个数据库 |
| 3 Deduplication | ✅ | 自动去重 |
| 4 Verification | ✅ | DOI验证 |
| 5 PDF Management | ❌ | 跳过 |
| 6 Citation Export | ✅ | GB/T 7714 |
| 7 Synthesis | ❌ | 跳过 |

### 检索策略

**中文**：
- CNKI：主题检索，近5年，CSSCI/北大核心
- 检索式：`SU=('核心概念')*('应用领域')`

**英文**：
- Semantic Scholar：主题检索，高被引优先
- arXiv：预印本，最新研究

### 输出

- 文献列表（GB/T 7714-2015 格式）
- 简单的分类列表

---

## 系统性综述模板

**适用场景**：撰写系统性文献综述（Systematic Review）

**预期耗时**：2-4小时

**预期文献量**：50-100篇

### Phase 配置

| Phase | 启用 | 配置 |
|-------|------|------|
| 0 Session Log | ✅ | 详细日志 |
| 1 Query Analysis | ✅ | 完整关键词扩展 |
| 2 Parallel Search | ✅ | 全部数据库 |
| 3 Deduplication | ✅ | 多层去重 |
| 4 Verification | ✅ | 完整验证 |
| 5 PDF Management | ✅ | 下载PDF |
| 6 Citation Export | ✅ | 多格式导出 |
| 7 Synthesis | ✅ | 完整综述 |

### 检索策略（PRISMA 流程）

```
识别阶段:
├── 中文数据库:
│   ├── CNKI (n=?)
│   ├── 万方 (n=?)
│   └── 维普 (n=?)
│
└── 英文数据库:
    ├── PubMed (n=?)
    ├── Semantic Scholar (n=?)
    ├── IEEE Xplore (n=?)
    └── Web of Science (n=?)

筛选阶段:
├── 去重后 (n=?)
├── 标题摘要筛选 (n=?)
└── 全文筛选 (n=?)

纳入阶段:
└── 最终纳入 (n=?)
```

### 中文检索式示例

```
# CNKI
SU=('深度学习'+'深度神经网络'+'DNN')*('医学图像'+'医学影像'+'医疗图像')*('诊断'+'检测'+'识别')

来源类别：CSSCI、北大核心、CSCD
时间范围：2020-2025
```

### 英文检索式示例

**PubMed**:
```
("deep learning"[MeSH Terms] OR "deep learning"[Title/Abstract] OR "neural network"[Title/Abstract]) 
AND ("medical imaging"[Title/Abstract] OR "radiology"[Title/Abstract]) 
AND ("diagnosis"[Title/Abstract] OR "detection"[Title/Abstract])

Filters: 2020/1/1 - 3000/12/31, Humans, English
```

**Semantic Scholar**:
```
("deep learning" OR "deep neural network" OR "convolutional neural network") 
AND ("medical image" OR "medical imaging" OR "radiology") 
AND ("diagnosis" OR "classification" OR "detection")

Year: 2020-2025
Fields of Study: Medicine, Computer Science
```

### 筛选标准

**纳入标准**：
1. 研究主题相关
2. 使用深度学习方法
3. 应用于医学图像
4. 近5年发表
5. 同行评审期刊或顶会

**排除标准**：
1. 非医学应用领域
2. 非图像数据
3. 纯理论/综述文章（除非高被引）
4. 无法获取全文
5. 非英文/中文

### 质量评估清单

- [ ] 检索策略清晰、可重复
- [ ] 覆盖多个数据库
- [ ] 纳入/排除标准明确
- [ ] 文献筛选过程记录完整
- [ ] PRISMA 流程图
- [ ] 风险偏倚评估

### 输出

1. PRISMA 流程图
2. 文献特征表
3. 质量评估结果
4. 系统性综述文档
5. 参考文献列表

---

## 文献计量分析模板

**适用场景**：分析某领域的研究趋势、热点、合作网络

**预期耗时**：3-6小时

**预期文献量**：200-500篇

### Phase 配置

| Phase | 启用 | 配置 |
|-------|------|------|
| 0 Session Log | ✅ | 详细日志 |
| 1 Query Analysis | ✅ | 广泛关键词 |
| 2 Parallel Search | ✅ | 全部数据库，大样本 |
| 3 Deduplication | ✅ | 严格去重 |
| 4 Verification | ✅ | 抽样验证 |
| 5 PDF Management | ❌ | 选择性下载 |
| 6 Citation Export | ✅ | 包含引用关系 |
| 7 Synthesis | ✅ | 计量分析 |

### 分析指标

**时间趋势**：
- 年度发文量
- 引用趋势
- 研究生命周期

**空间分布**：
- 国家/地区分布
- 机构合作网络
- 作者合作网络

**主题演化**：
- 关键词共现
- 主题聚类
- 研究前沿识别

**引用网络**：
- 高被引文献
- 知识基础
- 引文突现

### Python 分析代码框架

```python
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# 加载数据
df = pd.read_json('papers.json')

# 年度趋势
yearly_counts = df['year'].value_counts().sort_index()
plt.plot(yearly_counts.index, yearly_counts.values)
plt.title('Publication Trend')
plt.xlabel('Year')
plt.ylabel('Count')

# 期刊分布
top_journals = df['journal'].value_counts().head(10)
top_journals.plot(kind='barh')

# 作者合作网络
from networkx import Graph
G = Graph()
for authors in df['authors']:
    for i, a1 in enumerate(authors):
        for a2 in authors[i+1:]:
            G.add_edge(a1, a2)
```

### 可视化输出

- 年度发文趋势图
- 国家/机构合作网络图
- 关键词共现网络
- 引文时区图

---

## 模板选择决策树

```
开始
│
├─ 需要快速了解领域？
│  └─ 是 → 快速检索模板
│
├─ 需要撰写正式综述？
│  ├─ 系统性综述？
│  │  └─ 是 → 系统性综述模板
│  │
│  └─ 叙述性综述？
│     └─ 是 → 系统性综述模板（简化版）
│
├─ 需要分析研究趋势？
│  └─ 是 → 文献计量分析模板
│
└─ 特定用途？
   ├─ Meta分析 → 系统性综述模板（严格筛选）
   ├─ 技术路线调研 → 快速检索模板
   └─ 竞争情报 → 文献计量分析模板
```

---

## 推荐工具

### 文献检索
- **Zotero** + **Zotero Connector**: 文献管理
- **ResearchRabbit**: 文献网络探索
- **Connected Papers**: 可视化文献网络

### 计量分析
- **VOSviewer**: 知识图谱可视化
- **CiteSpace**: 科学计量与知识图谱
- **Gephi**: 网络分析

### 综述撰写
- **Rayyan**: 系统性综述筛选
- **Covidence**: Cochrane推荐
- **DistillerSR**: 企业级筛选工具

---

## PRISMA 资源

- PRISMA 2020 声明: http://prisma-statement.org/
- PRISMA 流程图生成器: http://prisma-statement.org/PRISMAStatement/FlowDiagram.aspx
- PRISMA 检查清单: http://prisma-statement.org/documents/PRISMA_2020_checklist.pdf
