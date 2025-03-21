import os
import sys
import json
import random
import asyncio
import concurrent.futures
from typing import List

from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

init(autoreset=True)

CONFIG_PATH = os.environ.get("CONFIG_PATH", os.path.join(os.path.dirname(__file__), "..", "config.json"))
try:
    with open(CONFIG_PATH, "r") as f:
        config_data = json.load(f)
except Exception as e:
    print(f"{Fore.RED}  ✖ Lỗi đọc config.json: {str(e)}{Style.RESET_ALL}")
    sys.exit(1)

THREADS = config_data.get("threads", {}).get("maxWorkers", 10)

BORDER_WIDTH = 80
SOMNIA_TESTNET_RPC_URL = 'https://dream-rpc.somnia.network'
SOMNIA_TESTNET_EXPLORER_URL = 'https://shannon-explorer.somnia.network'
SHUFFLE_WALLETS = True
SWAP_PONGPING_SLEEP_RANGE = [100, 300] 

TOKEN_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return (len(key) == 66)
    except ValueError:
        return False

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            msg = "Lỗi: File pvkey.txt không tồn tại" if language=='vi' else "Error: pvkey.txt file not found"
            print(f"{Fore.RED}  ✖ {msg}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add private keys here...\n")
            sys.exit(1)

        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append(key)
                    else:
                        warn = "Cảnh báo" if language=='vi' else "Warning"
                        skip = "không hợp lệ, bỏ qua" if language=='vi' else "is invalid, skipped"
                        print(f"{Fore.YELLOW}  ⚠ {warn}: line {i} {skip}: {key}{Style.RESET_ALL}")

        if not valid_keys:
            err = "Lỗi: Không tìm thấy private key hợp lệ" if language=='vi' else "Error: No valid private keys found"
            print(f"{Fore.RED}  ✖ {err}{Style.RESET_ALL}")
            sys.exit(1)

        return valid_keys
    except Exception as e:
        err = "Lỗi: Đọc pvkey.txt thất bại" if language=='vi' else "Error: Failed to read pvkey.txt"
        print(f"{Fore.RED}  ✖ {err}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def shuffle_wallets(keys: List[str]) -> List[str]:
    return random.sample(keys, len(keys))

def get_random_int(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)

def connect_web3(language: str = 'en'):
    try:
        w3 = Web3(Web3.HTTPProvider(SOMNIA_TESTNET_RPC_URL))
        if not w3.is_connected():
            msg = "Lỗi: Không thể kết nối RPC" if language=='vi' else "Error: Failed to connect to RPC"
            print(f"{Fore.RED}  ✖ {msg}{Style.RESET_ALL}")
            sys.exit(1)
        success = "Thành công: Đã kết nối mạng Somnia Testnet" if language=='vi' else "Success: Connected to Somnia Testnet"
        print(f"{Fore.GREEN}  ✔ {success} │ Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
        return w3
    except Exception as e:
        err = "Lỗi: Kết nối Web3 thất bại" if language=='vi' else "Error: Web3 connection failed"
        print(f"{Fore.RED}  ✖ {err}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def get_swap_amount(language: str = 'en') -> float:
    title_vi = "NHẬP SỐ LƯỢNG $PONG"
    title_en = "ENTER $PONG AMOUNT"
    print_border(title_vi if language=='vi' else title_en)

    while True:
        prompt_vi = "Số lượng $PONG muốn swap (vd: 100)"
        prompt_en = "Amount of $PONG to swap (e.g., 100)"
        input_txt = input(f"{Fore.YELLOW}  > {prompt_vi if language=='vi' else prompt_en}: {Style.RESET_ALL}")
        try:
            amount = float(input_txt)
            if amount <= 0:
                err = "Lỗi: Số lượng phải lớn hơn 0" if language=='vi' else "Error: Amount must be > 0"
                print(f"{Fore.RED}  ✖ {err}{Style.RESET_ALL}")
            else:
                sel = "Đã chọn" if language=='vi' else "Selected"
                print(f"{Fore.GREEN}  ✔ {sel}: {amount} $PONG{Style.RESET_ALL}")
                return amount
        except ValueError:
            err = "Lỗi: Vui lòng nhập số hợp lệ" if language=='vi' else "Error: Please enter a valid number"
            print(f"{Fore.RED}  ✖ {err}{Style.RESET_ALL}")

def get_swap_times(language: str = 'en') -> int:
    print_border("NHẬP SỐ LẦN SWAP" if language=='vi' else "ENTER NUMBER OF SWAPS")

    while True:
        prompt_vi = "Số lần swap cho mỗi ví (ví dụ: 1)"
        prompt_en = "Number of swaps per wallet (e.g., 1)"
        input_txt = input(f"{Fore.YELLOW}  > {prompt_vi if language=='vi' else prompt_en}: {Style.RESET_ALL}")
        try:
            times = int(input_txt)
            if times <= 0:
                err = "Lỗi: Số lần phải lớn hơn 0" if language=='vi' else "Error: # of swaps must be > 0"
                print(f"{Fore.RED}  ✖ {err}{Style.RESET_ALL}")
            else:
                sel = "Đã chọn" if language=='vi' else "Selected"
                print(f"{Fore.GREEN}  ✔ {sel}: {times}{Style.RESET_ALL}")
                return times
        except ValueError:
            err = "Lỗi: Số nguyên không hợp lệ" if language=='vi' else "Error: Must be a valid integer"
            print(f"{Fore.RED}  ✖ {err}{Style.RESET_ALL}")


async def approve_token(web3: Web3, private_key: str, token_address: str, spender_address: str,
                       amount: float, wallet_index: int, language: str='en') -> bool:
    from eth_account import Account
    try:
        account = Account.from_key(private_key)
        contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=TOKEN_ABI)
        decimals = contract.functions.decimals().call()
        amount_wei = int(amount * 10**decimals)

        tx = contract.functions.approve(
            Web3.to_checksum_address(spender_address),
            amount_wei
        ).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': web3.eth.gas_price
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ Ví {wallet_index} Approve {amount} $PONG: {SOMNIA_TESTNET_EXPLORER_URL}/tx/0x{tx_hash.hex()}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ Ví {wallet_index}: Approve thất bại{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}  ✖ Ví {wallet_index}: Approve error: {e}{Style.RESET_ALL}")
        return False

async def swap_token(web3: Web3, private_key: str, token_in: str, token_out: str,
                     amount_in: float, recipient: str, wallet_index: int, language: str='en') -> bool:
    from eth_account import Account
    try:
        account = Account.from_key(private_key)
        swap_router_address = "0x6aac14f090a35eea150705f72d90e4cdc4a49b2c"
        fee = 500
        amount_out_min = int(amount_in * 0.97 * 10**18) 
        amount_in_wei = int(amount_in * 10**18)

        SWAP_ROUTER_ABI = [
            {
                "inputs": [
                    {
                        "components": [
                            {"name": "tokenIn", "type": "address"},
                            {"name": "tokenOut", "type": "address"},
                            {"name": "fee", "type": "uint24"},
                            {"name": "recipient", "type": "address"},
                            {"name": "amountIn", "type": "uint256"},
                            {"name": "amountOutMinimum", "type": "uint256"},
                            {"name": "sqrtPriceLimitX96", "type": "uint160"}
                        ],
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "exactInputSingle",
                "outputs": [{"name": "amountOut", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        swap_router = web3.eth.contract(address=Web3.to_checksum_address(swap_router_address), abi=SWAP_ROUTER_ABI)

        tx_data = swap_router.functions.exactInputSingle(
            (
                Web3.to_checksum_address(token_in),
                Web3.to_checksum_address(token_out),
                fee,
                recipient,
                amount_in_wei,
                amount_out_min,
                0
            )
        ).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 300000,
            'gasPrice': web3.eth.gas_price,
            'chainId': web3.eth.chain_id
        })
        signed_tx = web3.eth.account.sign_transaction(tx_data, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ Ví {wallet_index} Swap {amount_in} $PONG -> $PING: {SOMNIA_TESTNET_EXPLORER_URL}/tx/0x{tx_hash.hex()}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ Ví {wallet_index}: Swap thất bại{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}  ✖ Ví {wallet_index}: Swap error: {e}{Style.RESET_ALL}")
        return False

async def process_one_wallet(web3: Web3, private_key: str, wallet_index: int,
                             amount: float, swap_times: int, language: str='en') -> int:
    token_in = "0x7968ac15a72629e05f41b8271e4e7292e0cc9f90"  # $PONG
    token_out = "0xbecd9b5f373877881d91cbdbaf013d97eb532154"  # $PING
    spender = "0x6aac14f090a35eea150705f72d90e4cdc4a49b2c"
    account = Account.from_key(private_key)
    recipient = account.address

    success_count = 0
    total_approve = amount * swap_times
    if not await approve_token(web3, private_key, token_in, spender, total_approve, wallet_index, language):
        return 0

    for i in range(1, swap_times+1):
        print(f"{Fore.CYAN}  > Swap {i}/{swap_times}{Style.RESET_ALL}")
        if await swap_token(web3, private_key, token_in, token_out, amount, recipient, wallet_index, language):
            success_count += 1
        print()
    return success_count


def process_one_wallet_sync(web3: Web3, private_key: str, wallet_index: int, amount: float,
                            swap_times: int, language: str) -> int:
    return asyncio.run(process_one_wallet(web3, private_key, wallet_index, amount, swap_times, language))


def run_swappong(language: str = 'en'):
    print()
    print_border("BẮT ĐẦU SWAP $PONG -> $PING" if language=='vi' else "START SWAPPING $PONG -> $PING")
    print()

    private_keys = load_private_keys(language=language)
    if SHUFFLE_WALLETS:
        private_keys = shuffle_wallets(private_keys)
    print(f"{Fore.YELLOW}  ℹ {'Tìm thấy' if language=='vi' else 'Found'} {len(private_keys)} {'ví' if language=='vi' else 'wallets'}{Style.RESET_ALL}")
    print()
    if not private_keys:
        print(f"{Fore.RED}  ✖ {'Không có ví nào để swap' if language=='vi' else 'No wallets to swap'}{Style.RESET_ALL}")
        return

    amount = get_swap_amount(language)
    swap_times = get_swap_times(language)
    print_separator()

    w3 = connect_web3(language)
    print()

    from concurrent.futures import ThreadPoolExecutor, as_completed
    successful_swaps = 0
    total_swaps = len(private_keys)*swap_times

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        for idx, pk in enumerate(private_keys, 1):
            futures.append(executor.submit(process_one_wallet_sync, w3, pk, idx, amount, swap_times, language))
        for f in as_completed(futures):
            successful_swaps += f.result()

    print()
    completed_msg = f"HOÀN THÀNH: {successful_swaps}/{total_swaps} LẦN SWAP THÀNH CÔNG" if language=='vi' \
                    else f"COMPLETED: {successful_swaps}/{total_swaps} SWAPS SUCCESSFUL"
    print_border(completed_msg, Fore.GREEN)
    print()


if __name__ == "__main__":
    run_swappong('en')
