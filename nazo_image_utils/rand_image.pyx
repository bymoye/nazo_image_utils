# cython: language_level=3
# distutils: language = c++
import json
from webp_support.webp_support cimport webp_supported
from nazo_rand.nazo_rand cimport cy_random_below
from libc.string cimport strcmp
from libc.string cimport strcpy
from libc.string cimport strdup
from libc.stdlib cimport malloc, free
from libc.stdio cimport snprintf
from cpython.bytes cimport PyBytes_FromString

cdef:
    const char* URLWEBP = b'webp'
    const char* URLJPEG = b'jpeg'
    const char* MOBILE = b"mobile"

cdef class RandImage:
    cdef:
        int imgpc_total, imgmb_total
        char** imgpc
        char** imgmb
        char* domain

    cdef inline char* pc(self) nogil:
        return self.imgpc[cy_random_below(self.imgpc_total)]

    cdef inline char* mobile(self) nogil:
        return self.imgmb[cy_random_below(self.imgmb_total)]

    cdef char** generate_img_urls(self, int number,const char* img_format, const char* method, const char* size) nogil:
        cdef int i
        cdef char** urls = <char**>malloc(number * sizeof(char*))
        cdef char* _hash
        if urls == NULL:
            with gil:
                raise MemoryError("Failed to allocate memory for URLs array")

        for i in range(number):
            _hash = self.mobile() if strcmp(method, MOBILE) == 0 else self.pc()
            urls[i] = <char*>malloc(256 * sizeof(char))
            if urls[i] == NULL:
                for j in range(i):
                    free(urls[j])
                free(urls)
                with gil:
                    raise MemoryError("Failed to allocate memory for URL string")

            snprintf(urls[i], 256, b"%s/%s/%s.%s.%s", self.domain, img_format, _hash, size, img_format)

        return urls

    cdef inline void _free_urls(self,char **urls, int n) nogil:
        cdef int i
        for i in range(n):
            if urls[i] != NULL:
                free(urls[i])
        free(urls)

    cpdef process(self, bytes ua, int number, bytes platform=b"pc",bytes encode=b"", bytes size=b"source"):
        """
        根据给定的参数生成图像URL。

        参数:
        ua: bytes - 用户代理, 用于检查WebP支持。
        n: int - 请求的图像URL数量, 范围为1-10。
        platform: bytes - 生成特定平台图像URL, 可选值为"mobile"和"pc".
        encode: bytes - 返回的URL编码方式, 可选值为"json".
        """
        cdef const char* img_format
        img_format = URLWEBP if webp_supported(ua) else URLJPEG
        cdef int i
        if encode == b"json":
            number = min(max(number, 1), 10)
        else:
            number = 1
        cdef char** urls = self.generate_img_urls(number, img_format, platform, size)
        # 判断urls的长度是否为1
        if encode != b"json":
            py_url = PyBytes_FromString(urls[0])
            self._free_urls(urls, number)
            return py_url

        py_urls = [urls[i].decode('utf-8') for i in range(number)]

        # 释放内存
        self._free_urls(urls, number)

        return py_urls

    def __cinit__(self, str pc_json_file, str mobile_json_file, str domain):
        cdef str key
        cdef int i
        cdef bytes encoded_key
        with open(pc_json_file) as pc:
            temp = json.load(pc)
            self.imgpc_total = len(temp)
            self.imgpc = <char**>malloc(self.imgpc_total * sizeof(char*))
            for i, key in enumerate(temp.keys()):
                encoded_key = key.encode('UTF-8')
                self.imgpc[i] = <char*>malloc(len(encoded_key) + 1)
                strcpy(self.imgpc[i], encoded_key)

        with open(mobile_json_file) as mb:
                    temp = json.load(mb)
                    self.imgmb_total = len(temp)
                    self.imgmb = <char**>malloc(self.imgmb_total * sizeof(char*))
                    for i, key in enumerate(temp.keys()):
                        encoded_key = key.encode('UTF-8')
                        self.imgmb[i] = <char*>malloc(len(encoded_key) + 1)  # +1 用于空终止字符
                        strcpy(self.imgmb[i], encoded_key)
        self.domain = strdup(domain.encode('utf-8'))

    def __dealloc__(self):
        cdef int i
        if self.imgpc is not NULL:
            for i in range(self.imgpc_total):
                if self.imgpc[i] is not NULL:
                    free(self.imgpc[i])
            free(self.imgpc)

        if self.imgmb is not NULL:
            for i in range(self.imgmb_total):
                if self.imgmb[i] is not NULL:
                    free(self.imgmb[i])
            free(self.imgmb)
        
        if self.domain is not NULL:
            free(self.domain)