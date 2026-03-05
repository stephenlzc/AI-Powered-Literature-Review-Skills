# AI LLM驱动架构使用指南

## 快速开始

### 1. 配置环境变量

复制环境变量模板并填写：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API Keys
```

必需的环境变量：
- `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`: LLM API
- `EXA_API_KEY`: EXA神经网络搜索引擎 (推荐)

可选的环境变量：
- `PUBMED_API_KEY` 和 `PUBMED_EMAIL`: PubMed医学文献
- `LIT_SURVEY_BASE_DIR`: 自定义输出目录

### 2. 配置文件

编辑 `config.yaml` 调整系统行为：

```yaml
# 启用/禁用EXA搜索
search:
  exa:
    enabled: true
    num_results: 50
    
# 选择LLM模型
llm:
  model_selection:
    query_analysis: "gpt-4o"
    synthesis: "gpt-4o"
```

### 3. 路径管理

新的路径系统支持多种配置方式：

```python
# 方式1: 从环境变量加载
from core.path_config import PathConfig
config = PathConfig.from_env()

# 方式2: 从配置文件加载
config = PathConfig.from_config_file("config.yaml")

# 方式3: 使用运行时解析器
from core.path_config import RuntimePathResolver
resolver = RuntimePathResolver(config, session_id="20240305_test")
output_path = resolver.get_output_path("results.json")
```

### 4. EXA搜索集成

```python
import asyncio
from adapters.exa_adapter import EXAAdapter, EXASearchConfig

async def search():
    config = EXASearchConfig(
        api_key="exa-your-api-key",
        search_type="neural",
        num_results=50
    )
    
    adapter = EXAAdapter(config)
    
    # 语义搜索
    results = await adapter.discover(
        "Transformer attention mechanisms for medical image analysis",
        year_range=(2020, 2024)
    )
    
    # 相似性扩展
    expanded = await adapter.expand_similar(results[:3], num_results_per_paper=5)
    
    return results + expanded

asyncio.run(search())
```

### 5. LLM查询分析

```python
import asyncio
from core.query_analyzer import LLMQueryAnalyzer

async def analyze():
    analyzer = LLMQueryAnalyzer(llm_client)
    
    result = await analyzer.analyze(
        query="基于深度学习的医学图像诊断研究",
        context="本研究探讨深度学习在医学图像分析中的应用..."
    )
    
    print(f"识别领域: {result.domain.value}")
    print(f"中文关键词: {result.keywords_zh}")
    print(f"EXA查询: {result.search_queries['exa']}")
    print(f"CNKI查询: {result.search_queries['cnki']}")

asyncio.run(analyze())
```

## 架构组件概览

| 组件 | 文件 | 功能 |
|------|------|------|
| PathConfig | `core/path_config.py` | 路径管理，支持环境变量和模板变量 |
| EXAAdapter | `adapters/exa_adapter.py` | EXA神经网络搜索引擎适配器 |
| LLMQueryAnalyzer | `core/query_analyzer.py` | LLM驱动的查询分析器 |
| config.yaml | 配置文件 | 系统配置，功能开关 |
| .env | 环境变量 | API Keys和路径配置 |

## 特性对比

| 功能 | 传统方式 | AI驱动方式 |
|------|---------|-----------|
| 关键词提取 | 硬编码TERM_MAPPINGS | LLM智能分词 |
| 领域识别 | 用户指定 | LLM自动识别 |
| 搜索策略 | 布尔逻辑检索 | EXA语义搜索 + 传统检索 |
| 路径管理 | 硬编码绝对路径 | 环境变量 + 动态解析 |
| 综述生成 | 模板填充 | LLM生成，逻辑连贯 |

## 依赖安装

```bash
# 核心依赖
pip install exa-py pyyaml

# 可选依赖
pip install networkx  # 用于交叉引用分析
pip install aiohttp   # 用于异步HTTP请求
```

## 更多信息

详见 `ARCHITECTURE.md` 了解完整的架构设计。
