# Fragment API Python

Professional Python library for Fragment.com API with async and sync support. Send Telegram Stars, Premium, and TON with automatic wallet validation.

## Features

- ✅ Async & Sync interfaces
- ✅ 3 payment methods (Stars, Premium, TON)
- ✅ Recipient lookup (get user info & avatar)
- ✅ Automatic wallet balance validation
- ✅ WalletV4R2 support
- ✅ Comprehensive error handling
- ✅ Type hints & logging

## Installation

```bash
pip install fragment-api-py
```

## Quick Start

### Synchronous

```python
from FragmentAPI import SyncFragmentAPI

api = SyncFragmentAPI(
    cookies="your_cookies",
    hash_value="your_hash",
    wallet_mnemonic="your mnemonic...",
    wallet_api_key="your_api_key"
)

# Get recipient info with avatar
recipient = api.get_recipient_stars('username')
print(f"Name: {recipient.name}")
print(f"Avatar: {recipient.avatar}")

# Send stars
result = api.buy_stars('username', 100)
if result.success:
    print(f"TX: {result.transaction_hash}")

api.close()
```

### Asynchronous

```python
import asyncio
from FragmentAPI import AsyncFragmentAPI

async def main():
    api = AsyncFragmentAPI(
        cookies="your_cookies",
        hash_value="your_hash",
        wallet_mnemonic="your mnemonic...",
        wallet_api_key="your_api_key"
    )
    
    # Get recipient info with avatar
    recipient = await api.get_recipient_stars('username')
    print(f"Name: {recipient.name}")
    print(f"Avatar: {recipient.avatar}")
    
    # Send stars
    result = await api.buy_stars('username', 100)
    if result.success:
        print(f"TX: {result.transaction_hash}")
    
    await api.close()

asyncio.run(main())
```

## Methods

### Recipient Lookup

#### get_recipient_stars(username)
Get recipient info for Stars transfer
- Returns: `UserInfo` with name, recipient address, avatar (URL or base64)

#### get_recipient_premium(username)
Get recipient info for Premium gift
- Returns: `UserInfo` with name, recipient address, avatar

#### get_recipient_ton(username)
Get recipient info for Ads account top-up
- Returns: `UserInfo` with name, recipient address, avatar

### Payments

#### buy_stars(username, quantity)
Send Telegram Stars to user
- `username` (str): Target username
- `quantity` (int): Number of stars (1-999999)

#### gift_premium(username, months)
Gift Premium subscription (3, 6, or 12 months)
- `username` (str): Target username
- `months` (int): Duration in months

#### topup_ton(username, amount)
Top up Telegram Ads account with TON
- `username` (str): Target username
- `amount` (int): Amount of TON (1-999999)

### Wallet

#### get_wallet_balance()
Get current wallet balance and address
- Returns: Dictionary with balance in TON/nanotons and address

## Recipient Info

```python
# Get user info before sending payment
user = api.get_recipient_stars('john_doe')

if user.found:
    print(f"Name: {user.name}")
    print(f"Address: {user.recipient}")
    print(f"Avatar: {user.avatar}")  # URL or base64 encoded image
```

**UserInfo object:**
- `name` - User's display name
- `recipient` - Blockchain address
- `found` - Boolean flag
- `avatar` - Avatar URL (HTTP/HTTPS) or base64 encoded image

## Setup

### 1. Get Fragment Cookies

1. Open fragment.com in browser
2. Press F12 → Application → Cookies
3. Copy cookies: `stel_ssid`, `stel_token`, `stel_dt`, `stel_ton_token`
4. Combine: `stel_ssid=value; stel_token=value; ...`

### 2. Get Hash Value

From DevTools Network tab → fragment.com/api requests → copy `hash` parameter

### 3. Setup TON Wallet

1. Get 24-word seed phrase from TON wallet (Tonkeeper, MyTonWallet, etc)
2. Fund wallet with TON for transactions

### 4. Get API Key

1. Go to https://tonconsole.com
2. Create project
3. Generate API key from Settings

## Exceptions

- `AuthenticationError` - Invalid cookies/hash
- `UserNotFoundError` - User doesn't exist
- `InvalidAmountError` - Invalid quantity/amount
- `InsufficientBalanceError` - Low wallet balance
- `TransactionError` - TX execution failed
- `NetworkError` - Network request failed
- `WalletError` - Wallet operation failed
- `PaymentInitiationError` - Fragment API error

## Error Handling

```python
from FragmentAPI import InsufficientBalanceError, UserNotFoundError

try:
    # Get recipient info
    user = api.get_recipient_stars('username')
    
    # Send payment
    result = api.buy_stars('username', 100)
    if not result.success:
        print(f"Error: {result.error}")
except InsufficientBalanceError as e:
    print(f"Low balance: {e}")
except UserNotFoundError as e:
    print(f"User not found: {e}")
finally:
    api.close()
```

## Security

Store credentials in environment variables:

```python
import os

api = SyncFragmentAPI(
    cookies=os.getenv('FRAGMENT_COOKIES'),
    hash_value=os.getenv('FRAGMENT_HASH'),
    wallet_mnemonic=os.getenv('WALLET_MNEMONIC'),
    wallet_api_key=os.getenv('WALLET_API_KEY')
)
```

## Requirements

- Python 3.7+
- requests >= 2.28.0
- aiohttp >= 3.8.0
- tonutils >= 0.3.0
- pytoniq-core >= 0.1.0

## Documentation

Full documentation: https://github.com/S1qwy/fragment-api-py

## License

MIT License

## Support

- GitHub: https://github.com/S1qwy/fragment-api-py
- Issues: https://github.com/S1qwy/fragment-api-py/issues