"""指针模块：模拟C++指针"""
Pointer_id = 0
_vars = []  # 存储所有var实例，模拟内存空间
from typing import Type, Any
import sys
import os

# 将cpp文件夹的父目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
class PointerError(Exception):
    """指针相关异常基类"""
    pass


class NullPointerError(PointerError):
    """空指针访问异常"""
    pass


class InvalidPointerError(PointerError):
    """无效指针（越界/已释放）异常"""
    pass


class TypeMismatchError(PointerError):
    """指针类型不匹配异常"""
    pass


class OperationNotSupportedError(PointerError):
    """类型不支持该运算异常"""
    pass

_tmp_var = None
class pointer:
    """模拟C++风格的指针类（支持*解包）"""
    def __init__(self, var=None, id=None, ptr_type=None):
        global Pointer_id
        
        # 空指针初始化（id=-1表示空指针）
        if id == -1 or (var is None and id is None):
            self.point_id = -1  # -1表示空指针
            self.var = None
            self.ptr_type = None
            return
        
        # 按id初始化（地址方式）
        if id is not None:
            self.point_id = id
            # 检查地址有效性
            if self.point_id < 0 or self.point_id >= len(_vars):
                raise InvalidPointerError(f"指针地址{self.point_id}越界，内存空间大小：{len(_vars)}")
            self.var = _vars[self.point_id]
        # 按var实例初始化（直接指向变量）
        elif var is not None:
            if not isinstance(var, _tmp_var):
                raise TypeMismatchError("指针只能指向var实例")
            self.var = var
            self.point_id = var._pointer.point_id  # 复用var的指针地址
        
        # 类型约束（支持任意类型）
        self.ptr_type = ptr_type if ptr_type else (self.var.type if self.var else None)
        
        # 自动分配指针ID（仅非空指针）
        if self.point_id != -1:
            self.id = Pointer_id  # 指针自身的唯一标识
            Pointer_id += 1

    def is_null(self):
        """判断是否为空指针"""
        return self.point_id == -1

    def is_valid(self):
        """判断指针是否有效（非空+未越界+指向的变量未被释放）"""
        if self.is_null():
            return False
        if self.point_id < 0 or self.point_id >= len(_vars):
            return False
        # 检查指向的变量是否已被释放
        target_var = _vars[self.point_id]
        return target_var is not None and target_var._pointer.point_id != -1

    def deref(self):
        """核心解引用方法"""
        if self.is_null():
            raise NullPointerError("解引用空指针")
        if not self.is_valid():
            raise InvalidPointerError(f"指针地址{self.point_id}无效（越界/指向已释放变量）")
        return self.var.value

    def get(self):
        """友好的取值方法（兜底）"""
        return self.deref()

    # ------------------- 实现迭代器协议（支持*解包） -------------------
    def __iter__(self):
        """返回迭代器自身"""
        # 迭代前检查指针有效性
        if self.is_null():
            raise NullPointerError("无法迭代空指针")
        if not self.is_valid():
            raise InvalidPointerError("无法迭代无效指针")
        self._iter_done = False  # 标记迭代是否完成
        return self

    def __next__(self):
        """返回唯一的迭代元素（指针指向的值）"""
        if self._iter_done:
            raise StopIteration  # 迭代结束
        self._iter_done = True
        return self.deref()

    # ------------------- 其他方法（不变） -------------------
    def __eq__(self, other):
        if not isinstance(other, pointer):
            return False
        if self.is_null() and other.is_null():
            return True
        return self.point_id == other.point_id

    def __lt__(self, other):
        if not isinstance(other, pointer):
            raise TypeMismatchError("只能与pointer实例比较")
        if self.is_null() or other.is_null():
            raise NullPointerError("空指针无法比较大小")
        return self.point_id < other.point_id

    def __add__(self, other):
        if not isinstance(other, int):
            raise TypeMismatchError("指针只能与整数进行偏移运算")
        if self.is_null():
            raise NullPointerError("空指针无法进行偏移运算")
        new_id = self.point_id + other
        return pointer(id=new_id, ptr_type=self.ptr_type)

    def __sub__(self, other):
        if not isinstance(other, int):
            raise TypeMismatchError("指针只能与整数进行偏移运算")
        if self.is_null():
            raise NullPointerError("空指针无法进行偏移运算")
        new_id = self.point_id - other
        return pointer(id=new_id, ptr_type=self.ptr_type)

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            raise TypeError("数组索引必须为整数")
        new_ptr = self + index
        if not new_ptr.is_valid():
            raise InvalidPointerError(f"指针偏移{index}后地址{new_ptr.point_id}无效")
        new_ptr.set_value(value)

    def set_value(self, value):
        if self.is_null():
            raise NullPointerError("给空指针赋值")
        if not self.is_valid():
            raise InvalidPointerError(f"指针地址{self.point_id}无效，无法赋值")
        # 放宽类型检查：只要能转换为目标类型即可（支持任意类型）
        try:
            self.var.value = self.ptr_type(value)
        except (TypeError, ValueError):
            raise TypeMismatchError(f"无法将'{value}'转换为{self.ptr_type.__name__}类型")

    def __repr__(self):
        if self.is_null():
            return "NULL_POINTER"
        return f"Pointer<{self.ptr_type.__name__}>(address={self.point_id}, id={self.id})"

    def __str__(self):
        if self.is_null():
            return "NULL_POINTER"
        try:
            return f"Pointer(value={self.deref()}, address={self.point_id})"
        except InvalidPointerError:
            return f"INVALID_POINTER(address={self.point_id})"


# ------------------- 核心修改：var类支持任意类型，动态判断运算 -------------------
class var:
    """模拟C++的变量类，支持任意类型存储，动态判断运算支持性"""
    def __init__(self, _type, value=None):
        """
        初始化变量（支持任意类型）
        :param _type: 变量类型（任意Python类型：int/str/list/dict/自定义类等）
        :param value: 变量初始值，None则用类型默认值
        """
        # 支持任意类型的默认值初始化
        if value is None:
            # 处理不同类型的默认值（兼容内置类型和自定义类型）
            try:
                self.value = _type()  # 调用类型的默认构造
            except (TypeError, ValueError):
                self.value = None  # 无默认构造的类型设为None
        else:
            # 类型转换（兼容任意类型）
            try:
                self.value = _type(value)
            except (TypeError, ValueError):
                raise TypeMismatchError(f"初始值{value}无法转换为{_type.__name__}类型")
        
        self.type = _type  # 存储变量类型（支持任意类型）
        _vars.append(self)
        self._pointer = pointer(id=len(_vars)-1, ptr_type=_type)  # 地址为_vars中的索引

    # ------------------- 核心工具方法：动态检查运算支持性（修复类型检查） -------------------
    def _check_operation_support(self, other, op_name):
        """
        检查操作数是否支持目标运算（放宽类型检查，适配Python原生规则）
        :param other: 另一个操作数（var实例/原生对象/数组指针等）
        :param op_name: 运算方法名（如__add__/__mul__）
        :return: (self_val, other_val) 提取后的操作数值
        """
        # 提取self的值
        self_val = self.value
        
        # 提取other的值（兼容var实例、数组指针、原生类型）
        if isinstance(other, self.__class__):  # 同类型var实例
            other_val = other.value
        elif hasattr(other, 'value'):  # 兼容数组指针/其他有value属性的类（动态检查）
            other_val = other.value
        else:  # 原生类型（int/str/list等）
            other_val = other
        
        # 检查self是否支持该运算
        if op_name not in dir(self_val):
            raise OperationNotSupportedError(f"{self.type.__name__}类型不支持{op_name.replace('__', '')}运算")
        
        return self_val, other_val

    # ------------------- 算术运算重载（增加异常捕获，适配跨类型运算） -------------------
    def __add__(self, other):
        """重载+：动态检查是否支持加法运算"""
        self_val, other_val = self._check_operation_support(other, "__add__")
        # 执行加法并返回新var实例（保持原类型）
        try:
            result = self_val + other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持加法运算：{e}")
        return var(self.type, result)

    def __radd__(self, other):
        """重载反向+：支持原生对象 + var"""
        return self.__add__(other)

    def __sub__(self, other):
        """重载-：动态检查是否支持减法运算"""
        self_val, other_val = self._check_operation_support(other, "__sub__")
        try:
            result = self_val - other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持减法运算：{e}")
        return var(self.type, result)

    def __rsub__(self, other):
        """重载反向-：支持原生对象 - var"""
        self_val, other_val = self._check_operation_support(other, "__sub__")
        try:
            result = other_val - self_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{type(other_val).__name__}与{self.type.__name__}类型不支持减法运算：{e}")
        return var(self.type, result)

    def __mul__(self, other):
        """重载*：动态检查是否支持乘法运算（修复列表×int的核心）"""
        self_val, other_val = self._check_operation_support(other, "__mul__")
        try:
            result = self_val * other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持乘法运算：{e}")
        return var(self.type, result)

    def __rmul__(self, other):
        """重载反向*：支持原生对象 * var"""
        return self.__mul__(other)

    def __truediv__(self, other):
        """重载/：动态检查是否支持除法运算"""
        self_val, other_val = self._check_operation_support(other, "__truediv__")
        try:
            if other_val == 0:
                raise ZeroDivisionError("除数不能为0")
            result = self_val / other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持除法运算：{e}")
        return var(self.type, result)

    def __rtruediv__(self, other):
        """重载反向/：支持原生对象 / var"""
        self_val, other_val = self._check_operation_support(other, "__truediv__")
        try:
            if self_val == 0:
                raise ZeroDivisionError("除数不能为0")
            result = other_val / self_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{type(other_val).__name__}与{self.type.__name__}类型不支持除法运算：{e}")
        return var(self.type, result)

    # ------------------- 比较运算重载（增加异常捕获） -------------------
    def __eq__(self, other):
        """重载==：动态检查是否支持相等比较"""
        self_val, other_val = self._check_operation_support(other, "__eq__")
        try:
            return self_val == other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持相等比较：{e}")

    def __ne__(self, other):
        """重载!=：动态检查是否支持不等比较"""
        self_val, other_val = self._check_operation_support(other, "__ne__")
        try:
            return self_val != other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持不等比较：{e}")

    def __gt__(self, other):
        """重载>：动态检查是否支持大于比较"""
        self_val, other_val = self._check_operation_support(other, "__gt__")
        try:
            return self_val > other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持大于比较：{e}")

    def __lt__(self, other):
        """重载<：动态检查是否支持小于比较"""
        self_val, other_val = self._check_operation_support(other, "__lt__")
        try:
            return self_val < other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持小于比较：{e}")

    def __ge__(self, other):
        """重载>=：动态检查是否支持大于等于比较"""
        self_val, other_val = self._check_operation_support(other, "__ge__")
        try:
            return self_val >= other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持大于等于比较：{e}")

    def __le__(self, other):
        """重载<=：动态检查是否支持小于等于比较"""
        self_val, other_val = self._check_operation_support(other, "__le__")
        try:
            return self_val <= other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持小于等于比较：{e}")

    # ------------------- 赋值运算重载（增加异常捕获） -------------------
    def __iadd__(self, other):
        """重载+=：直接修改自身值"""
        self_val, other_val = self._check_operation_support(other, "__add__")
        try:
            self.value = self_val + other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持+=运算：{e}")
        return self

    def __isub__(self, other):
        """重载-=：直接修改自身值"""
        self_val, other_val = self._check_operation_support(other, "__sub__")
        try:
            self.value = self_val - other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持-=运算：{e}")
        return self

    def __imul__(self, other):
        """重载*=：直接修改自身值"""
        self_val, other_val = self._check_operation_support(other, "__mul__")
        try:
            self.value = self_val * other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持*=运算：{e}")
        return self

    def __itruediv__(self, other):
        """重载/=：直接修改自身值"""
        self_val, other_val = self._check_operation_support(other, "__truediv__")
        try:
            if other_val == 0:
                raise ZeroDivisionError("除数不能为0")
            self.value = self_val / other_val
        except TypeError as e:
            raise OperationNotSupportedError(f"{self.type.__name__}与{type(other_val).__name__}类型不支持/=运算：{e}")
        return self

    # ------------------- 其他方法（不变） -------------------
    def get_pointer(self):
        """获取变量的指针（模拟C++的 &var）"""
        if self._pointer.point_id == -1:
            raise InvalidPointerError("变量已被释放，无法获取指针")
        return self._pointer

    def __del__(self):
        """析构函数：释放变量，标记指针为无效"""
        if hasattr(self, '_pointer'):
            self._pointer.point_id = -1  # 标记指针无效
            self._pointer.var = None
        # 从_vars中标记为已释放（保留位置模拟内存地址）
        if self in _vars:
            idx = _vars.index(self)
            _vars[idx] = None  # None表示该地址已释放

    def __repr__(self):
        """变量的字符串表示（支持任意类型）"""
        return f"var<{self.type.__name__}>(value={self.value}, address={self._pointer.point_id})"

_tmp_var = var

__all__ = ["PointerError","NullPointerError","InvalidPointerError","TypeMismatchError","OperationNotSupportedError","pointer","var"]

# ------------------- 测试任意类型支持+动态运算判断 -------------------
if __name__ == "__main__":
    # 1. 基础数值类型（int/float）
    a = var(int, 10)
    b = var(int, 5)
    print(f"int类型加法：a + b = {a + b}")  # var<int>(value=15, address=0)
    print(f"int类型比较：a > b = {a > b}")  # True

    # 2. 字符串类型（支持拼接、比较，不支持加减乘除）
    s1 = var(str, "hello")
    s2 = var(str, "world")
    print(f"字符串拼接：s1 + s2 = {s1 + s2}")  # var<str>(value=helloworld, address=2)
    print(f"字符串比较：s1 < s2 = {s1 < s2}")  # True
    try:
        s1 - s2  # 字符串不支持减法，触发异常
    except OperationNotSupportedError as e:
        print(f"字符串减法异常：{e}")  # str类型不支持sub运算

    # 3. 列表类型（支持拼接、乘法，不支持除法）
    lst1 = var(list, [1, 2])
    lst2 = var(list, [3, 4])
    print(f"列表拼接：lst1 + lst2 = {lst1 + lst2}")  # var<list>(value=[1,2,3,4], address=4)
    print(f"列表乘法：lst1 * 2 = {lst1 * 2}")        # var<list>(value=[1,2,1,2], address=4)
    try:
        lst1 / 2  # 列表不支持除法，触发异常
    except OperationNotSupportedError as e:
        print(f"列表除法异常：{e}")  # list类型不支持truediv运算

    # 4. 自定义类（支持自定义运算）
    class Person:
        def __init__(self, age):
            self.age = age
        
        # 自定义加法：年龄相加
        def __add__(self, other):
            if isinstance(other, Person):
                return Person(self.age + other.age)
            raise TypeError("只能和Person实例相加")
        
        # 自定义比较：按年龄比较
        def __gt__(self, other):
            if isinstance(other, Person):
                return self.age > other.age
            raise TypeError("只能和Person实例比较")
        
        def __repr__(self):
            return f"Person(age={self.age})"

    p1 = var(Person, Person(20))
    p2 = var(Person, Person(18))
    print(f"自定义类加法：p1 + p2 = {p1 + p2}")  # var<Person>(value=Person(age=38), address=6)
    print(f"自定义类比较：p1 > p2 = {p1 > p2}")  # True

    # 5. 指针解包测试（兼容任意类型）
    p_s1 = s1.get_pointer()
    print("字符串指针解包：", *p_s1)  # hello
    p_lst1 = lst1.get_pointer()
    print("列表指针解包：", *p_lst1)  # [1, 2]