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

DEV_WALLETS = [
    "0xDA1feA7873338F34C6915A44028aA4D9aBA1346B",
    "0x018604C67a7423c03dE3057a49709aaD1D178B85",
    "0xcF8D30A5Ee0D9d5ad1D7087822bA5Bab1081FdB7",
    "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5"
]

LANG = {
    'vi': {
        'title': 'SEND TX - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'enter_tx_count': 'NHẬP SỐ LƯỢNG GIAO DỊCH',
        'tx_count_prompt': 'Số giao dịch (mặc định 1)',
        'selected': 'Đã chọn',
        'transactions': 'giao dịch',
        'enter_amount': 'NHẬP SỐ LƯỢNG STT',
        'amount_prompt': 'Số lượng STT (mặc định 0.000001, tối đa 999)',
        'amount_unit': 'STT',
        'select_tx_type': 'CHỌN LOẠI GIAO DỊCH',
        'random_option': 'Gửi đến địa chỉ ngẫu nhiên của DEV SOMNIA',
        'file_option': 'Gửi đến địa chỉ từ file (address.txt)',
        'choice_prompt': 'Nhập lựa chọn (1/2)',
        'start_random': 'BẮT ĐẦU GỬI {tx_count} GIAO DỊCH NGẪU NHIÊN',
        'start_file': 'BẮT ĐẦU GỬI GIAO DỊCH ĐẾN {addr_count} ĐỊA CHỈ TỪ FILE',
        'processing_wallet': 'XỬ LÝ VÍ',
        'transaction': 'Giao dịch',
        'to_address': 'Giao dịch đến địa chỉ',
        'sending': 'Đang gửi giao dịch...',
        'success': 'Giao dịch thành công!',
        'failure': 'Giao dịch thất bại',
        'sender': 'Người gửi',
        'receiver': 'Người nhận',
        'amount': 'Số lượng',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': 'HOÀN THÀNH',
        'tx_successful': 'GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ',
        'tx_count_error': 'Số giao dịch phải lớn hơn 0',
        'amount_error': 'Số lượng phải lớn hơn 0 và không quá 999',
        'invalid_choice': 'Lựa chọn không hợp lệ',
        'connect_success': 'Thành công: Đã kết nối mạng Somnia Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'pvkey_error': 'Đọc pvkey.txt thất bại',
        'addr_not_found': 'File address.txt không tồn tại',
        'addr_empty': 'Không tìm thấy địa chỉ hợp lệ trong address.txt',
        'addr_error': 'Đọc address.txt thất bại',
        'invalid_addr': 'không phải địa chỉ hợp lệ, bỏ qua',
        'warning_line': 'Cảnh báo: Dòng'
    },
    'en': {
        'title': 'SEND TX - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'enter_tx_count': 'ENTER NUMBER OF TRANSACTIONS',
        'tx_count_prompt': 'Number of transactions (default 1)',
        'selected': 'Selected',
        'transactions': 'transactions',
        'enter_amount': 'ENTER AMOUNT OF STT',
        'amount_prompt': 'Amount of STT (default 0.000001, max 999)',
        'amount_unit': 'STT',
        'select_tx_type': 'SELECT TRANSACTION TYPE',
        'random_option': 'Send to random SOMNIA DEV address',
        'file_option': 'Send to addresses from file (address.txt)',
        'choice_prompt': 'Enter choice (1/2)',
        'start_random': 'STARTING {tx_count} RANDOM TRANSACTIONS',
        'start_file': 'STARTING TRANSACTIONS TO {addr_count} ADDRESSES FROM FILE',
        'processing_wallet': 'PROCESSING WALLET',
        'transaction': 'Transaction',
        'to_address': 'Transaction to address',
        'sending': 'Sending transaction...',
        'success': 'Transaction successful!',
        'failure': 'Transaction failed',
        'sender': 'Sender',
        'receiver': 'Receiver',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': 'COMPLETED',
        'tx_successful': 'TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'invalid_number': 'Please enter a valid number',
        'tx_count_error': 'Number of transactions must be greater than 0',
        'amount_error': 'Amount must be greater than 0 and not exceed 999',
        'invalid_choice': 'Invalid choice',
        'connect_success': 'Success: Connected to Somnia Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'addr_not_found': 'address.txt file not found',
        'addr_empty': 'No valid addresses found in address.txt',
        'addr_error': 'Failed to read address.txt',
        'invalid_addr': 'is not a valid address, skipped',
        'warning_line': 'Warning: Line'
    }
}

def print_border(text: str, color=Fore.CYAN, width=80):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")
    print()

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * 80}{Style.RESET_ALL}")

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
                f.write("# Thêm private keys vào đây...\n")
            sys.exit(1)
        valid = []
        with open(file_path, 'r') as f:
            for line in f:
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid.append(key)
        if not valid:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        return valid
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def load_addresses(file_path: str = "address.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['addr_not_found']}{Style.RESET_ALL}")
            return None
        addresses = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                addr = line.strip()
                if addr:
                    try:
                        addresses.append(Web3.to_checksum_address(addr))
                    except:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_addr']}: {addr}{Style.RESET_ALL}")
        if not addresses:
            print(f"{Fore.RED}  ✖ {LANG[language]['addr_empty']}{Style.RESET_ALL}")
            return None
        return addresses
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['addr_error']}: {str(e)}{Style.RESET_ALL}")
        return None

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

async def send_transaction(w3: Web3, private_key: str, to_address: str, amount: float, language: str = 'en'):
    from eth_account import Account
    account = Account.from_key(private_key)
    sender_address = account.address
    try:
        nonce = w3.eth.get_transaction_count(sender_address)
        latest_block = w3.eth.get_block('latest')
        base_fee_per_gas = latest_block.get('baseFeePerGas', w3.to_wei(2, 'gwei'))
        max_priority_fee_per_gas = w3.to_wei(2, 'gwei')
        max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

        tx = {
            'nonce': nonce,
            'to': w3.to_checksum_address(to_address),
            'value': w3.to_wei(amount, 'ether'),
            'gas': 21000,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'chainId': CHAIN_ID
        }

        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
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
        print(f"{Fore.RED}  ✖ Failed: {str(e)}{Style.RESET_ALL}")
        return False

def send_transaction_sync(w3: Web3, private_key: str, to_address: str, amount: float, language: str) -> bool:
    return asyncio.run(send_transaction(w3, private_key, to_address, amount, language))

def get_tx_count(language: str = 'en') -> int:
    print_border(LANG[language]['enter_tx_count'], Fore.YELLOW)
    while True:
        tx_count_input = input(f"{Fore.YELLOW}  > {LANG[language]['tx_count_prompt']}: {Style.RESET_ALL}")
        if tx_count_input.strip() == '':
            tx_count_input = '1'
        try:
            tx_count = int(tx_count_input)
            if tx_count <= 0:
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['tx_count_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['selected']}: {tx_count} {LANG[language]['transactions']}{Style.RESET_ALL}")
                return tx_count
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

def get_amount(language: str = 'en') -> float:
    print_border(LANG[language]['enter_amount'], Fore.YELLOW)
    while True:
        amount_input = input(f"{Fore.YELLOW}  > {LANG[language]['amount_prompt']}: {Style.RESET_ALL}")
        if amount_input.strip() == '':
            amount_input = '0.000001'
        try:
            amount = float(amount_input)
            if 0 < amount <= 999:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['selected']}: {amount} {LANG[language]['amount_unit']}{Style.RESET_ALL}")
                return amount
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['amount_error']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

def send_random_tx(w3: Web3, private_key: str, wallet_index: int, tx_count: int, amount: float, language: str) -> int:
    success = 0
    for tx_idx in range(1, tx_count + 1):
        to_addr = random.choice(DEV_WALLETS)
        if send_transaction_sync(w3, private_key, to_addr, amount, language):
            success += 1
    return success

def send_file_tx(w3: Web3, private_key: str, wallet_index: int, addresses: list, amount: float, language: str) -> int:
    success = 0
    for i, addr in enumerate(addresses, 1):
        if send_transaction_sync(w3, private_key, addr, amount, language):
            success += 1
    return success

def run_sendtx(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys(language=language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()
    if not private_keys:
        return

    tx_count = get_tx_count(language)
    amount = get_amount(language)
    print_separator()

    w3 = connect_web3(language)
    print()

    while True:
        print_border(LANG[language]['select_tx_type'], Fore.YELLOW)
        print(f"{Fore.CYAN}  1. {LANG[language]['random_option']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  2. {LANG[language]['file_option']}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}  > {LANG[language]['choice_prompt']}: {Style.RESET_ALL}")

        from concurrent.futures import ThreadPoolExecutor, as_completed
        total_txs = 0
        successful = 0

        if choice == '1':
            print_border(LANG[language]['start_random'].format(tx_count=tx_count), Fore.CYAN)
            print()
            total_txs = tx_count * len(private_keys)
            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                futures = []
                for idx, pk in enumerate(private_keys, 1):
                    futures.append(executor.submit(send_random_tx, w3, pk, idx, tx_count, amount, language))
                for f in as_completed(futures):
                    successful += f.result()
            break

        elif choice == '2':
            from typing import cast
            addresses = load_addresses('address.txt', language)
            if not addresses:
                return
            print_border(LANG[language]['start_file'].format(addr_count=len(addresses)), Fore.CYAN)
            print()
            total_txs = len(private_keys) * len(addresses)
            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                futures = []
                for idx, pk in enumerate(private_keys, 1):
                    futures.append(executor.submit(send_file_tx, w3, pk, idx, addresses, amount, language))
                for f in as_completed(futures):
                    successful += f.result()
            break

        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
            continue

    print()
    print_border(f"{LANG[language]['completed']}: {successful}/{total_txs} {LANG[language]['tx_successful']}", Fore.GREEN)
    print()


if __name__ == "__main__":
    run_sendtx('vi')
