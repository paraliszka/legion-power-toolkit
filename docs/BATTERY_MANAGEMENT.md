# Battery Management Guide

This guide explains the battery management features of the Legion Power Manager and provides best practices for maintaining your laptop's battery health.

## Feature Overview

### 1. Conservation Mode
**What it does:** Limits the maximum battery charge to approximately 60% of total capacity.

**When to use:**
- You primarily use your laptop plugged into AC power (e.g., gaming, desktop replacement usage).
- You want to extend the overall lifespan of your Lithium-Ion battery.

**Why:** Keeping a Lithium-Ion battery at 100% charge for prolonged periods (high voltage state) accelerates chemical degradation. Keeping it around 50-60% is optimal for long-term storage and health.

### 2. Rapid Charge
**What it does:** Allows the battery to charge significantly faster than normal.

**When to use:**
- You are in a rush and need to top up the battery quickly before heading out.

**Why:** Higher current increases heat and stress on the battery. Frequent use may degrade battery capacity faster than standard charging. Use only when necessary.

## The "Mutex" Logic

The laptop's Embedded Controller (EC) cannot handle Conservation Mode and Rapid Charge simultaneously, as they are contradictory instructions (limit charge vs. force charge).

**How Legion Power Manager handles this:**
Our software enforces a **Mutual Exclusion (Mutex)** logic to prevent conflicts:

1.  **Enabling Conservation Mode:**
    - If Rapid Charge is currently ON, the system will **automatically turn it OFF** before enabling Conservation Mode.

2.  **Enabling Rapid Charge:**
    - If Conservation Mode is currently ON, the system will **automatically turn it OFF** before enabling Rapid Charge.

This ensures the hardware never receives conflicting commands and the user experience is seamless.

## Best Practices

1.  **Desk Usage:** If you stay at your desk for days, enable **Conservation Mode**.
2.  **Travel:** If you plan to travel, disable Conservation Mode to charge to 100%.
3.  **Heat:** Avoid charging the battery while the laptop is extremely hot (e.g., immediately after a heavy gaming session).
4.  **Cycling:** It's a myth that you need to fully discharge Li-ion batteries. Shallow cycles are better. Avoid dropping below 20% if possible.
