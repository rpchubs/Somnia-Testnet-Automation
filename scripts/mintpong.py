import os
import sys
import json
import random
import asyncio
from typing import List
from web3 import Web3
from colorama import init, Fore, Style
import concurrent.futures

init(autoreset=True)

BORDER_WIDTH = 80

CONFIG_PATH = os.environ.get("CONFIG_PATH", os.path.join(os.path.dirname(__file__), "..", "config.json"))
try:
    with open(CONFIG_PATH, "r") as f:
        config_data = json.load(f)
except Exception as e:
    print(f"{Fore.RED}  ✖ Error reading config.json: {str(e)}{Style.RESET_ALL}")
    sys.exit(1)

THREADS = config_data.get("threads", {}).get("maxWorkers", 10)

SOMNIA_TESTNET_RPC_URL = 'https://dream-rpc.somnia.network'
SOMNIA_TESTNET_EXPLORER_URL = 'https://shannon-explorer.somnia.network'
SHUFFLE_WALLETS = True
MINT_PONGPING_SLEEP_RANGE = [100, 300] 


def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"\n{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}\n")


def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False


def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ File pvkey.txt does not exist{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add private keys here\n")
            sys.exit(1)

        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#') and is_valid_private_key(key):
                    if not key.startswith('0x'):
                        key = '0x' + key
                    valid_keys.append(key)
        if not valid_keys:
            print(f"{Fore.RED}  ✖ No valid private key found{Style.RESET_ALL}")
            sys.exit(1)

        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ Failed to read pvkey.txt: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


def shuffle_wallets(keys: List[str]) -> List[str]:
    return random.sample(keys, len(keys))


def connect_web3(language: str):
    try:
        web3 = Web3(Web3.HTTPProvider(SOMNIA_TESTNET_RPC_URL))
        if not web3.is_connected():
            print(f"{Fore.RED}  ✖ Unable to connect to RPC{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}  ✔ Connected to Somnia Testnet │ Chain ID: {web3.eth.chain_id}{Style.RESET_ALL}")
        return web3
    except Exception as e:
        print(f"{Fore.RED}  ✖ Web3 connection failed: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


def bytecode_mint_pongping(address: str) -> str:
    address_clean = address.replace("0x", "").lower()
    return f"0x40c10f19000000000000000000000000{address_clean}00000000000000000000000000000000000000000000003635c9adc5dea00000"


def mint_worker(index: int, private_key: str, language: str) -> bool:
    try:
        web3 = connect_web3(language)
        account = web3.eth.account.from_key(private_key)
        address = account.address
        contract_address = "0x7968ac15a72629e05f41b8271e4e7292e0cc9f90"

        balance = web3.eth.get_balance(address)
        if balance < web3.to_wei(0.001, 'ether'):
            print(f"{Fore.YELLOW}  ⚠ Wallet {index}: Insufficient STT balance │ {address}{Style.RESET_ALL}")
            return False

        nonce = web3.eth.get_transaction_count(address)
        gas_price = web3.eth.gas_price
        tx = {
            'to': Web3.to_checksum_address(contract_address),
            'value': 0,
            'data': bytecode_mint_pongping(address),
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': gas_price,
            'chainId': web3.eth.chain_id
        }

        try:
            gas_estimate = web3.eth.estimate_gas(tx)
            tx['gas'] = gas_estimate + 10000
        except:
            pass

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"{Fore.GREEN}  ✔ Wallet {index}: Tx sent - {SOMNIA_TESTNET_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ Wallet {index}: Successfully minted $PONG{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ Wallet {index}: Mint failed{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}  ✖ Wallet {index}: Error: {str(e)}{Style.RESET_ALL}")
        return False


def run_mintpong(language: str = 'en'):
    print_border("START MINTING $PONG", Fore.CYAN)

    private_keys = load_private_keys(language=language)
    if SHUFFLE_WALLETS:
        private_keys = shuffle_wallets(private_keys)

    print(f"{Fore.YELLOW}  ℹ Found {len(private_keys)} wallet(s){Style.RESET_ALL}")

    successful = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        for i, key in enumerate(private_keys, start=1):
            futures.append(executor.submit(mint_worker, i, key, language))
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                successful += 1

    print_border(f"COMPLETED: {successful}/{len(private_keys)} wallet(s) succeeded", Fore.GREEN)


if __name__ == "__main__":
    run_mintpong("en")
