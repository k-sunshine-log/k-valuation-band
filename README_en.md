# 📊 K-Valuation Band

Automates the generation of **PER and PBR valuation band charts** for Samsung Electronics and SK Hynix, and serves them via GitHub Pages.

[🇰🇷 한국어 버전](./README.md)

## What is a Band Chart?

This project visualizes the historical context of the stock price by generating bands based on the Price-to-Earnings Ratio (PER) and Price-to-Book Ratio (PBR), making it easier to see if the current stock price is undervalued or overvalued.
To smooth out the step-like changes in earnings/book-value release periods, we apply a **120-business-day (approx. 6 months) moving average smoothing technique**.

### PER Band Standard
Due to the highly cyclical nature of the semiconductor sector, this project abandons the quantile distribution method for PER and instead applies **fixed multiples** that are standard in brokerage reports.
*   **Samsung Electronics:** 8x, 10x, 12x, 15x, 20x
*   **SK Hynix:** 5x, 8x, 12x, 15x, 20x

### PBR Band Standard
Because book value (PBR) is relatively stable compared to earnings, we use the **statistical distribution (quantiles)** from the last 5 years' data to draw the PBR bands:
| Quantile | Color (Line) | Interpretation |
| --- | --- | --- |
| **10%** | Red hue (#FF6B6B) | Historically Undervalued (Bottom) |
| **25%** | Orange hue (#FFB347) | Slightly Undervalued |
| **50%** | Blue hue (#87CEEB) | 5-Year Average (Neutral) |
| **75%** | Green hue (#77DD77) | Slightly Overvalued |
| **90%** | Purple hue (#DDA0DD) | Historically Overvalued (Overheated) |

## Supported Stocks

- 🏢 Samsung Electronics (005930)
- 💾 SK Hynix (000660)

## Tech Stack

- `pykrx` — Collecting KRX stock data
- `matplotlib` — Visualizing band charts
- `GitHub Actions` — Automated weekday updates
- `GitHub Pages` — Static web hosting

## Local Execution

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Auto Update

GitHub Actions will automatically refresh the charts **every weekday at 20:30 (KST)**.
