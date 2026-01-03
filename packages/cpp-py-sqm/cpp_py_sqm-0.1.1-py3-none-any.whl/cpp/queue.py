"""队列模块：模拟C++ std::queue，基于Vector实现"""
from typing import Type, Any, Optional
try:
    from .vector import Vector
except ImportError:
    # 备用导入路径（同一目录）
    import vector as vector_module
    Vector = vector_module.Vector

class Queue:
    """队列类（FIFO 先进先出），复刻C++ std::queue"""
    def __init__(self, elem_type: Type):
        """
        初始化队列
        :param elem_type: 队列元素类型（int/float/str等）
        """
        self.elem_type = elem_type
        # 底层用Vector存储数据，利用其动态扩容能力
        self._container = Vector(elem_type)
        # 队首指针（索引），优化出队性能（避免频繁删除头部元素）
        self._front_idx = 0

    # ========== 核心属性 ==========
    @property
    def size(self) -> int:
        """返回队列中元素数量"""
        return len(self._container) - self._front_idx

    @property
    def empty(self) -> bool:
        """判断队列是否为空"""
        return self.size == 0

    # ========== 核心操作 ==========
    def push(self, value: Any):
        """入队：将元素添加到队尾"""
        # 转换为指定类型，保证类型安全
        typed_value = self.elem_type(value)
        self._container.push_back(typed_value)

    def pop(self) -> Any:
        """出队：移除并返回队首元素"""
        if self.empty:
            raise IndexError("pop: 空队列无法出队")
        
        # 获取队首元素
        front_value = self._container[self._front_idx]
        # 移动队首指针（懒删除，避免频繁移动数组元素）
        self._front_idx += 1
        
        # 优化：当队首指针超过容器1/4且容器容量>8时，缩容并重置指针（释放内存）
        if self._front_idx > len(self._container) // 4 and len(self._container) > 8:
            # 创建新容器，复制有效元素
            new_container = Vector(self.elem_type, self.size)
            for i in range(self._front_idx, len(self._container)):
                new_container.push_back(self._container[i])
            self._container = new_container
            self._front_idx = 0
        
        return front_value

    def front(self) -> Any:
        """查看队首元素（不移除）"""
        if self.empty:
            raise IndexError("front: 空队列无队首元素")
        return self._container[self._front_idx]

    def back(self) -> Any:
        """查看队尾元素（不移除）"""
        if self.empty:
            raise IndexError("back: 空队列无队尾元素")
        return self._container[len(self._container) - 1]

    def clear(self):
        """清空队列"""
        self._container = Vector(self.elem_type)
        self._front_idx = 0

    # ========== 扩展操作 ==========
    def swap(self, other: 'Queue'):
        """交换两个同类型队列的内容"""
        if not isinstance(other, Queue) or other.elem_type != self.elem_type:
            raise TypeError("只能交换同类型的Queue")
        # 交换底层容器和队首指针
        self._container.swap(other._container)
        self._front_idx, other._front_idx = other._front_idx, self._front_idx

    def emplace(self, *args, **kwargs):
        """原地构造元素入队（简化版，适配基础类型）"""
        # 基础类型直接构造，复杂类型可扩展
        if args and not kwargs:
            self.push(self.elem_type(*args))
        elif kwargs and not args:
            self.push(self.elem_type(**kwargs))
        else:
            raise ValueError("emplace仅支持基础类型的参数构造")

    # ========== 字符串表示 ==========
    def __str__(self) -> str:
        """返回队列的字符串表示"""
        if self.empty:
            return f"Queue<{self.elem_type.__name__}> [] (size: 0)"
        
        # 提取有效元素（从front_idx到末尾）
        elements = []
        for i in range(self._front_idx, len(self._container)):
            elements.append(str(self._container[i]))
        
        return (f"Queue<{self.elem_type.__name__}> [{' -> '.join(elements)}] "
                f"(size: {self.size})")

    def __repr__(self) -> str:
        """返回详细表示"""
        return self.__str__()

    # ========== 运算符重载 ==========
    def __len__(self) -> int:
        """返回队列大小（兼容Python len()）"""
        return self.size

    def __eq__(self, other: 'Queue') -> bool:
        """判断两个队列是否相等"""
        if not isinstance(other, Queue) or other.elem_type != self.elem_type:
            return False
        if self.size != other.size:
            return False
        # 逐元素比较
        self_ptr = self._front_idx
        other_ptr = other._front_idx
        while self_ptr < len(self._container) and other_ptr < len(other._container):
            if self._container[self_ptr] != other._container[other_ptr]:
                return False
            self_ptr += 1
            other_ptr += 1
        return True

class Deque(Queue):
    """双端队列（Deque），支持头部/尾部入队出队"""
    def push_front(self, value: Any):
        """头部入队"""
        typed_value = self.elem_type(value)
        # 若队首指针>0，直接插入到front_idx-1位置
        if self._front_idx > 0:
            self._front_idx -= 1
            self._container.insert(self._front_idx, typed_value)
        else:
            # front_idx=0时，插入到容器头部
            self._container.insert(0, typed_value)
    
    def pop_back(self) -> Any:
        """尾部出队"""
        if self.empty:
            raise IndexError("pop_back: 空队列无法出队")
        return self._container.pop_back()

# ========== 便捷函数 ==========
def make_queue(elem_type: Type, *elements: Any) -> Queue:
    """快速创建队列并初始化元素"""
    q = Queue(elem_type)
    for elem in elements:
        q.push(elem)
    return q

__all__ = ["Queue","Deque","make_queue"]
# ========== 测试代码 ==========
if __name__ == "__main__":
    # 测试1：基础操作
    print("=== 测试1：队列基础操作 ===")
    q = Queue(int)
    print("初始队列：", q)  # 空队列
    
    # 入队
    q.push(10)
    q.push(20)
    q.push(30)
    print("入队10,20,30后：", q)  # [10 -> 20 -> 30] (size:3)
    
    # 查看队首/队尾
    print("队首元素：", q.front())  # 10
    print("队尾元素：", q.back())   # 30
    
    # 出队
    popped = q.pop()
    print(f"出队元素：{popped}，队列：", q)  # [20 -> 30] (size:2)
    
    # 测试2：懒删除优化
    print("\n=== 测试2：懒删除优化 ===")
    # 连续出队，触发缩容
    q.pop()  # 出队20
    q.pop()  # 出队30（队列为空）
    print("出队所有元素后：", q)  # 空队列
    q.push(40)
    q.push(50)
    print("重新入队40,50后：", q)  # [40 -> 50] (size:2)
    print("底层容器容量：", q._container.capacity)  # 已缩容为4（默认初始容量）
    
    # 测试3：快速创建队列
    print("\n=== 测试3：快速创建队列 ===")
    q2 = make_queue(str, "hello", "world", "cpp")
    print("字符串队列：", q2)  # [hello -> world -> cpp] (size:3)
    
    # 测试4：队列比较
    print("\n=== 测试4：队列比较 ===")
    q3 = make_queue(int, 10, 20, 30)
    q4 = make_queue(int, 10, 20, 30)
    q5 = make_queue(int, 10, 20, 40)
    print(f"q3 == q4: {q3 == q4}")  # True
    print(f"q3 == q5: {q3 == q5}")  # False
    
    # 测试5：emplace入队
    print("\n=== 测试5：emplace入队 ===")
    q6 = Queue(float)
    q6.emplace(3.14)
    q6.emplace(2.718)
    print("emplace入队后：", q6)  # [3.14 -> 2.718] (size:2)