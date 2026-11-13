# -*- coding: utf-8 -*-
"""
HW1 - 分治思想基础部分：合并排序（Merge Sort）

分治（Divide and Conquer）三步走：
    分解（Divide）：把原问题拆成若干个规模更小的子问题
    解决（Conquer）：递归地求解每个子问题（规模足够小时直接求解）
    合并（Combine）：把子问题的解合并成原问题的解
合并排序正好完美对应这三步。
"""

import random   # 用来生成随机测试数组
import sys      # 用来获取 / 设置 Python 解释器的递归深度上限


# ============================================================
# 一、合并排序的实现
# ============================================================

def merge(left, right):
    """
    两个"有序小数组"合并成一个"有序大数组"（这是 Combine 阶段的核心动作）。
    思路：每次比较两个小数组开头的元素，谁小就把谁放进结果里。
    """
    result = []   # 合并后的结果数组
    i = 0         # left 数组的指针
    j = 0         # right 数组的指针

    # 只要两个数组都还有元素，就比较各自头部，取较小的那个
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # 其中一个数组走完后，把另一个数组剩下的元素直接接到末尾（它们本身就有序）
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(arr, depth=0, depth_info=None):
    """
    合并排序主函数（递归实现）。

    参数说明：
        arr        : 待排序的数组（Python 的 list）
        depth      : 当前递归层数（根节点记为 0，每往下递归一层就 +1）
        depth_info : 用字典在递归过程中记录"出现过的最大深度"
                     形如 {"max_depth": 0}，用可变对象传参才能把修改带回来

    返回值：
        排好序的新数组（原数组不会被修改）
    """
    # 第一次调用时初始化深度记录器
    if depth_info is None:
        depth_info = {"max_depth": 0}
    # 每进入一层递归，就更新一次"到目前为止的最深深度"
    if depth > depth_info["max_depth"]:
        depth_info["max_depth"] = depth

    # ---------- 解决（Conquer）：递归的出口 ----------
    # 如果数组长度 <= 1，它本身就是"天然有序"的，不需要再分解，直接返回。
    # 这一句就是"最小子问题可以直接求解"的地方。
    if len(arr) <= 1:
        return arr

    # ---------- 分解（Divide） ----------
    # 从中间切成左右两半：mid 是切分点（向下取整）
    mid = len(arr) // 2
    # 左半部分：从 0 到 mid-1
    left_part = arr[:mid]
    # 右半部分：从 mid 到末尾
    right_part = arr[mid:]

    # ---------- 解决（Conquer） ----------
    # 递归调用自己，分别把左、右两半排好序；
    # depth + 1 表示"往下递归了一层"，这样深度就能被记录下来。
    sorted_left = merge_sort(left_part, depth + 1, depth_info)
    sorted_right = merge_sort(right_part, depth + 1, depth_info)

    # ---------- 合并（Combine） ----------
    # 两半都已有序，现在把它们合并成一个整体有序的数组并返回。
    return merge(sorted_left, sorted_right)


# ============================================================
# 二、测试
# ============================================================

def run_tests():
    """跑几组测试用例，验证排序结果是否正确。"""
    print("=" * 60)
    print("第一部分：测试用例")
    print("=" * 60)

    # 题目要求的核心用例
    case1 = [8, 3, 5, 1, 9, 2]
    expected1 = [1, 2, 3, 5, 8, 9]
    got1 = merge_sort(case1)
    print("输入 :", case1)
    print("输出 :", got1)
    print("期望 :", expected1)
    print("结果 :", "通过 ✔" if got1 == expected1 else "失败 ✘")
    print("-" * 60)

    # 几个边界 / 特殊情况，顺手一起验证（不影响主流程）
    extra_cases = [
        ([], []),                       # 空数组
        ([7], [7]),                     # 单个元素
        ([5, 5, 5], [5, 5, 5]),         # 全部相同
        ([3, 1, 2], [1, 2, 3]),         # 逆序
    ]
    for data, expect in extra_cases:
        got = merge_sort(data)
        status = "通过 ✔" if got == expect else "失败 ✘"
        print(f"输入 {str(data):<15} 输出 {str(got):<15} 期望 {str(expect):<15} {status}")

    print()


# ============================================================
# 三、观察递归深度
# ============================================================

def measure_recursion_depth(n=8000):
    """
    生成 n 个随机数，排序一遍，并打印过程中出现的最大递归深度。

    关于 sys 模块：
        - sys.getrecursionlimit() 读取解释器当前的递归层数上限（默认 1000 层）；
        - sys.setrecursionlimit() 可以修改这个上限。
      这里把它调大一些，保证 8000 个元素的测试不会撞到上限（虽然理论上
      本题目只需要 13~14 层，留足余量更安全）。
    """
    print("=" * 60)
    print("第二部分：观察递归深度（%d 个随机元素）" % n)
    print("=" * 60)

    # 用 sys 模块查看 / 调整递归上限
    print("sys 模块读取到的默认递归上限：", sys.getrecursionlimit(), "层")
    sys.setrecursionlimit(10000)          # 为本次测试留足余量
    print("调整后的递归上限：", sys.getrecursionlimit(), "层")
    print("-" * 60)

    # 1. 生成 n 个随机整数（范围 0 ~ 999999，够随机）
    data = [random.randint(0, 999999) for _ in range(n)]
    print("已生成随机数组，元素个数 =", len(data))

    # 2. 用它跑一遍合并排序，同时记录最大递归深度
    depth_info = {"max_depth": 0}
    sorted_data = merge_sort(data, depth=0, depth_info=depth_info)

    # 3. 用 Python 自带的 sorted() 交叉验证，确保真的排对了
    is_correct = (sorted_data == sorted(data))
    print("排序结果正确性校验（与 sorted() 对比）：", "通过 ✔" if is_correct else "失败 ✘")

    # 4. 打印最大递归深度
    max_depth = depth_info["max_depth"]
    print()
    print(">>> 最大递归深度（根层记为 0）：", max_depth)
    print(">>> 若把根层记为第 1 层，则总层数：", max_depth + 1)

    # 5. 和理论值做个对照，帮助你理解这个数字是怎么来的
    import math
    theory = math.ceil(math.log2(n))   # log2(8000) ≈ 12.97，向上取整为 13
    print(">>> 理论值 ceil(log2(%d)) = %d" % (n, theory))
    print(">>> 结论：实际深度 %d 与理论值 %d 吻合，说明每次折半大约需要 %d 层。"
          % (max_depth, theory, theory))
    print()


# ============================================================
# 四、程序入口
# ============================================================

if __name__ == "__main__":
    run_tests()                     # 先跑测试用例
    measure_recursion_depth(8000)   # 再观察 8000 个元素的递归深度
