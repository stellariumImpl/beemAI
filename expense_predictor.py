from typing import List, Dict, Tuple
from collections import defaultdict


def predict_payer(expense_type: str, amount: float, data: List[Dict]) -> Tuple[str, str]:
    filtered_data = [item for item in data if item['confirmed']]

    if not filtered_data:
        return None, "No historical data available. Please choose a payer."

    # 如果没有该类型的历史数据
    if not any(item['type'].lower() == expense_type.lower() for item in filtered_data):
        # 找出支付总额最多的人
        payer_totals = defaultdict(float)
        for item in filtered_data:
            payer_totals[item['payer'].lower()] += float(item['amount'])

        top_payer = max(payer_totals, key=payer_totals.get)
        reason = f"{top_payer.capitalize()} has paid the most overall (${payer_totals[top_payer]:.2f}). This is a new expense type."
        return top_payer, reason

    # 计算每个类别的总支出
    category_totals = defaultdict(float)
    for item in filtered_data:
        category_totals[item['type'].lower()] += float(item['amount'])

    # 找出与目标类别最相关的类别
    target_total = category_totals[expense_type.lower()]
    related_category = max(category_totals,
                           key=lambda k: abs(category_totals[k] - target_total) if k != expense_type.lower() else 0)

    # 在相关类别中找出支付最多的人
    related_payers = defaultdict(float)
    for item in filtered_data:
        if item['type'].lower() == related_category:
            related_payers[item['payer'].lower()] += float(item['amount'])

    suggested_payer = max(related_payers, key=related_payers.get)
    reason = f"{suggested_payer.capitalize()} has paid the most (${related_payers[suggested_payer]:.2f}) in the most related category '{related_category}'."

    return suggested_payer, reason


def get_next_payer(expense_type: str, amount: float, data: List[Dict], rejected_payers: List[str]) -> Tuple[str, str]:
    filtered_data = [item for item in data if
                     item['type'].lower() == expense_type.lower() and item['confirmed'] and item[
                         'payer'].lower() not in rejected_payers]

    if not filtered_data:
        return None, "No more potential payers. Consider splitting the bill."

    payer_totals = defaultdict(float)
    for expense in filtered_data:
        payer = expense['payer'].lower()
        payer_totals[payer] += float(expense['amount'])

    next_payer = max(payer_totals, key=payer_totals.get)
    reason = f"{next_payer.capitalize()} has paid ${payer_totals[next_payer]:.2f} for {expense_type} expenses."

    return next_payer, reason