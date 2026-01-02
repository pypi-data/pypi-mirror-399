# f(x) Protocol Python SDK - Complete Documentation

**Version:** 0.3.0  
**Creator:** Christopher Stampar (@cstampar)  
**Last Updated:** December 22, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Authentication](#authentication)
5. [Core Classes](#core-classes)
6. [Token Balance Methods](#token-balance-methods)
7. [V1 Protocol Methods](#v1-protocol-methods)
8. [V2 Protocol Methods](#v2-protocol-methods)
9. [Governance Methods](#governance-methods)
10. [Convex Finance Integration](#convex-finance-integration)
11. [Curve Finance Integration](#curve-finance-integration)
12. [Utility Methods](#utility-methods)
13. [Error Handling](#error-handling)
14. [Examples](#examples)

---

## Introduction

The f(x) Protocol Python SDK provides a production-grade interface for interacting with the f(x) Protocol on Ethereum. It abstracts Web3.py boilerplate and provides human-readable interfaces for both V1 and V2 products, including Convex Finance and Curve Finance integrations.

### Key Features

- **High-Precision**: Uses Python `Decimal` for all amounts to prevent floating-point errors
- **Secure Authentication**: Multiple secure credential sources (env vars, .env files, Colab secrets, browser wallets)
- **Read-Only Mode**: Full querying capabilities without private keys
- **Comprehensive Coverage**: V1, V2, Convex, and Curve Finance integrations
- **Production-Ready**: Robust error handling, logging, and type hints

---

## Installation

```bash
pip install fx-sdk
```

### Requirements

- Python >= 3.8
- Web3.py >= 6.0.0
- eth-account >= 0.5.0

---

## Quick Start

### Read-Only Mode (No Private Key)

```python
from fx_sdk.client import ProtocolClient

client = ProtocolClient(
    rpc_url="https://eth.llamarpc.com"
)

# Get fxUSD balance for any address
balance = client.get_fxusd_balance("0x1234...")
print(f"fxUSD Balance: {balance}")
```

### Write Mode (With Authentication)

```python
from fx_sdk.client import ProtocolClient

# Private key loaded from environment variable
client = ProtocolClient(
    rpc_url="https://eth.llamarpc.com"
)

# Mint fxUSD
tx_hash = client.mint_f_token(
    market_address="0x...",
    base_in=1.0
)
print(f"Transaction: {tx_hash}")
```

---

## Authentication

The SDK supports multiple secure authentication methods. **Never hardcode private keys in your code!**

### Priority Order

1. Explicit `private_key` parameter (lowest priority, for testing only)
2. `FX_PROTOCOL_PRIVATE_KEY` environment variable
3. `.env` file (`FX_PROTOCOL_PRIVATE_KEY`)
4. Google Colab secret (`fx_protocol_private_key`)
5. Browser wallet (if `use_browser_wallet=True`)

### Environment Variable

```bash
export FX_PROTOCOL_PRIVATE_KEY="0x..."
```

```python
client = ProtocolClient(rpc_url="https://eth.llamarpc.com")
```

### .env File

Create `.env`:
```
FX_PROTOCOL_PRIVATE_KEY=0x...
```

```python
client = ProtocolClient(rpc_url="https://eth.llamarpc.com")
```

### Google Colab

```python
# Store secret in Colab: 'fx_protocol_private_key'
client = ProtocolClient(rpc_url="https://eth.llamarpc.com")
```

### Browser Wallet

```python
client = ProtocolClient(
    rpc_url="https://eth.llamarpc.com",
    use_browser_wallet=True
)
```

---

## Core Classes

### ProtocolClient

The main client class for interacting with the f(x) Protocol.

#### Initialization

```python
ProtocolClient(
    rpc_url: str,
    private_key: Optional[str] = None,
    abi_dir: Optional[str] = None,
    log_level: int = logging.INFO,
    use_browser_wallet: bool = False
)
```

**Parameters:**
- `rpc_url` (str): Ethereum RPC endpoint URL
- `private_key` (Optional[str]): Private key (not recommended, use env vars)
- `abi_dir` (Optional[str]): Custom ABI directory (defaults to package ABIs)
- `log_level` (int): Logging level (default: `logging.INFO`)
- `use_browser_wallet` (bool): Connect to browser wallet (default: `False`)

**Example:**
```python
client = ProtocolClient(
    rpc_url="https://eth.llamarpc.com",
    log_level=logging.DEBUG
)
```

---


## Token Balance Methods

### Generic Token Methods

#### `get_token_balance(token_address, account_address=None)`

Get the human-readable balance of any ERC-20 token.

**Parameters:**
- `token_address` (str): ERC-20 token contract address
- `account_address` (Optional[str]): Account address (defaults to client's address)

**Returns:** `Decimal` - Human-readable token balance

**Example:**
```python
balance = client.get_token_balance(
    token_address="0x085780639CC2cACd35E474e71f4d000e2405d8f6",
    account_address="0x1234..."
)
print(f"Balance: {balance}")
```

#### `get_token_total_supply(token_address)`

Get the total supply of a token.

**Parameters:**
- `token_address` (str): Token contract address

**Returns:** `Decimal` - Total supply

#### `get_allowance(token_address, owner, spender)`

Get the allowance of a spender for a token owner.

**Parameters:**
- `token_address` (str): Token contract address
- `owner` (str): Token owner address
- `spender` (str): Spender address

**Returns:** `Decimal` - Allowance amount

### Protocol Token Balance Methods

All methods follow the same pattern: `get_{token}_balance(account_address=None)`

**Available Methods:**
- `get_fxusd_balance()` - fxUSD balance
- `get_feth_balance()` - fETH balance
- `get_rusd_balance()` - rUSD balance
- `get_btcusd_balance()` - btcUSD balance
- `get_cvxusd_balance()` - cvxUSD balance
- `get_arusd_balance()` - arUSD balance
- `get_xeth_balance()` - xETH balance
- `get_xcvx_balance()` - xCVX balance
- `get_xwbtc_balance()` - xWBTC balance
- `get_xeeth_balance()` - xeETH balance
- `get_xezeth_balance()` - xezETH balance
- `get_xsteth_balance()` - xstETH balance
- `get_xfrxeth_balance()` - xfrxETH balance
- `get_fxsave_balance()` - fxSAVE balance
- `get_fxsp_balance()` - fxSP balance
- `get_fxn_balance()` - FXN balance
- `get_vefxn_balance()` - veFXN balance
- `get_cvxfxn_balance()` - cvxFXN balance

**Example:**
```python
fxusd = client.get_fxusd_balance()
feth = client.get_feth_balance()
print(f"fxUSD: {fxusd}, fETH: {feth}")
```

#### `get_all_balances(account_address=None)`

Get all protocol token balances in a single call.

**Returns:** `Dict[str, Decimal]` - Dictionary mapping token names to balances

**Example:**
```python
balances = client.get_all_balances("0x1234...")
for token, balance in balances.items():
    print(f"{token}: {balance}")
```

---

## V1 Protocol Methods

### Market Information

#### `get_v1_nav()`

Get Net Asset Value (NAV) for V1 fETH and xETH.

**Returns:** `Dict[str, Decimal]` with keys:
- `fETH_NAV`: fETH Net Asset Value
- `xETH_NAV`: xETH Net Asset Value

#### `get_v1_collateral_ratio()`

Get the current collateral ratio of the V1 market.

**Returns:** `Decimal` - Collateral ratio

### Rebalance Pools

#### `get_v1_rebalance_pools()`

Get all registered V1 rebalance pool addresses.

**Returns:** `List[str]` - List of pool addresses

#### `get_v1_rebalance_pool_balances(pool_address, account_address=None)`

Get balances for an account in a V1 rebalance pool.

**Parameters:**
- `pool_address` (str): Rebalance pool address
- `account_address` (Optional[str]): Account address

**Returns:** `Dict[str, Decimal]` with keys:
- `staked`: Staked balance
- `unlocked`: Unlocked balance
- `unlocking`: Balance currently unlocking

### V1 Treasury Operations

#### `mint_via_treasury(base_in, recipient=None, option=0)`

Mint fETH and xETH via the V1 Treasury.

**Parameters:**
- `base_in` (Union[int, float, Decimal, str]): Amount of base token (stETH) to deposit
- `recipient` (Optional[str]): Recipient address (defaults to client address)
- `option` (int): Minting option (0 = default)

**Returns:** `str` - Transaction hash

**Example:**
```python
tx_hash = client.mint_via_treasury(base_in=1.0)
print(f"Minted via treasury: {tx_hash}")
```

#### `redeem_via_treasury(f_token_in=0, x_token_in=0, owner=None)`

Redeem fETH and/or xETH via the V1 Treasury.

**Parameters:**
- `f_token_in` (Union[int, float, Decimal, str]): Amount of f-token to redeem
- `x_token_in` (Union[int, float, Decimal, str]): Amount of x-token to redeem
- `owner` (Optional[str]): Owner address (defaults to client address)

**Returns:** `str` - Transaction hash

---

## V2 Protocol Methods

### Pool Information

#### `get_v2_pool_info()`

Get information about the V2 fxUSD Base Pool.

**Returns:** `Dict[str, Any]` with pool information

#### `get_steth_price()`

Get the current stETH price from the oracle.

**Returns:** `Decimal` - stETH price

#### `get_fxusd_total_supply()`

Get the total supply of fxUSD.

**Returns:** `Decimal` - Total fxUSD supply

### V2 Position Management

#### `operate_position(pool_address, position_id, new_collateral, new_debt)`

Operate (modify) a V2 position.

**Parameters:**
- `pool_address` (str): Pool address
- `position_id` (int): Position ID
- `new_collateral` (Union[int, float, Decimal, str]): New collateral amount
- `new_debt` (Union[int, float, Decimal, str]): New debt amount

**Returns:** `str` - Transaction hash

#### `rebalance_position(pool_address, receiver, position_id, max_fxusd, max_stable)`

Rebalance a V2 position.

**Parameters:**
- `pool_address` (str): Pool address
- `receiver` (str): Receiver address
- `position_id` (int): Position ID
- `max_fxusd` (Union[int, float, Decimal, str]): Maximum fxUSD to use
- `max_stable` (Union[int, float, Decimal, str]): Maximum stable token to use

**Returns:** `str` - Transaction hash

#### `liquidate_position(pool_address, receiver, position_id, max_fxusd, max_stable)`

Liquidate a V2 position.

**Parameters:**
- `pool_address` (str): Pool address
- `receiver` (str): Receiver address
- `position_id` (int): Position ID
- `max_fxusd` (Union[int, float, Decimal, str]): Maximum fxUSD to use
- `max_stable` (Union[int, float, Decimal, str]): Maximum stable token to use

**Returns:** `str` - Transaction hash

#### `get_position_info(position_id)`

Get information about a V2 position.

**Parameters:**
- `position_id` (int): Position ID

**Returns:** `Dict[str, Any]` - Position information

### V2 Minting & Redeeming

#### `mint_f_token(market_address, base_in, recipient=None, min_f_token_out=0)`

Mint f-token (e.g., fxUSD) from base token.

**Parameters:**
- `market_address` (str): Market contract address
- `base_in` (Union[int, float, Decimal, str]): Amount of base token to deposit
- `recipient` (Optional[str]): Recipient address
- `min_f_token_out` (Union[int, float, Decimal, str]): Minimum f-token output (slippage protection)

**Returns:** `str` - Transaction hash

**Example:**
```python
tx_hash = client.mint_f_token(
    market_address="0x...",
    base_in=1.0,
    min_f_token_out=0.99
)
```

#### `mint_x_token(market_address, base_in, recipient=None, min_x_token_out=0)`

Mint x-token from base token.

**Parameters:**
- `market_address` (str): Market contract address
- `base_in` (Union[int, float, Decimal, str]): Amount of base token to deposit
- `recipient` (Optional[str]): Recipient address
- `min_x_token_out` (Union[int, float, Decimal, str]): Minimum x-token output

**Returns:** `str` - Transaction hash

#### `mint_both_tokens(market_address, base_in, recipient=None, min_f_token_out=0, min_x_token_out=0)`

Mint both f-token and x-token simultaneously.

**Parameters:**
- `market_address` (str): Market contract address
- `base_in` (Union[int, float, Decimal, str]): Amount of base token to deposit
- `recipient` (Optional[str]): Recipient address
- `min_f_token_out` (Union[int, float, Decimal, str]): Minimum f-token output
- `min_x_token_out` (Union[int, float, Decimal, str]): Minimum x-token output

**Returns:** `str` - Transaction hash

#### `redeem(market_address, f_token_in=0, x_token_in=0, recipient=None, min_base_out=0)`

Redeem f-token and/or x-token for base token.

**Parameters:**
- `market_address` (str): Market contract address
- `f_token_in` (Union[int, float, Decimal, str]): Amount of f-token to redeem
- `x_token_in` (Union[int, float, Decimal, str]): Amount of x-token to redeem
- `recipient` (Optional[str]): Recipient address
- `min_base_out` (Union[int, float, Decimal, str]): Minimum base token output

**Returns:** `str` - Transaction hash

### Stability Pool & Savings

#### `deposit_to_stability_pool(amount)`

Deposit to the fxUSD Stability Pool.

**Parameters:**
- `amount` (Union[int, float, Decimal, str]): Amount of fxUSD to deposit

**Returns:** `str` - Transaction hash

#### `withdraw_from_stability_pool(amount)`

Withdraw from the fxUSD Stability Pool.

**Parameters:**
- `amount` (Union[int, float, Decimal, str]): Amount to withdraw

**Returns:** `str` - Transaction hash

#### `deposit_fxsave(amount)`

Deposit to fxSAVE (Saving fxUSD).

**Parameters:**
- `amount` (Union[int, float, Decimal, str]): Amount of fxUSD to deposit

**Returns:** `str` - Transaction hash

#### `redeem_fxsave(amount)`

Redeem from fxSAVE.

**Parameters:**
- `amount` (Union[int, float, Decimal, str]): Amount to redeem

**Returns:** `str` - Transaction hash

---


## Governance Methods

### veFXN Staking

#### `deposit_to_vefxn(amount, unlock_time)`

Lock FXN to create veFXN (vote-escrowed FXN).

**Parameters:**
- `amount` (Union[int, float, Decimal, str]): Amount of FXN to lock
- `unlock_time` (int): Unix timestamp when lock expires

**Returns:** `str` - Transaction hash

**Example:**
```python
import time
# Lock for 1 year
unlock_time = int(time.time()) + (365 * 24 * 60 * 60)
tx_hash = client.deposit_to_vefxn(amount=1000, unlock_time=unlock_time)
```

#### `get_vefxn_locked_info(account_address=None)`

Get locked FXN information for an account.

**Returns:** `Dict[str, Any]` with keys:
- `amount`: Locked FXN amount
- `end`: Unlock timestamp

### Gauge Voting

#### `vote_for_gauge_weight(gauge_address, user_weight)`

Vote for a gauge's weight allocation.

**Parameters:**
- `gauge_address` (str): Gauge contract address
- `user_weight` (int): Weight to allocate (0-10000, where 10000 = 100%)

**Returns:** `str` - Transaction hash

**Example:**
```python
# Allocate 50% of voting power to a gauge
tx_hash = client.vote_for_gauge_weight(
    gauge_address="0x...",
    user_weight=5000
)
```

#### `get_gauge_weight(gauge_address)`

Get the absolute weight of a gauge.

**Returns:** `Decimal` - Gauge weight

#### `get_gauge_relative_weight(gauge_address)`

Get the relative weight of a gauge (0-1).

**Returns:** `Decimal` - Relative weight

### Gauge Rewards

#### `claim_gauge_rewards(gauge_address, account=None)`

Claim rewards from a specific gauge.

**Parameters:**
- `gauge_address` (str): Gauge contract address
- `account` (Optional[str]): Account address (defaults to client address)

**Returns:** `str` - Transaction hash

#### `claim_all_gauge_rewards()`

Claim rewards from all gauges where the user has staked.

**Returns:** `List[str]` - List of transaction hashes

**Example:**
```python
tx_hashes = client.claim_all_gauge_rewards()
print(f"Claimed from {len(tx_hashes)} gauges")
```

#### `get_claimable_rewards(gauge_address, token_address, account_address=None)`

Get claimable rewards for a specific token from a gauge.

**Parameters:**
- `gauge_address` (str): Gauge contract address
- `token_address` (str): Reward token address
- `account_address` (Optional[str]): Account address

**Returns:** `Decimal` - Claimable reward amount

#### `get_all_gauge_balances(account_address=None)`

Get all gauge staked balances for an account.

**Returns:** `Dict[str, Decimal]` - Dictionary mapping gauge addresses to staked amounts

### Vesting

#### `claim_fxn_vesting()`

Claim vested FXN tokens.

**Returns:** `str` - Transaction hash

#### `claim_feth_vesting()`

Claim vested fETH tokens.

**Returns:** `str` - Transaction hash

#### `claim_fxusd_vesting()`

Claim vested fxUSD tokens.

**Returns:** `str` - Transaction hash

---

## Convex Finance Integration

The SDK provides comprehensive integration with Convex Finance for f(x) Protocol pools. Convex vaults are user-specific contracts that allow staking LP tokens and claiming rewards.

### Vault Management

#### `create_convex_vault(pool_id)`

Create a new Convex vault for a specific pool.

**Parameters:**
- `pool_id` (int): Convex pool ID

**Returns:** `Dict[str, Any]` with keys:
- `vault_address`: Created vault address
- `tx_hash`: Transaction hash
- `pool_id`: Pool ID

**Example:**
```python
result = client.create_convex_vault(pool_id=37)
print(f"Vault created: {result['vault_address']}")
```

#### `get_convex_vault_address(wallet_address, pool_id)`

Get the vault address for a wallet and pool ID.

**Parameters:**
- `wallet_address` (str): Wallet address
- `pool_id` (int): Convex pool ID

**Returns:** `Optional[str]` - Vault address if exists, None otherwise

#### `get_convex_vault_address_or_create(pool_id)`

Get existing vault address or create a new one.

**Parameters:**
- `pool_id` (int): Convex pool ID

**Returns:** `str` - Vault address

#### `get_convex_vault_address_from_tx(tx_hash)`

Extract vault address from a createVault transaction.

**Parameters:**
- `tx_hash` (str): Transaction hash from `create_convex_vault()`

**Returns:** `Optional[str]` - Vault address if found

### Vault Operations

#### `deposit_to_convex_vault(vault_address, amount, manage=False)`

Deposit LP tokens to a Convex vault.

**Parameters:**
- `vault_address` (str): User's vault address
- `amount` (Union[int, float, Decimal, str]): Amount of LP tokens to deposit
- `manage` (bool): Whether to manage the deposit (auto-stake)

**Returns:** `str` - Transaction hash

**Example:**
```python
tx_hash = client.deposit_to_convex_vault(
    vault_address="0x...",
    amount=100.0
)
```

#### `withdraw_from_convex_vault(vault_address, amount)`

Withdraw LP tokens from a Convex vault.

**Parameters:**
- `vault_address` (str): User's vault address
- `amount` (Union[int, float, Decimal, str]): Amount to withdraw

**Returns:** `str` - Transaction hash

#### `claim_convex_vault_rewards(vault_address, claim=True, token_list=None)`

Claim rewards from a Convex vault.

**Parameters:**
- `vault_address` (str): User's vault address
- `claim` (bool): Whether to claim rewards
- `token_list` (Optional[List[str]]): Specific tokens to claim (None = all)

**Returns:** `str` - Transaction hash

### Vault Queries (Read-Only)

#### `get_convex_vault_balance(vault_address, token_address=None)`

Get staked balance in a Convex vault.

**Parameters:**
- `vault_address` (str): User's vault address
- `token_address` (Optional[str]): Token address (optional)

**Returns:** `Decimal` - Staked balance

#### `get_convex_vault_rewards(vault_address)`

Get claimable rewards for a Convex vault.

**Parameters:**
- `vault_address` (str): User's vault address

**Returns:** `Dict[str, Any]` with keys:
- `token_addresses`: List of reward token addresses
- `amounts`: Dictionary mapping token addresses to claimable amounts

**Example:**
```python
rewards = client.get_convex_vault_rewards("0x...")
for token, amount in rewards['amounts'].items():
    print(f"{token}: {amount}")
```

#### `get_convex_vault_info(vault_address)`

Get information about a Convex vault.

**Parameters:**
- `vault_address` (str): User's vault address

**Returns:** `Dict[str, Any]` with keys:
- `owner`: Vault owner address
- `pid`: Pool ID
- `staking_token`: Staking token address
- `gauge_address`: Gauge address
- `rewards`: Rewards contract address

### cvxFXN Staking

#### `deposit_fxn_to_cvxfxn(amount)`

Convert FXN to cvxFXN.

**Parameters:**
- `amount` (Union[int, float, Decimal, str]): Amount of FXN to convert

**Returns:** `str` - Transaction hash

#### `stake_cvxfxn(amount)`

Stake cvxFXN tokens for additional rewards.

**Parameters:**
- `amount` (Union[int, float, Decimal, str]): Amount of cvxFXN to stake

**Returns:** `str` - Transaction hash

#### `unstake_cvxfxn(amount)`

Unstake cvxFXN tokens.

**Parameters:**
- `amount` (Union[int, float, Decimal, str]): Amount to unstake

**Returns:** `str` - Transaction hash

#### `claim_cvxfxn_staking_rewards()`

Claim cvxFXN staking rewards.

**Returns:** `str` - Transaction hash

#### `get_cvxfxn_balance(account_address=None)`

Get cvxFXN token balance.

**Returns:** `Decimal` - cvxFXN balance

#### `get_staked_cvxfxn_balance(account_address=None)`

Get staked cvxFXN balance.

**Returns:** `Decimal` - Staked balance

#### `get_cvxfxn_staking_rewards(account_address=None)`

Get claimable cvxFXN staking rewards.

**Returns:** `Dict[str, Decimal]` - Reward token addresses to amounts

#### `get_cvxfxn_staking_info()`

Get cvxFXN staking information (reward rate, period finish, etc.).

**Returns:** `Dict[str, Any]` - Staking information

### Helper Methods

#### `get_all_user_vaults(wallet_address)`

Discover all vault addresses for a user across all pools.

**Parameters:**
- `wallet_address` (str): Wallet address

**Returns:** `List[str]` - List of vault addresses

#### `get_convex_pool_info(pool_id=None, pool_key=None)`

Get pool information by ID or key.

**Parameters:**
- `pool_id` (Optional[int]): Pool ID
- `pool_key` (Optional[str]): Pool key (e.g., "fxusd_v2_stability_fxn")

**Returns:** `Dict[str, Any]` - Pool information

#### `get_all_convex_pools()`

Get all registered Convex pools.

**Returns:** `Dict[str, Dict[str, Any]]` - Dictionary of pool keys to pool information

#### `get_vault_balances_batch(vault_addresses)`

Query multiple vault balances efficiently.

**Parameters:**
- `vault_addresses` (List[str]): List of vault addresses

**Returns:** `Dict[str, Decimal]` - Dictionary mapping vault addresses to balances

#### `get_vault_rewards_batch(vault_addresses)`

Query multiple vault rewards efficiently.

**Parameters:**
- `vault_addresses` (List[str]): List of vault addresses

**Returns:** `Dict[str, Dict[str, Any]]` - Dictionary mapping vault addresses to rewards

#### `get_user_vaults_summary(wallet_address)`

Get comprehensive overview of all user vaults.

**Parameters:**
- `wallet_address` (str): Wallet address

**Returns:** `Dict[str, Any]` - Summary with balances and rewards for all vaults

---


## Curve Finance Integration

The SDK provides comprehensive integration with Curve Finance for swapping, liquidity management, and gauge staking.

### Pool Information

#### `get_curve_pool_info(pool_address)`

Get comprehensive information about a Curve pool.

**Parameters:**
- `pool_address` (str): Curve pool address

**Returns:** `Dict[str, Any]` with keys:
- `coins`: List of coin addresses
- `balances`: List of coin balances
- `virtual_price`: Virtual price
- `lp_token`: LP token address

#### `find_curve_pool(token_a, token_b)`

Find a Curve pool by token pair.

**Parameters:**
- `token_a` (str): First token address
- `token_b` (str): Second token address

**Returns:** `Optional[str]` - Pool address if found

#### `get_curve_pool_from_lp_token(lp_token_address)`

Find a Curve pool from its LP token address.

**Parameters:**
- `lp_token_address` (str): LP token address

**Returns:** `Optional[str]` - Pool address if found

#### `get_curve_pool_balances(pool_address)`

Get current balances for all coins in a Curve pool.

**Parameters:**
- `pool_address` (str): Curve pool address

**Returns:** `List[Decimal]` - List of coin balances

#### `get_curve_pool_virtual_price(pool_address)`

Get the virtual price of a Curve pool.

**Parameters:**
- `pool_address` (str): Curve pool address

**Returns:** `Decimal` - Virtual price

#### `get_curve_swap_rate(pool_address, token_in, token_out, amount_in)`

Calculate the output amount for a swap before executing.

**Parameters:**
- `pool_address` (str): Curve pool address
- `token_in` (str): Input token address
- `token_out` (str): Output token address
- `amount_in` (Union[int, float, Decimal, str]): Input amount

**Returns:** `Decimal` - Expected output amount

### Swap Operations

#### `curve_swap(pool_address, token_in, token_out, amount_in, min_amount_out=None)`

Execute a token swap on Curve.

**Parameters:**
- `pool_address` (str): Curve pool address
- `token_in` (str): Input token address
- `token_out` (str): Output token address
- `amount_in` (Union[int, float, Decimal, str]): Input amount
- `min_amount_out` (Optional[Union[int, float, Decimal, str]]): Minimum output (slippage protection, default 0.5%)

**Returns:** `str` - Transaction hash

**Example:**
```python
tx_hash = client.curve_swap(
    pool_address="0x...",
    token_in="0x085780639CC2cACd35E474e71f4d000e2405d8f6",  # fxUSD
    token_out="0x...",  # USDC
    amount_in=1000.0,
    min_amount_out=995.0  # 0.5% slippage
)
```

### Liquidity Management

#### `curve_add_liquidity(pool_address, amounts, min_lp_tokens=None)`

Add liquidity to a Curve pool.

**Parameters:**
- `pool_address` (str): Curve pool address
- `amounts` (List[Union[int, float, Decimal, str]]): Amounts for each coin
- `min_lp_tokens` (Optional[Union[int, float, Decimal, str]]): Minimum LP tokens (slippage protection)

**Returns:** `str` - Transaction hash

**Example:**
```python
tx_hash = client.curve_add_liquidity(
    pool_address="0x...",
    amounts=[1000.0, 1000.0],  # 2-coin pool
    min_lp_tokens=1990.0
)
```

#### `curve_remove_liquidity(pool_address, lp_token_amount, min_amounts=None)`

Remove liquidity from a Curve pool.

**Parameters:**
- `pool_address` (str): Curve pool address
- `lp_token_amount` (Union[int, float, Decimal, str]): Amount of LP tokens to burn
- `min_amounts` (Optional[List[Union[int, float, Decimal, str]]]): Minimum amounts for each coin

**Returns:** `str` - Transaction hash

### Gauge Staking

#### `get_curve_gauge_info(gauge_address)`

Get information about a Curve gauge.

**Parameters:**
- `gauge_address` (str): Gauge contract address

**Returns:** `Dict[str, Any]` - Gauge information

#### `curve_stake_lp_tokens(gauge_address, lp_token_amount)`

Stake LP tokens in a Curve gauge to earn CRV rewards.

**Parameters:**
- `gauge_address` (str): Gauge contract address
- `lp_token_amount` (Union[int, float, Decimal, str]): Amount of LP tokens to stake

**Returns:** `str` - Transaction hash

#### `curve_unstake_lp_tokens(gauge_address, lp_token_amount, claim_rewards=False)`

Unstake LP tokens from a Curve gauge.

**Parameters:**
- `gauge_address` (str): Gauge contract address
- `lp_token_amount` (Union[int, float, Decimal, str]): Amount to unstake
- `claim_rewards` (bool): Whether to claim rewards when unstaking

**Returns:** `str` - Transaction hash

#### `curve_claim_gauge_rewards(gauge_address)`

Claim CRV and other rewards from a Curve gauge.

**Parameters:**
- `gauge_address` (str): Gauge contract address

**Returns:** `str` - Transaction hash

#### `get_curve_gauge_balance(gauge_address, account_address=None)`

Get staked LP token balance in a Curve gauge.

**Parameters:**
- `gauge_address` (str): Gauge contract address
- `account_address` (Optional[str]): Account address

**Returns:** `Decimal` - Staked balance

#### `get_curve_gauge_rewards(gauge_address, account_address=None)`

Get claimable rewards from a Curve gauge.

**Parameters:**
- `gauge_address` (str): Gauge contract address
- `account_address` (Optional[str]): Account address

**Returns:** `Dict[str, Decimal]` - Dictionary mapping reward token addresses to amounts

#### `get_curve_gauge_from_pool(pool_address)`

Find the gauge address for a Curve pool.

**Parameters:**
- `pool_address` (str): Curve pool address

**Returns:** `Optional[str]` - Gauge address if found

### Helper Methods

#### `get_curve_pools_from_registry()`

Get all pools from the Curve registry.

**Returns:** `List[Dict[str, Any]]` - List of pool information

#### `get_curve_pool_from_registry(pool_name)`

Get a specific pool from the registry by name.

**Parameters:**
- `pool_name` (str): Pool name

**Returns:** `Optional[Dict[str, Any]]` - Pool information if found

#### `get_curve_gauge_balances_batch(gauge_addresses, account_address=None)`

Query multiple gauge balances efficiently.

**Parameters:**
- `gauge_addresses` (List[str]): List of gauge addresses
- `account_address` (Optional[str]): Account address

**Returns:** `Dict[str, Decimal]` - Dictionary mapping gauge addresses to balances

#### `get_curve_gauge_rewards_batch(gauge_addresses, account_address=None)`

Query multiple gauge rewards efficiently.

**Parameters:**
- `gauge_addresses` (List[str]): List of gauge addresses
- `account_address` (Optional[str]): Account address

**Returns:** `Dict[str, Dict[str, Decimal]]` - Dictionary mapping gauge addresses to rewards

#### `get_user_curve_positions_summary(account_address=None)`

Get comprehensive overview of all user Curve positions.

**Parameters:**
- `account_address` (Optional[str]): Account address

**Returns:** `Dict[str, Any]` - Summary with balances and rewards for all positions

---

## Utility Methods

### Token Operations

#### `approve(token_address, spender_address, amount)`

Approve a spender to spend tokens.

**Parameters:**
- `token_address` (str): Token contract address
- `spender_address` (str): Spender address
- `amount` (Union[int, float, Decimal, str]): Approval amount

**Returns:** `str` - Transaction hash

#### `transfer(token_address, recipient_address, amount)`

Transfer tokens to another address.

**Parameters:**
- `token_address` (str): Token contract address
- `recipient_address` (str): Recipient address
- `amount` (Union[int, float, Decimal, str]): Transfer amount

**Returns:** `str` - Transaction hash

### Transaction Building

All write operations have corresponding `build_*_transaction()` methods that return unsigned transaction data instead of executing immediately. This allows for:
- Offline signing
- Gas estimation without execution
- Batch transaction building

**Example:**
```python
# Build transaction without sending
tx_data = client.build_mint_f_token_transaction(
    market_address="0x...",
    base_in=1.0
)

# Sign and broadcast separately
signed_tx = client.account.sign_transaction(tx_data)
tx_hash = client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
```

### Infrastructure Queries

#### `get_pool_manager_info(pool_address)`

Get Pool Manager information for a pool.

**Parameters:**
- `pool_address` (str): Pool address

**Returns:** `Dict[str, Any]` - Pool information

#### `get_reserve_pool_bonus_ratio(token_address)`

Get bonus ratio for a token in the Reserve Pool.

**Parameters:**
- `token_address` (str): Token address

**Returns:** `Decimal` - Bonus ratio

#### `get_steth_treasury_info()`

Get stETH Treasury information.

**Returns:** `Dict[str, Any]` - Treasury information

#### `get_treasury_nav()`

Get Net Asset Values from the treasury.

**Returns:** `Dict[str, Decimal]` with keys:
- `base_nav`: Base token NAV
- `f_nav`: F-token NAV
- `x_nav`: X-token NAV

#### `get_market_info(market_address)`

Get information for a market.

**Parameters:**
- `market_address` (str): Market contract address

**Returns:** `Dict[str, Any]` - Market information

#### `get_peg_keeper_info()`

Get Peg Keeper information.

**Returns:** `Dict[str, Any]` - Peg Keeper information

#### `get_position_info(position_id)`

Get V2 position information.

**Parameters:**
- `position_id` (int): Position ID

**Returns:** `Dict[str, Any]` - Position information

### Rebalance Pool Operations

#### `deposit_to_rebalance_pool(pool_address, amount, recipient=None)`

Deposit to a V1 rebalance pool.

**Parameters:**
- `pool_address` (str): Rebalance pool address
- `amount` (Union[int, float, Decimal, str]): Deposit amount
- `recipient` (Optional[str]): Recipient address

**Returns:** `str` - Transaction hash

#### `unlock_rebalance_pool_assets(pool_address, amount)`

Unlock assets in a rebalance pool.

**Parameters:**
- `pool_address` (str): Rebalance pool address
- `amount` (Union[int, float, Decimal, str]): Amount to unlock

**Returns:** `str` - Transaction hash

#### `withdraw_unlocked_rebalance_pool_assets(pool_address, claim_rewards=True)`

Withdraw unlocked assets from a rebalance pool.

**Parameters:**
- `pool_address` (str): Rebalance pool address
- `claim_rewards` (bool): Whether to claim rewards

**Returns:** `str` - Transaction hash

#### `claim_rebalance_pool_rewards(pool_address, tokens)`

Claim rewards from a rebalance pool.

**Parameters:**
- `pool_address` (str): Rebalance pool address
- `tokens` (List[str]): List of reward token addresses

**Returns:** `str` - Transaction hash

### Gateway Operations

#### `mint_f_token_via_gateway(amount_eth, min_f_token_out=0)`

Mint f-token via the stETH Gateway using ETH.

**Parameters:**
- `amount_eth` (Union[int, float, Decimal, str]): Amount of ETH to deposit
- `min_f_token_out` (Union[int, float, Decimal, str]): Minimum f-token output

**Returns:** `str` - Transaction hash

#### `mint_x_token_via_gateway(amount_eth, min_x_token_out=0)`

Mint x-token via the stETH Gateway using ETH.

**Parameters:**
- `amount_eth` (Union[int, float, Decimal, str]): Amount of ETH to deposit
- `min_x_token_out` (Union[int, float, Decimal, str]): Minimum x-token output

**Returns:** `str` - Transaction hash

### Flash Loans

#### `flash_loan(token_address, amount, receiver, data=b"")`

Execute a flash loan.

**Parameters:**
- `token_address` (str): Token address
- `amount` (Union[int, float, Decimal, str]): Loan amount
- `receiver` (str): Receiver contract address
- `data` (bytes): Additional data

**Returns:** `str` - Transaction hash

### Swaps

#### `swap(token_in, amount_in, encoding, routes)`

Execute a swap via the Multi-Path Converter.

**Parameters:**
- `token_in` (str): Input token address
- `amount_in` (Union[int, float, Decimal, str]): Input amount
- `encoding` (int): Encoding type
- `routes` (List[int]): Swap routes

**Returns:** `str` - Transaction hash

---

## Error Handling

The SDK uses a custom exception hierarchy for clear error reporting.

### Exception Classes

#### `FXProtocolError`

Base exception for all SDK errors.

#### `TransactionFailedError(FXProtocolError)`

Raised when a blockchain transaction fails.

#### `InsufficientBalanceError(FXProtocolError)`

Raised when the user has insufficient balance for an operation.

#### `ContractCallError(FXProtocolError)`

Raised when a read call to a contract fails.

#### `InvalidAddressError(FXProtocolError)`

Raised when an invalid Ethereum address is provided.

#### `ConfigurationError(FXProtocolError)`

Raised when the SDK is misconfigured (e.g., RPC connection failed).

### Error Handling Example

```python
from fx_sdk.exceptions import (
    FXProtocolError,
    InsufficientBalanceError,
    ContractCallError
)

try:
    tx_hash = client.mint_f_token(
        market_address="0x...",
        base_in=1000.0
    )
except InsufficientBalanceError as e:
    print(f"Insufficient balance: {e}")
except ContractCallError as e:
    print(f"Contract call failed: {e}")
except FXProtocolError as e:
    print(f"Protocol error: {e}")
```

---

## Examples

### Example 1: Check All Balances

```python
from fx_sdk.client import ProtocolClient

client = ProtocolClient(rpc_url="https://eth.llamarpc.com")

# Get all protocol token balances
balances = client.get_all_balances("0x1234...")

for token, balance in balances.items():
    if balance > 0:
        print(f"{token}: {balance}")
```

### Example 2: Mint fxUSD

```python
from fx_sdk.client import ProtocolClient

# Initialize with private key from environment
client = ProtocolClient(rpc_url="https://eth.llamarpc.com")

# Mint fxUSD from stETH
tx_hash = client.mint_f_token(
    market_address="0x...",
    base_in=1.0,  # 1 stETH
    min_f_token_out=0.99  # 1% slippage tolerance
)

print(f"Transaction: {tx_hash}")

# Wait for confirmation
receipt = client.w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Confirmed in block: {receipt['blockNumber']}")
```

### Example 3: Convex Vault Management

```python
from fx_sdk.client import ProtocolClient

client = ProtocolClient(rpc_url="https://eth.llamarpc.com")

# Get or create vault for pool 37 (fxUSD V2 Stability Pool)
vault_address = client.get_convex_vault_address_or_create(pool_id=37)

# Deposit LP tokens
tx_hash = client.deposit_to_convex_vault(
    vault_address=vault_address,
    amount=100.0
)

# Check balance
balance = client.get_convex_vault_balance(vault_address)
print(f"Staked: {balance}")

# Check rewards
rewards = client.get_convex_vault_rewards(vault_address)
for token, amount in rewards['amounts'].items():
    print(f"Reward {token}: {amount}")

# Claim rewards
if sum(rewards['amounts'].values()) > 0:
    tx_hash = client.claim_convex_vault_rewards(vault_address)
    print(f"Claimed rewards: {tx_hash}")
```

### Example 4: Curve Swap

```python
from fx_sdk.client import ProtocolClient

client = ProtocolClient(rpc_url="https://eth.llamarpc.com")

# Find pool
pool_address = client.find_curve_pool(
    token_a="0x085780639CC2cACd35E474e71f4d000e2405d8f6",  # fxUSD
    token_b="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC
)

# Calculate swap rate
amount_out = client.get_curve_swap_rate(
    pool_address=pool_address,
    token_in="0x085780639CC2cACd35E474e71f4d000e2405d8f6",
    token_out="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    amount_in=1000.0
)

print(f"Expected output: {amount_out} USDC")

# Execute swap
tx_hash = client.curve_swap(
    pool_address=pool_address,
    token_in="0x085780639CC2cACd35E474e71f4d000e2405d8f6",
    token_out="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    amount_in=1000.0,
    min_amount_out=amount_out * Decimal("0.995")  # 0.5% slippage
)

print(f"Swap transaction: {tx_hash}")
```

### Example 5: Governance Operations

```python
from fx_sdk.client import ProtocolClient
import time

client = ProtocolClient(rpc_url="https://eth.llamarpc.com")

# Lock FXN for 1 year
unlock_time = int(time.time()) + (365 * 24 * 60 * 60)
tx_hash = client.deposit_to_vefxn(
    amount=1000.0,
    unlock_time=unlock_time
)

# Vote for gauge weight
tx_hash = client.vote_for_gauge_weight(
    gauge_address="0x...",
    user_weight=5000  # 50%
)

# Claim all gauge rewards
tx_hashes = client.claim_all_gauge_rewards()
print(f"Claimed from {len(tx_hashes)} gauges")
```

### Example 6: Read-Only Analytics

```python
from fx_sdk.client import ProtocolClient

# No private key needed for read operations
client = ProtocolClient(rpc_url="https://eth.llamarpc.com")

# Get protocol metrics
nav = client.get_treasury_nav()
print(f"Base NAV: {nav['base_nav']}")
print(f"F-token NAV: {nav['f_nav']}")
print(f"X-token NAV: {nav['x_nav']}")

# Get stETH price
price = client.get_steth_price()
print(f"stETH Price: {price}")

# Get fxUSD supply
supply = client.get_fxusd_total_supply()
print(f"fxUSD Total Supply: {supply}")

# Get pool information
pool_info = client.get_pool_manager_info("0x...")
print(f"Pool Info: {pool_info}")
```

---

## Complete Method Reference

For a complete list of all 155+ public methods, see the source code or use Python's `help()` function:

```python
from fx_sdk.client import ProtocolClient

# Get help for a specific method
help(ProtocolClient.mint_f_token)

# List all methods
methods = [m for m in dir(ProtocolClient) if not m.startswith('_')]
print(f"Total methods: {len(methods)}")
```

---

## Additional Resources

- **f(x) Protocol Website**: https://fx.aladdin.club/
- **PyPI Package**: https://pypi.org/project/fx-sdk/
- **GitHub Repository**: (if public)
- **Documentation**: This file

---

## Version History

### v0.3.0 (December 22, 2025)
- Removed APY calculation methods
- Enhanced error handling
- Improved documentation

### v0.2.0 (December 22, 2025)
- Added Convex Finance integration
- Added Curve Finance integration
- Added batch operations
- Added helper methods

### v0.1.0 (December 20, 2025)
- Initial release
- Core f(x) Protocol V1 and V2 support
- Secure authentication
- High-precision Decimal handling

---

**End of Documentation**

