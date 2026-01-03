# Sharesight Python SDK

An unofficial Python SDK for the [Sharesight](https://www.sharesight.com/) API (v2 and v3).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/sharesight-python.svg)](https://pypi.org/project/sharesight-python/)

## Features

- 🔐 OAuth2 authentication with automatic token refresh
- 💾 Optional token persistence between sessions
- 📊 Full support for portfolios, holdings, trades, and payouts
- 📈 Access to reports (performance, diversity, capital gains, tax)
- 🏢 Custom investment support for property/alternative assets
- ⚡ Built on [httpx](https://www.python-httpx.org/) for modern async support

---

## Getting API Credentials

Before using this SDK, you need to obtain API credentials from Sharesight.

### For Personal Use (Investor Plan or Higher)

If you're an existing Sharesight customer on the **Investor plan or higher** and want to access your own data:

1. **Email Sharesight Support** at [support@sharesight.com](mailto:support@sharesight.com)
2. **Request API access** - Include the email address associated with your Sharesight account
3. **Receive credentials** - Sharesight will send you a `Client ID` and `Client Secret`

> 📧 **Example email:**
> 
> *Subject: API Access Request*
> 
> *Hi Sharesight Team,*
> 
> *I would like to request API access to use with my Sharesight account.*
> 
> *Account email: your.email@example.com*
> 
> *Thank you!*

### For Commercial/Partner Use

If you're building an application for others to use, you'll need to go through Sharesight's partner program. See the [Sharesight API overview](https://portfolio.sharesight.com/api) for more details.

---

## Installation

```bash
pip install sharesight-python
```

### Requirements

- Python 3.8+

### Alternative Installation Methods

**From source (editable mode):**
```bash
git clone https://github.com/dejersey/sharesight-python.git
cd sharesight-python
pip install -e .
```

---

## Configuration

### Using Environment Variables (Recommended)

Set your credentials as environment variables:

```bash
export SHARESIGHT_CLIENT_ID="your_client_id"
export SHARESIGHT_CLIENT_SECRET="your_client_secret"
```

Then initialize the client without arguments:

```python
from sharesight import SharesightClient

client = SharesightClient()
```

### Using Direct Configuration

```python
from sharesight import SharesightClient

client = SharesightClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

### Persisting Tokens Between Sessions

Use `FileTokenStore` to cache tokens locally, avoiding re-authentication on each run:

```python
from sharesight import SharesightClient, FileTokenStore

client = SharesightClient(
    token_store=FileTokenStore(".sharesight_token.json")
)
```

> ⚠️ **Security Warning:** Token files contain sensitive credentials. Ensure they have restricted permissions and are listed in `.gitignore`:
> ```bash
> chmod 600 .sharesight_token.json
> ```

---

## Quick Start

```python
from sharesight import SharesightClient

# Initialize client (uses environment variables)
client = SharesightClient()

# List all portfolios
portfolios = client.portfolios.list()
for portfolio in portfolios:
    print(f"📁 {portfolio['name']} (ID: {portfolio['id']})")

# Get holdings for a portfolio
holdings = client.holdings.list(portfolio_id=123456)
for holding in holdings:
    print(f"  └─ {holding['instrument']['name']}")
```

---

## API Reference

### Portfolios

```python
# List all portfolios
portfolios = client.portfolios.list()

# Get portfolio details
portfolio = client.portfolios.get(portfolio_id=123456)

# Get portfolio valuation
valuation = client.portfolios.get_valuation(
    portfolio_id=123456,
    balance_date="2025-12-31"  # Optional
)

# Create a new portfolio
new_portfolio = client.portfolios.create(
    name="My New Portfolio",
    currency="AUD"
)

# Update portfolio
client.portfolios.update(portfolio_id=123456, data={"name": "Renamed Portfolio"})

# Delete portfolio
client.portfolios.delete(portfolio_id=123456)
```

### Holdings

```python
# List holdings in a portfolio
holdings = client.holdings.list(portfolio_id=123456)

# Get holding details
holding = client.holdings.get(holding_id=789)

# Get holding valuation
valuation = client.holdings.get_valuation(holding_id=789)

# Update holding
client.holdings.update(holding_id=789, data={"notes": "Updated notes"})

# Delete holding
client.holdings.delete(holding_id=789)
```

### Trades

```python
# List trades for a portfolio
trades = client.trades.list(portfolio_id=123456)

# Get trade details
trade = client.trades.get(trade_id=456)

# Create a trade
new_trade = client.trades.create(
    portfolio_id=123456,
    trade_data={
        "holding_id": 789,
        "transaction_type": "BUY",
        "quantity": 100,
        "price": 10.50,
        "transaction_date": "2025-01-01"
    }
)

# Update trade
client.trades.update(trade_id=456, trade_data={"price": 10.75})

# Delete trade
client.trades.delete(trade_id=456)
```

### Payouts (Dividends)

```python
# List payouts for a holding
payouts = client.trades.list_payouts(holding_id=789)

# Create a payout
payout = client.trades.create_payout(
    holding_id=789,
    payout_data={
        "amount": 150.00,
        "transaction_date": "2025-01-15",
        "comments": "Quarterly dividend"
    }
)

# Create a payout with an attachment (e.g., statement PDF)
payout = client.trades.create_payout(
    holding_id=789,
    payout_data={
        "amount": 500.00,
        "transaction_date": "2025-01-15"
    },
    attachment_path="/path/to/statement.pdf"
)

# Update payout
client.trades.update_payout(payout_id=111, payout_data={"amount": 160.00})

# Delete payout
client.trades.delete_payout(payout_id=111)
```

### Custom Investments

For tracking property, private equity, or other alternative assets:

```python
# List all custom investments
custom_investments = client.investments.list_custom()

# Filter by portfolio
custom_investments = client.investments.list_custom(portfolio_id=123456)

# Get custom investment details
investment = client.investments.get_custom(investment_id=999)
```

### Reports

```python
# Performance report
performance = client.reports.get_performance(
    portfolio_id=123456,
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Diversity report
diversity = client.reports.get_diversity(
    portfolio_id=123456,
    grouping="market"  # or "sector", "country", etc.
)

# Capital gains report
capital_gains = client.reports.get_capital_gains(
    portfolio_id=123456,
    start_date="2024-07-01",
    end_date="2025-06-30"
)

# Tax report
tax_report = client.reports.get_tax_report(
    portfolio_id=123456,
    start_date="2024-07-01",
    end_date="2025-06-30"
)
```

### Market Data

```python
# List all supported markets
markets = client.market.list_markets()

# List all supported currencies
currencies = client.market.list_currencies()

# List all supported countries
countries = client.market.list_countries()
```

---

## Error Handling

```python
from sharesight import (
    SharesightClient,
    SharesightAuthError,
    SharesightAPIError,
    SharesightRateLimitError
)

client = SharesightClient()

try:
    portfolios = client.portfolios.list()
except SharesightAuthError as e:
    print(f"Authentication failed: {e}")
except SharesightRateLimitError as e:
    print(f"Rate limited. Try again later.")
except SharesightAPIError as e:
    print(f"API error ({e.status_code}): {e.response_body}")
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Links

- [Sharesight API Overview](https://portfolio.sharesight.com/api)
- [Sharesight API v3 Documentation](https://portfolio.sharesight.com/api/3/overview)
- [Sharesight Website](https://www.sharesight.com/)

---

## Disclaimer

This is an **unofficial** SDK and is not affiliated with, endorsed by, or supported by Sharesight. Use at your own risk.
