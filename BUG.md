# Bug 报告 - Literature Survey v2.0

本文档记录项目中已知的问题和待修复的bug。

**最后更新**: 2024-03-06  
**版本**: v2.0.0

---

## 🔴 严重 (Critical)

### BUG-001: f-string 语法错误导致无法编译

**位置**: `scripts/citation_formatter.py:224`

**问题描述**:
```python
lines = [f"@{bibtex_type}{{{cite_key}}},"]
#                           ^ 单个大括号在f-string中会导致SyntaxError
```

**错误信息**:
```
SyntaxError: f-string: single '}' is not allowed
```

**影响**: 整个模块无法导入和使用

**修复建议**:
```python
# 方案1: 使用双大括号转义
lines = [f"@{bibtex_type}{{{cite_key}}},"]

# 方案2: 使用format方法
lines = ["@{}{{{}}},".format(bibtex_type, cite_key)]

# 方案3: 字符串拼接
lines = ["@" + bibtex_type + "{" + cite_key + "},"]
```

**优先级**: 🔴 P0 - 阻塞性问题

---

### BUG-002: LLM 客户端未实现导致核心功能不可用

**位置**: 
- `scripts/ai_keyword_extractor.py:345`
- `scripts/ai_strategy_planner.py:358`

**问题描述**:
```python
async def _call_llm(self, system_prompt: str, ...):
    if self.llm is None:
        return self._mock_llm_response(user_prompt)  # 仅返回模拟数据
    raise NotImplementedError("LLM client not implemented")
```

**影响**: 
- AI关键词提取功能无法正常工作
- AI策略规划功能无法正常工作
- 核心AI驱动流程无法运行

**修复建议**:
1. 实现 OpenAI 客户端封装
2. 实现 Anthropic 客户端封装
3. 提供统一的LLM调用接口

```python
# 建议实现
class LLMClient:
    def __init__(self, provider: str, api_key: str, ...):
        self.provider = provider
        # 初始化对应客户端
    
    async def complete(self, system: str, user: str, ...) -> str:
        if self.provider == "openai":
            return await self._call_openai(...)
        elif self.provider == "anthropic":
            return await self._call_anthropic(...)
```

**优先级**: 🔴 P0 - 核心功能缺失

---

## 🟠 高优先级 (High)

### BUG-003: 核心工作流功能未实现（仅TODO标记）

**位置**: `scripts/ai_workflow.py`

**问题描述**:
代码中多处功能只有TODO标记，未实际实现：

```python
# Line 174-176
# Phase 3: 并行文献搜索（待实现具体搜索逻辑）
print("  (此阶段需要接入具体的搜索API)")
# TODO: 实现并行搜索

# Line 184-186  
# Phase 4: 智能去重
print("  (此阶段需要实际文献数据)")
# TODO: 实现去重

# Line 197
# TODO: 添加文献到引用管理器

# Line 201
# Phase 6: 综述生成（待实现）
print("  (此阶段需要接入LLM进行撰写)")
```

**缺失功能**:
1. 并行文献搜索（所有数据库）
2. 智能去重算法
3. 文献添加到引用管理器
4. 综述生成（Writing模块）
5. 质量审查（Reviewer模块）

**影响**: 工作流无法完成完整的文献综述生成

**优先级**: 🟠 P1 - 功能不完整

---

### BUG-004: 缺少必要的数据库适配器实现

**位置**: 项目整体

**问题描述**:
配置文件 `config.yaml` 中配置了多个数据库，但没有对应的适配器实现：

| 数据库 | 配置 | 适配器 | 状态 |
|--------|------|--------|------|
| EXA | ✅ | ❌ | 缺失 |
| Semantic Scholar | ✅ | ❌ | 缺失 |
| PubMed | ✅ | ❌ | 缺失 |
| arXiv | ✅ | ❌ | 缺失 |
| CNKI | ✅ | ❌ | 缺失 |
| OpenAlex | ✅ | ❌ | 缺失 |

**影响**: 无法执行实际的文献搜索

**修复建议**:
为每个数据库创建适配器类：
```python
# adapters/exa_adapter.py
class ExaAdapter:
    async def search(self, query: str, ...) -> List[Paper]:
        ...

# adapters/semantic_scholar_adapter.py  
class SemanticScholarAdapter:
    async def search(self, query: str, ...) -> List[Paper]:
        ...
```

**优先级**: 🟠 P1 - 核心功能缺失

---

### BUG-005: 模块导入问题

**位置**: `scripts/ai_keyword_extractor.py:416`

**问题描述**:
```python
def _extract_json_from_text(self, text: str) -> Dict:
    import re  # 在函数内部导入，应该放在文件顶部
```

**问题**:
- `re` 模块在函数内导入，违反PEP8规范
- 可能导致性能问题（每次调用都重新导入）

**修复建议**:
```python
# 移到文件顶部
import re

class AIKeywordExtractor:
    ...
```

**优先级**: 🟡 P2 - 代码规范

---

## 🟡 中优先级 (Medium)

### BUG-006: 模拟数据在生产环境可能误导用户

**位置**:
- `scripts/ai_keyword_extractor.py:347-416`
- `scripts/ai_strategy_planner.py:360-427`

**问题描述**:
当 `llm is None` 时，系统返回模拟数据而不是报错：

```python
def _mock_llm_response(self, prompt: str) -> str:
    # 返回固定的测试数据
    if "深度学习" in prompt:
        return json.dumps({...})
```

**风险**:
1. 用户可能误以为功能正常工作
2. 生产环境返回虚假数据
3. 难以发现LLM配置问题

**修复建议**:
```python
async def _call_llm(self, ...):
    if self.llm is None:
        if os.getenv("LIT_SURVEY_MOCK_MODE") == "true":
            return self._mock_llm_response(user_prompt)
        raise RuntimeError(
            "LLM client not configured. "
            "Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable."
        )
```

**优先级**: 🟡 P2 - 用户体验

---

### BUG-007: 路径变量解析可能失败

**位置**: `scripts/config_manager.py:177-200`

**问题描述**:
```python
def resolve_path(self, path_template: str, **extra_vars) -> str:
    # 递归解析变量，但没有检测循环引用
    max_iterations = 10
    result = path_template
    
    for _ in range(max_iterations):
        new_result = self.VAR_PATTERN.sub(...)
        if new_result == result:
            break
        result = new_result
```

**问题**:
1. 循环引用检测缺失（如 `{A}` → `{B}` → `{A}`）
2. 未解析的变量会原样保留，可能导致路径错误
3. 变量名冲突时没有警告

**修复建议**:
```python
def resolve_path(self, path_template: str, **extra_vars) -> str:
    seen = set()
    max_iterations = 10
    result = path_template
    
    for i in range(max_iterations):
        if result in seen:
            raise ValueError(f"Circular reference detected: {path_template}")
        seen.add(result)
        
        new_result = self.VAR_PATTERN.sub(...)
        
        # 检查未解析的变量
        unresolved = self.VAR_PATTERN.findall(new_result)
        if unresolved and i == max_iterations - 1:
            raise ValueError(f"Unresolved variables: {unresolved}")
        
        if new_result == result:
            break
        result = new_result
```

**优先级**: 🟡 P2 - 健壮性

---

### BUG-008: 异步代码缺少错误处理

**位置**: `scripts/verify_references.py`

**问题描述**:
多个异步方法缺少try-except块：

```python
async def _query_crossref(self, doi: str) -> Dict:
    async with self.session.get(url) as response:
        if response.status == 200:
            return await response.json()
        # 其他状态码未处理
```

**问题**:
- 网络错误未捕获
- API返回非200状态码未处理
- 可能导致整个工作流中断

**修复建议**:
```python
async def _query_crossref(self, doi: str) -> Dict:
    try:
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                return {"status": "not_found"}
            else:
                response.raise_for_status()
    except aiohttp.ClientError as e:
        logger.error(f"Crossref query failed for {doi}: {e}")
        return {"status": "error", "message": str(e)}
```

**优先级**: 🟡 P2 - 健壮性

---

## 🟢 低优先级 (Low)

### BUG-009: 类型注解不完整

**位置**: 多个文件

**问题描述**:
部分函数缺少返回类型注解：

```python
# scripts/keyword_extractor.py
def calculate_similarity(str1: str, str2: str):  # 缺少 -> float
    ...

# scripts/deduplicate_papers.py  
def normalize_doi(doi: str):  # 缺少 -> str
    ...
```

**影响**: 代码可读性和IDE自动补全

**优先级**: 🟢 P3 - 代码质量

---

### BUG-010: 硬编码的默认值

**位置**: `scripts/ai_keyword_extractor.py`

**问题描述**:
```python
# Line 86
DOMAIN_TEMPLATES = {
    "computer_science": {
        "method_keywords": ["algorithm", "model", "approach", ...],
        # 硬编码的学科关键词
    }
}
```

**问题**:
- 学科关键词硬编码，难以扩展
- 无法通过配置更新

**修复建议**:
```python
# 从配置文件加载
DOMAIN_TEMPLATES = load_domain_templates()

# 或在初始化时传入
extractor = AIKeywordExtractor(
    domain_templates=custom_templates
)
```

**优先级**: 🟢 P3 - 可维护性

---

### BUG-011: 缺少输入验证

**位置**: 多个模块

**问题描述**:
公共方法缺少参数验证：

```python
# scripts/citation_manager.py
def add_paper(self, paper: Paper, assign_id: bool = True) -> str:
    # 没有验证paper是否为空
    # 没有验证必要字段是否存在
```

**修复建议**:
```python
def add_paper(self, paper: Paper, assign_id: bool = True) -> str:
    if paper is None:
        raise ValueError("paper cannot be None")
    if not paper.title:
        raise ValueError("paper.title is required")
    # ...
```

**优先级**: 🟢 P3 - 健壮性

---

## 📝 改进建议 (Enhancements)

### ENH-001: 添加单元测试

**描述**: 项目缺少单元测试覆盖

**建议**:
```
tests/
├── test_keyword_extractor.py
├── test_citation_manager.py
├── test_config_manager.py
└── test_ai_workflow.py
```

**优先级**: 🟡 P2

---

### ENH-002: 添加日志系统

**描述**: 目前使用print输出，应使用标准日志库

**建议**:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing paper: %s", paper.title)
logger.error("Failed to download PDF: %s", e)
```

**优先级**: 🟡 P2

---

### ENH-003: 添加进度指示器

**描述**: 长时间运行的任务缺少进度反馈

**建议**:
```python
from tqdm import tqdm

for paper in tqdm(papers, desc="Analyzing papers"):
    await analyze_paper(paper)
```

**优先级**: 🟢 P3

---

## 📊 Bug 统计

| 级别 | 数量 | 状态 |
|------|------|------|
| 🔴 Critical | 2 | 待修复 |
| 🟠 High | 2 | 待修复 |
| 🟡 Medium | 4 | 待修复 |
| 🟢 Low | 3 | 待修复 |
| **总计** | **11** | - |

---

## 🔧 修复路线图

### 第一阶段 (v2.0.1) - 紧急修复
- [ ] BUG-001: f-string语法错误
- [ ] BUG-002: 实现LLM客户端

### 第二阶段 (v2.1.0) - 功能完善
- [ ] BUG-003: 实现核心工作流功能
- [ ] BUG-004: 实现数据库适配器
- [ ] ENH-002: 添加日志系统

### 第三阶段 (v2.2.0) - 质量提升
- [ ] BUG-005, BUG-009: 代码规范
- [ ] BUG-006, BUG-007, BUG-008: 健壮性改进
- [ ] ENH-001: 单元测试

---

## 💡 如何贡献

如果您发现了新的bug或有修复建议：

1. 在此文件中添加bug描述
2. 提交PR修复
3. 更新测试用例

**报告格式**:
```markdown
### BUG-XXX: [标题]

**位置**: [文件:行号]

**问题描述**: [详细描述]

**复现步骤**: [步骤]

**预期行为**: [描述]

**实际行为**: [描述]

**修复建议**: [建议]

**优先级**: [级别]
```
