"""栈模块：模拟C++ std::stack，基于Vector实现"""
from typing import Type, Any, Optional
try:
    from .vector import Vector
except ImportError:
    # 备用导入路径（同一目录）
    import vector as vector_module
    Vector = vector_module.Vector

class Stack:
    """栈类（LIFO 后进先出），复刻C++ std::stack"""
    def __init__(self, elem_type: Type, initial_capacity: int = 4):
        """
        初始化栈
        :param elem_type: 栈元素类型（int/float/str等）
        :param initial_capacity: 初始容量（默认4，复用Vector的容量策略）
        """
        self.elem_type = elem_type
        # 底层用Vector存储数据，利用其动态扩容/缩容能力
        self._container = Vector(elem_type, initial_capacity)

    # ========== 核心属性 ==========
    @property
    def size(self) -> int:
        """返回栈中元素数量"""
        return self._container.size

    @property
    def capacity(self) -> int:
        """返回栈的当前容量"""
        return self._container.capacity

    @property
    def empty(self) -> bool:
        """判断栈是否为空"""
        return self._container.empty

    # ========== 核心操作（对标C++ std::stack） ==========
    def push(self, value: Any):
        """入栈：将元素添加到栈顶（尾部）"""
        # 严格类型转换，保证类型安全
        typed_value = self.elem_type(value)
        self._container.push_back(typed_value)

    def pop(self) -> Any:
        """出栈：移除并返回栈顶元素"""
        if self.empty:
            raise IndexError("pop: 空栈无法出栈")
        return self._container.pop_back()

    def top(self) -> Any:
        """查看栈顶元素（不移除）"""
        if self.empty:
            raise IndexError("top: 空栈无栈顶元素")
        # 栈顶是Vector的最后一个元素
        return self._container[self.size - 1]

    def clear(self):
        """清空栈"""
        self._container.clear()

    def swap(self, other: 'Stack'):
        """交换两个同类型栈的内容"""
        if not isinstance(other, Stack) or other.elem_type != self.elem_type:
            raise TypeError("只能交换同类型的Stack")
        self._container.swap(other._container)

    def emplace(self, *args, **kwargs):
        """原地构造元素入栈（简化版，适配基础类型）"""
        """
        示例：
        stack.emplace(3.14)  # 等价于 stack.push(float(3.14))
        stack.emplace("hello")  # 等价于 stack.push(str("hello"))
        """
        if args and not kwargs:
            self.push(self.elem_type(*args))
        elif kwargs and not args:
            self.push(self.elem_type(**kwargs))
        else:
            raise ValueError("emplace仅支持基础类型的参数构造")

    # ========== 扩展操作 ==========
    def reserve(self, new_capacity: int):
        """预分配栈的容量（避免频繁扩容）"""
        self._container.reserve(new_capacity)

    def shrink_to_fit(self):
        """缩容：释放未使用的容量，匹配当前元素数量"""
        self._container.shrink_to_fit()

    # ========== 字符串表示/运算符重载 ==========
    def __str__(self) -> str:
        """返回栈的字符串表示（栈顶在右侧）"""
        if self.empty:
            return f"Stack<{self.elem_type.__name__}> [] (size: 0, capacity: {self.capacity})"
        
        # 提取元素，栈顶显示在右侧（用「→」标识）
        elements = [str(self._container[i]) for i in range(self.size)]
        return (f"Stack<{self.elem_type.__name__}> [{' | '.join(elements)}] "
                f"(size: {self.size}, capacity: {self.capacity}, 栈顶→最后元素)")

    def __repr__(self) -> str:
        """返回详细表示"""
        return self.__str__()

    def __len__(self) -> int:
        """返回栈大小（兼容Python len()）"""
        return self.size

    def __eq__(self, other: 'Stack') -> bool:
        """判断两个栈是否相等（元素顺序+内容完全一致）"""
        if not isinstance(other, Stack) or other.elem_type != self.elem_type:
            return False
        if self.size != other.size:
            return False
        # 逐元素比较（栈的顺序严格一致）
        for i in range(self.size):
            if self._container[i] != other._container[i]:
                return False
        return True
    def __iter__(self):
        """迭代栈（从栈底到栈顶）"""
        for elem in self._container:
            yield elem

    def __getitem__(self, index: int) -> Any:
        """访问栈中指定位置的元素（仅用于调试，不推荐业务使用）"""
        if not isinstance(index, int):
            raise TypeError("索引必须是整数")
        if index < 0:
            # 支持负索引（-1=栈顶，-2=栈顶前一个）
            index = self.size + index
        self._container._check_index(index)
        return self._container[index]

    def reverse(self):
        """反转栈（栈顶变栈底，栈底变栈顶）"""
        self._container.reverse()

# ========== 便捷函数 ==========
def make_stack(elem_type: Type, *elements: Any) -> Stack:
    """快速创建栈并初始化元素（最后一个元素为栈顶）"""
    stack = Stack(elem_type, len(elements))
    for elem in elements:
        stack.push(elem)
    return stack

__all__ = ["Stack","make_stack"]
# ========== 测试代码 ==========
if __name__ == "__main__":
    # 测试1：基础操作
    print("=== 测试1：栈基础操作 ===")
    s = Stack(int)
    print("初始栈：", s)  # 空栈
    
    # 入栈
    s.push(10)
    s.push(20)
    s.push(30)
    print("入栈10,20,30后：", s)  # [10 | 20 | 30] (栈顶→30)
    
    # 查看栈顶
    print("栈顶元素：", s.top())  # 30
    
    # 出栈
    popped = s.pop()
    print(f"出栈元素：{popped}，栈：", s)  # [10 | 20] (栈顶→20)
    
    # 测试2：容量管理
    print("\n=== 测试2：容量管理 ===")
    print("当前容量：", s.capacity)  # 4（默认初始容量）
    s.reserve(10)  # 预分配容量
    print("预分配容量后：", s.capacity)  # 10
    s.shrink_to_fit()  # 缩容
    print("缩容后容量：", s.capacity)  # 4（匹配当前size=2，最小容量4）
    
    # 测试3：快速创建栈
    print("\n=== 测试3：快速创建栈 ===")
    s2 = make_stack(str, "first", "second", "top")
    print("字符串栈：", s2)  # [first | second | top] (栈顶→top)
    
    # 测试4：栈比较
    print("\n=== 测试4：栈比较 ===")
    s3 = make_stack(int, 1, 2, 3)
    s4 = make_stack(int, 1, 2, 3)
    s5 = make_stack(int, 1, 2, 4)
    print(f"s3 == s4: {s3 == s4}")  # True
    print(f"s3 == s5: {s3 == s5}")  # False
    
    # 测试5：emplace入栈
    print("\n=== 测试5：emplace入栈 ===")
    s6 = Stack(float)
    s6.emplace(3.14)
    s6.emplace(2.718)
    print("emplace入栈后：", s6)  # [3.14 | 2.718] (栈顶→2.718)
    
    # 测试6：清空栈
    print("\n=== 测试6：清空栈 ===")
    s6.clear()
    print("清空后：", s6)  # 空栈