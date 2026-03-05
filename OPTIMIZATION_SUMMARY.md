# 优化总结 - AI驱动文献综述 v2.0

本文档总结了基于DIFY工作流的优化内容。

---

## 🎯 优化点总览

### 1. ✅ LLM驱动的关键词提取

**原方案**: 基于规则的关键词匹配  
**优化后**: AI智能提取中英文双语关键词

**新特性**:
- 自动识别学科领域
- 生成同义词、缩写、相关词
- 自动构建多数据库检索表达式
- 支持中英文双语输出

**文件**: `scripts/ai_keyword_extractor.py`

**使用示例**:
```python
from scripts import extract_keywords

result = await extract_keywords(
    query="基于深度学习的医学图像诊断研究",
    year_range=(2020, 2024),
    target_language="both"
)

print(result.keywords.en.primary)  # ['deep learning', 'medical imaging', ...]
print(result.keywords.zh.primary)  # ['深度学习', '医学图像', ...]
```

---

### 2. ✅ 优化的文献交叉引用方案

**原方案**: 简单的Markdown链接  
**优化后**: 支持多种交叉引用格式

**支持的格式**:
- **Word书签**: 可点击跳转到参考文献
- **Markdown链接**: 支持超链接跳转
- **行内编号**: `[C1]`, `[E1]` 格式
- **作者-年份**: `(Smith et al., 2023)`

**文件**: `scripts/citation_manager.py`

**使用示例**:
```python
from scripts import create_citation_manager

manager = create_citation_manager(
    style="gb7714",
    cross_ref="bookmark"  # bookmark/hyperlink/both
)

# 添加文献
manager.add_paper(paper)

# 生成引用
print(manager.format_citation("C1"))  # [C1]
print(manager.format_citation(["C1", "E1"]))  # [C1,E1]

# 生成参考文献列表
refs = manager.generate_reference_list("markdown")
```

---

### 3. ✅ 动态路径管理（无硬编码绝对路径）

**原方案**: 硬编码绝对路径  
**优化后**: 模板化路径，支持运行时变量

**支持的变量**:
- `{PROJECT_ROOT}` - 项目根目录
- `{SESSION_ID}` - 会话ID
- `{DATE}` - 当前日期
- `{TOPIC}` - 研究主题
- 用户自定义变量

**文件**: `scripts/config_manager.py`

**配置示例** (`config.yaml`):
```yaml
paths:
  base_dir: "{PROJECT_ROOT}/sessions/{DATE}_{SESSION_ID}"
  output_dir: "{base_dir}/output"
  filenames:
    final: "文献综述_{TOPIC}_{DATE}.md"
```

**使用示例**:
```python
from scripts import load_config

config = load_config()
config.set_runtime_var("SESSION_ID", "my_session")
config.set_runtime_var("TOPIC", "深度学习医学图像")

# 自动解析变量
output_path = config.get_full_path("final")
# 结果: ./sessions/20240306_my_session/output/文献综述_深度学习医学图像_20240306.md
```

---

### 4. ✅ AI驱动的工作流决策

**原方案**: 固定的流程和规则  
**优化后**: AI自动决策和动态调整

**AI决策能力**:
1. **自动领域识别**: AI分析主题，识别学科领域
2. **智能数据库选择**: 根据领域自动选择最合适的数据库
3. **自适应检索策略**: 根据初步结果动态调整
4. **质量阈值自适应**: 根据文献丰度自动调整质量标准

**文件**: `scripts/ai_strategy_planner.py`

**使用示例**:
```python
from scripts import create_strategy

plan = await create_strategy(
    query="基于深度学习的医学图像诊断研究",
    year_range=(2020, 2024),
    num_papers=50
)

print(plan.domain_analysis)  # 领域分析结果
print(plan.selected_databases)  # AI选择的数据库
print(plan.search_strategy)  # 检索策略
```

---

## 📁 新增文件清单

| 文件 | 大小 | 功能 |
|------|------|------|
| `config.yaml` | 10KB | 完整的配置文件模板 |
| `.env.example` | 1.7KB | 环境变量示例文件 |
| `scripts/config_manager.py` | 16KB | 动态配置管理 |
| `scripts/ai_strategy_planner.py` | 17KB | AI策略规划器 |
| `scripts/ai_keyword_extractor.py` | 17KB | AI关键词提取 |
| `scripts/citation_manager.py` | 18KB | 引用管理器（支持交叉引用） |
| `scripts/ai_workflow.py` | 13KB | AI工作流主控 |
| `scripts/__init__.py` | 2KB | 更新后的模块导出 |

---

## 🔄 与DIFY工作流的集成

### DIFY工作流中的Prompts迁移

从您的DIFY工作流中提取的Prompts已整合到以下模块：

1. **Keywords节点** → `ai_keyword_extractor.py`
2. **Outline节点** → 策略规划器的大纲生成功能
3. **Writing节点** → 待整合到综述生成模块
4. **Reviewer节点** → 待整合到质量审查模块

### EXA搜索集成

EXA API配置已添加到配置文件中：

```yaml
databases:
  exa:
    api_key: "${EXA_API_KEY}"
    base_url: "https://api.exa.ai"
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pyyaml aiohttp
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的API Keys
```

### 3. 运行工作流

```bash
# 命令行方式
python scripts/ai_workflow.py "基于深度学习的医学图像诊断研究" \
    --year-start 2020 \
    --year-end 2024 \
    --num-papers 50

# 或Python代码方式
from scripts import run_workflow

results = await run_workflow(
    query="基于深度学习的医学图像诊断研究",
    year_range=(2020, 2024),
    interactive=True
)
```

---

## 📊 优化效果对比

| 维度 | 优化前 | 优化后 |
|------|--------|--------|
| 关键词提取 | 基于规则，固定词库 | AI智能提取，双语支持 |
| 交叉引用 | Markdown链接 | Word书签+超链接 |
| 路径管理 | 硬编码绝对路径 | 模板化，运行时解析 |
| 数据库选择 | 固定EXA | AI动态选择多数据库 |
| 策略调整 | 人工调整 | AI自适应调整 |
| 配置方式 | 代码修改 | YAML配置+环境变量 |

---

## 🎓 使用建议

### 对于DIFY用户

1. 可以将 `ai_keyword_extractor.py` 和 `ai_strategy_planner.py` 作为自定义节点集成到DIFY
2. 使用 `citation_manager.py` 的Prompt优化交叉引用格式
3. 配置管理逻辑可以迁移到DIFY的环境变量配置中

### 对于Kimi CLI用户

1. 使用 `run_workflow()` 函数一键运行完整流程
2. 通过 `config.yaml` 自定义各种参数
3. 使用交互式模式进行配置

---

## 🔮 后续优化建议

1. **完整集成EXA搜索**: 实现 `exa_adapter.py` 模块
2. **综述生成模块**: 整合DIFY的Writing和Reviewer Prompts
3. **并行搜索**: 实现多数据库并行检索
4. **PDF自动下载**: 集成Unpaywall等开放获取服务
5. **Word文档生成**: 使用python-docx生成带书签的Word文档

---

## 📚 相关文档

- `README.md` - 项目说明
- `SKILL.md` - Skill主入口
- `AGENTS.md` - 项目架构文档
- `scripts/README.md` - 脚本使用指南
