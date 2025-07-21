from typing import Optional, Union

class RandImage:
    def __init__(self, pc_json_path: str, mobile_json_path: str, domain: str) -> None:
        """初始化

        Args:
            pc_json_path (str): pc_json文件路径

            mobile_json_path (str): mobile_json文件路径

            domain (bytes): 主域名
        """
        ...
    def process(
        self,
        ua: bytes,
        number: int,
        platform: Optional[bytes] = b"pc",
        encode: Optional[bytes] = b"",
        size: Optional[bytes] = b"source",
    ) -> Union[bytes, list[str]]:
        """处理程序

        Args:
            ua (bytes): 用户浏览器 user-agent 标识, 用于检查AVIF和WebP支持。

            number (int): 请求的图像URL数量, 范围为1-10。

            platform (bytes): 平台(决定竖图还是横图) 传递 b"pc" 或 b"mobile"

            encode (bytes): 编码 仅传递 b"json" 或者不传

            size (bytes): 尺寸 (仅决定返回的图片尺寸格式)

        Returns:
            bytes | list[str]: 返回图像URL列表或JSON字符串 \n 最终格式为: `[domain]/[avif|webp|jpeg]/[md5].{size}.[avif|webp|jpeg]`
            例如: `https://nazo.run/avif/0a4d55a8d778e5022fab701977c5d840.source.avif`
            格式优先级: AVIF > WebP > JPEG
        """

        ...
