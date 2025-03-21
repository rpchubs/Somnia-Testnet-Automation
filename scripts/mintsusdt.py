import os
import sys
import json
import random
import asyncio
import concurrent.futures

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

NETWORK_URL = "https://dream-rpc.somnia.network"
CHAIN_ID = 50312
EXPLORER_URL = "https://shannon-explorer.somnia.network/tx/0x"
CONTRACT_ADDRESS = "0x65296738D4E5edB1515e40287B6FDf8320E6eE04" 
MINT_AMOUNT = 1000  
MINT_DATA = "0x1249c58b"  

LANG = {
    'vi': {
        'title': 'MINT sUSDT - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': 'XỬ LÝ VÍ',
        'checking_balance': 'Kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ',
        'preparing_tx': 'Chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'success': 'Mint 1000 sUSDT thành công!',
        'failure': 'Mint thất bại',
        'address': 'Địa chỉ',
        'amount': 'Số lượng',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': 'Thành công: Đã kết nối mạng Somnia Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'pvkey_error': 'Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'already_minted': 'Ví này đã mint sUSDT! Không thực hiện lại yêu cầu này.'
    },
    'en': {
        'title': 'MINT sUSDT - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'success': 'Successfully minted 1000 sUSDT!',
        'failure': 'Mint failed',
        'address': 'Address',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'pausing': 'Pausing',
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'connect_success': 'Success: Connected to Somnia Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'already_minted': 'This wallet has already minted sUSDT! Skipping this request.'
    }
}

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
        return len(key) == 66
    except ValueError:
        return False

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm private keys vào đây, mỗi key trên một dòng\n# 0x1234...\n")
            sys.exit(1)

        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append((i, key))
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}{Style.RESET_ALL}")

        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)

        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def connect_web3(language: str = 'en'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if not w3.is_connected():
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} │ Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
        return w3
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def has_minted_susdt(w3: Web3, address: str, language: str = 'en') -> bool:
    susdt_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        }
    ]
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=susdt_abi)
    try:
        balance = contract.functions.balanceOf(address).call()
        return balance > 0
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {'Không kiểm tra được số dư sUSDT' if language == 'vi' else 'Failed to check sUSDT balance'}: {str(e)}{Style.RESET_ALL}")
        return False

async def mint_susdt(w3: Web3, private_key: str, wallet_index: int, language: str = 'en'):
    from eth_account import Account
    account = Account.from_key(private_key)
    sender_address = account.address

    if has_minted_susdt(w3, sender_address, language):
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['already_minted']}{Style.RESET_ALL}")
        return False

    try:
        print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
        balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
        if balance < 0.001:
            print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance']}: {balance:.4f} STT < 0.001 STT{Style.RESET_ALL}")
            return False

        print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
        nonce = w3.eth.get_transaction_count(sender_address)
        tx_params = {
            'nonce': nonce,
            'to': Web3.to_checksum_address(CONTRACT_ADDRESS),
            'value': 0,
            'data': MINT_DATA,
            'chainId': CHAIN_ID,
            'gas': 200000,
            'gasPrice': int(w3.eth.gas_price * random.uniform(1.03, 1.1))
        }

        print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
        signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

        receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {LANG[language]['success']} │ Tx: {tx_link}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Thất bại / Failed'}: {str(e)}{Style.RESET_ALL}")
        return False

def mint_susdt_sync(w3: Web3, private_key: str, wallet_index: int, language: str) -> bool:
    return asyncio.run(mint_susdt(w3, private_key, wallet_index, language))

def run_mintsusdt(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()
    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    from concurrent.futures import ThreadPoolExecutor, as_completed
    successful_mints = 0
    total_wallets = len(private_keys)

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        for i, (line_num, privkey) in enumerate(private_keys, start=1):
            futures.append(executor.submit(mint_susdt_sync, w3, privkey, i, language))
        for future in as_completed(futures):
            if future.result():
                successful_mints += 1

    print_border(f"{LANG[language]['completed'].format(successful=successful_mints, total=total_wallets)}", Fore.GREEN)
    print()


if __name__ == "__main__":
    run_mintsusdt('vi') 
