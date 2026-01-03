"""数组模块：提供固定大小数组及相关操作"""
from typing import Type, List, Any
import sys
import os

# 将cpp文件夹的父目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 导入pointer模块（确保路径正确）
try:
    import pointer
except ImportError:
    raise ImportError("请确保pointer.py在当前目录或Python路径中")

class Array:
    def __init__(self, type: Type, size: int):
        """
        初始化数组
        :param type: 元素类型（如int, float等）
        :param size: 数组大小（正整数）
        """
        if not isinstance(size, int) or size <= 0:
            raise ValueError("数组大小必须是正整数")
        
        self.type = type
        self.size = size
        self._elements = [pointer.var(type) for _ in range(size)]
    
    def __getitem__(self, index: int) -> pointer.var:
        """重载[]：获取指定索引的元素"""
        self._check_index(index)
        return self._elements[index]
    
    def __setitem__(self, index: int, value: Any):
        """重载[]：设置指定索引的元素值"""
        self._check_index(index)
        self._elements[index].value = value
    
    def _check_index(self, index: int):
        """检查索引是否合法"""
        if not isinstance(index, int):
            raise TypeError("数组索引必须是整数")
        if index < 0 or index >= self.size:
            raise IndexError(f"数组索引{index}越界，大小为{self.size}")
    
    def __len__(self) -> int:
        """返回数组大小"""
        return self.size
    
    def __str__(self) -> str:
        """返回数组的字符串表示"""
        elements_str = ", ".join(str(elem.value) for elem in self._elements)
        return f"{self.type.__name__}[{self.size}] = [{elements_str}]"

class ArrayPointer(pointer.var):
    """数组指针类，支持指针运算"""
    def __init__(self, array: Array, index: int = 0):
        """
        初始化数组指针
        :param array: 指向的数组
        :param index: 初始指向的索引
        """
        if not isinstance(array, Array):
            raise TypeError("数组指针必须指向Array类型")
        
        self.array = array
        self.current_index = index
        super().__init__(array.type)
        self._update_value()
    
    def _update_value(self):
        """更新指针指向的值"""
        self.value = self.array[self.current_index].value
    
    def __add__(self, offset: int) -> 'ArrayPointer':
        """指针加法：返回新指针"""
        if not isinstance(offset, int):
            raise TypeError("指针偏移量必须是整数")
        
        new_index = self.current_index + offset
        return ArrayPointer(self.array, new_index)
    
    def __iadd__(self, offset: int) -> 'ArrayPointer':
        """指针自增：修改自身"""
        if not isinstance(offset, int):
            raise TypeError("指针偏移量必须是整数")
        
        self.current_index += offset
        self._check_bounds()
        self._update_value()
        return self
    
    def __sub__(self, offset: int) -> 'ArrayPointer':
        """指针减法：返回新指针"""
        return self.__add__(-offset)
    
    def __isub__(self, offset: int) -> 'ArrayPointer':
        """指针自减：修改自身"""
        return self.__iadd__(-offset)
    
    def _check_bounds(self):
        """检查指针是否在数组范围内"""
        if self.current_index < 0 or self.current_index >= self.array.size:
            raise IndexError(f"指针越界，数组大小为{self.array.size}")
    
    def __str__(self) -> str:
        """返回指针的字符串表示"""
        return f"Pointer to {self.array.type.__name__} at index {self.current_index}: {self.value}"

__all__ = ["Array","ArrayPointer"]
# 测试代码
if __name__ == "__main__":
    arr = Array(int, 5)
    arr[0] = 10
    arr[2] = 30
    print("一维数组：", arr)
    
    ptr = ArrayPointer(arr, 0)
    ptr += 2
    print("数组指针：", ptr)