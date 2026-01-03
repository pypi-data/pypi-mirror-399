"""多维数组模块：提供固定大小的多维数组及相关操作"""
import pointer
from typing import Type, List, Tuple, Any

# 修复导入（确保路径正确）
try:
    from cpp.cpp_array import Array, ArrayPointer
except ImportError:
    try:
        from .cpp_array import Array, ArrayPointer
    except ImportError:
        from cpp_array import Array, ArrayPointer

class MultiArray:
    """多维数组类，支持任意维度的数组操作"""
    def __init__(self, elem_type: Type, *dims: int):
        """
        初始化多维数组
        :param elem_type: 元素类型（如int, float等）
        :param dims: 各维度大小（如2,3表示2行3列的二维数组）
        """
        if not dims or any(d <= 0 for d in dims):
            raise ValueError("多维数组的每个维度大小必须是正整数")
        
        self.elem_type = elem_type
        self.dims = dims  # 维度元组（如(2,3,4)表示三维数组）
        self.ndim = len(dims)  # 维度数量
        self.size = 1  # 总元素数量
        for d in dims:
            self.size *= d
        
        # 递归创建多维数组（底层基于一维数组存储）
        self._data = Array(elem_type, self.size)
        self._shape = self._create_shape(dims, elem_type)

    def _create_shape(self, dims: Tuple[int, ...], elem_type: Type) -> Any:
        """递归创建多维数组的结构（嵌套列表形式）"""
        if len(dims) == 1:
            return self._data  # 最后一维直接使用一维数组
        
        current_dim = dims[0]
        remaining_dims = dims[1:]
        return [self._create_shape(remaining_dims, elem_type) for _ in range(current_dim)]

    def _flatten_index(self, indices: Tuple[int, ...]) -> int:
        """将多维索引转换为一维索引（行优先）"""
        if len(indices) != self.ndim:
            raise IndexError(f"索引维度不匹配，需要{self.ndim}维，实际{len(indices)}维")
        
        # 检查各维度索引合法性
        for i, (idx, dim) in enumerate(zip(indices, self.dims)):
            if not isinstance(idx, int) or idx < 0 or idx >= dim:
                raise IndexError(f"第{i}维索引{idx}越界，范围[0, {dim-1}]")
        
        # 行优先计算一维索引（正确逻辑）
        flat_idx = 0
        for i in range(self.ndim):
            flat_idx = flat_idx * self.dims[i] + indices[i]
        return flat_idx

    def __getitem__(self, indices: Tuple[int, ...]) -> Any:
        """重载[]：获取指定多维索引的元素或子数组"""
        if not isinstance(indices, tuple):
            indices = (indices,)
        
        # 如果索引维度小于总维度，返回子数组
        if len(indices) < self.ndim:
            current = self._shape
            for idx in indices:
                current = current[idx]
            return current
        
        # 否则返回具体元素
        flat_idx = self._flatten_index(indices)
        return self._data[flat_idx]

    def __setitem__(self, indices: Tuple[int, ...], value: Any):
        """重载[]：设置指定多维索引的元素值"""
        if not isinstance(indices, tuple):
            indices = (indices,)
        
        if len(indices) != self.ndim:
            raise IndexError(f"设置元素需要{self.ndim}维索引，实际{len(indices)}维")
        
        flat_idx = self._flatten_index(indices)
        self._data[flat_idx] = value

    def __str__(self) -> str:
        """返回多维数组的字符串表示"""
        return self._str_helper(self._shape, self.ndim)

    def _str_helper(self, obj: Any, depth: int) -> str:
        """递归生成字符串表示"""
        if isinstance(obj, Array):
            return "[" + ", ".join(str(elem.value) for elem in obj) + "]"
        return "[" + ", ".join(self._str_helper(item, depth-1) for item in obj) + "]"

class MultiArrayPointer(pointer.var):
    """多维数组指针类，支持指针运算"""
    def __init__(self, multi_array: MultiArray, *indices: int):
        """
        初始化多维数组指针
        :param multi_array: 指向的多维数组
        :param indices: 初始指向的多维索引
        """
        if not isinstance(multi_array, MultiArray):
            raise TypeError("多维指针必须指向MultiArray类型")
        
        self.multi_array = multi_array
        self.current_indices = list(indices) if indices else [0]*multi_array.ndim
        self._check_indices()
        
        super().__init__(multi_array.elem_type)
        self._update_value()

    def _check_indices(self):
        """检查多维索引是否合法"""
        if len(self.current_indices) != self.multi_array.ndim:
            raise IndexError(
                f"索引维度不匹配，数组{self.multi_array.ndim}维，指针{len(self.current_indices)}维"
            )
        for i, (idx, dim) in enumerate(zip(self.current_indices, self.multi_array.dims)):
            if idx < 0 or idx >= dim:
                raise IndexError(f"第{i}维指针越界，范围[0, {dim-1}]")

    def _update_value(self):
        """更新指针指向的值"""
        flat_idx = self.multi_array._flatten_index(tuple(self.current_indices))
        self.value = self.multi_array._data[flat_idx].value

    def __add__(self, offset: int) -> 'MultiArrayPointer':
        """指针加法：按一维顺序移动指针（返回新指针）"""
        if not isinstance(offset, int):
            raise TypeError("指针偏移量必须是整数")
        
        # 转换为一维索引计算偏移
        flat_idx = self.multi_array._flatten_index(tuple(self.current_indices))
        new_flat_idx = flat_idx + offset
        new_indices = self._unflatten_index(new_flat_idx)
        return MultiArrayPointer(self.multi_array, *new_indices)

    def __iadd__(self, offset: int) -> 'MultiArrayPointer':
        """指针自增：按一维顺序移动指针（修改自身）"""
        if not isinstance(offset, int):
            raise TypeError("指针偏移量必须是整数")
        
        flat_idx = self.multi_array._flatten_index(tuple(self.current_indices))
        new_flat_idx = flat_idx + offset
        self.current_indices = self._unflatten_index(new_flat_idx)
        self._check_indices()
        self._update_value()
        return self

    def _unflatten_index(self, flat_idx: int) -> List[int]:
        """
        将一维索引转换为多维索引（修复核心：行优先C风格）
        :param flat_idx: 一维索引
        :return: 多维索引列表
        """
        if flat_idx < 0 or flat_idx >= self.multi_array.size:
            raise IndexError(f"指针偏移越界，总元素数{self.multi_array.size}")
        
        indices = []
        remaining = flat_idx
        # 从最后一维开始计算（行优先的逆过程）
        dims_reversed = list(self.multi_array.dims)[::-1]
        
        for dim in dims_reversed:
            indices.append(remaining % dim)
            remaining = remaining // dim
        
        # 反转回原维度顺序
        indices = indices[::-1]
        return indices

    def __sub__(self, offset: int) -> 'MultiArrayPointer':
        """指针减法：返回新指针"""
        return self.__add__(-offset)
    
    def __isub__(self, offset: int) -> 'MultiArrayPointer':
        """指针自减：修改自身"""
        return self.__iadd__(-offset)

    def __str__(self) -> str:
        """返回指针的字符串表示"""
        return (f"MultiPointer to {self.multi_array.elem_type.__name__} "
                f"at indices {tuple(self.current_indices)}: {self.value}")

__all__ = ["MultiArray","MultiArrayPointer"]

# 测试代码（验证修复效果）
if __name__ == "__main__":
    # 创建2x3的二维int数组
    arr_2d = MultiArray(int, 2, 3)
    # 赋值：按行优先填充 0-5
    for i in range(2):
        for j in range(3):
            arr_2d[i, j] = i * 3 + j
    print("二维数组初始值：", arr_2d)  # 应输出：[[0, 1, 2], [3, 4, 5]]
    
    # 创建指针指向(0,0)
    ptr = MultiArrayPointer(arr_2d, 0, 0)
    print("初始指针：", ptr)  # 应输出：MultiPointer to int at indices (0, 0): 0
    
    # 指针+4（一维索引从0→4）
    ptr += 4
    print("指针+4后：", ptr)  # 应输出：MultiPointer to int at indices (1, 1): 4
    
    # 指针+1（一维索引从4→5）
    ptr += 1
    print("指针+1后：", ptr)  # 应输出：MultiPointer to int at indices (1, 2): 5
    
    # 指针-2（一维索引从5→3）
    ptr -= 2
    print("指针-2后：", ptr)  # 应输出：MultiPointer to int at indices (1, 0): 3
    
    # 测试三维数组
    arr_3d = MultiArray(float, 2, 2, 2)
    arr_3d[0,0,0] = 1.1
    arr_3d[0,1,1] = 2.2
    arr_3d[1,1,1] = 3.3
    ptr_3d = MultiArrayPointer(arr_3d, 0, 0, 0)
    ptr_3d += 5
    print("\n三维数组指针+5后：", ptr_3d)  # 应输出：MultiPointer to float at indices (1, 0, 1): 0.0