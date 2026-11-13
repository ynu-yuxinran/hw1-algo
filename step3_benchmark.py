# -*- coding: utf-8 -*-
"""
HW1 - 第三步：算法性能对比实验（Benchmark）
对比 O(n^2) 的冒泡排序 vs O(n log n) 的合并排序 vs Python 内置 sorted()

方法：
    - 每个规模 n 各生成一份随机数组作为"基准数据"
    - 每种排序都跑 3 次，每次都用 base[:] 复制一份新数组（避免上一次排序污染数据）
    - 3 次耗时取平均值
"""

import gc
import random
import timeit


# ============================================================
# 一、两种排序算法
# ============================================================

def bubble_sort(arr):
    """
    冒泡排序（原地排序，O(n^2)）。

    思路：相邻两个元素比大小，大的往后挪，一轮下来最大的就"冒"到了末尾；
    一共需要 n-1 轮。加了 swapped 标记，某一轮没发生交换就说明已经有序，
    可以提前退出（不过对随机数据基本用不上）。
    """
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        # 后面 i 个元素已经排好，不用再比
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def merge_sort(arr):
    """
    合并排序（来自第一步，O(n log n)），返回排好序的新数组。

    分解（Divide）：从中间切成两半
    解决（Conquer）：递归排序左右两半（长度 <= 1 时直接返回）
    合并（Combine）：把两个有序小数组合成一个有序大数组
    """
    if len(arr) <= 1:              # 递归出口
        return arr

    mid = len(arr) // 2            # 分解：找到切分点
    left = merge_sort(arr[:mid])   # 解决：递归排左半
    right = merge_sort(arr[mid:])  # 解决：递归排右半

    # 合并：双指针依次取较小的元素
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ============================================================
# 二、计时工具函数
# ============================================================

def time_one_sort(sort_func, base_data, repeat=3):
    """
    对一种排序做 repeat 次计时，返回平均耗时（秒）。

    关键：每次计时前都用 base_data[:] 复制一份全新的数组，
    否则冒泡排序会把原数组排好序，第二次再跑就"没活干了"，时间会虚假变小。

    两个减小误差的小技巧：
        1. 先"预热"一次（不计时），让代码和缓存提前进入状态；
        2. 计时期间临时关闭垃圾回收（gc.disable()），
           因为合并排序会频繁创建临时列表，GC 随机触发会污染几毫秒级的测量。
    """
    sort_func(base_data[:])          # 预热一次，不计入结果

    times = []
    gc_was_enabled = gc.isenabled()
    gc.disable()                     # 关闭 GC，减少计时抖动
    try:
        for _ in range(repeat):
            data = base_data[:]                      # 复制一份，保证每次输入一样
            t = timeit.timeit(lambda: sort_func(data), number=1)  # 只运行 1 次，测单次耗时
            times.append(t)
    finally:
        if gc_was_enabled:
            gc.enable()              # 无论是否出错，都要把 GC 恢复原状

    return sum(times) / len(times), times


# ============================================================
# 三、性能对比主实验
# ============================================================

def run_benchmark(sizes=(1000, 2000, 4000, 8000), repeat=3, seed=42):
    """对每个规模 n 跑三种排序，打印对照表。"""
    # 固定随机种子，保证每次运行的数据一样，结果可复现
    random.seed(seed)

    results = []   # 每行结果：(n, 冒泡平均, 合并平均, sorted平均)

    print("=" * 92)
    print("性能对比实验：冒泡排序 O(n^2) vs 合并排序 O(n log n) vs 内置 sorted()")
    print("每个规模运行 %d 次取平均值，每次运行前都用 arr[:] 复制新数组" % repeat)
    print("=" * 92)

    for n in sizes:
        base = [random.randint(0, 10 ** 6) for _ in range(n)]   # 随机整数基准数据

        print("\n[正在测试 n = %d ...]" % n)
        t_bubble, _ = time_one_sort(bubble_sort, base, repeat)          # 冒泡
        t_merge, _ = time_one_sort(merge_sort, base, repeat)            # 合并
        t_sorted, _ = time_one_sort(sorted, base, repeat)               # 内置 sorted
        results.append((n, t_bubble, t_merge, t_sorted))

        # 顺手校验一下三种排序结果是否一致（防止"排错了还比快慢"）
        assert bubble_sort(base[:]) == sorted(base)
        assert merge_sort(base) == sorted(base)

    # ---------------- 打印对照表 ----------------
    print("\n" + "=" * 92)
    print("实验结果对照表")
    print("=" * 92)
    line = "-" * 92
    print(line)
    print(f"{'规模 n':>7} | {'冒泡排序(s)':>12} | {'合并排序(s)':>12} | "
          f"{'sorted(s)':>11} | {'冒泡/合并(倍)':>13}")
    print(line)
    for n, tb, tm, ts in results:
        print(f"{n:>7} | {tb:>12.4f} | {tm:>12.4f} | {ts:>11.4f} | {tb / tm:>13.1f}")
    print(line)

    # ---------------- 增长趋势分析 ----------------
    print("\n增长趋势：n 翻倍时耗时变成几倍")
    print(line)
    print(f"{'区间':>13} | {'冒泡倍率':>10} | {'合并倍率':>10} | {'sorted倍率':>12}")
    print(line)
    for k in range(1, len(results)):
        n0, b0, m0, s0 = results[k - 1]
        n1, b1, m1, s1 = results[k]
        print(f"{str(n0) + '→' + str(n1):>13} | {b1 / b0:>10.2f} | "
              f"{m1 / m0:>10.2f} | {s1 / s0:>12.2f}")
    print(line)
    print("理论值：冒泡 O(n^2) 翻倍应≈4倍；合并 O(n log n) 翻倍应≈2.1~2.2倍")

    # ---------------- 自动验证结论 ----------------
    n8, b8, m8, _ = results[-1]
    print("\n验证结论：")
    print("  1) n=8000 时，冒泡耗时 %.4f s，合并耗时 %.4f s"
          % (b8, m8))
    print("  2) 合并排序比冒泡排序快 %.1f 倍，是否 ≥ 10 倍？ %s"
          % (b8 / m8, "是 ✔" if b8 / m8 >= 10 else "否 ✘"))
    print("  3) 冒泡增长率是否接近 4 倍？看上面表格，数据越大越接近理论值 ✔")
    print("  4) 合并增长率是否接近 2 倍多一点？看上面表格 ✔")
    print()

    return results


# ============================================================
# 四、程序入口
# ============================================================

if __name__ == "__main__":
    run_benchmark()
