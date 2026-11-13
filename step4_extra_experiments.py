# -*- coding: utf-8 -*-
"""
HW1 - 第四步：两个额外实验
    实验一：用二分查找找"月供最接近 5000"的利率档位（100 档模拟利率表）
    实验二：100,000 个元素的合并排序，检查会不会撞上 Python 的默认递归上限

说明：合并排序直接复用第一步写好的 step1_merge_sort.py 里的 merge_sort。
"""

import random
import sys

# 从第一步的文件里"引入"之前写好的 merge_sort（不重复抄一遍代码）
from step1_merge_sort import merge_sort


# ============================================================
# 实验一：二分查找找"月供最接近 5000"的利率
# ============================================================

def build_rate_table(n=100, start=3.00, step=0.03):
    """
    生成 n 档模拟利率（单位：%），从 start 开始，每档 +step，保证严格升序。
    默认生成 3.00%、3.03%、...、5.97%，一共 100 档。
    """
    return [round(start + step * i, 2) for i in range(n)]


def monthly_payment(rate_percent, principal=1_000_000, years=30):
    """
    模拟"等额本息"月供公式（近似即可，重点是它随利率单调递增）。

    参数：
        rate_percent : 年利率（百分数，例如 4.30 表示 4.30%）
        principal    : 贷款本金（默认 100 万）
        years        : 贷款年限（默认 30 年 = 360 期）

    月供 = 本金 × 月利率 / (1 - (1 + 月利率)^(-期数))
    利率越高 → 月供越高，严格递增，正好满足二分查找"必须有序"的前提。
    """
    monthly_rate = rate_percent / 100 / 12        # 年利率换算成月利率
    months = years * 12                           # 总期数
    payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** (-months))
    return round(payment, 2)                      # 保留 2 位小数，方便展示


def find_closest_rate(rates, payments, target=5000):
    """
    用二分查找，在"月供数组"里找最接近 target 的那一档。

    由于月供随利率递增（数组有序），二分可以快速定位到 target 的"插入位置"，
    真正的答案只可能是插入位置左边或右边的一个元素，再比较这两个候选即可。

    返回：
        (index, comparisons)
        index       : 最接近 target 的档位下标
        comparisons : 查找过程中一共比较了多少次
    """
    lo, hi = 0, len(payments) - 1
    comparisons = 0

    # 二分：不断找"第一个 >= target 的位置"，用 half-open 写法避免死循环
    while lo < hi:
        mid = (lo + hi) // 2
        comparisons += 1                    # 比较了一次 payments[mid] 和 target
        if payments[mid] < target:
            lo = mid + 1                    # 月供太小 → 答案在右半边
        else:
            hi = mid                        # 月供够大 → 答案可能在左半边（含 mid）

    # 循环结束后 lo 就是第一个 >= target 的位置
    # 最接近的只可能是 lo 本身，或者它左边一个 lo-1
    candidates = []
    if lo < len(payments):
        candidates.append(lo)
    if lo > 0:
        candidates.append(lo - 1)

    best = candidates[0]
    comparisons += 1                        # 把第一个候选当作"当前最优"，算一次比较
    for idx in candidates[1:]:
        comparisons += 1                    # 每比较一个候选，计数 +1
        if abs(payments[idx] - target) < abs(payments[best] - target):
            best = idx

    return best, comparisons


def run_experiment_1():
    """实验一完整流程 + 自我验证。"""
    print("=" * 66)
    print("实验一：100 档利率表中，找「月供最接近 5000」的档位")
    print("=" * 66)

    rates = build_rate_table(100)                              # 100 档利率
    payments = [monthly_payment(r) for r in rates]             # 对应的月供
    target = 5000

    print("档位数量：", len(rates))
    print("利率范围：%.2f%% ~ %.2f%%" % (rates[0], rates[-1]))
    print("月供范围：%.2f ~ %.2f" % (payments[0], payments[-1]))
    print("月供是否随利率升序：",
          all(payments[i] < payments[i + 1] for i in range(len(payments) - 1)))
    print("-" * 66)

    # 二分查找最接近 5000 的档位
    best_index, comparisons = find_closest_rate(rates, payments, target)

    print("目标月供：%d 元" % target)
    print(">>> 最接近的利率档位：第 %d 档，利率 %.2f%%，月供 %.2f 元"
          % (best_index, rates[best_index], payments[best_index]))
    print(">>> 与目标的差距：%.2f 元" % abs(payments[best_index] - target))
    print(">>> 二分查找比较次数：%d 次（100 档理论上约 7 次，log2(100)≈6.6）"
          % comparisons)
    print("-" * 66)

    # 自我验证：用暴力遍历所有 100 档，看答案是否一致
    brute_index = min(range(len(payments)),
                      key=lambda i: abs(payments[i] - target))
    print("暴力验证：逐档扫描得到最接近的是第 %d 档（利率 %.2f%%，月供 %.2f 元）"
          % (brute_index, rates[brute_index], payments[brute_index]))
    print("两者是否一致：", "是 ✔" if brute_index == best_index else "否 ✘")
    print("结论：二分查找在有序的月供数组上，用 %d 次比较就找到了正确答案。"
          % comparisons)
    print()


# ============================================================
# 实验二：10 万元素合并排序 vs 默认递归上限
# ============================================================

def run_experiment_2(n=100_000):
    """生成 10 万个随机数，用合并排序排序，同时观察递归上限。"""
    print("=" * 66)
    print("实验二：%d 个元素的合并排序，检查是否会撞递归上限" % n)
    print("=" * 66)

    # 1. 用 sys 模块打印当前默认递归上限（Python 默认是 1000 层）
    limit = sys.getrecursionlimit()
    print("sys.getrecursionlimit() 读到的当前递归上限：%d 层" % limit)

    # 2. 生成 10 万个随机整数
    random.seed(2026)                                  # 固定种子，结果可复现
    data = [random.randint(0, 10 ** 6) for _ in range(n)]
    print("已生成随机数组，元素个数：", len(data))

    # 3. 直接调用合并排序（不修改递归上限，看它能不能扛住）
    sorted_data = merge_sort(data)

    # 4. 打印成功信息 + 校验结果
    print("合并排序执行完毕，没有报错 ✔")
    print("排序结果正确性（与 sorted() 对比）：",
          "通过 ✔" if sorted_data == sorted(data) else "失败 ✘")
    print("前 10 个元素：", sorted_data[:10])

    # 5. 解释为什么没有撞上限：合并排序是"折半递归"，深度只有 log2(n)
    import math
    theory_depth = math.ceil(math.log2(n))
    print("说明：合并排序每次折半，递归深度约为 log2(%d) ≈ %d 层，"
          % (n, theory_depth))
    print("      远小于默认上限 %d 层，所以不会触发 RecursionError。"
          % limit)
    print("      真正会撞上限的是不折半的递归写法，例如 10 万层的链表递归。")
    print()


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":
    run_experiment_1()
    run_experiment_2()
