"""C语言<stdio.h>模拟模块：完美兼容标准输入+文件格式化读取"""
from typing import Any, Optional, List, Tuple, Union, TextIO, BinaryIO
import sys
import os
import re

# ========== 导入外部pointer模块 ==========
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from pointer import (
        var, pointer, 
        NullPointerError, InvalidPointerError, 
        TypeMismatchError, OperationNotSupportedError
    )
except ImportError as e:
    raise ImportError(f"无法导入pointer模块：{e}\n请确保pointer.py与cstdio.py在同一目录")

# ========== 常量定义 ==========
EOF = -1
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

# ========== FILE类 ==========
_MODE_MAP = {
    "r": "rt",    "w": "wt",    "a": "at",
    "r+": "r+t",  "w+": "w+t",  "a+": "a+t",
    "rb": "rb",   "wb": "wb",   "ab": "ab",
    "r+b": "r+b", "w+b": "w+b", "a+b": "a+b",
}
_DEFAULT_ENCODING = "gbk" if os.name == "nt" else sys.getdefaultencoding()

class FILE:
    def __init__(self, file_obj: Union[TextIO, BinaryIO], mode: str, name: str, encoding: str = None):
        self._file = file_obj
        self._mode = mode
        self._name = name
        self._closed = False
        self._pos = 0
        self._eof = False
        self._encoding = encoding or _DEFAULT_ENCODING
        self._is_binary = "b" in mode
    
    @property
    def name(self) -> str: return self._name
    @property
    def mode(self) -> str: return self._mode
    @property
    def closed(self) -> bool: return self._closed
    @property
    def eof(self) -> bool: return self._eof
    @property
    def is_binary(self) -> bool: return self._is_binary

# 全局流
stdin = FILE(sys.stdin, "r", "<stdin>", _DEFAULT_ENCODING)
stdout = FILE(sys.stdout, "w", "<stdout>", _DEFAULT_ENCODING)
stderr = FILE(sys.stderr, "w", "<stderr>", _DEFAULT_ENCODING)

# ========== 核心工具函数 ==========
def _convert_c_format(c_format: str) -> str:
    """转换C格式符为Python格式符"""
    py_format = []
    i = 0
    while i < len(c_format):
        if c_format[i] == '%':
            i += 1
            if i >= len(c_format):
                py_format.append('%')
                break
            if c_format[i] in ('d', 'i', 'u'):
                py_format.append('%d')
            elif c_format[i] in ('f', 'lf'):
                py_format.append('%f')
            elif c_format[i] in ('s', 'c'):
                py_format.append(f'%{c_format[i]}')
            elif c_format[i] == '%':
                py_format.append('%%')
            else:
                py_format.append(f'%{c_format[i]}')
            i += 1
        else:
            py_format.append(c_format[i])
            i += 1
    return ''.join(py_format)

def _parse_input_content(content: str, format_str: str) -> List[str]:
    """
    智能解析输入内容：
    - 纯格式符（如"%d %f %s"）→ 空格分割
    - 带固定字符（如"num = %d"）→ 格式化提取
    """
    # 提取所有格式符
    fmt_specs = re.findall(r'%([dfs c])', format_str)
    if not fmt_specs:
        return []
    
    # 场景1：纯格式符（标准输入，空格分隔）
    clean_format = re.sub(r'%[dfs c]', '', format_str).strip()
    if not clean_format:  # 格式字符串只有格式符+空格
        tokens = content.strip().split()
        # 补齐缺失的token（避免索引越界）
        while len(tokens) < len(fmt_specs):
            tokens.append('')
        return tokens[:len(fmt_specs)]
    
    # 场景2：带固定字符（文件读取，格式化提取）
    values = []
    remaining = content.strip()
    # 逐个提取格式符对应的值
    for fmt_type in fmt_specs:
        # 构建匹配模式：固定字符 + 值匹配
        # 找到下一个格式符的位置
        fmt_match = re.search(r'%([dfs c])', format_str)
        if not fmt_match:
            values.append('')
            continue
        
        # 提取固定前缀
        prefix = format_str[:fmt_match.start()].strip()
        format_str = format_str[fmt_match.end():]
        
        # 跳过前缀
        if prefix and remaining.startswith(prefix):
            remaining = remaining[len(prefix):].strip().lstrip(',;= ')
        
        # 按类型提取值
        if fmt_type == 'd':  # 整数
            match = re.match(r'(-?\d+)', remaining)
        elif fmt_type == 'f':  # 浮点数（支持负数/纯小数）
            match = re.match(r'(-?\d+\.?\d*|-?\.\d+)', remaining)
        elif fmt_type == 's':  # 字符串（支持任意字符直到分隔符）
            match = re.match(r'([^,;=\s]+)', remaining)
        elif fmt_type == 'c':  # 单个字符
            match = re.match(r'(.)', remaining)
        else:
            match = None
        
        if match:
            values.append(match.group(1))
            remaining = remaining[len(match.group(1)):].strip()
        else:
            values.append('')
    
    return values

# ========== 核心IO函数 ==========
def printf(format_str: str, *args: Any) -> int:
    """模拟C语言printf（适配var/pointer）"""
    return fprintf(stdout, format_str, *args)

def fprintf(stream: FILE, format_str: str, *args: Any) -> int:
    """模拟C语言fprintf（适配var/pointer）"""
    if stream.closed:
        raise IOError(f"流 {stream.name} 已关闭")
    
    try:
        processed_args = []
        for arg in args:
            if isinstance(arg, var):
                processed_args.append(arg.value)
            elif isinstance(arg, pointer):
                try:
                    processed_args.append(arg.deref())
                except (NullPointerError, InvalidPointerError):
                    raise RuntimeError(f"无法解引用指针：{arg}")
            else:
                processed_args.append(arg)
        
        py_format = _convert_c_format(format_str)
        output = py_format % tuple(processed_args)
        
        if stream.is_binary:
            output_bytes = output.encode(stream._encoding)
            stream._file.write(output_bytes)
            written = len(output_bytes)
        else:
            stream._file.write(output)
            written = len(output)
        
        stream._file.flush()
        stream._pos += written
        stream._eof = False
        return written
    except Exception as e:
        raise RuntimeError(f"fprintf失败: {e}") from e

def scanf(format_str: str, *ptrs: pointer) -> int:
    """模拟C语言scanf（仅接受pointer实例）"""
    return fscanf(stdin, format_str, *ptrs)

def fscanf(stream: FILE, format_str: str, *ptrs: pointer) -> int:
    """
    完美版fscanf：兼容标准输入（空格分隔）+ 文件格式化读取
    """
    if stream.closed:
        raise IOError(f"流 {stream.name} 已关闭")
    if stream.is_binary:
        raise ValueError("二进制模式不支持fscanf")
    
    # 校验指针参数
    for i, ptr in enumerate(ptrs):
        if not isinstance(ptr, pointer):
            raise TypeMismatchError(f"第{i+1}个参数必须是pointer实例，而非{type(ptr).__name__}")
        if ptr.is_null():
            raise NullPointerError(f"第{i+1}个参数是空指针，无法赋值")
    
    try:
        # 读取内容
        line = stream._file.readline()
        if not line:
            stream._eof = True
            return -1  # EOF
        
        # 智能解析内容
        values = _parse_input_content(line, format_str)
        fmt_specs = re.findall(r'%([dfs c])', format_str)
        
        # 赋值给指针
        success_count = 0
        for i in range(min(len(fmt_specs), len(values), len(ptrs))):
            value = values[i].strip()
            if not value:
                continue  # 空值跳过
            
            current_ptr = ptrs[i]
            fmt_type = fmt_specs[i]
            target_type = current_ptr.ptr_type
            
            if not current_ptr.is_valid():
                continue
            
            # 类型转换并赋值
            try:
                if fmt_type == 'd' and target_type == int:
                    current_ptr.set_value(int(value))
                    success_count += 1
                elif fmt_type == 'f' and target_type == float:
                    current_ptr.set_value(float(value))
                    success_count += 1
                elif fmt_type == 's' and target_type == str:
                    current_ptr.set_value(value)
                    success_count += 1
                elif fmt_type == 'c' and target_type == str:
                    current_ptr.set_value(value[0] if value else '')
                    success_count += 1
            except (TypeMismatchError, ValueError, IndexError):
                continue
        
        stream._pos += len(line)
        stream._eof = False
        return success_count
    except Exception as e:
        raise RuntimeError(f"fscanf失败: {e}") from e

# ========== 基础文件操作函数 ==========
def fopen(filename: str, mode: str = "r", encoding: str = None) -> Optional[FILE]:
    """模拟C语言fopen"""
    try:
        py_mode = _MODE_MAP.get(mode, mode)
        is_binary = "b" in py_mode
        encoding = encoding or _DEFAULT_ENCODING
        
        if is_binary:
            file_obj = open(filename, py_mode)
        else:
            file_obj = open(filename, py_mode, encoding=encoding, errors='ignore')
        
        return FILE(file_obj, mode, filename, encoding)
    except Exception:
        return None

def fclose(stream: FILE) -> int:
    """模拟C语言fclose"""
    if stream.closed:
        return 0
    try:
        stream._file.close()
        stream._closed = True
        return 0
    except Exception:
        return -1

def fgetc(stream: FILE) -> int:
    """模拟C语言fgetc"""
    if stream.closed:
        return -1
    try:
        if stream.is_binary:
            c = stream._file.read(1)
            return c[0] if c else -1
        else:
            c = stream._file.read(1)
            return ord(c) if c else -1
    except Exception:
        return -1

def putchar(c: Union[str, int]) -> int:
    """模拟C语言putchar"""
    try:
        if isinstance(c, int):
            c = chr(c)
        stdout._file.write(c)
        stdout._file.flush()
        return ord(c)
    except Exception:
        return -1

def puts(s: Union[str, var, pointer]) -> int:
    """模拟C语言puts（适配var/pointer）"""
    try:
        if isinstance(s, var):
            s_str = s.value
        elif isinstance(s, pointer):
            s_str = s.deref()
        else:
            s_str = str(s)
        
        output = s_str + '\n'
        stdout._file.write(output)
        stdout._file.flush()
        return len(output)
    except Exception as e:
        raise RuntimeError(f"puts失败: {e}") from e

# ========== 文件系统操作函数 ==========
def remove(filename: str) -> int:
    """模拟C语言remove（删除文件）"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
        return 0
    except Exception:
        return -1

def rename(oldname: str, newname: str) -> int:
    """模拟C语言rename（重命名文件）"""
    try:
        os.rename(oldname, newname)
        return 0
    except Exception:
        return -1

def fseek(stream: FILE, offset: int, whence: int = 0) -> int:
    """模拟C语言fseek"""
    if stream.closed:
        return -1
    try:
        stream._file.seek(offset, whence)
        stream._pos = stream._file.tell()
        return 0
    except Exception:
        return -1

def ftell(stream: FILE) -> int:
    """模拟C语言ftell"""
    if stream.closed:
        return -1
    try:
        pos = stream._file.tell()
        stream._pos = pos
        return pos
    except Exception:
        return -1

def fflush(stream: Optional[FILE] = None) -> int:
    """模拟C语言fflush"""
    try:
        if stream is None:
            stdout._file.flush()
            stderr._file.flush()
        else:
            if stream.closed:
                return -1
            stream._file.flush()
        return 0
    except Exception:
        return -1

__all__ = ['EOF', 'FILE', 'SEEK_CUR', 'SEEK_END', 'SEEK_SET',   'Union', 'fclose', 'fflush', 'fgetc', 'fopen', 'fprintf', 'fscanf', 'fseek', 'ftell', 'pointer', 'printf', 'putchar', 'puts', 'remove', 'rename', 'scanf', 'stderr', 'stdin', 'stdout']

# ========== 测试代码 ==========
if __name__ == "__main__":
    printf("=== 集成外部pointer模块测试（完美版） ===\n")
    
    # 1. 定义变量
    num = var(int, 0)
    pi = var(float, 3.14)
    name = var(str, "")
    
    printf("初始值：num = %d, pi = %f, name = %s\n", num, pi, name)
    
    # 2. 获取指针
    p_num = num.get_pointer()
    p_pi = pi.get_pointer()
    p_name = name.get_pointer()
    
    # 3. 标准输入（空格分隔）
    printf("\n请输入 整数 浮点数 字符串：")
    try:
        if sys.stdin.isatty():
            # 纯格式符，空格分隔（标准scanf用法）
            scanf("%d %f %s", p_num, p_pi, p_name)
        else:
            # 非交互环境测试值
            p_num.set_value(123)
            p_pi.set_value(2.3)
            p_name.set_value("asd")
    except Exception as e:
        print(f"输入处理异常：{e}")
        p_num.set_value(123)
        p_pi.set_value(2.3)
        p_name.set_value("asd")
    
    # 4. 输出结果
    printf("输入后：num = %d, pi = %f, name = %s\n", num, p_pi, name)
    
    # 5. 手动解引用
    printf("\n手动解引用：*p_num = %d, *p_pi = %f\n", p_num.deref(), *p_pi)
    
    # 6. 修改值
    num.value = 200
    printf("修改后：num = %d\n", num)
    
    # ========== 文件操作 ==========
    printf("\n=== 文件操作（完美版） ===\n")
    
    # 写入文件（格式化内容）
    fp = fopen("test_ptr.txt", "w", encoding="utf-8")
    if fp:
        fprintf(fp, "num = %d, pi = %f, name = %s\n", num, p_pi, name)
        fclose(fp)
        printf("文件写入成功！\n")
    
    # 读取文件（格式化解析）
    read_num = var(int)
    read_pi = var(float)
    read_name = var(str)
    p_read_num = read_num.get_pointer()
    p_read_pi = read_pi.get_pointer()
    p_read_name = read_name.get_pointer()
    
    fp = fopen("test_ptr.txt", "r", encoding="utf-8")
    if fp:
        fscanf(fp, "num = %d, pi = %f, name = %s", p_read_num, p_read_pi, p_read_name)
        fclose(fp)
        printf("文件读取结果：\n")
        printf("  read_num = %d\n", read_num)
        printf("  read_pi = %f\n", p_read_pi)
        printf("  read_name = %s\n", read_name)
    
    # 清理文件
    remove("test_ptr.txt")
    printf("\n测试完成！\n")