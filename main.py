import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# 1. INPUTS AND DATA
# -----------------------------

# Scenario distribution
scenarios = [
    {"price": 25350, "prob": 0.20},  # Bull
    {"price": 24000, "prob": 0.60},  # Base
    {"price": 21250, "prob": 0.20},  # Bear
]

# Risk-free rate: 3.42% per annum
# Convert to monthly rate for compounding from 'now' to end of Apr 2025
# For simplicity, assume 1 month to expiry in this example. 
# If more precise, you'd adjust # of months from 'now' to 29 Apr 2025.
annual_rf_rate = 0.0342
months_to_expiry = 1  # example
monthly_rf_rate = annual_rf_rate / 12

# Option chain data for Calls (strike -> premium)
call_prices = {
    21000: 2478, 21200: 2292, 21400: 2111, 21600: 1933, 21800: 1761,
    22000: 1594, 22200: 1434, 22400: 1175, 22600: 1124, 22800:  884,
    23000:  780, 23200:  645, 23400:  575, 23600:  476, 23800:  400,
    24000:  341, 24200:  307, 24400:  236, 24600:  210, 24800:  165,
    25000:  130, 25200:  101, 25400:   88, 25600:   75, 25800:   67,
    26000:   47, 26200:   39, 26400:   31, 26600:   35, 26800:   20,
    27000:   16, 27200:   13, 27400:   11, 27600:    9, 27800:    8,
    28000:    8, 28200:    7, 28400:    6, 28600:    5, 28800:    4,
    29000:    3, 29200:    1, 29400:    1, 29600:    1
}

# Define your candidate strikes for the spread. You can expand this range.
lower_strike_candidates = [22000, 22400, 22800, 23200, 23600, 24000, 24400, 24800]
upper_strike_candidates = [24200, 24600, 25000, 25400, 25800, 26200, 26600, 27000]

# -----------------------------
# 2. CALCULATE EXPECTED PROFIT & SD FOR EACH SPREAD
# -----------------------------

def bull_call_spread_payoff(final_price, lower_strike, upper_strike):
    """
    Payoff of a bull call spread at expiration given the final_price.
    Bull Call Spread = Long Call(lower_strike) + Short Call(upper_strike).
    """
    # Long call payoff
    long_call_payoff = max(final_price - lower_strike, 0)
    # Short call payoff (short position => subtract payoff)
    short_call_payoff = -max(final_price - upper_strike, 0)
    return long_call_payoff + short_call_payoff

def future_value_of_spread_cost(lower_strike, upper_strike, monthly_rate):
    """
    We buy the call at lower_strike and short the call at upper_strike.
    The net cost is: call_prices[lower_strike] - call_prices[upper_strike].
    Then we compound it by (1 + monthly_rate) to get FV at expiry
    (assuming 1 month to expiry for simplicity).
    """
    cost_now = call_prices[lower_strike] - call_prices[upper_strike]
    return cost_now * (1 + monthly_rate)

results = []
labels = []
index_label = 0

for ls in lower_strike_candidates:
    for us in upper_strike_candidates:
        if us > ls:
            # 1) Compute future value of spread cost
            cost_future_value = future_value_of_spread_cost(ls, us, monthly_rf_rate)
            
            # 2) Compute scenario payoffs
            #    Then net payoff = spread payoff - cost_future_value
            #    But be consistent: we either bring the cost to expiry or discount payoff to present.
            #    This code calculates final payoff at expiry minus the cost_future_value at expiry.
            payoffs = []
            for scenario in scenarios:
                final_price = scenario["price"]
                prob = scenario["prob"]
                
                spread_payoff = bull_call_spread_payoff(final_price, ls, us)
                net_payoff = spread_payoff - cost_future_value  # at expiry
                
                payoffs.append(net_payoff)
            
            # 3) Compute expected profit
            expected_profit = sum(
                scenario["prob"] * payoff 
                for scenario, payoff in zip(scenarios, payoffs)
            )
            
            # 4) Compute standard deviation
            #    SD = sqrt( E[(X - E[X])^2] ), summation across scenarios
            var = 0
            for scenario, payoff in zip(scenarios, payoffs):
                var += scenario["prob"] * (payoff - expected_profit)**2
            sd = np.sqrt(var)
            
            # Keep track of results
            label = chr(ord('A') + index_label)
            index_label += 1
            labels.append(label)
            
            results.append({
                "label": label,
                "lower_strike": ls,
                "upper_strike": us,
                "expected_profit": expected_profit,
                "sd": sd
            })

# -----------------------------
# 3. PLOT EXPECTED PROFIT VS. STANDARD DEVIATION
# -----------------------------

# Convert results to arrays
x_vals = [r["sd"] for r in results]
y_vals = [r["expected_profit"] for r in results]

plt.figure(figsize=(10, 6))
plt.scatter(x_vals, y_vals, color='blue')

for i, r in enumerate(results):
    plt.text(x_vals[i]*1.01, y_vals[i]*1.01, r["label"], fontsize=9)

plt.xlabel("Standard Deviation of Profit")
plt.ylabel("Expected Profit")
plt.title("Bull Call Spread: Expected Profit vs. Standard Deviation")
plt.grid(True)
plt.tight_layout()
plt.show()

# -----------------------------
# 4. FIND "OPTIMAL" COMBINATION
# -----------------------------
# For demonstration, define "optimal" as the combination
# giving the maximum Expected Profit / minimum SD (like a ratio).
# You can change your own definition of 'optimal' as needed.

best_combo = None
best_ratio = -999

for r in results:
    # Example criterion: maximize the ratio (Expected Profit / SD).
    # (You could also do a custom function or a higher preference for Exp Profit.)
    if r["sd"] == 0:
        continue  # avoid division by zero
    ratio = r["expected_profit"] / r["sd"]
    if ratio > best_ratio:
        best_ratio = ratio
        best_combo = r

if best_combo:
    print("Optimal combination based on (Expected Profit/SD) ratio:")
    print("Label:", best_combo["label"])
    print("  Lower strike:", best_combo["lower_strike"])
    print("  Upper strike:", best_combo["upper_strike"])
    print("  Expected Profit: {:.2f}".format(best_combo["expected_profit"]))
    print("  Standard Deviation: {:.2f}".format(best_combo["sd"]))
    print("  Ratio (Exp Profit / SD): {:.2f}".format(best_ratio))
else:
    print("No valid combination found.")