# Illustrative subscription economics

Prepared 3 November 2026. USD. This is a pre-launch scenario model, not a prediction, valuation, investment recommendation, measured unit economics, or user trading-return estimate. No paying customers, willingness-to-pay experiments, churn history, production load tests, or commercial data quotes exist in the project.

Run `python research/business/model.py` from the project root. Editable inputs are in assumptions.json; results.json and CSV files are regenerated. economics.ipynb is a calculation companion executed top-to-bottom with saved text outputs. It contains no plots. Model assertions check the price mix, AI cost, independently summed 1,000-payer example, cohort recurrence and revenue/cost arithmetic.

## Base assumptions

- Proposed plans are $19, $49 and $99/month, with an invented 50%/40%/10% mix: $39 average. These prices are not chosen launch prices or validated demand.
- 60 AI requests per payer/month, averaging 5,000 input and 2,000 billable output tokens each: $1.80 at sourced $2/$10 per-million rates. All applicable billed reasoning/output must fit this allowance. Provider tools and research overhead need separate budgets.
- Per payer/month: $1.20 execution workload; $3 commercial-data allowance; $2 frontline support; $0.60 identity/storage/notifications; $0.60 subsidy for three limited active-free users. All are unmeasured planning allowances, not vendor quotes or capacity guarantees.
- Payment processing assumes 4% plus $0.30 on one monthly transaction, and a separate 1% revenue refund allowance. This is a blended planning assumption, not an exact Paystack fee, and does not fully model disputes or currency conversion.
- Direct variable cost totals $11.45/payer. Shared operations allowances are added at each scale. Broker-account runtime is assumed shared/multiplexed, not one costly desktop terminal per customer.
- Free users have limited features and no unlimited AI or live automation. Registered users are not the same as active-free or paying users. More active-free users or more broker accounts per payer increase costs.

## Scale results

| Payers | Gross MRR | Direct service cost | Direct cost/payer | Engineering/admin allowance | Acquisition allowance | Modeled operating balance before tax |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | $3,900 | $1,445 | $14.45 | $3,000 | $300 | -$845 |
| 500 | $19,500 | $6,325 | $12.65 | $6,000 | $1,500 | $5,675 |
| 1,000 | $39,000 | $12,450 | $12.45 | $10,000 | $3,000 | $13,550 |
| 5,000 | $195,000 | $60,250 | $12.05 | $30,000 | $15,000 | $89,750 |
| 10,000 | $390,000 | $119,500 | $11.95 | $50,000 | $30,000 | $190,500 |

Direct service cost includes variable costs plus shared compute/research/monitoring/tooling allowances of $300/$600/$1,000/$3,000/$5,000. These allocations are planning inputs and do not prove redundancy, uptime or capacity. Engineering/admin is separate from per-user frontline support. No free founder labor is assumed in this allowance, but actual hiring/legal/insurance needs may exceed it.

Scale acquisition allowance equals 10% of opening payers acquired monthly at an assumed $30 each. With 5% churn that approximates 5% net monthly growth. Actual acquisition spending in growth.csv uses each scenario's gross additions instead, not the scale shortcut. Paying-user churn is an assumed percentage of the prior month, not a percent of signups.

## Time-based scenarios

All month numbers begin at a future commercial launch; development duration and the launch date are unknown. Explicit monthly gross additions are stored in assumptions.json. Starting payers are zero. All scenarios assume 5% monthly paid churn. These are deliberately chosen acquisition trajectories with no assigned probabilities; the working case is not a most-likely forecast.

| Month after commercial launch | Slower adoption | Working case | Strong adoption |
| ---: | --- | --- | --- |
| 3 | About 43 payers / $1,688 gross MRR | About 115 / $4,488 | About 313 / $12,195 |
| 6 | About 123 / $4,803 | About 299 / $11,673 | About 986 / $38,458 |
| 12 | About 373 / $14,533 | About 837 / $32,652 | About 3,281 / $127,961 |

Gross MRR is the end-month subscription run rate, not cash collected or cumulative sales. Dollar estimates use unrounded expected payer counts; payer counts are rounded for readability. The optional cumulative balances in results.json assume all end-month payers pay a full month; they ignore proration/payment timing and must not be used as cash-flow forecasts.

## Important sensitivity

At 1,000 paying users, base operating balance is $13,550/month. Changing only the data allowance to $10/payer reduces it to $6,550; $25/payer makes it -$8,450. Changing acquisition cost to $100/new payer reduces it to $6,550. Increasing AI calls fivefold at the same token lengths reduces it to $6,350. Combining fivefold AI, $25 data and $100 acquisition yields -$22,650. These cases are stress assumptions, not measured vendor ranges or confidence intervals.

Fixed-capacity breakeven is about 449 paying users if the $11,000 shared/engineering/admin cost at 1,000-user capacity and other unit assumptions are held fixed. Other capacity choices change the threshold; do not apply this value universally.

## Exclusions and next evidence

Excluded: tax/VAT collection/remittance, one-time development, independent security audits, launch legal work, unquoted mandatory licensing/regulatory/commercial integration fees, payment disputes beyond the allowance, and any company-funded trading losses/capital. Users are assumed to retain their funds with their brokers and pay their own trading spreads/commissions/financing. No performance fees, broker rebates, ads, or affiliate revenue are modeled. No guarantee that a payment provider will approve this business category is assumed.

Next evidence: commercial data/display/redistribution quote; broker third-party agreement and per-account expenses; load tests; actual AI token/tool use; user support workload; price experiments; acquisition funnel and cost; paid retention; legal/operating obligations for first countries. These determine whether the attractive scenarios are achievable.

## Public price anchors

Vendor pages were read on 3 November 2026. Source URLs and roles are in assumptions.json. OpenAI standard input/output prices are used directly; DigitalOcean/Supabase prices only anchor the plausibility of starting infrastructure allowances, not capacity; Paystack shows fee variation, not the model's exact blended fee; market-data policy establishes that rights require checking, not a $3 quote. No vendor has been selected or purchased based on this model.
