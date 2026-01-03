"""字符串模块：模拟C++ std::string，兼容C风格字符串操作"""
from typing import Optional, List, Tuple, Union, Iterable
import sys
try:
    from .cstdio import printf, fprintf, FILE, EOF
except ImportError:
    # 备用导入路径
    import cstdio as cstdio_module
    printf = cstdio_module.printf
    fprintf = cstdio_module.fprintf
    FILE = cstdio_module.FILE
    EOF = cstdio_module.EOF

class String:
    """C++风格字符串类，复刻std::string核心功能"""
    def __init__(self, value: Union[str, bytes, "String"] = ""):
        """
        初始化字符串
        :param value: 初始值（字符串/字节/String对象）
        """
        # 底层存储Python原生字符串，保证编码安全
        if isinstance(value, bytes):
            self._data = value.decode("utf-8", errors="ignore")
        elif isinstance(value, String):
            self._data = value._data
        else:
            self._data = str(value)
    
    # ========== 核心属性（对标C++ string） ==========
    @property
    def size(self) -> int:
        """返回字符串长度（字符数），等价于C++ string::size()"""
        return len(self._data)
    
    @property
    def length(self) -> int:
        """返回字符串长度（同size），等价于C++ string::length()"""
        return self.size
    
    @property
    def empty(self) -> bool:
        """判断字符串是否为空，等价于C++ string::empty()"""
        return self.size == 0
    
    @property
    def c_str(self) -> str:
        """返回C风格字符串（以\0结尾），等价于C++ string::c_str()"""
        return self._data + "\0"
    
    # ========== 元素访问 ==========
    def at(self, index: int) -> str:
        """
        访问指定位置字符（带越界检查），等价于C++ string::at()
        :param index: 索引（0-based）
        :return: 字符
        """
        if index < 0 or index >= self.size:
            raise IndexError(f"索引{index}越界，字符串长度{self.size}")
        return self._data[index]
    
    def front(self) -> str:
        """返回第一个字符，等价于C++ string::front()"""
        if self.empty:
            raise IndexError("空字符串无首字符")
        return self._data[0]
    
    def back(self) -> str:
        """返回最后一个字符，等价于C++ string::back()"""
        if self.empty:
            raise IndexError("空字符串无尾字符")
        return self._data[-1]
    
    def __getitem__(self, index: int) -> str:
        """重载[]运算符（无越界检查），模拟C++ string[]"""
        # 兼容负索引（C++不支持，但Python习惯）
        return self._data[index]
    
    # ========== 修改操作 ==========
    def clear(self):
        """清空字符串，等价于C++ string::clear()"""
        self._data = ""
    
    def push_back(self, c: str):
        """追加单个字符，等价于C++ string::push_back()"""
        if len(c) != 1:
            raise ValueError("push_back仅支持单个字符")
        self._data += c
    
    def pop_back(self):
        """删除最后一个字符，等价于C++ string::pop_back()"""
        if self.empty:
            raise IndexError("空字符串无法pop_back")
        self._data = self._data[:-1]
    
    def append(self, other: Union[str, "String"], count: Optional[int] = None):
        """
        追加字符串，等价于C++ string::append()
        :param other: 要追加的字符串
        :param count: 追加的字符数（None=全部）
        """
        other_str = other._data if isinstance(other, String) else str(other)
        if count is not None:
            other_str = other_str[:count]
        self._data += other_str
    
    def assign(self, value: Union[str, "String"], count: Optional[int] = None):
        """
        赋值字符串，等价于C++ string::assign()
        :param value: 新值
        :param count: 取前count个字符（None=全部）
        """
        new_data = value._data if isinstance(value, String) else str(value)
        if count is not None:
            new_data = new_data[:count]
        self._data = new_data
    
    def insert(self, pos: int, value: Union[str, "String"], count: Optional[int] = None):
        """
        插入字符串，等价于C++ string::insert()
        :param pos: 插入位置
        :param value: 要插入的字符串
        :param count: 插入的字符数（None=全部）
        """
        if pos < 0 or pos > self.size:
            raise IndexError(f"插入位置{pos}越界")
        
        insert_str = value._data if isinstance(value, String) else str(value)
        if count is not None:
            insert_str = insert_str[:count]
        
        self._data = self._data[:pos] + insert_str + self._data[pos:]
    
    def erase(self, pos: int, count: Optional[int] = None):
        """
        删除字符，等价于C++ string::erase()
        :param pos: 起始位置
        :param count: 删除的字符数（None=删除到末尾）
        """
        if pos < 0 or pos >= self.size:
            raise IndexError(f"删除位置{pos}越界")
        
        if count is None:
            self._data = self._data[:pos]
        else:
            end_pos = pos + count
            self._data = self._data[:pos] + self._data[end_pos:]
    
    def replace(self, pos: int, count: int, new_str: Union[str, "String"]):
        """
        替换字符，等价于C++ string::replace()
        :param pos: 起始位置
        :param count: 替换的字符数
        :param new_str: 新字符串
        """
        if pos < 0 or pos + count > self.size:
            raise IndexError("替换位置越界")
        
        new_str_data = new_str._data if isinstance(new_str, String) else str(new_str)
        self._data = self._data[:pos] + new_str_data + self._data[pos+count:]
    
    def resize(self, new_size: int, fill_char: str = ' '):
        """
        调整字符串大小，等价于C++ string::resize()
        :param new_size: 新大小
        :param fill_char: 填充字符（默认空格）
        """
        if len(fill_char) != 1:
            raise ValueError("fill_char必须是单个字符")
        
        if new_size < 0:
            raise ValueError("new_size不能为负数")
        
        current_size = self.size
        if new_size > current_size:
            # 扩容，填充字符
            self._data += fill_char * (new_size - current_size)
        elif new_size < current_size:
            # 缩容，截断
            self._data = self._data[:new_size]
    
    # ========== 查找操作 ==========
    def find(self, substr: Union[str, "String"], pos: int = 0) -> int:
        """
        查找子串（从左到右），等价于C++ string::find()
        :param substr: 子串
        :param pos: 起始查找位置
        :return: 子串起始索引，未找到返回-1（模拟C++ string::npos）
        """
        if pos < 0 or pos >= self.size:
            return -1
        
        substr_str = substr._data if isinstance(substr, String) else str(substr)
        idx = self._data.find(substr_str, pos)
        return idx if idx != -1 else -1
    
    def rfind(self, substr: Union[str, "String"], pos: Optional[int] = None) -> int:
        """
        反向查找子串（从右到左），等价于C++ string::rfind()
        :param substr: 子串
        :param pos: 结束查找位置（None=末尾）
        :return: 子串起始索引，未找到返回-1
        """
        if pos is None:
            pos = self.size - 1
        if pos < 0 or pos >= self.size:
            return -1
        
        substr_str = substr._data if isinstance(substr, String) else str(substr)
        idx = self._data.rfind(substr_str, 0, pos+1)
        return idx if idx != -1 else -1
    
    def find_first_of(self, chars: Union[str, "String"], pos: int = 0) -> int:
        """
        查找第一个匹配字符，等价于C++ string::find_first_of()
        :param chars: 字符集合
        :param pos: 起始位置
        :return: 索引，未找到返回-1
        """
        if pos < 0 or pos >= self.size:
            return -1
        
        chars_str = chars._data if isinstance(chars, String) else str(chars)
        for i in range(pos, self.size):
            if self._data[i] in chars_str:
                return i
        return -1
    
    def find_last_of(self, chars: Union[str, "String"], pos: Optional[int] = None) -> int:
        """
        查找最后一个匹配字符，等价于C++ string::find_last_of()
        :param chars: 字符集合
        :param pos: 结束位置（None=末尾）
        :return: 索引，未找到返回-1
        """
        if pos is None:
            pos = self.size - 1
        if pos < 0 or pos >= self.size:
            return -1
        
        chars_str = chars._data if isinstance(chars, String) else str(chars)
        for i in range(pos, -1, -1):
            if self._data[i] in chars_str:
                return i
        return -1
    
    # ========== 子串操作 ==========
    def substr(self, pos: int, count: Optional[int] = None) -> "String":
        """
        截取子串，等价于C++ string::substr()
        :param pos: 起始位置
        :param count: 截取长度（None=截取到末尾）
        :return: 新的String对象
        """
        if pos < 0 or pos >= self.size:
            raise IndexError(f"子串起始位置{pos}越界")
        
        if count is None:
            substr_data = self._data[pos:]
        else:
            if count < 0:
                raise ValueError("count不能为负数")
            substr_data = self._data[pos:pos+count]
        
        return String(substr_data)
    
    # ========== 比较操作 ==========
    def compare(self, other: Union[str, "String"]) -> int:
        """
        比较字符串，等价于C++ string::compare()
        :param other: 比较的字符串
        :return: 0=相等，<0=当前字符串小，>0=当前字符串大
        """
        other_str = other._data if isinstance(other, String) else str(other)
        if self._data < other_str:
            return -1
        elif self._data > other_str:
            return 1
        else:
            return 0
    
    # ========== C风格字符串转换 ==========
    def to_bytes(self, encoding: str = "utf-8") -> bytes:
        """转换为字节串（模拟C风格char*）"""
        return self._data.encode(encoding)
    
    def to_int(self) -> int:
        """转换为整数（模拟atoi）"""
        try:
            return int(self._data)
        except ValueError:
            raise ValueError(f"无法将'{self._data}'转换为整数")
    
    def to_float(self) -> float:
        """转换为浮点数（模拟atof）"""
        try:
            return float(self._data)
        except ValueError:
            raise ValueError(f"无法将'{self._data}'转换为浮点数")
    
    # ========== 运算符重载 ==========
    def __add__(self, other: Union[str, "String"]) -> "String":
        """重载+运算符，字符串拼接"""
        new_str = String(self)
        new_str.append(other)
        return new_str
    
    def __iadd__(self, other: Union[str, "String"]) -> "String":
        """重载+=运算符，原地拼接"""
        self.append(other)
        return self
    
    def __eq__(self, other: Union[str, "String"]) -> bool:
        """重载==运算符"""
        other_str = other._data if isinstance(other, String) else str(other)
        return self._data == other_str
    
    def __ne__(self, other: Union[str, "String"]) -> bool:
        """重载!=运算符"""
        return not self.__eq__(other)
    
    def __lt__(self, other: Union[str, "String"]) -> bool:
        """重载<运算符"""
        other_str = other._data if isinstance(other, String) else str(other)
        return self._data < other_str
    
    def __gt__(self, other: Union[str, "String"]) -> bool:
        """重载>运算符"""
        other_str = other._data if isinstance(other, String) else str(other)
        return self._data > other_str
    
    def __le__(self, other: Union[str, "String"]) -> bool:
        """重载<=运算符"""
        return self.__lt__(other) or self.__eq__(other)
    
    def __ge__(self, other: Union[str, "String"]) -> bool:
        """重载>=运算符"""
        return self.__gt__(other) or self.__eq__(other)
    
    def __len__(self) -> int:
        """重载len()"""
        return self.size
    
    def __str__(self) -> str:
        """字符串表示"""
        return self._data
    
    def __repr__(self) -> str:
        """详细表示"""
        return f"String('{self._data}') (size: {self.size})"
    
    # ========== 迭代器（简化版） ==========
    def __iter__(self):
        """迭代字符串中的字符"""
        return iter(self._data)
    
    # ========== 静态工具方法 ==========
    @staticmethod
    def from_int(num: int) -> "String":
        """从整数创建字符串（模拟itoa）"""
        return String(str(num))
    
    @staticmethod
    def from_float(num: float) -> "String":
        """从浮点数创建字符串"""
        return String(str(num))
    
    @staticmethod
    def join(sep: "String", iterable: Iterable[Union[str, "String"]]) -> "String":
        """
        连接字符串，模拟C++ string::join（简化版）
        :param sep: 分隔符
        :param iterable: 字符串集合
        :return: 连接后的字符串
        """
        sep_str = sep._data if isinstance(sep, String) else str(sep)
        str_list = []
        for item in iterable:
            str_list.append(item._data if isinstance(item, String) else str(item))
        return String(sep_str.join(str_list))

# ========== 全局常量（对标C++） ==========
STRING_NPOS = -1  # 模拟std::string::npos

__all__ = ["String","STRING_NPOS"]
# ========== 测试代码 ==========
if __name__ == "__main__":
    # 测试1：基础初始化与属性
    printf("=== 测试1：基础初始化与属性 ===\n")
    s1 = String("Hello")
    s2 = String("World")
    printf("s1 = %s (size: %d)\n", s1, s1.size)
    printf("s2 = %s (size: %d)\n", s2, s2.size)
    printf("s1.empty = %s\n", "true" if s1.empty else "false")
    
    # 测试2：拼接与运算符重载
    printf("\n=== 测试2：拼接与运算符重载 ===\n")
    s3 = s1 + " " + s2
    printf("s1 + ' ' + s2 = %s\n", s3)
    s1 += " C++ String"
    printf("s1 += ' C++ String' → %s\n", s1)
    
    # 测试3：元素访问与修改
    printf("\n=== 测试3：元素访问与修改 ===\n")
    printf("s3.front() = %c\n", s3.front())
    printf("s3.back() = %c\n", s3.back())
    printf("s3[1] = %c\n", s3[1])
    
    s3.push_back('!')
    printf("s3.push_back('!') → %s\n", s3)
    s3.pop_back()
    printf("s3.pop_back() → %s\n", s3)
    
    # 测试4：查找与替换
    printf("\n=== 测试4：查找与替换 ===\n")
    s4 = String("Hello Python C++")
    idx = s4.find("Python")
    printf("s4.find('Python') = %d\n", idx)
    
    s4.replace(idx, 6, "C-style String")
    printf("s4.replace() → %s\n", s4)
    
    # 测试5：子串与比较
    printf("\n=== 测试5：子串与比较 ===\n")
    sub = s4.substr(6, 7)
    printf("s4.substr(6,7) = %s\n", sub)
    
    s5 = String("Hello")
    s6 = String("Hello")
    s7 = String("World")
    printf("s5 == s6: %s\n", "true" if s5 == s6 else "false")
    printf("s5 < s7: %s\n", "true" if s5 < s7 else "false")
    
    # 测试6：转换与工具方法
    printf("\n=== 测试6：转换与工具方法 ===\n")
    num_str = String("12345")
    printf("num_str.to_int() = %d\n", num_str.to_int())
    
    float_str = String("3.14159")
    printf("float_str.to_float() = %f\n", float_str.to_float())
    
    # 连接字符串
    parts = [String("a"), String("b"), String("c")]
    joined = String.join(String("-"), parts)
    printf("join('-', [a,b,c]) = %s\n", joined)
    
    # 测试7：修改操作（insert/erase/resize）
    printf("\n=== 测试7：修改操作 ===\n")
    s8 = String("Test")
    s8.insert(2, "XX")
    printf("s8.insert(2, 'XX') → %s\n", s8)
    
    s8.erase(2, 2)
    printf("s8.erase(2,2) → %s\n", s8)
    
    s8.resize(8, '*')
    printf("s8.resize(8, '*') → %s\n", s8)