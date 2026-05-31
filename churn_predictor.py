"""客户复购预警系统"""

from datetime import datetime, timedelta


class Customer:
    """客户档案，记录购买历史用于流失风险分析。"""

    def __init__(self, name: str, email: str, first_purchase: str,
                 last_purchase: str, total_spent: float, purchase_count: int):
        """初始化客户档案。

        Args:
            name: 客户姓名
            email: 客户邮箱
            first_purchase: 首次购买日期，格式"YYYY-MM-DD"
            last_purchase: 最近购买日期，格式"YYYY-MM-DD"
            total_spent: 累计消费金额（元）
            purchase_count: 购买次数
        """
        self.name = name
        self.email = email
        self.first_purchase = datetime.strptime(first_purchase, "%Y-%m-%d")
        self.last_purchase = datetime.strptime(last_purchase, "%Y-%m-%d")
        self.total_spent = total_spent
        self.purchase_count = purchase_count

    @property
    def avg_purchase_interval(self) -> int:
        """计算平均购买间隔天数。

        Returns:
            平均间隔天数，购买次数少于2次时返回999
        """
        if self.purchase_count < 2:
            return 999
        delta = self.last_purchase - self.first_purchase
        return delta.days // (self.purchase_count - 1)

    @property
    def days_since_last(self) -> int:
        """计算距上次购买的天数。

        Returns:
            距上次购买的天数
        """
        return (datetime.now() - self.last_purchase).days


class ChurnPredictor:
    """客户流失预警器，基于购买间隔分析流失风险并给出召回建议。"""

    def __init__(self):
        """初始化预警器，设置风险阈值为平均间隔的1.5倍。"""
        self.risk_threshold = 1.5  # 超过平均间隔1.5倍标记为风险

    def predict(self, customers: list) -> list:
        """分析客户列表的流失风险。

        Args:
            customers: Customer 实例列表

        Returns:
            风险分析结果列表，按风险等级排序（高→中→低），每项包含客户信息、风险等级、建议动作
        """
        results = []
        for c in customers:
            interval = c.avg_purchase_interval
            since = c.days_since_last

            if interval == 999:
                risk = "低"
                reason = "仅一次购买，需观察"
            elif since > interval * 2:
                risk = "高"
                reason = f"距上次购买{since}天，远超平均周期{interval}天"
            elif since > interval * self.risk_threshold:
                risk = "中"
                reason = f"距上次购买{since}天，接近预警线({int(interval*self.risk_threshold)}天)"
            else:
                risk = "低"
                reason = "近期有购买，状态正常"

            results.append({
                "客户": c.name,
                "邮箱": c.email,
                "上次购买": c.last_purchase.strftime("%Y-%m-%d"),
                "购买频次": f"{c.purchase_count}次",
                "平均间隔": f"{interval}天",
                "流失风险": risk,
                "原因": reason,
                "建议动作": self._action(risk, c),
            })
        return sorted(results, key=lambda r: {"高": 0, "中": 1, "低": 2}[r["流失风险"]])

    def _action(self, risk: str, c: Customer) -> str:
        """根据风险等级生成召回行动建议。

        Args:
            risk: 风险等级，"高"、"中"或"低"
            c: Customer 实例

        Returns:
            行动建议文本
        """
        actions = {
            "高": f"发送召回优惠券，安排专属客服回访{c.name}",
            "中": f"推送新品推荐邮件，限时折扣刺激复购",
            "低": "保持常规推送即可",
        }
        return actions.get(risk, "")


if __name__ == "__main__":
    predictor = ChurnPredictor()
    customers = [
        Customer("张三", "zhang@test.com", "2025-10-01", "2026-05-01", 5000, 5),
        Customer("李四", "li@test.com", "2025-06-01", "2025-12-01", 2000, 2),
        Customer("王五", "wang@test.com", "2026-04-01", "2026-04-01", 500, 1),
    ]
    for r in predictor.predict(customers):
        print(f"[{r['流失风险']}] {r['客户']} — {r['原因']}")
        print(f"  建议: {r['建议动作']}")
        print()
