"""标准输入输出流模块，模拟C++ iostream"""
# iostream.py
import pointer  # 确保pointer.py在同一目录下
from collections.abc import Iterable
from typing import Any, Optional, TextIO
import sys
import cpp_array

class cin:
    """模拟C++的cin输入流，支持>>链式输入、getline、freopen重定向、getchar"""
    def __init__(self):
        self._input_buffer = []          # 输入缓冲区（存储未处理的输入值）
        self._char_buffer = ""           # 字符缓冲区（用于getchar逐字符读取）
        self._redirect_file: Optional[TextIO] = None  # 重定向的输入文件
        self._original_stdin = sys.stdin # 保存原始标准输入

    def freopen(self, filename: str, mode: str = "r") -> bool:
        """
        模拟C++的freopen：重定向cin到文件输入
        :param filename: 重定向的文件名
        :param mode: 文件打开模式（默认"r"只读）
        :return: 成功返回True，失败返回False
        """
        try:
            # 关闭已打开的重定向文件
            if self._redirect_file and not self._redirect_file.closed:
                self._redirect_file.close()
            # 打开新文件并重定向
            self._redirect_file = open(filename, mode, encoding="utf-8")
            sys.stdin = self._redirect_file  # 替换标准输入
            self._input_buffer.clear()       # 清空原有缓冲区
            self._char_buffer = ""           # 清空字符缓冲区
            return True
        except (FileNotFoundError, PermissionError, IOError) as e:
            print(f"freopen输入文件失败：{e}")
            return False

    def fclose(self) -> None:
        """关闭重定向的输入文件，恢复标准输入"""
        if self._redirect_file and not self._redirect_file.closed:
            self._redirect_file.close()
        sys.stdin = self._original_stdin  # 恢复原始标准输入
        self._redirect_file = None
        self._input_buffer.clear()
        self._char_buffer = ""

    def getchar(self) -> Optional[int]:
        """
        模拟C的getchar：逐字符读取输入（返回字符的ASCII码，EOF返回-1）
        :return: 字符ASCII码（如'a'返回97），EOF返回-1，失败返回None
        """
        try:
            # 字符缓冲区为空时，读取一行/一个字符
            if not self._char_buffer:
                if self._redirect_file and not self._redirect_file.closed:
                    # 从重定向文件读取
                    char = self._redirect_file.read(1)  # 逐字符读取
                else:
                    # 从标准输入读取
                    char = sys.stdin.read(1)
                
                if not char:  # EOF（文件结束/输入流关闭）
                    return -1
                self._char_buffer = char
            
            # 取出第一个字符并返回ASCII码
            char = self._char_buffer[0]
            self._char_buffer = self._char_buffer[1:]
            return ord(char)
        except Exception as e:
            print(f"getchar读取失败：{e}")
            return None

    def getline(self, line_var: pointer.var, sep: str = None):
        """
        模拟C++的cin.getline()，读取整行到可迭代类型的var对象
        :param line_var: 可迭代类型的var对象（str/list/tuple等）
        :param sep: 拆分分隔符（None表示按字符拆分，仅对list/tuple生效）
        """
        # 1. 基础类型检查
        if not isinstance(line_var, pointer.var) and not isinstance(line_var, cpp_array.Array):
            raise TypeError("getline只能接收pointer.var类型参数")
        
        # 2. 检查是否为可迭代类型（排除int/float等非可迭代类型）
        if not issubclass(line_var.type, Iterable):
            raise TypeError(
                f"getline的参数必须是可迭代类型的var（如str/list/tuple），不支持{line_var.type.__name__}"
            )
        
        # 3. 读取整行输入（支持重定向）
        try:
            if self._redirect_file and not self._redirect_file.closed:
                input_line = self._redirect_file.readline().rstrip('\n')  # 保留换行符外的字符
            else:
                input_line = input().rstrip('\n')
        except EOFError:
            input_line = ""
        
        # 4. 适配不同可迭代类型的存储逻辑
        target_type = line_var.type
        try:
            if isinstance(line_var, cpp_array.Array):
                for i in range(len(input_line)):
                    line_var[i].value = line_var.type(line_var.type(input_line[i]))
            elif target_type is str:
                # 字符串类型：直接存储整行
                line_var.value = target_type(input_line)
            elif target_type in (list, tuple):
                # 列表/元组类型：按分隔符拆分（无分隔符则按字符拆分）
                if sep is None:
                    # 无分隔符：按字符拆分
                    data = list(input_line)
                else:
                    # 有分隔符：按分隔符拆分
                    data = input_line.split(sep)
                # 转换为目标类型（list/tuple）
                line_var.value = target_type(data)
            else:
                # 其他可迭代类型：尝试直接转换
                line_var.value = target_type(input_line)
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"无法将输入行'{input_line}'转换为{target_type.__name__}类型：{str(e)}"
            )

    def _read_input(self):
        """内部方法：读取输入并填充缓冲区（按需读取，支持重定向）"""
        if not self._input_buffer:
            try:
                if self._redirect_file and not self._redirect_file.closed:
                    # 从重定向文件读取一行
                    input_line = self._redirect_file.readline().strip()
                else:
                    # 从标准输入读取一行
                    input_line = input().strip()
                
                if input_line:
                    self._input_buffer = input_line.split()
                else:
                    self._input_buffer = []
            except EOFError:
                self._input_buffer = []

    def __rshift__(self, var_obj: pointer.var):
        """重载>>：核心输入方法（单次输入一个变量，支持重定向）"""
        # 1. 检查参数类型
        if not isinstance(var_obj, pointer.var) and not isinstance(var_obj, cpp_array.Array):
            raise TypeError(f">> 只支持pointer.var或cpp_array.Array类型，不支持{type(var_obj).__name__}")
        
        # 2. 读取输入（缓冲区为空则读取新行）
        self._read_input()
        
        # 3. 处理输入值（无输入则循环读取，直到有输入/EOF）
        while not self._input_buffer:
            self._read_input()
            # 检查是否EOF（缓冲区仍为空则抛出异常）
            if not self._input_buffer and (self._redirect_file and self._redirect_file.closed):
                raise EOFError("输入流已结束（EOF）")
        
        # 4. 转换并赋值（按变量类型转换）
        val_str = self._input_buffer.pop(0)  # 取出缓冲区第一个值
        if isinstance(var_obj, cpp_array.Array):
            for i in range(len(val_str)):
                var_obj[i].value = var_obj.type(var_obj.type(val_str[i]))
        else:
            try:
                var_obj.value = var_obj.type(val_str)
            except (ValueError, TypeError):
                raise ValueError(f"无法将'{val_str}'转换为{var_obj.type.__name__}类型")
            
        # 5. 返回self支持链式调用
        return self

class cout:
    """模拟C++的cout输出流，支持<<链式输出、freopen重定向、fflush"""
    def __init__(self):
        self._redirect_file: Optional[TextIO] = None  # 重定向的输出文件
        self._original_stdout = sys.stdout           # 保存原始标准输出

    def freopen(self, filename: str, mode: str = "w") -> bool:
        """
        模拟C++的freopen：重定向cout到文件输出
        :param filename: 重定向的文件名
        :param mode: 文件打开模式（默认"w"写入，"a"追加）
        :return: 成功返回True，失败返回False
        """
        try:
            # 关闭已打开的重定向文件
            if self._redirect_file and not self._redirect_file.closed:
                self._redirect_file.close()
            # 打开新文件并重定向
            self._redirect_file = open(filename, mode, encoding="utf-8")
            sys.stdout = self._redirect_file  # 替换标准输出
            return True
        except (PermissionError, IOError) as e:
            print(f"freopen输出文件失败：{e}")
            return False

    def fflush(self) -> None:
        """模拟C的fflush：刷新输出缓冲区（立即写入文件）"""
        if self._redirect_file and not self._redirect_file.closed:
            self._redirect_file.flush()
        sys.stdout.flush()

    def fclose(self) -> None:
        """关闭重定向的输出文件，恢复标准输出"""
        self.fflush()  # 刷新缓冲区后关闭
        if self._redirect_file and not self._redirect_file.closed:
            self._redirect_file.close()
        sys.stdout = self._original_stdout  # 恢复原始标准输出
        self._redirect_file = None

    def __lshift__(self, value: Any):
        """重载<<：输出值（不换行），支持重定向"""
        try:
            if isinstance(value, pointer.var):
                print(value.value, end="")
            elif isinstance(value, cpp_array.Array):
                print(*[i.value for i in value], sep="", end="")
            else:
                print(value, end="")
            self.fflush()  # 实时刷新（可选，根据需求调整）
        except Exception as e:
            print(f"输出失败：{e}")
        return self  # 返回self支持链式调用
    
    def endl(self):
        """模拟C++的endl（换行+刷新缓冲区）"""
        print()
        self.fflush()
        return self

# 单例模式：模拟C++的全局cin/cout对象
cin = cin()
cout = cout()

# 模拟C++的endl常量和C的EOF常量
endl = '\n'
EOF = -1

# 模拟C的全局getchar函数（直接调用cin.getchar）
def getchar() -> Optional[int]:
    return cin.getchar()

# 模拟C的freopen函数（根据mode自动判断输入/输出）
def freopen(filename: str, mode: str = "r") -> bool:
    if mode in ("r", "rb"):
        return cin.freopen(filename, mode)
    elif mode in ("w", "wb", "a", "ab"):
        return cout.freopen(filename, mode)
    else:
        print(f"不支持的文件模式：{mode}")
        return False

# 模拟C的fclose函数（关闭所有重定向文件）
def fclose() -> None:
    cin.fclose()
    cout.fclose()

# 模拟C的fflush函数（刷新输出缓冲区）
def fflush() -> None:
    cout.fflush()

__all__ = ["cin","cout","endl","EOF","getchar","freopen","fclose","fflush"]

if __name__ == "__main__":
    # ==================== 测试1：基础getchar ====================
    cout << "测试1：逐字符读取输入（输入任意字符，按回车后按Ctrl+Z/EOF结束）：" << endl
    cout << "提示：Windows按【Ctrl+Z+回车】，Linux/Mac按【Ctrl+D】触发EOF" << endl
    char_count = 0
    while True:
        c = getchar()
        if c == EOF:  # EOF（结束符）
            break
        if c == ord('\n'):  # 跳过换行符（避免重复处理）
            continue
        cout << f"  读取到字符：'{chr(c)}' (ASCII码: {c})" << endl
        char_count += 1
    cout << f"getchar读取结束，共读取 {char_count} 个有效字符" << endl << endl

    # ==================== 测试2：freopen重定向输入 ====================
    # 1. 创建测试输入文件（test_input.txt）
    test_input_content = "100 200\nhello world\n3.14"
    with open("test_input.txt", "w", encoding="utf-8") as f:
        f.write(test_input_content)
    cout << "测试2：创建测试输入文件 test_input.txt，内容：" << endl
    cout << f"  {test_input_content}" << endl

    # 2. 重定向cin到test_input.txt
    if freopen("test_input.txt", "r"):
        cout << "  ✅ 重定向输入文件成功" << endl
        # 读取重定向文件中的整数
        a = pointer.var(int)
        b = pointer.var(int)
        cin >> a >> b
        cout << f"  从文件读取的整数：a = {a.value}, b = {b.value}" << endl
        
        # 读取文件中的字符串（整行）
        s = pointer.var(str)
        cin.getline(s)
        cout << f"  从文件读取的字符串：'{s.value}'" << endl
        
        # 读取文件中的浮点数
        f_num = pointer.var(float)
        cin >> f_num
        cout << f"  从文件读取的浮点数：{f_num.value}" << endl
        
        # 关闭重定向，恢复标准输入
        fclose()
        cout << "  ✅ 关闭输入重定向，恢复标准IO" << endl
    else:
        cout << "  ❌ 重定向输入文件失败" << endl
    cout << endl

    # ==================== 测试3：freopen重定向输出 ====================
    # 1. 重定向cout到test_output.txt
    if freopen("test_output.txt", "w"):
        cout << "测试3：重定向输出到文件 test_output.txt" << endl
        cout << "  这是重定向后的输出内容1" << endl
        cout << "  整数变量：" << pointer.var(int, 123).value << endl
        cout << "  字符串变量：" << pointer.var(str, "测试重定向输出").value << endl
        cout << "  浮点数变量：" << pointer.var(float, 9.8).value << endl
        # 刷新缓冲区并关闭文件
        fflush()
        fclose()
        cout << "✅ 输出重定向完成，已写入 test_output.txt" << endl
        
        # 验证文件内容
        with open("test_output.txt", "r", encoding="utf-8") as f:
            file_content = f.read()
        cout << "  test_output.txt 内容：" << endl
        cout << "  ------------------------" << endl
        cout << file_content
        cout << "  ------------------------" << endl
    else:
        cout << "❌ 重定向输出文件失败" << endl
    cout << endl

    # ==================== 测试4：恢复标准IO后的正常输入输出 ====================
    cout << "测试4：恢复标准IO，输入一个字符串（支持空格）：" << endl
    cout << "请输入："  # 不换行，让输入紧跟提示
    s = pointer.var(str)
    cin.getline(s)
    cout << f"✅ 你输入的字符串是：'{s.value}'" << endl

    # ==================== 测试5：混合测试（getchar + 重定向） ====================
    cout << endl << "测试5：混合测试 - 读取文件中的字符" << endl
    # 重定向到test_input.txt
    if freopen("test_input.txt", "r"):
        cout << "  逐字符读取 test_input.txt 内容：" << endl
        while True:
            c = getchar()
            if c == EOF:
                break
            if c == ord('\n'):
                cout << "  [换行符]" << endl
                continue
            cout << f"    '{chr(c)}' (ASCII: {c})" << endl
        fclose()
    cout << "✅ 所有测试完成！" << endl