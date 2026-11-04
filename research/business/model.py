"""Deterministic, assumption-driven business scenarios. No live company metrics."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load():
    return json.loads((ROOT / "assumptions.json").read_text(encoding="utf-8"))


def components(a, price=None, ai_calls=None, data_cost=None):
    price = price if price is not None else sum(p["price"] * p["mix"] for p in a["monthly_plans"])
    ai = a["ai"]
    calls = ai_calls if ai_calls is not None else ai["calls_per_payer"]
    return {
        "ai": calls * (ai["input_tokens_per_call"] * ai["input_per_million"] + ai["billable_output_tokens_per_call"] * ai["output_per_million"]) / 1_000_000,
        "execution": a["execution_per_payer"],
        "market_data": data_cost if data_cost is not None else a["market_data_per_payer"],
        "support": a["support_per_payer"],
        "identity_storage_notifications": a["identity_storage_notifications_per_payer"],
        "active_free_subsidy": a["active_free_per_payer"] * a["cost_per_active_free"],
        "payment_processing": price * a["payment_percentage"] + a["payment_fixed"],
        "refund_allowance": price * a["refund_percentage"],
    }


def capacity(a, n, field):
    points = a["capacity_anchors"]
    if n <= points[0]["payers"]:
        return points[0][field]
    for left, right in zip(points, points[1:]):
        if n <= right["payers"]:
            fraction = (n - left["payers"]) / (right["payers"] - left["payers"])
            return left[field] + fraction * (right[field] - left[field])
    raise ValueError("Model not calibrated above 10,000 paying users")


def economics(a, n, new_payers=None, price=None, ai_calls=None, data_cost=None, cac=None):
    price = price if price is not None else sum(p["price"] * p["mix"] for p in a["monthly_plans"])
    variable = sum(components(a, price, ai_calls, data_cost).values())
    shared = capacity(a, n, "shared_operations")
    team = capacity(a, n, "engineering_admin_allowance")
    new_payers = n * a["run_rate_new_payers_fraction"] if new_payers is None else new_payers
    acquisition = new_payers * (a["cost_per_gross_new_payer"] if cac is None else cac)
    revenue = n * price
    service = n * variable + shared
    return {
        "paying_users": n, "active_free_users": n * a["active_free_per_payer"],
        "gross_monthly_subscription_revenue": revenue,
        "direct_service_cost": service, "direct_cost_per_payer": service / n if n else None,
        "service_contribution": revenue - service,
        "engineering_admin_allowance": team, "acquisition_budget": acquisition,
        "modeled_operating_balance_before_tax": revenue - service - team - acquisition,
        "all_in_modeled_cost": service + team + acquisition,
    }


def build(a):
    price = sum(p["price"] * p["mix"] for p in a["monthly_plans"])
    scale = [economics(a, n) for n in [100, 500, 1000, 5000, 10000]]
    growth = []
    for name, schedule in a["gross_new_payers_by_month"].items():
        active = 0.0
        cumulative = 0.0
        cumulative_revenue = 0.0
        for month, additions in enumerate(schedule, 1):
            churned = active * a["monthly_paid_churn"]
            active = active - churned + additions
            # Approximate earned monthly revenue/cost: all end-month payers treated as a full month.
            row = economics(a, active, new_payers=additions)
            cumulative += row["modeled_operating_balance_before_tax"]
            cumulative_revenue += row["gross_monthly_subscription_revenue"]
            growth.append({"scenario":name,"month_after_commercial_launch":month,"gross_new_payers":additions,"expected_churned_payers":churned,**row,"cumulative_modeled_operating_balance":cumulative,"cumulative_gross_subscription_revenue":cumulative_revenue})
    sensitivity = []
    for label, params in [
        ("Base assumptions", {}),
        ("AI calls 5x: 300 per payer", {"ai_calls":300}),
        ("Market data $10 per payer", {"data_cost":10}),
        ("Market data $25 per payer", {"data_cost":25}),
        ("Acquisition cost $100", {"cac":100}),
        ("Average subscription $29", {"price":29}),
        ("Combined: 5x AI, $25 data, $100 CAC", {"ai_calls":300,"data_cost":25,"cac":100}),
    ]:
        sensitivity.append({"case":label, **economics(a, 1000, **params)})
    # Break-even holds the 1,000-payer capacity and acquisition allowance per payer fixed.
    fixed_1000 = capacity(a,1000,"shared_operations") + capacity(a,1000,"engineering_admin_allowance")
    contribution_after_acquisition = price - sum(components(a).values()) - a["run_rate_new_payers_fraction"] * a["cost_per_gross_new_payer"]
    result = {"status":a["status"],"currency":"USD","average_monthly_price":price,"variable_components":components(a),"variable_cost_per_payer":sum(components(a).values()),"scale":scale,"growth":growth,"sensitivity_at_1000_payers":sensitivity,"fixed_capacity_break_even_payers":fixed_1000/contribution_after_acquisition}
    validate(a, result)
    return result


def validate(a, r):
    assert abs(sum(p["mix"] for p in a["monthly_plans"]) - 1) < 1e-9
    assert abs(r["average_monthly_price"] - 39) < 1e-9
    assert abs(r["variable_components"]["ai"] - 1.8) < 1e-9
    # Independently check one cost stack and its operating arithmetic.
    expected = 1.8 + 1.2 + 3 + 2 + 0.6 + 3*0.2 + 39*0.04 + 0.3 + 39*0.01
    row = next(x for x in r["scale"] if x["paying_users"] == 1000)
    assert abs(row["direct_service_cost"] - (expected*1000 + 1000)) < 1e-8
    assert abs(row["modeled_operating_balance_before_tax"] - (39000 - 12450 - 10000 - 3000)) < 1e-8
    for name, schedule in a["gross_new_payers_by_month"].items():
        rows = [x for x in r["growth"] if x["scenario"] == name]
        previous = 0.0
        for index, row in enumerate(rows):
            expected = previous * 0.95 + schedule[index]
            assert abs(row["paying_users"] - expected) < 1e-8
            assert abs(row["gross_monthly_subscription_revenue"] - row["paying_users"] * 39) < 1e-8
            previous = row["paying_users"]
    for row in r["scale"] + r["growth"] + r["sensitivity_at_1000_payers"]:
        assert abs(row["gross_monthly_subscription_revenue"] - row["all_in_modeled_cost"] - row["modeled_operating_balance_before_tax"]) < 1e-7


def write_outputs(a, r):
    (ROOT / "results.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    for key, filename in [("scale","scale.csv"),("growth","growth.csv"),("sensitivity_at_1000_payers","sensitivity.csv")]:
        with (ROOT / filename).open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=r[key][0].keys())
            writer.writeheader()
            writer.writerows(r[key])


if __name__ == "__main__":
    assumptions=load()
    results=build(assumptions)
    write_outputs(assumptions, results)
    print(json.dumps({"variable_cost":results["variable_cost_per_payer"],"scale":results["scale"],"milestones":[{"scenario":x["scenario"],"month":x["month_after_commercial_launch"],"payers":round(x["paying_users"]),"mrr":round(x["gross_monthly_subscription_revenue"]),"balance":round(x["modeled_operating_balance_before_tax"]),"cumulative":round(x["cumulative_modeled_operating_balance"])} for x in results["growth"] if x["month_after_commercial_launch"] in [3,6,12]],"sensitivity":results["sensitivity_at_1000_payers"],"break_even":results["fixed_capacity_break_even_payers"]},indent=2))
