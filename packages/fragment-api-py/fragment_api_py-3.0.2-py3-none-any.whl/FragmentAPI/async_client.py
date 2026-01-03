"""
Asynchronous Fragment API client for async/await support
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from .core import FragmentAPICore
from .wallet import WalletManager
from .exceptions import (
    UserNotFoundError, InvalidAmountError, PaymentInitiationError,
    TransactionError, NetworkError, AuthenticationError, FragmentAPIException,
    InsufficientBalanceError
)
from .models import UserInfo, TransactionData, PurchaseResult
from .utils import parse_cookies, validate_username, validate_amount, get_default_headers, nano_to_ton

logger = logging.getLogger(__name__)


class AsyncFragmentAPI:
    """
    Asynchronous client for Fragment API with automatic wallet transaction handling
    
    Provides async/await interface for sending Telegram Stars, Premium, and TON.
    Automatically validates wallet balance before initiating transactions.
    """

    BASE_URL = "https://fragment.com/api"
    DEFAULT_TIMEOUT = 15
    TRANSFER_FEE_TON = 0.001

    def __init__(self, cookies: str, hash_value: str, wallet_mnemonic: str, 
                 wallet_api_key: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize async Fragment API client with wallet support
        
        Args:
            cookies: Authenticated session cookies from Fragment.com
                    Get from browser: DevTools -> Application -> Cookies
                    Format: 'stel_ssid=value; stel_token=value; ...'
            hash_value: API hash for request authentication
            wallet_mnemonic: 24-word mnemonic for WalletV4R2
            wallet_api_key: API key from https://tonconsole.com
            timeout: Request timeout in seconds (default 15)
        
        Raises:
            AuthenticationError: If provided credentials are invalid
        
        Example:
            >>> api = AsyncFragmentAPI(
            ...     cookies="stel_ssid=abc123;...",
            ...     hash_value="abc123def456",
            ...     wallet_mnemonic="abandon ability able...",
            ...     wallet_api_key="AHQSQGXHKZZS..."
            ... )
        """
        if not all([cookies, hash_value, wallet_mnemonic, wallet_api_key]):
            raise AuthenticationError("All credentials are required")
        
        self.core = FragmentAPICore(cookies, hash_value, timeout)
        self.wallet = WalletManager(wallet_mnemonic, wallet_api_key)
        self.session: Optional[aiohttp.ClientSession] = None

    async def _check_user(self, username: str, method: str) -> UserInfo:
        """
        Check if user exists using specified API method
        
        Args:
            username: Target username to check
            method: API method name for user search
        
        Returns:
            UserInfo object with recipient address
        
        Raises:
            UserNotFoundError: If user not found
            NetworkError: If request fails
        """
        if not validate_username(username):
            raise UserNotFoundError(f"Invalid username format: {username}")
        
        try:
            result = self.core._make_request({
                'query': username,
                'method': method,
                'quantity': '' if 'Stars' in method else '3'
            })
        except Exception as e:
            raise NetworkError(f"Failed to check user: {e}")
        
        if 'error' in result:
            raise UserNotFoundError(f"User not found: {result.get('error')}")
        
        found_data = result.get('found', {})
        if not found_data or not found_data.get('recipient'):
            raise UserNotFoundError(f"User {username} not found")
        
        return UserInfo(
            name=found_data.get('name', username),
            recipient=found_data.get('recipient'),
            found=True
        )

    async def buy_stars(self, username: str, quantity: int) -> PurchaseResult:
        """
        Purchase and send Telegram Stars to user
        
        Process:
        1. Validates username and quantity
        2. Checks if user exists on Fragment
        3. Retrieves wallet balance
        4. Initiates purchase request on Fragment
        5. Verifies sufficient balance for transaction
        6. Sends TON transaction to Fragment contract
        7. Returns transaction hash
        
        Args:
            username: Target Telegram username (with or without @)
            quantity: Number of stars (1-999999)
        
        Returns:
            PurchaseResult with:
            - success: True if completed successfully
            - transaction_hash: Blockchain transaction ID
            - error: Error message if failed
            - user: UserInfo object
            - balance_checked: Whether balance was validated
        
        Raises:
            UserNotFoundError: If username doesn't exist
            InvalidAmountError: If quantity is invalid
            InsufficientBalanceError: If wallet lacks funds
        
        Example:
            >>> result = await api.buy_stars('john_doe', 100)
            >>> if result.success:
            ...     print(f"TX: {result.transaction_hash}")
            ... else:
            ...     print(f"Error: {result.error}")
        """
        if not validate_amount(quantity, 1, 999999):
            raise InvalidAmountError(f"Invalid quantity: {quantity}")
        
        try:
            user = await self._check_user(username, 'searchStarsRecipient')
            
            init = self.core._make_request({
                'recipient': user.recipient,
                'quantity': quantity,
                'method': 'initBuyStarsRequest'
            })
            
            if 'error' in init:
                raise PaymentInitiationError(init.get('error'))
            
            req_id = init.get('req_id')
            buy_response = self.core._make_request({
                'transaction': '1',
                'id': req_id,
                'show_sender': '0',
                'method': 'getBuyStarsLink'
            })
            
            if 'error' in buy_response:
                raise TransactionError(buy_response.get('error'))
            
            transaction = buy_response.get('transaction', {})
            messages = transaction.get('messages', [{}])
            
            dest_address = messages[0].get('address')
            amount_nano = messages[0].get('amount')
            raw_boc = messages[0].get('payload')
            
            wallet_balance = await self.wallet.get_balance()
            required_amount = nano_to_ton(amount_nano)
            total_with_fee = required_amount + self.TRANSFER_FEE_TON
            
            if not wallet_balance.has_sufficient_balance(amount_nano):
                raise InsufficientBalanceError(
                    f"Insufficient balance. Required: {total_with_fee:.6f} TON, "
                    f"Available: {wallet_balance.balance_ton:.6f} TON"
                )
            
            tx_hash = await self.wallet.send_transaction(dest_address, amount_nano, raw_boc)
            
            return PurchaseResult(
                success=True,
                transaction_hash=tx_hash,
                user=user,
                balance_checked=True,
                required_amount=total_with_fee
            )
        
        except (UserNotFoundError, InvalidAmountError, InsufficientBalanceError, 
                PaymentInitiationError, TransactionError) as e:
            return PurchaseResult(
                success=False,
                error=str(e),
                user=None,
                balance_checked=False
            )
        except Exception as e:
            logger.error(f"Error buying stars: {e}")
            return PurchaseResult(
                success=False,
                error=str(e),
                user=None,
                balance_checked=False
            )

    async def gift_premium(self, username: str, months: int = 3) -> PurchaseResult:
        """
        Gift Telegram Premium subscription to user
        
        Process:
        1. Validates username and months (3, 6, or 12)
        2. Checks if user exists
        3. Retrieves current wallet balance
        4. Initiates premium gift request
        5. Validates sufficient wallet balance
        6. Sends transaction to Fragment contract
        7. Returns confirmation with transaction hash
        
        Args:
            username: Target username
            months: Subscription duration (3, 6, or 12 months)
        
        Returns:
            PurchaseResult with transaction details
        
        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidAmountError: If months not in [3, 6, 12]
            InsufficientBalanceError: If insufficient wallet balance
        
        Example:
            >>> result = await api.gift_premium('jane_doe', 6)
            >>> print(f"Success: {result.success}")
            >>> if result.balance_checked:
            ...     print(f"Balance was: {result.required_amount} TON")
        """
        if months not in [3, 6, 12]:
            raise InvalidAmountError(f"Invalid months: {months}. Must be 3, 6, or 12")
        
        try:
            user = await self._check_user(username, 'searchPremiumGiftRecipient')
            
            init = self.core._make_request({
                'recipient': user.recipient,
                'months': months,
                'method': 'initGiftPremiumRequest'
            })
            
            if 'error' in init:
                raise PaymentInitiationError(init.get('error'))
            
            req_id = init.get('req_id')
            buy_response = self.core._make_request({
                'transaction': '1',
                'id': req_id,
                'show_sender': '0',
                'method': 'getGiftPremiumLink'
            })
            
            if 'error' in buy_response:
                raise TransactionError(buy_response.get('error'))
            
            transaction = buy_response.get('transaction', {})
            messages = transaction.get('messages', [{}])
            
            dest_address = messages[0].get('address')
            amount_nano = messages[0].get('amount')
            raw_boc = messages[0].get('payload')
            
            wallet_balance = await self.wallet.get_balance()
            required_amount = nano_to_ton(amount_nano)
            total_with_fee = required_amount + self.TRANSFER_FEE_TON
            
            if not wallet_balance.has_sufficient_balance(amount_nano):
                raise InsufficientBalanceError(
                    f"Insufficient balance. Required: {total_with_fee:.6f} TON, "
                    f"Available: {wallet_balance.balance_ton:.6f} TON"
                )
            
            tx_hash = await self.wallet.send_transaction(dest_address, amount_nano, raw_boc)
            
            return PurchaseResult(
                success=True,
                transaction_hash=tx_hash,
                user=user,
                balance_checked=True,
                required_amount=total_with_fee
            )
        
        except (UserNotFoundError, InvalidAmountError, InsufficientBalanceError,
                PaymentInitiationError, TransactionError) as e:
            return PurchaseResult(
                success=False,
                error=str(e),
                user=None,
                balance_checked=False
            )
        except Exception as e:
            logger.error(f"Error gifting premium: {e}")
            return PurchaseResult(
                success=False,
                error=str(e),
                user=None,
                balance_checked=False
            )

    async def topup_ton(self, username: str, amount: int) -> PurchaseResult:
        """
        Top up Telegram Ads account with TON cryptocurrency
        
        Process:
        1. Validates username and amount
        2. Checks if user exists
        3. Reads current wallet balance from blockchain
        4. Initiates ads topup request on Fragment
        5. Verifies wallet has sufficient balance + fee
        6. Sends transaction to Fragment contract
        7. Returns blockchain transaction hash
        
        Args:
            username: Target username
            amount: Amount of TON to send (1-999999)
        
        Returns:
            PurchaseResult with transaction hash and balance info
        
        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidAmountError: If amount is invalid
            InsufficientBalanceError: If wallet balance insufficient
        
        Example:
            >>> result = await api.topup_ton('ads_user', 10)
            >>> if result.balance_checked:
            ...     print(f"Required {result.required_amount} TON")
        """
        if not validate_amount(amount, 1, 999999):
            raise InvalidAmountError(f"Invalid amount: {amount}")
        
        try:
            user = await self._check_user(username, 'searchAdsTopupRecipient')
            
            init = self.core._make_request({
                'recipient': user.recipient,
                'amount': str(amount),
                'method': 'initAdsTopupRequest'
            })
            
            if 'error' in init:
                raise PaymentInitiationError(init.get('error'))
            
            req_id = init.get('req_id')
            buy_response = self.core._make_request({
                'transaction': '1',
                'id': req_id,
                'show_sender': '0',
                'method': 'getAdsTopupLink'
            })
            
            if 'error' in buy_response:
                raise TransactionError(buy_response.get('error'))
            
            transaction = buy_response.get('transaction', {})
            messages = transaction.get('messages', [{}])
            
            dest_address = messages[0].get('address')
            amount_nano = messages[0].get('amount')
            raw_boc = messages[0].get('payload')
            
            wallet_balance = await self.wallet.get_balance()
            required_amount = nano_to_ton(amount_nano)
            total_with_fee = required_amount + self.TRANSFER_FEE_TON
            
            if not wallet_balance.has_sufficient_balance(amount_nano):
                raise InsufficientBalanceError(
                    f"Insufficient balance. Required: {total_with_fee:.6f} TON, "
                    f"Available: {wallet_balance.balance_ton:.6f} TON"
                )
            
            tx_hash = await self.wallet.send_transaction(dest_address, amount_nano, raw_boc)
            
            return PurchaseResult(
                success=True,
                transaction_hash=tx_hash,
                user=user,
                balance_checked=True,
                required_amount=total_with_fee
            )
        
        except (UserNotFoundError, InvalidAmountError, InsufficientBalanceError,
                PaymentInitiationError, TransactionError) as e:
            return PurchaseResult(
                success=False,
                error=str(e),
                user=None,
                balance_checked=False
            )
        except Exception as e:
            logger.error(f"Error topping up TON: {e}")
            return PurchaseResult(
                success=False,
                error=str(e),
                user=None,
                balance_checked=False
            )

    async def get_wallet_balance(self) -> Dict[str, Any]:
        """
        Get current wallet balance and address
        
        Queries TON blockchain directly to retrieve:
        - Current balance in TON and nanotons
        - Wallet address
        - Wallet readiness for transactions
        
        Returns:
            Dictionary with balance information
        
        Raises:
            WalletError: If balance retrieval fails
        
        Example:
            >>> balance_info = await api.get_wallet_balance()
            >>> print(f"Balance: {balance_info['balance_ton']} TON")
        """
        try:
            balance = await self.wallet.get_balance()
            return {
                'balance_ton': balance.balance_ton,
                'balance_nano': balance.balance_nano,
                'address': balance.address,
                'is_ready': balance.is_ready
            }
        except Exception as e:
            logger.error(f"Failed to get wallet balance: {e}")
            raise

    async def close(self) -> None:
        """
        Close aiohttp session and cleanup resources
        
        Should be called when done with the client.
        """
        self.core.close()
        if self.session:
            await self.session.close()

    async def __aenter__(self):
        """
        Async context manager entry
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit
        """
        await self.close()