# buct-pdf

北京化工大学课程平台PDF下载工具，支持登录、下载PPT和PDF文件。

## 功能特性

- 🔐 自动登录北化课程平台
- 📄 下载PPT文件并转换为PDF
- 📥 直接下载PDF文件
- 🖥️ 命令行界面支持
- 📦 可作为Python库导入使用

## 安装

### 使用 pip 安装

```bash
pip install buct-pdf
```

### 从源码安装

```bash
git clone https://github.com/your-username/buct-pdf.git
cd buct-pdf
pip install -e .
```

## 使用方法

### 作为命令行工具

#### 交互式模式（推荐）

```bash
buct-pdf -i
```

#### 直接使用（保持原有体验）

```bash
python buct-pdf.py
```

### 作为Python库

```python
from buct_pdf import GetsPdf, LoginError, NetworkError

# 创建下载器实例
downloader = GetsPdf()

try:
    # 登录
    downloader.login("your_student_id", "your_password")
    
    # 下载PPT并转换为PDF
    ppt_url = "https://course.buct.edu.cn/meol/analytics/resPdfShow.do?resId=12345&lid=67890"
    pdf_path = downloader.download_ppt_to_pdf(ppt_url, "./downloads")
    print(f"PPT下载完成: {pdf_path}")
    
    # 直接下载PDF文件
    pdf_url = "https://course.buct.edu.cn/meol/analytics/resPdfShow.do?resId=54321&lid=09876"
    pdf_path = downloader.download_pdf(pdf_url, "./downloads")
    print(f"PDF下载完成: {pdf_path}")
    
except LoginError as e:
    print(f"登录错误: {e}")
except NetworkError as e:
    print(f"网络错误: {e}")
finally:
    # 注销登录
    downloader.logout()
```

## API文档

### GetsPdf 类

主要的下载器类，提供所有核心功能。

#### 方法

- `login(username, password)`: 登录到北化课程平台
- `logout()`: 注销登录
- `is_logged_in()`: 检查登录状态
- `download_ppt_to_pdf(url, output_dir=".")`: 下载PPT并转换为PDF
- `download_pdf(url, output_dir=".")`: 直接下载PDF文件
- `set_base_url(base_url)`: 设置基础URL（用于测试）
- `get_session()`: 获取认证后的session对象

### 异常类

- `LoginError`: 登录相关错误
- `NetworkError`: 网络相关错误

## 开发

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/buct-pdf.git
cd buct-pdf

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e .
```

### 运行测试

```bash
python -m pytest tests/
```

### 代码格式化

```bash
black buct_pdf/
ruff check buct_pdf/
```

## 项目结构

```
buct-pdf/
├── buct_pdf/           # 主要库代码
│   ├── __init__.py    # 库入口
│   ├── core.py        # 核心功能实现
│   └── cli.py         # 命令行接口
├── examples/          # 使用示例
├── tests/            # 测试代码
├── buct-pdf.py       # 兼容性脚本
├── pyproject.toml    # 项目配置
└── README.md         # 项目说明
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v0.1.0
- 初始版本发布
- 支持登录、PPT下载和PDF下载功能
- 提供命令行和Python库两种使用方式