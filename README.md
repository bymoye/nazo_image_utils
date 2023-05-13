# Nazo Image Utils

Nazo Image Utils 是一个用于处理随机图像和图像处理的 Python 包。它包含两个类：`RandImage` 和 `ProcessImage`。

## 安装

您可以使用 pip 安装 Nazo Image Utils：

```shell
pip install nazo-image-utils
```

## ProcessImage

ProcessImage 是一个用于处理图像的类。

### 初始化

```python
from nazo_image_utils import ProcessImage

process_image = ProcessImage(
    flush: bool = False,
    filter: bool = True,
    gallery_path: str = "./gallary",
    pc_filter_size: Size = PC_SIZE,
    mobile_filter_size: Size = MOBILE_SIZE,
)
```

`gallery_path` 为待处理图像的目录。

当 `flush` 为 `True` 时，会忽视已生成的 `json` 文件中的内容。

当 `filter` 为 `True` 时，会对图像进行过滤，只保留合格的图像。

默认情况下, pc 端的合格图像尺寸为 1920x1080，移动端的合格图像尺寸为 1080x1920。

初始化 ProcessImage 类的实例。

### 方法

#### `try_process`

```python
process_image.try_process()
```

尝试处理所指定文件夹中的所有图片, 会分别存储到 `webp` 和 `jpeg` 文件夹中。

默认情况下一个图片会分别生成三张图片, 分别为不同的分辨率的图片, 定为:`source` , `th` , `md`。

还会生成两个文件分别为: `manifest.json` 和 `manifest_mobile.json`, 里面格式为:

```json
{ "md5": { "source": "file_name" } }
```

## RandImage

RandImage 是一个用于生成随机图像 URL 的类。

### 初始化

```python
from nazo_image_utils import RandImage

rand_image = RandImage(pc_json_path="./manifest.json", mobile_json_path="./manifest_mobile.json", domain=b"https://example.com")
```

初始化 RandImage 类的实例。

### 方法

#### `process`

```python
result = rand_image.process(
    ua: bytes,
    number: int,
    platform: Optional[bytes] = b"pc",
    encode: Optional[bytes] = b"",
    size: Optional[bytes] = b"source",
)
```

处理程序，生成随机图像的 URL。

##### 参数

- `ua` (bytes): 用户浏览器 user-agent 标识，用于检查 WebP 支持。
- `number` (int): 请求的图像 URL 数量，范围为 1-10。
- `platform` (bytes): 平台（决定竖图还是横图），传递 `b"pc"` 或 `b"mobile"`。
- `encode` (bytes): 编码，仅传递 `b"json"` 或者不传。
- `size` (bytes): 尺寸（仅决定返回的图片尺寸格式）。

##### 返回值

- `bytes` 或 `list[str]`: 返回图像 URL 列表或 JSON 字符串。最终格式为: `[domain]/[webp|jpeg]/[md5].{size}.[webp|jpeg]`，例如: `https://nazo.run/webp/0a4d55a8d778e5022fab701977c5d840.source.webp`。

## 许可证

本项目采用 MIT 许可证进行许可 - 请参阅 [LICENSE](LICENSE) 文件获取更多详细信息。
