# Nazo Image Utils

Nazo Image Utils 是一个高性能的图像处理和随机图像生成 Python 包。它包含两个主要组件：`RandImage` 和 `ProcessImage`，支持现代图像格式（AVIF、WebP、JPEG）。

## 🚀 特性

- 🖼️ **多格式支持**: 支持 AVIF、WebP、JPEG 三种图像格式
- ⚡ **高性能**: 使用 Cython 优化和多进程处理
- 🎯 **智能格式选择**: 根据浏览器支持自动选择最佳格式（AVIF > WebP > JPEG）
- 🔧 **渐进式编码**: 支持渐进式 JPEG 和 AVIF
- 📱 **响应式**: 自动识别横图/竖图适配不同设备
- 🛠️ **原生工具集成**: 支持使用 `avifenc` 获得最佳 AVIF 质量

## 📦 安装

您可以使用 pip 安装 Nazo Image Utils：

```shell
pip install nazo-image-utils
```

### 可选依赖

为了获得最佳的 AVIF 支持，建议安装 `avifenc` 工具：

**Windows:**

```shell
winget install avif-tools
```

**Ubuntu/Debian:**

```shell
sudo apt install libavif-bin
```

**macOS:**

```shell
brew install libavif
```

## 🔧 ProcessImage

ProcessImage 是一个高性能的图像批处理类，支持多种现代图像格式。

### 初始化

```python
from nazo_image_utils import ProcessImage

process_image = ProcessImage(
    flush: bool = False,           # 是否清空缓存
    filter: bool = True,           # 是否过滤不合格图像
    gallery_path: str = "./gallary", # 待处理图像目录
    pc_filter_size: Size = PC_SIZE,     # PC端最小尺寸 (1920x1080)
    mobile_filter_size: Size = MOBILE_SIZE, # 移动端最小尺寸 (1080x1920)
)
```

### 配置说明

- `gallery_path`: 待处理图像的源目录
- `flush`: 当为 `True` 时，忽略已生成的 manifest 文件，重新处理所有图像
- `filter`: 当为 `True` 时，过滤掉小于指定尺寸的图像
- `pc_filter_size`: PC 端图像的最小合格尺寸（默认：1920×1080）
- `mobile_filter_size`: 移动端图像的最小合格尺寸（默认：1080×1920）

### 方法

#### `try_process()`

```python
process_image.try_process()
```

批量处理指定文件夹中的所有图片，生成多种格式和尺寸的图像文件。

**处理结果：**

- 创建 `avif/`、`webp/`、`jpeg/` 三个目录
- 每张图片生成三种尺寸：
  - `source`: 原始尺寸
  - `th`: 缩略图 (900×600)
  - `md`: 微型图 (50×30)
- 生成两个 manifest 文件：
  - `manifest.json`: PC 端图像索引
  - `manifest_mobile.json`: 移动端图像索引

**格式优化：**

- **AVIF**: 使用原生 `avifenc` 工具，启用渐进式编码
- **WebP**: 高质量有损压缩，方法级别 6
- **JPEG**: 渐进式编码，禁用色度子采样

### Manifest 文件格式

```json
{
  "md5_hash": {
    "source": "original_filename.jpg"
  }
}
```

## 🎲 RandImage

RandImage 是一个高性能的随机图像 URL 生成器，使用 Cython 优化以获得最佳性能。

### 初始化

```python
from nazo_image_utils import RandImage

rand_image = RandImage(
    pc_json_path="./manifest.json",
    mobile_json_path="./manifest_mobile.json",
    domain="https://example.com"
)
```

### 方法

#### `process()`

```python
result = rand_image.process(
    ua: bytes,                          # 用户代理字符串
    number: int,                        # 请求的URL数量 (1-10)
    platform: bytes = b"pc",           # 平台类型
    encode: bytes = b"",                # 编码方式
    size: bytes = b"source",            # 图像尺寸
)
```

根据用户代理和平台生成优化的图像 URL。

### 参数详解

- **`ua`** (bytes): 用户浏览器的 User-Agent 字符串，用于检测 AVIF 和 WebP 支持
- **`number`** (int): 请求的图像 URL 数量，范围 1-10
- **`platform`** (bytes): 图像方向
  - `b"pc"`: 横向图像 (宽 > 高)
  - `b"mobile"`: 纵向图像 (高 > 宽)
- **`encode`** (bytes): 返回格式
  - `b""`: 返回单个 URL (bytes)
  - `b"json"`: 返回 URL 列表 (list[str])
- **`size`** (bytes): 图像尺寸
  - `b"source"`: 原始尺寸
  - `b"th"`: 缩略图尺寸
  - `b"md"`: 微型图尺寸

### 返回值

- **单个 URL** (当 `encode != b"json"`): `bytes` 类型的图像 URL
- **URL 列表** (当 `encode == b"json"`): `list[str]` 类型的 URL 列表

### 智能格式选择

系统会根据用户代理自动选择最佳图像格式：

1. **AVIF** - 如果浏览器支持（最新、最高效）
2. **WebP** - 如果浏览器支持但不支持 AVIF
3. **JPEG** - 后备选项，确保兼容性

### URL 格式

生成的 URL 格式为：

```
{domain}/{format}/{md5_hash}.{size}.{format}
```

**示例：**

```
https://nazo.run/avif/0a4d55a8d778e5022fab701977c5d840.source.avif
https://nazo.run/webp/1b5e66b9d889e6033gbc802088c6e951.th.webp
https://nazo.run/jpeg/2c6f77c0e990f7044hcd913199d7f062.md.jpeg
```

## 💡 使用示例

### 基本图像处理

```python
from nazo_image_utils import ProcessImage

# 创建处理器实例
processor = ProcessImage(
    gallery_path="./my_images",
    filter=True,
    flush=False
)

# 处理所有图像
processor.try_process()
```

### 生成随机图像 URL

```python
from nazo_image_utils import RandImage

# 初始化随机图像生成器
rand_img = RandImage(
    pc_json_path="./manifest.json",
    mobile_json_path="./manifest_mobile.json",
    domain="https://cdn.example.com"
)

# 获取单个 PC 图像 URL
url = rand_img.process(
    ua=b"Mozilla/5.0 (compatible; AVIF support)",
    number=1,
    platform=b"pc",
    size=b"source"
)

# 获取多个移动端图像 URL 列表
urls = rand_img.process(
    ua=b"Mozilla/5.0 (Mobile; WebP support)",
    number=5,
    platform=b"mobile",
    encode=b"json",
    size=b"th"
)
```

### 在 Web 应用中使用

```python
from flask import Flask, request
from nazo_image_utils import RandImage

app = Flask(__name__)
rand_img = RandImage("./manifest.json", "./manifest_mobile.json", "https://cdn.mysite.com")

@app.route('/api/random-image')
def get_random_image():
    user_agent = request.headers.get('User-Agent', '').encode('utf-8')
    platform = b"mobile" if "Mobile" in request.headers.get('User-Agent', '') else b"pc"

    url = rand_img.process(
        ua=user_agent,
        number=1,
        platform=platform,
        size=b"source"
    )

    return {"image_url": url.decode('utf-8')}
```

## 🔧 运行脚本

为了避免多进程相关问题，建议使用提供的 `main.py` 脚本：

```python
# main.py
from nazo_image_utils import ProcessImage

if __name__ == "__main__":
    processor = ProcessImage(
        flush=False,
        filter=True,
        gallery_path="./gallary"
    )
    processor.try_process()
```

运行：

```shell
python main.py
```

## 📋 系统要求

- Python 3.7+
- PIL/Pillow
- Cython (用于编译)
- tqdm (进度条)
- ujson (JSON 处理)

### 可选依赖

- `avifenc` (推荐，用于最佳 AVIF 质量)
- `modern-image-support` (用于浏览器兼容性检测)

## 🎯 性能优化

- **多进程处理**: 使用 8 个进程并行处理图像
- **Cython 优化**: 核心随机选择逻辑使用 C 扩展
- **内存管理**: 自动内存分配和释放
- **原生工具**: 使用 `avifenc` 获得最佳 AVIF 压缩
- **智能缓存**: 基于 MD5 的重复检测

## 📄 许可证

详见 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证进行许可 - 请参阅 [LICENSE](LICENSE) 文件获取更多详细信息。
