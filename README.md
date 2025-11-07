# Gemini File Search API 测试工具

一个简单的网页应用程序，用于测试 Google Gemini API 的文件搜索功能（File Search）。

## 功能特性

- 创建和管理文件搜索商店（File Search Stores）
- 上传文件到文件搜索商店
- 支持两种上传方式：
  - 直接上传到商店（一步完成）
  - 分步上传和导入（支持自定义元数据）
- 查询文件搜索商店
- 查看引用信息（Grounding Metadata）
- 支持元数据过滤
- 实时操作日志显示

## 系统要求

- Python 3.8+
- Gemini API Key

## 安装步骤

### 1. 克隆或下载项目

```bash
cd gemini-file-sample
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 设置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Gemini API Key：

```
GEMINI_API_KEY=your_actual_api_key_here
```

获取 API Key：https://aistudio.google.com/app/apikey

### 5. 运行应用

```bash
python app.py
```

或者直接设置环境变量运行：

```bash
export GEMINI_API_KEY=your_api_key_here  # macOS/Linux
# 或
set GEMINI_API_KEY=your_api_key_here  # Windows

python app.py
```

### 6. 访问应用

打开浏览器访问：http://localhost:5000

## 使用指南

### 1. 文件搜索商店管理

#### 创建商店
1. 切换到"文件搜索商店管理"标签
2. 输入商店名称（可选，默认为 my-file-search-store）
3. 点击"创建商店"
4. 记下生成的商店名称（格式：fileSearchStores/xxx）

#### 查看商店列表
- 点击"刷新列表"按钮查看所有已创建的商店

#### 删除商店
1. 在删除区域输入完整的商店名称
2. 点击"删除商店"
3. 确认删除

### 2. 文件上传

#### 方法 1: 直接上传到商店
1. 切换到"文件上传"标签
2. 输入目标商店名称（从商店管理页面复制）
3. （可选）输入自定义文件名称
4. 选择要上传的文件
5. 点击"上传并导入"
6. 等待上传和处理完成

#### 方法 2: 分步上传和导入
**步骤 1 - 上传文件：**
1. 输入文件名称
2. 选择文件
3. 点击"上传文件"
4. 复制返回的文件名称

**步骤 2 - 导入到商店：**
1. 输入目标商店名称
2. 粘贴上一步获得的文件名称
3. （可选）添加自定义元数据：
   - 点击"添加元数据"
   - 输入键值对（如：author = Robert Graves）
   - 选择类型（字符串或数字）
4. 点击"导入到商店"

### 3. 查询测试

1. 切换到"查询测试"标签
2. 输入商店名称（多个商店用逗号分隔）
3. 输入查询内容（例如："Can you tell me about Robert Graves?"）
4. （可选）输入元数据过滤器（例如："author=Robert Graves"）
5. 点击"执行查询"
6. 查看结果和引用信息

## 支持的文件类型

根据 Gemini API 文档，支持的文件类型包括：
- 文本文件（.txt, .md, etc.）
- 文档文件（.pdf, .doc, .docx, etc.）
- 其他应用程序文件

最大文件大小：100MB

## 限制

- 每个项目最多 10 个文件搜索商店
- 文件大小限制：100MB
- 存储空间限制（根据用户层级）：
  - 免费：1 GB
  - 第 1 级：10 GB
  - 第 2 级：100 GB
  - 第 3 级：1 TB

## 定价

- 索引创建时：$0.15 / 百万个词元（嵌入定价）
- 存储空间：免费
- 查询时嵌入：免费
- 检索的文档词元：按普通内容词元计费

## 项目结构

```
gemini-file-sample/
├── app.py                 # Flask 后端服务器
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量示例
├── .gitignore            # Git 忽略文件
├── README.md             # 项目说明
├── templates/
│   └── index.html        # 前端 HTML 界面
├── static/
│   ├── css/
│   │   └── style.css     # 样式文件
│   └── js/
│       └── main.js       # JavaScript 交互逻辑
└── uploads/              # 临时上传文件夹（自动创建）
```

## 故障排除

### API Key 错误
确保 `.env` 文件中的 API Key 正确，或通过环境变量设置：
```bash
export GEMINI_API_KEY=your_key_here
```

### 文件上传失败
- 检查文件大小是否超过 100MB
- 确保文件类型受支持
- 检查网络连接

### 查询没有结果
- 确认文件已成功导入商店
- 等待几秒让索引完成
- 尝试不同的查询内容

### 操作超时
- 大文件可能需要更长处理时间
- 检查操作日志了解详细信息

## 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5, CSS3, JavaScript (Vanilla)
- **API**: Google Gemini API (google-genai)

## 参考资料

- [Gemini API 文件搜索文档](https://ai.google.dev/gemini-api/docs/file-search)
- [Google AI Studio](https://aistudio.google.com/)

## 授权

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
