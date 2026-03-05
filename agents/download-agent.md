# Download Agent 模板

用于下载文献PDF的专用Agent。

---

## Agent 信息

| 属性 | 值 |
|------|-----|
| **名称** | Download Agent |
| **类型** | Bash Agent / Task Agent |
| **用途** | 文献PDF下载和管理 |
| **关键规则** | 尊重版权，仅下载开放获取或有权限的文献 |

---

## 核心原则

> **LEGAL NOTICE**: Only download papers you have legal access to. This includes:
> - Open access papers
> - Papers from your institutional subscriptions
> - Papers for which you have explicit permission
> - Fair use for educational/research purposes where permitted

---

## 任务描述

为已验证的文献获取PDF文件，优先使用开放获取渠道。

---

## 输入格式

```json
{
  "papers": [
    {
      "id": "E1",
      "title": "Deep learning for image recognition",
      "doi": "10.1038/nature14539",
      "pdf_url": null,
      "is_oa": false,
      "open_access_info": {
        "is_oa": false,
        "oa_status": "closed"
      }
    }
  ],
  "session_id": "20240115_dl_survey",
  "output_dir": "./literature/pdfs",
  "naming_scheme": "{id}_{first_author}_{year}_{short_title}",
  "max_file_size_mb": 50,
  "timeout_seconds": 120,
  "verify_downloads": true
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `papers` | Array | 是 | 待下载的文献列表 |
| `session_id` | String | 是 | 会话标识 |
| `output_dir` | String | 否 | 输出目录（默认./literature/pdfs） |
| `naming_scheme` | String | 否 | 文件命名模板 |
| `max_file_size_mb` | Integer | 否 | 最大文件大小（默认50MB） |
| `timeout_seconds` | Integer | 否 | 下载超时（默认120秒） |
| `verify_downloads` | Boolean | 否 | 验证下载完整性（默认true） |

---

## PDF获取优先级

### 渠道优先级

```
1. 直接PDF链接（从数据库获取的pdf_url）
   └─ 最快，但需要数据库支持
   
2. Unpaywall API（开放获取检查）
   └─ 覆盖广泛，合法合规
   
3. 预印本服务器
   ├─ arXiv (arxiv.org)
   ├─ bioRxiv (biorxiv.org)
   ├─ medRxiv (medrxiv.org)
   └─ SSRN (ssrn.com)
   
4. 机构访问（需要用户配置）
   └─ 通过机构订阅访问
   
5. 作者主页/ResearchGate
   └─ 尝试获取，成功率较低
```

### 各渠道详细说明

#### 1. Unpaywall API

```python
import requests

def get_unpaywall_pdf(doi, email):
    url = f"https://api.unpaywall.org/v2/{doi}"
    response = requests.get(url, params={"email": email})
    data = response.json()
    
    if data.get("is_oa"):
        best_oa = data.get("best_oa_location", {})
        return {
            "pdf_url": best_oa.get("url_for_pdf"),
            "landing_page": best_oa.get("url_for_landing_page"),
            "version": best_oa.get("version"),  # publishedVersion, acceptedVersion, submittedVersion
            "license": best_oa.get("license")
        }
    return None
```

#### 2. arXiv

```python
def get_arxiv_pdf(arxiv_id):
    # arXiv ID格式: 1706.03762 或 arxiv:1706.03762
    arxiv_id = arxiv_id.replace("arxiv:", "").strip()
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
```

#### 3. 直接下载

```python
import requests
from pathlib import Path

def download_pdf(url, output_path, timeout=120, max_size_mb=50):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AcademicResearch/1.0)"
    }
    
    response = requests.get(url, headers=headers, timeout=timeout, stream=True)
    response.raise_for_status()
    
    # 检查文件大小
    content_length = response.headers.get('content-length')
    if content_length:
        size_mb = int(content_length) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise FileTooLarge(f"File size {size_mb:.1f}MB exceeds limit")
    
    # 验证内容类型
    content_type = response.headers.get('content-type', '')
    if 'pdf' not in content_type.lower():
        # 有些服务器不设置正确的content-type
        pass  # 继续下载，后续验证
    
    # 下载文件
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return output_path
```

---

## 执行步骤

### Step 1: 准备下载

1. 创建输出目录
2. 检查已有文件（避免重复下载）
3. 初始化下载日志

### Step 2: 渠道选择

为每篇文献确定最佳下载渠道：

```python
def select_download_channel(paper):
    # 1. 如果有直接PDF链接
    if paper.get("pdf_url"):
        return "direct", paper["pdf_url"]
    
    # 2. 检查Unpaywall
    if paper.get("doi"):
        unpaywall = check_unpaywall(paper["doi"])
        if unpaywall and unpaywall.get("pdf_url"):
            return "unpaywall", unpaywall["pdf_url"]
    
    # 3. 检查是否为预印本
    if "arxiv" in paper.get("source_db", "").lower():
        arxiv_id = extract_arxiv_id(paper)
        if arxiv_id:
            return "arxiv", f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # 4. 无可用渠道
    return None, None
```

### Step 3: 执行下载

```python
for paper in papers:
    channel, url = select_download_channel(paper)
    
    if not channel:
        log_failed(paper, "No download channel available")
        continue
    
    try:
        filename = generate_filename(paper)
        output_path = f"{output_dir}/{filename}"
        
        # 检查是否已存在
        if Path(output_path).exists():
            log_skip(paper, "File already exists")
            continue
        
        # 下载
        download_pdf(url, output_path, timeout, max_size_mb)
        
        # 验证
        if verify_downloads:
            if not verify_pdf(output_path):
                raise InvalidPDF("Downloaded file is not a valid PDF")
        
        log_success(paper, output_path, channel)
        
    except Exception as e:
        log_failed(paper, str(e))
```

### Step 4: 验证下载

```python
def verify_pdf(file_path):
    """验证文件是否为有效的PDF"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            return header.startswith(b'%PDF-')
    except Exception:
        return False
```

### Step 5: 生成报告

记录下载结果到日志文件。

---

## 文件命名规范

### 命名模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{id}` | 文献编号 | E1, C1 |
| `{first_author}` | 第一作者姓氏 | LeCun, 张三 |
| `{year}` | 发表年份 | 2015 |
| `{short_title}` | 缩短的标题 | Deep_learning_image |
| `{journal}` | 期刊名缩写 | Nature |

### 默认命名格式

```
{ID}_{FirstAuthor}_{Year}_{ShortTitle}.pdf

示例：
E1_LeCun_2015_Deep_learning_image_recognition.pdf
C1_张三_2023_基于深度学习的图像识别研究.pdf
E2_Vaswani_2017_Attention_is_all_you_need.pdf
```

### 生成短标题

```python
def generate_short_title(title, max_words=5):
    """生成短标题（用于文件名）"""
    # 移除标点，分割单词
    words = re.sub(r'[^\w\s]', '', title).split()
    # 取前N个单词
    short = '_'.join(words[:max_words])
    return short
```

---

## 输出格式

```json
{
  "agent": "download",
  "session_id": "20240115_dl_survey",
  "timestamp": "2024-01-15T10:40:00Z",
  "summary": {
    "total": 50,
    "successful": 42,
    "failed": 5,
    "skipped": 3,
    "total_size_mb": 256.5
  },
  "successful": [
    {
      "id": "E1",
      "title": "Deep learning for image recognition",
      "channel": "unpaywall",
      "file_path": "./literature/pdfs/E1_LeCun_2015_Deep_learning_image.pdf",
      "file_size_mb": 3.2,
      "download_time_sec": 4.5
    }
  ],
  "failed": [
    {
      "id": "E15",
      "title": "...",
      "reason": "Paywall - no open access available",
      "attempted_channels": ["unpaywall", "direct"]
    }
  ],
  "skipped": [
    {
      "id": "E23",
      "reason": "File already exists"
    }
  ]
}
```

---

## 错误处理

### 常见错误类型

| 错误代码 | 含义 | 处理建议 |
|----------|------|---------|
| `PAYWALL` | 付费墙，无开放获取 | 记录，跳过 |
| `TIMEOUT` | 下载超时 | 重试或跳过 |
| `FILE_TOO_LARGE` | 文件超过大小限制 | 跳过 |
| `NETWORK_ERROR` | 网络错误 | 重试 |
| `INVALID_PDF` | 下载的不是有效PDF | 删除，尝试其他渠道 |
| `ACCESS_DENIED` | 访问被拒绝 | 跳过 |
| `NOT_FOUND` | 404错误 | 跳过 |

### 付费墙处理

```python
class PaywallError(Exception):
    """遇到付费墙"""
    pass

def handle_paywall(paper):
    # 1. 记录到failed列表
    log_failed(paper, "Paywall")
    
    # 2. 尝试其他渠道
    for channel in ["unpaywall", "arxiv", "institution"]:
        try:
            return try_channel(paper, channel)
        except PaywallError:
            continue
    
    # 3. 所有渠道都失败
    return None
```

---

## 文件组织

### 目录结构

```
project/
└── literature/
    ├── pdfs/                          # PDF文件
    │   ├── E1_LeCun_2015_....pdf
    │   ├── E2_Vaswani_2017_....pdf
    │   └── ...
    ├── metadata/
    │   ├── papers_index.json          # 文献索引
    │   └── download_log.json          # 下载日志
    └── failed/
        └── failed_downloads.txt       # 下载失败列表
```

### 文献索引文件

```json
{
  "papers": [
    {
      "id": "E1",
      "doi": "10.1038/nature14539",
      "pdf_path": "./literature/pdfs/E1_LeCun_2015_....pdf",
      "download_info": {
        "channel": "unpaywall",
        "date": "2024-01-15",
        "size_mb": 3.2,
        "verified": true
      }
    }
  ]
}
```

---

## 示例

### 示例 1: 开放获取下载

**输入**:
```json
{
  "papers": [
    {
      "id": "E1",
      "title": "Attention is all you need",
      "doi": "10.48550/arXiv.1706.03762",
      "is_oa": true
    }
  ]
}
```

**处理**:
1. 识别为arXiv开放获取
2. 生成下载链接：`https://arxiv.org/pdf/1706.03762.pdf`
3. 下载并验证

**输出**:
```json
{
  "id": "E1",
  "status": "success",
  "channel": "arxiv",
  "file_path": "./literature/pdfs/E1_Vaswani_2017_Attention_is_all_you_need.pdf",
  "file_size_mb": 1.8
}
```

### 示例 2: 付费墙处理

**输入**:
```json
{
  "papers": [
    {
      "id": "E2",
      "title": "Premium Journal Article",
      "doi": "10.xxxx/premium",
      "is_oa": false
    }
  ]
}
```

**处理**:
1. 检查Unpaywall - 有开放获取版本
2. 通过Unpaywall下载
3. 记录为开放获取

**输出**:
```json
{
  "id": "E2",
  "status": "success",
  "channel": "unpaywall",
  "file_path": "./literature/pdfs/E2_Author_2023_Premium_Journal.pdf",
  "notes": "Downloaded OA version via Unpaywall"
}
```

---

## 注意事项

1. **尊重版权**: 仅下载有权限访问的文献
2. **Unpaywall优先**: 优先使用合法开放获取渠道
3. **验证完整性**: 始终验证下载的PDF是否有效
4. **避免重复**: 检查文件是否已存在
5. **错误记录**: 详细记录失败原因
6. **限速礼貌**: 避免对服务器造成过大压力
