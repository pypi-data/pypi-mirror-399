"""
Synchronous Fragment API client for traditional function calls
"""

import logging
from typing import Dict, Any
from .core import FragmentAPICore
from .wallet import WalletManager
from .exceptions import (
    UserNotFoundError, InvalidAmountError, PaymentInitiationError,
    TransactionError, NetworkError, FragmentAPIException,
    InsufficientBalanceError
)
from .models import UserInfo, PurchaseResult
from .utils import validate_username, validate_amount, nano_to_ton

logger = logging.getLogger(__name__)


class SyncFragmentAPI(FragmentAPICore):
    """
    Synchronous client for Fragment API with traditional blocking calls
    
    Provides a blocking interface for all Fragment API operations.
    Automatically manages wallet balance checking before transactions.
    """

    TRANSFER_FEE_TON = 0.001

    def __init__(self, cookies: str, hash_value: str, wallet_mnemonic: str, 
                 wallet_api_key: str, timeout: int = 15):
        """
        Initialize synchronous Fragment API client
        
        Args:
            cookies: Authenticated session cookies from Fragment.com
                    Get from browser: DevTools -> Application -> Cookies
                    Format: 'stel_ssid=value; stel_token=value; ...'
            hash_value: API hash for request authentication
            wallet_mnemonic: 24-word mnemonic for WalletV4R2
            wallet_api_key: API key from https://tonconsole.com
            timeout: Request timeout in seconds (default 15)
        
        Raises:
            AuthenticationError: If credentials are invalid
        
        Example:
            >>> api = SyncFragmentAPI(
            ...     cookies="stel_ssid=abc123;...",
            ...     hash_value="abc123def456",
            ...     wallet_mnemonic="abandon ability able...",
            ...     wallet_api_key="AHQSQGXHKZZS..."
            ... )
        """
        super().__init__(cookies, hash_value, timeout)
        self.wallet = WalletManager(wallet_mnemonic, wallet_api_key)

    def _check_user(self, username: str, method: str) -> UserInfo:
        """
        Check if user exists synchronously
        
        Args:
            username: Username to check
            method: API method name
        
        Returns:
            UserInfo object if found
        
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        if not validate_username(username):
            raise UserNotFoundError(f"Invalid username format: {username}")
        
        try:
            result = self._make_request({
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

    def buy_stars(self, username: str, quantity: int) -> PurchaseResult:
        """
        Synchronously purchase and deliver Telegram Stars
        
        Process:
        1. Validates username and quantity
        2. Checks if user exists on Fragment
        3. Retrieves wallet balance
        4. Initiates purchase request on Fragment
        5. Verifies sufficient balance for transaction
        6. Sends TON transaction to Fragment contract
        7. Returns transaction hash
        
        Args:
            username: Target username to send stars to
            quantity: Number of stars (minimum 1, maximum 999999)
        
        Returns:
            PurchaseResult containing transaction hash or error
        
        Raises:
            UserNotFoundError: If username doesn't exist
            InvalidAmountError: If quantity is invalid
            InsufficientBalanceError: If wallet lacks funds
        
        Example:
            >>> api = SyncFragmentAPI(cookies, hash, mnemonic, key)
            >>> result = api.buy_stars('username', 100)
            >>> if result.success:
            ...     print(f"Transaction: {result.transaction_hash}")
            ...     print(f"Balance checked: {result.balance_checked}")
        """
        if not validate_amount(quantity, 1, 999999):
            raise InvalidAmountError(f"Invalid quantity: {quantity}")
        
        try:
            user = self._check_user(username, 'searchStarsRecipient')
            
            init = self._make_request({
                'recipient': user.recipient,
                'quantity': quantity,
                'method': 'initBuyStarsRequest'
            })
            
            if 'error' in init:
                raise PaymentInitiationError(init.get('error'))
            
            req_id = init.get('req_id')
            buy_response = self._make_request({
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
            
            wallet_balance = self.wallet.get_balance_sync()
            required_amount = nano_to_ton(amount_nano)
            total_with_fee = required_amount + self.TRANSFER_FEE_TON
            
            if not wallet_balance.has_sufficient_balance(amount_nano):
                raise InsufficientBalanceError(
                    f"Insufficient balance. Required: {total_with_fee:.6f} TON, "
                    f"Available: {wallet_balance.balance_ton:.6f} TON"
                )
            
            tx_hash = self.wallet.send_transaction_sync(dest_address, amount_nano, raw_boc)
            
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

    def gift_premium(self, username: str, months: int = 3) -> PurchaseResult:
        """
        Synchronously gift Telegram Premium subscription to user
        
        Process:
        1. Validates username and months (3, 6, or 12)
        2. Checks if user exists
        3. Retrieves current wallet balance from blockchain
        4. Initiates premium gift request
        5. Validates sufficient wallet balance for transaction + fee
        6. Sends transaction to Fragment contract
        7. Returns confirmation with transaction hash
        
        Args:
            username: Target username
            months: Premium duration (3, 6, or 12 months)
        
        Returns:
            PurchaseResult with transaction details
        
        Raises:
            UserNotFoundError: If username not found
            InvalidAmountError: If months not in [3, 6, 12]
            InsufficientBalanceError: If insufficient wallet balance
        
        Example:
            >>> api = SyncFragmentAPI(cookies, hash, mnemonic, key)
            >>> result = api.gift_premium('username', 6)
            >>> print(f"Success: {result.success}")
            >>> if result.balance_checked:
            ...     print(f"Required: {result.required_amount} TON")
        """
        if months not in [3, 6, 12]:
            raise InvalidAmountError(f"Invalid months: {months}. Must be 3, 6, or 12")
        
        try:
            user = self._check_user(username, 'searchPremiumGiftRecipient')
            
            init = self._make_request({
                'recipient': user.recipient,
                'months': months,
                'method': 'initGiftPremiumRequest'
            })
            
            if 'error' in init:
                raise PaymentInitiationError(init.get('error'))
            
            req_id = init.get('req_id')
            buy_response = self._make_request({
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
            
            wallet_balance = self.wallet.get_balance_sync()
            required_amount = nano_to_ton(amount_nano)
            total_with_fee = required_amount + self.TRANSFER_FEE_TON
            
            if not wallet_balance.has_sufficient_balance(amount_nano):
                raise InsufficientBalanceError(
                    f"Insufficient balance. Required: {total_with_fee:.6f} TON, "
                    f"Available: {wallet_balance.balance_ton:.6f} TON"
                )
            
            tx_hash = self.wallet.send_transaction_sync(dest_address, amount_nano, raw_boc)
            
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

    def topup_ton(self, username: str, amount: int) -> PurchaseResult:
        """
        Synchronously top up Telegram Ads account balance with TON
        
        Process:
        1. Validates username and amount
        2. Checks if user exists on Fragment
        3. Reads current wallet balance from TON blockchain
        4. Initiates ads topup request on Fragment
        5. Verifies wallet has sufficient balance + transaction fee
        6. Sends transaction to Fragment contract
        7. Returns blockchain transaction hash
        
        Args:
            username: Target username
            amount: Amount of TON to transfer (1-999999)
        
        Returns:
            PurchaseResult with transaction information
        
        Raises:
            UserNotFoundError: If user not found
            InvalidAmountError: If amount is invalid
            InsufficientBalanceError: If wallet balance insufficient
        
        Example:
            >>> api = SyncFragmentAPI(cookies, hash, mnemonic, key)
            >>> result = api.topup_ton('username', 5)
            >>> if not result.success:
            ...     print(f"Error: {result.error}")
            ... else:
            ...     print(f"TX: {result.transaction_hash}")
        """
        if not validate_amount(amount, 1, 999999):
            raise InvalidAmountError(f"Invalid amount: {amount}")
        
        try:
            user = self._check_user(username, 'searchAdsTopupRecipient')
            
            init = self._make_request({
                'recipient': user.recipient,
                'amount': str(amount),
                'method': 'initAdsTopupRequest'
            })
            
            if 'error' in init:
                raise PaymentInitiationError(init.get('error'))
            
            req_id = init.get('req_id')
            buy_response = self._make_request({
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
            
            wallet_balance = self.wallet.get_balance_sync()
            required_amount = nano_to_ton(amount_nano)
            total_with_fee = required_amount + self.TRANSFER_FEE_TON
            
            if not wallet_balance.has_sufficient_balance(amount_nano):
                raise InsufficientBalanceError(
                    f"Insufficient balance. Required: {total_with_fee:.6f} TON, "
                    f"Available: {wallet_balance.balance_ton:.6f} TON"
                )
            
            tx_hash = self.wallet.send_transaction_sync(dest_address, amount_nano, raw_boc)
            
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

    def get_wallet_balance(self) -> Dict[str, Any]:
        """
        Get current wallet balance and address synchronously
        
        Queries TON blockchain directly to retrieve:
        - Current balance in TON and nanotons
        - Wallet address
        - Wallet readiness for transactions
        
        Returns:
            Dictionary with:
            - balance_ton: Balance in TON (float)
            - balance_nano: Balance in nanotons (string)
            - address: Wallet blockchain address
            - is_ready: Whether wallet is ready
        
        Raises:
            WalletError: If balance retrieval fails
        
        Example:
            >>> api = SyncFragmentAPI(cookies, hash, mnemonic, key)
            >>> balance_info = api.get_wallet_balance()
            >>> print(f"Balance: {balance_info['balance_ton']} TON")
            >>> print(f"Address: {balance_info['address']}")
        """
        try:
            balance = self.wallet.get_balance_sync()
            return {
                'balance_ton': balance.balance_ton,
                'balance_nano': balance.balance_nano,
                'address': balance.address,
                'is_ready': balance.is_ready
            }
        except Exception as e:
            logger.error(f"Failed to get wallet balance: {e}")
            raise