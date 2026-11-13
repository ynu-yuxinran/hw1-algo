# -*- coding: utf-8 -*-
"""
HW1 - 第二步：二分查找（Binary Search）

核心前提：数组必须是"有序"的（升序）。
原理：每次取中间元素和目标比较，比较一次就能排除掉一半的元素，
      所以 1024 个元素最多大约 10 次比较就能找到（log2(1024) = 10）。
"""

import random   # 用于生成随机利率 / 打乱数组


# ============================================================
# 一、生成模拟利率表
# ============================================================

def build_rate_table(n=1024):
    """
    生成 n 个"升序排列"的模拟利率，范围从 0.01 到 n*0.01。

    这里故意让利率正好落在 0.01 的整数倍上（0.01, 0.02, ..., 10.24），
    这样一共就是 1024 档，且 3.75% 恰好是其中的一档，方便后面查找。

    注意：用 round(..., 2) 是为了避免 0.01 这种小数在计算机里的浮点误差，
    保证表里的值和 3.75 能严格相等。
    """
    return [round(0.01 * (i + 1), 2) for i in range(n)]


# ============================================================
# 二、二分查找
# ============================================================

def binary_search(rates, target):
    """
    在有序列表 rates 中查找 target。

    参数：
        rates  : 有序（升序）的利率表
        target : 要查找的目标利率

    返回：
        (index, comparisons)
        index       : 找到时是目标所在下标，找不到返回 -1
        comparisons : 本次查找一共比较了多少次

    另外：函数内部会直接打印"一共比较了多少次"（题目要求）。
    """
    low = 0                     # 搜索区间的左边界（包含）
    high = len(rates) - 1       # 搜索区间的右边界（包含）
    comparisons = 0             # 比较次数计数器

    # 只要区间里还有元素，就继续找
    while low <= high:
        # 取中间位置（用 // 保证是整数下标）
        mid = (low + high) // 2
        comparisons += 1        # 每比较一次，计数器 +1

        if rates[mid] == target:
            # 命中目标，打印比较次数并返回下标
            print(f"  找到 {target}%，位于第 {mid} 档，共比较 {comparisons} 次")
            return mid, comparisons

        elif rates[mid] < target:
            # 中间值太小了 → 目标一定在右半边，丢掉左半边
            low = mid + 1

        else:
            # 中间值太大了 → 目标一定在左半边，丢掉右半边
            high = mid - 1

    # 循环结束还没返回，说明区间被搜空了：目标不存在
    print(f"  未找到 {target}%，共比较 {comparisons} 次")
    return -1, comparisons


# ============================================================
# 三、测试环境
# ============================================================

def run_ordered_experiment():
    """实验一：在有序的 1024 档利率表里查找 3.75%。"""
    print("=" * 62)
    print("实验一：有序利率表（1024 档，升序）")
    print("=" * 62)

    rates = build_rate_table(1024)
    print("利率表档位数：", len(rates))
    print("最小值：", rates[0], "  最大值：", rates[-1])
    print("是否升序：", all(rates[i] < rates[i + 1] for i in range(len(rates) - 1)))
    print("-" * 62)

    # 查找 3.75%
    target = 3.75
    index, comparisons = binary_search(rates, target)

    print("-" * 62)
    # 再验证一下：确实找到了，而且那个位置真的是 3.75
    if index != -1:
        print("校验：rates[%d] = %s，是否为 3.75？ %s"
              % (index, rates[index], "是 ✔" if rates[index] == target else "否 ✘"))
    print("比较次数 = %d，是否 ≤ 10 次？ %s"
          % (comparisons, "满足 ✔" if comparisons <= 10 else "不满足 ✘"))
    print("理论说明：log2(1024) = 10，所以最多约 10 次比较")
    print()

    return rates


def run_unordered_experiment(rates):
    """实验二（故意翻车）：把有序表打乱，再查找同一个 3.75%。"""
    print("=" * 62)
    print("实验二（故意翻车）：把利率表打乱成无序，再查 3.75%")
    print("=" * 62)

    # 为了每次运行结果都一样，固定随机种子（做实验时可复现）
    random.seed(2026)

    shuffled = rates[:]          # 复制一份，避免污染有序表
    random.shuffle(shuffled)     # 打乱顺序

    print("打乱后前 10 个值：", shuffled[:10])
    print("是否升序：", all(shuffled[i] < shuffled[i + 1] for i in range(len(shuffled) - 1)))
    print("-" * 62)

    target = 3.75
    index, comparisons = binary_search(shuffled, target)
    print("-" * 62)

    # 关键：二分查找在无序数据上给的答案"可能是假的"，必须自己校验
    if index == -1:
        print("现象：明明表里有 3.75（%s），二分查找却说找不到。"
              % ("确实存在" if target in shuffled else "不存在"))
        print("原因：二分查找靠'排好序'来决定往左还是往右找，")
        print("      数据无序时，这个判断是错的，可能把目标所在的一半直接丢掉。")
    elif shuffled[index] == target:
        print("现象：这次返回的下标 %d 碰巧真的存着 3.75，结果正确。" % index)
        print("原因：运气好，比较路径碰巧没有丢掉目标，但方法本身不可靠。")
    else:
        print("现象：函数报告'找到了'，下标是 %d，但该位置的值是 %s，不是 3.75！"
              % (index, shuffled[index]))
        print("原因：二分查找靠'排好序'来决定往左还是往右找，")
        print("      数据无序时，第一次比较就可能把目标所在的一半丢掉，")
        print("      于是返回了一个'错误但看起来成功'的结果——这是最危险的情况。")

    print("校验：3.75 在打乱后的表里是否存在？", "存在" if target in shuffled else "不存在")
    print("校验：官方答案（暴力查找）下标 =", shuffled.index(target) if target in shuffled else "无")
    print("校验：二分查找只比较了 %d 次，而暴力查找最多要看 1024 次。" % comparisons)
    print("结论：有序是二分查找的生命线，无序数据必须先排序再查。")
    print()


# ============================================================
# 四、程序入口
# ============================================================

if __name__ == "__main__":
    ordered_rates = run_ordered_experiment()   # 先跑正常的
    run_unordered_experiment(ordered_rates)    # 再跑故意翻车的
