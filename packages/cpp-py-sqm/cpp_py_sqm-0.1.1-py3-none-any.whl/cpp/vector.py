"""可变数组模块：模拟C++ std::vector，非递归快速排序（解决递归溢出）"""
from typing import Type, Any, Optional, Callable, List, Tuple
import sys
try:
    from .cpp_array import Array, ArrayPointer
    import pointer
except ImportError:
    # 备用导入路径（同一目录）
    import cpp_array as array_module
    Array = array_module.Array
    ArrayPointer = array_module.ArrayPointer
    import pointer

# 适度提高递归限制（可选，主要依赖非递归实现）
sys.setrecursionlimit(10000)

class Vector:
    """可变数组（动态数组）类，复刻C++ std::vector + 非递归快速排序"""
    def __init__(self, elem_type: Type, initial_capacity: int = 4):
        """
        初始化可变数组
        :param elem_type: 元素类型（int/float/str等）
        :param initial_capacity: 初始容量（默认4）
        """
        if not isinstance(initial_capacity, int) or initial_capacity < 0:
            raise ValueError("初始容量必须是非负整数")
        
        self.elem_type = elem_type
        self._size = 0  # 实际元素数量
        self._capacity = initial_capacity if initial_capacity > 0 else 4  # 容量（最小4）
        self._data = Array(elem_type, self._capacity)  # 底层数组

    # ========== 核心属性（无修改） ==========
    @property
    def size(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def empty(self) -> bool:
        return self._size == 0

    # ========== 基础操作（无修改） ==========
    def push_back(self, value: Any):
        if self._size >= self._capacity:
            self._resize_capacity(self._capacity * 2)
        self._data[self._size] = self.elem_type(value)
        self._size += 1

    def pop_back(self) -> Any:
        if self.empty:
            raise IndexError("pop_back: 空数组无法删除元素")
        self._size -= 1
        value = self._data[self._size].value
        if self._capacity > 8 and self._size < self._capacity // 4:
            self._resize_capacity(max(self._capacity // 2, 4))
        return value

    def reserve(self, new_capacity: int):
        if not isinstance(new_capacity, int) or new_capacity < 0:
            raise ValueError("容量必须是非负整数")
        if new_capacity > self._capacity:
            self._resize_capacity(new_capacity)

    def resize(self, new_size: int, default_value: Any = None):
        if not isinstance(new_size, int) or new_size < 0:
            raise ValueError("大小必须是非负整数")
        
        if new_size < self._size:
            self._size = new_size
        elif new_size > self._size:
            if new_size > self._capacity:
                self._resize_capacity(max(new_size, self._capacity * 2))
            default = self.elem_type(default_value) if default_value is not None else self.elem_type()
            for i in range(self._size, new_size):
                self._data[i] = default
            self._size = new_size

    def clear(self):
        self._size = 0

    def shrink_to_fit(self):
        if self._capacity > self._size:
            self._resize_capacity(max(self._size, 4))

    # ========== 插入/删除/查找/反转/批量操作（无修改） ==========
    def insert(self, index: int, value: Any):
        self._check_insert_index(index)
        if self._size >= self._capacity:
            self._resize_capacity(self._capacity * 2)
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i-1].value
        self._data[index] = self.elem_type(value)
        self._size += 1

    def erase(self, index: int, count: int = 1) -> int:
        self._check_index(index)
        if count <= 0:
            return 0
        actual_count = min(count, self._size - index)
        if actual_count == 0:
            return 0
        for i in range(index, self._size - actual_count):
            self._data[i] = self._data[i + actual_count].value
        self._size -= actual_count
        if self._capacity > 8 and self._size < self._capacity // 4:
            self._resize_capacity(max(self._capacity // 2, 4))
        return actual_count

    def find(self, value: Any) -> int:
        target = self.elem_type(value)
        for i in range(self._size):
            if self._data[i].value == target:
                return i
        return -1

    def reverse(self):
        if self._size <= 1:
            return
        left = 0
        right = self._size - 1
        while left < right:
            self._data[left], self._data[right] = self._data[right], self._data[left]
            left += 1
            right -= 1

    def assign(self, values: List[Any]):
        self.clear()
        self.reserve(len(values))
        for val in values:
            self.push_back(val)

    def swap(self, other: 'Vector'):
        if not isinstance(other, Vector) or other.elem_type != self.elem_type:
            raise TypeError("只能交换同类型的Vector")
        self._data, other._data = other._data, self._data
        self._size, other._size = other._size, self._size
        self._capacity, other._capacity = other._capacity, self._capacity

    # ========== 核心修复：非递归快速排序 ==========
    def sort(self, cmp: Optional[Callable[[Any, Any], bool]] = None):
        """
        非递归快速排序（解决递归溢出）
        :param cmp: 比较函数（a, b）→ bool，返回True表示a应在b前面
        """
        if self._size <= 1:
            return
        
        # 提取元素到临时列表
        temp = [self._data[i].value for i in range(self._size)]
        
        # 默认升序比较函数（优化：相等时返回False，避免逻辑失衡）
        if cmp is None:
            def cmp(a, b):
                return a < b
        # 包装比较函数，确保鲁棒性
        def safe_cmp(a, b):
            try:
                return cmp(a, b)
            except:
                return a < b  # 降级为默认升序
        
        # 非递归快速排序（用栈模拟递归）
        self._quick_sort_iterative(temp, 0, self._size - 1, safe_cmp)
        
        # 写回原数组
        for i in range(self._size):
            self._data[i] = temp[i]

    def _quick_sort_iterative(self, arr: List[Any], low: int, high: int, cmp: Callable[[Any, Any], bool]):
        """
        非递归快速排序（栈实现）
        :param arr: 待排序列表
        :param low: 左边界
        :param high: 右边界
        :param cmp: 安全的比较函数
        """
        # 用栈存储待排序的区间 (low, high)
        stack = [(low, high)]
        
        while stack:
            # 弹出当前区间
            current_low, current_high = stack.pop()
            if current_low >= current_high:
                continue
            
            # 分区获取基准索引
            pivot_idx = self._partition_optimized(arr, current_low, current_high, cmp)
            
            # 将左右子区间压入栈（先压右，后压左，保证左区间先处理）
            stack.append((pivot_idx + 1, current_high))
            stack.append((current_low, pivot_idx - 1))

    def _partition_optimized(self, arr: List[Any], low: int, high: int, cmp: Callable[[Any, Any], bool]) -> int:
        """
        优化的分区函数（三数取中法+处理重复元素）
        :param arr: 待排序列表
        :param low: 左边界
        :param high: 右边界
        :param cmp: 比较函数
        :return: 基准元素索引
        """
        # 1. 三数取中法选择基准（避免有序数组的最坏情况）
        mid = (low + high) // 2
        # 排序左、中、右三个元素，将中间值放到high位置作为基准
        if cmp(arr[mid], arr[low]):
            arr[low], arr[mid] = arr[mid], arr[low]
        if cmp(arr[high], arr[low]):
            arr[low], arr[high] = arr[high], arr[low]
        if cmp(arr[mid], arr[high]):
            arr[mid], arr[high] = arr[high], arr[mid]
        
        pivot = arr[high]
        i = low - 1
        
        # 2. 遍历分区（处理重复元素）
        for j in range(low, high):
            # 优化：相等元素随机分配，避免重复元素导致的分区失衡
            if cmp(arr[j], pivot) or (arr[j] == pivot and (j % 2 == 0)):
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        # 3. 将基准放到正确位置
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    # ========== 索引/指针/内部工具（无修改） ==========
    def __getitem__(self, index: int) -> Any:
        self._check_index(index)
        return self._data[index].value

    def __setitem__(self, index: int, value: Any):
        self._check_index(index)
        self._data[index] = self.elem_type(value)

    def begin(self) -> ArrayPointer:
        if self.empty:
            raise IndexError("空数组无法获取begin指针")
        return ArrayPointer(self._data, 0)

    def end(self) -> ArrayPointer:
        return ArrayPointer(self._data, self._size)

    def _check_index(self, index: int):
        if not isinstance(index, int):
            raise TypeError("索引必须是整数")
        if index < 0 or index >= self._size:
            raise IndexError(f"索引{index}越界，实际元素数量{self._size}")

    def _check_insert_index(self, index: int):
        if not isinstance(index, int):
            raise TypeError("索引必须是整数")
        if index < 0 or index > self._size:
            raise IndexError(f"插入索引{index}越界，合法范围[0, {self._size}]")

    def _resize_capacity(self, new_capacity: int):
        new_data = Array(self.elem_type, new_capacity)
        for i in range(self._size):
            new_data[i] = self._data[i].value
        self._data = new_data
        self._capacity = new_capacity

    # ========== 字符串表示/迭代/运算符（无修改） ==========
    def __str__(self) -> str:
        if self.empty:
            return f"Vector<{self.elem_type.__name__}> [] (size: 0, capacity: {self._capacity})"
        elements = [str(self._data[i].value) for i in range(self._size)]
        return (f"Vector<{self.elem_type.__name__}> [{', '.join(elements)}] "
                f"(size: {self._size}, capacity: {self._capacity})")

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self):
        for i in range(self._size):
            yield self._data[i].value

    def __len__(self) -> int:
        return self._size

    def __add__(self, other: 'Vector') -> 'Vector':
        if not isinstance(other, Vector) or other.elem_type != self.elem_type:
            raise TypeError("只能拼接同类型的Vector")
        new_vec = Vector(self.elem_type, self._size + other._size)
        for i in range(self._size):
            new_vec.push_back(self[i])
        for i in range(other._size):
            new_vec.push_back(other[i])
        return new_vec

# ========== 便捷函数 ==========
def make_vector(elem_type: Type, *elements: Any) -> Vector:
    vec = Vector(elem_type, len(elements))
    for elem in elements:
        vec.push_back(elem)
    return vec

# ========== 测试代码（验证修复效果） ==========
if __name__ == "__main__":
    import random
    import time

    # 测试1：大规模数据排序（10000条随机数）
    print("=== 非递归快速排序性能测试（10000条）===")
    random.seed(42)
    test_data = [random.randint(0, 100000) for _ in range(10000)]
    vec = Vector(int)
    vec.assign(test_data)

    start_time = time.time()
    vec.sort()  # 默认升序
    end_time = time.time()
    print(f"升序排序耗时：{end_time - start_time:.6f} 秒")
    print(f"排序后前10个元素：{[vec[i] for i in range(10)]}")
    print(f"排序后后10个元素：{[vec[i] for i in range(9990, 10000)]}")

    # 测试2：降序排序
    start_time = time.time()
    vec.sort(lambda a, b: a > b)  # 自定义降序
    end_time = time.time()
    print(f"\n降序排序耗时：{end_time - start_time:.6f} 秒")
    print(f"降序后前10个元素：{[vec[i] for i in range(10)]}")

    # 测试3：重复元素排序（极端场景）
    print("\n=== 重复元素排序测试 ===")
    repeat_vec = Vector(int)
    repeat_vec.assign([5]*2000 + [3]*2000 + [8]*2000)
    repeat_vec.sort()
    print(f"重复元素排序后前5个：{[repeat_vec[i] for i in range(5)]}")
    print(f"重复元素排序后中间5个：{[repeat_vec[i] for i in range(3000, 3005)]}")
    print(f"重复元素排序后最后5个：{[repeat_vec[i] for i in range(5995, 6000)]}")

    # 测试4：小数据排序
    small_vec = make_vector(int, 5, 2, 8, 1, 9, 3, 7, 4, 6)
    print(f"\n=== 小数据排序 ===")
    print(f"排序前：{small_vec}")
    small_vec.sort()
    print(f"排序后：{small_vec}")