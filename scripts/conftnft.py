import os
import sys
import json
import random
import time
import concurrent.futures
import asyncio

from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

init(autoreset=True)

BORDER_WIDTH = 80

CONFIG_PATH = os.environ.get("CONFIG_PATH", os.path.join(os.path.dirname(__file__), "..", "config.json"))
try:
    with open(CONFIG_PATH, "r") as f:
        config_data = json.load(f)
except Exception as e:
    print(f"{Fore.RED}  ✖ Lỗi đọc config.json: {str(e)}{Style.RESET_ALL}")
    sys.exit(1)
THREADS = config_data.get("threads", {}).get("maxWorkers", 10)

# Constants
NETWORK_URL = "https://dream-rpc.somnia.network"
CHAIN_ID = 50312
EXPLORER_URL = "https://shannon-explorer.somnia.network/tx/0x"
CONFT_NFT_ADDRESS = "0xFC79f0EaC5bEcf21fDcf037bAdb977b2b43DE497"
AMOUNT = 0.1  

LANG = {
    'vi': {
        'title': 'MINT NFT CONFT - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': 'XỬ LÝ VÍ',
        'checking_balance': 'Kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ',
        'preparing_tx': 'Chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'success': 'Giao dịch thành công!',
        'failure': 'Giao dịch thất bại',
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
        'already_minted': 'Ví này đã mint! Không thực hiện lại yêu cầu này.'
    },
    'en': {
        'title': 'MINT NFT CONFT - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'success': 'Transaction successful!',
        'failure': 'Transaction failed',
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
        'already_minted': 'This wallet has already minted! Skipping this request.'
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
                f.write("# Thêm private keys vào đây, mỗi key trên một dòng\n# Ví dụ: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
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

def get_fee(w3: Web3, language: str = 'en') -> dict:
    tx_params = {}
    try:
        fee_history = w3.eth.fee_history(20, 'latest', [40])
        is_eip1559 = any(fee_history.get('baseFeePerGas', [0]))
        if not is_eip1559:
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))
            tx_params['gasPrice'] = gas_price
            print(f"{Fore.YELLOW}  ℹ {'Gas Price (Legacy)' if language == 'en' else 'Giá Gas (Cũ)'}: {w3.from_wei(gas_price, 'gwei'):.2f} Gwei{Style.RESET_ALL}")
        else:
            base_fee = fee_history.get('baseFeePerGas', [0])[-1]
            priority_fees = [fee[0] for fee in fee_history.get('reward', [[0]]) if fee[0] != 0] or [0]
            priority_fees.sort()
            median_priority_fee = priority_fees[len(priority_fees) // 2]
            priority_fee = int(median_priority_fee * random.uniform(1.03, 1.1))
            max_fee = int((base_fee + priority_fee) * random.uniform(1.03, 1.1))
            tx_params['type'] = '0x2'
            tx_params['maxFeePerGas'] = max_fee
            tx_params['maxPriorityFeePerGas'] = priority_fee
            print(f"{Fore.YELLOW}  ℹ {'Max Fee' if language == 'en' else 'Phí Tối Đa'}: {w3.from_wei(max_fee, 'gwei'):.2f} Gwei{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  ℹ {'Priority Fee' if language == 'en' else 'Phí Ưu Tiên'}: {w3.from_wei(priority_fee, 'gwei'):.2f} Gwei{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Failed to fetch fee history' if language == 'en' else 'Không lấy được lịch sử phí'}: {str(e)}{Style.RESET_ALL}")
        tx_params['gasPrice'] = int(w3.eth.gas_price * 1.1)
    return tx_params

def estimate_gas(w3: Web3, tx_params: dict, language: str = 'en') -> dict:
    try:
        gas_estimate = int(w3.eth.estimate_gas(tx_params) * random.uniform(1.03, 1.1))
        tx_params['gas'] = gas_estimate
        print(f"{Fore.YELLOW}  ℹ {'Gas Estimated' if language == 'en' else 'Gas Ước Lượng'}: {gas_estimate}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {'Failed to estimate gas, using default' if language == 'en' else 'Không ước lượng được gas, dùng mặc định'}: 200000 ({str(e)}){Style.RESET_ALL}")
        tx_params['gas'] = 200000
    return tx_params

def has_minted(w3: Web3, address: str) -> bool:
    nft_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        }
    ]
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONFT_NFT_ADDRESS), abi=nft_abi)
    try:
        balance = contract.functions.balanceOf(address).call()
        return balance > 0
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ Failed to check NFT balance: {str(e)}{Style.RESET_ALL}")
        return False

async def buy_conft_nft(w3: Web3, private_key: str, wallet_index: int, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    if has_minted(w3, sender_address):
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['already_minted']}{Style.RESET_ALL}")
        return False

    try:
        print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
        balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
        if balance < AMOUNT:
            print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance']}: {balance:.4f} STT < {AMOUNT:.4f} STT{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
        nonce = w3.eth.get_transaction_count(sender_address)
        tx_params = {
            'nonce': nonce,
            'to': Web3.to_checksum_address(CONFT_NFT_ADDRESS),
            'value': w3.to_wei(AMOUNT, 'ether'),
            'chainId': CHAIN_ID,
            'data': '0x1249c58b'
        }
        tx_params.update(get_fee(w3, language))
        tx_params = estimate_gas(w3, tx_params, language)
        
        print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
        signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
        
        loop = asyncio.get_event_loop()
        receipt = await loop.run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
        
        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {LANG[language]['success']} │ Tx: {tx_link}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['amount']}: {AMOUNT:.4f} STT{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['balance']}: {balance - AMOUNT:.4f} STT{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}  ✖ Failed: {str(e)}{Style.RESET_ALL}")
        return False

def process_one_wallet_sync(w3: Web3, language: str, wallet_index: int,
                              total_wallets: int, profile_num: int, private_key: str):
    try:
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({wallet_index}/{total_wallets})", Fore.MAGENTA)
        result = asyncio.run(buy_conft_nft(w3, private_key, wallet_index, language))
        if wallet_index < total_wallets:
            delay = random.uniform(10, 30)
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} seconds{Style.RESET_ALL}")
            time.sleep(delay)
        print_separator()
        return result
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        print_separator()
        return False

def run_conftnft(language: str = 'en'):
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
    total_txs = len(private_keys)
    random.shuffle(private_keys)
    successful_txs = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        for idx, (profile_num, pkey) in enumerate(private_keys, start=1):
            futures.append(
                executor.submit(
                    process_one_wallet_sync,
                    w3, language, idx, total_txs, profile_num, pkey
                )
            )
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                successful_txs += 1

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_txs, total=total_txs)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    run_conftnft('vi')
