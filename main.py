import os
import sys
import asyncio
from colorama import init, Fore, Style
import inquirer
from banner import display_banner
init(autoreset=True)

BORDER_WIDTH = 80

def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..." 
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')

async def run_faucetstt(language: str):
    from scripts.faucetstt import run_faucetstt as faucetstt_run
    faucetstt_run(language)

async def run_sendtx(language: str):
    from scripts.sendtx import run_sendtx as sendtx_run
    sendtx_run(language)

async def run_deploytoken(language: str):
    from scripts.deploytoken import run_deploytoken as deploytoken_run
    deploytoken_run(language)

async def run_sendtoken(language: str):
    from scripts.sendtoken import run_sendtoken as sendtoken_run
    sendtoken_run(language)

# async def run_deploynft(language: str):
#     from scripts.deploynft import run_deploynft as deploynft_run
#     deploynft_run(language)

async def run_mintpong(language: str):
    from scripts.mintpong import run_mintpong as mintpong_run
    mintpong_run(language)

async def run_mintping(language: str):
    from scripts.mintping import run_mintping as mintping_run
    mintping_run(language)

async def run_swappong(language: str):
    from scripts.swappong import run_swappong as swappong_run
    swappong_run(language)

async def run_swapping(language: str):
    from scripts.swapping import run_swapping as swapping_run
    swapping_run(language)

async def run_conftnft(language: str):
    from scripts.conftnft import run_conftnft as conftnft_run
    conftnft_run(language)

async def run_mintsusdt(language: str):
    from scripts.mintsusdt import run_mintsusdt as mintsusdt_run
    mintsusdt_run(language)

async def run_buymeme(language: str):
    from scripts.buymeme import run_buymeme as buymeme_run
    buymeme_run(language)

async def run_sellmeme(language: str):
    from scripts.sellmeme import run_sellmeme as sellmeme_run
    sellmeme_run(language)

async def cmd_exit(language: str):
    print_border(f"Exiting...", Fore.GREEN)
    sys.exit(0)

SCRIPT_MAP = {
    "faucetstt": run_faucetstt,
    "sendtx": run_sendtx,
    "deploytoken": run_deploytoken,
    "sendtoken": run_sendtoken,
    # "deploynft": run_deploynft,
    "mintpong": run_mintpong,
    "mintping": run_mintping,
    "swappong": run_swappong,
    "swapping": run_swapping,
    "conftnft": run_conftnft,
    "mintsusdt": run_mintsusdt,
    "buymeme": run_buymeme,
    "sellmeme": run_sellmeme,
    "exit": cmd_exit
}

def get_available_scripts(language):
    scripts = {
        'vi': [
            {"name": "1. Faucet token $STT | Somnia Testnet", "value": "faucetstt"},
            {"name": "2. Mint $PONG | Somnia Testnet", "value": "mintpong"},
            {"name": "3. Mint $PING | Somnia Testnet", "value": "mintping"},
            {"name": "4. Send TX ngẫu nhiên hoặc File (address.txt) | Somnia Testnet", "value": "sendtx"},
            {"name": "5. Deploy Token smart-contract | Somnia Testnet", "value": "deploytoken"},
            {"name": "6. Send Token ERC20 ngẫu nhiên hoặc File (addressERC20.txt) | Somnia Testnet", "value": "sendtoken"},
            # {"name": "7. Deploy NFT smart-contract | Somnia Testnet", "value": "deploynft", "separator": True},
            {"name": "7. Swap $PONG -> $PING | Somnia Testnet", "value": "swappong"},
            {"name": "8. Swap $PING -> $PONG | Somnia Testnet", "value": "swapping", "separator": True},
            {"name": "9. Mint NFT Community Member of Somnia (CMS - CoNFT) | Somnia Testnet", "value": "conftnft"},
            {"name": "10. Mint 1000 sUSDT | Somnia Testnet", "value": "mintsusdt"},
            {"name": "11. Memecoin Trading - Mua Memecoin ( SOMI / SMSM / SMI ) | Somnia Testnet", "value": "buymeme"},
            {"name": "12. Memecoin Trading - Bán Memecoin ( SOMI / SMSM / SMI ) | Somnia Testnet", "value": "sellmeme"},
            {"name": "13. Exit", "value": "exit"},
        ],
        'en': [
            {"name": "1. Faucet token $STT", "value": "faucetstt"},
            {"name": "2. Mint $PONG | Somnia Testnet", "value": "mintpong"},
            {"name": "3. Mint $PING | Somnia Testnet", "value": "mintping"},
            {"name": "4. Send Random TX or File (address.txt) | Somnia Testnet", "value": "sendtx"},
            {"name": "5. Deploy Token smart-contract | Somnia Testnet", "value": "deploytoken"},
            {"name": "6. Send Token ERC20 Random or File (addressERC20.txt) | Somnia Testnet", "value": "sendtoken"},
            {"name": "7. Swap $PONG -> $PING | Somnia Testnet", "value": "swappong"},
            {"name": "8. Swap $PING -> $PONG | Somnia Testnet", "value": "swapping", "separator": True},
            {"name": "9. Mint NFT Community Member of Somnia (CMS - CoNFT) | Somnia Testnet", "value": "conftnft"},
            {"name": "10. Mint 1000 sUSDT | Somnia Testnet", "value": "mintsusdt"},
            {"name": "11. Memecoin Trading - Buy Memecoin ( SOMI / SMSM / SMI ) | Somnia Testnet", "value": "buymeme"},
            {"name": "12. Memecoin Trading - Sell Memecoin ( SOMI / SMSM / SMI ) | Somnia Testnet", "value": "sellmeme"},
            {"name": "13. Exit", "value": "exit"},
        ]
    }
    return scripts[language]

def run_script(script_func, language):
    if asyncio.iscoroutinefunction(script_func):
        asyncio.run(script_func(language))
    else:
        script_func(language)

def select_language():
    while True:
        print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border("CHỌN NGÔN NGỮ / SELECT LANGUAGE", Fore.YELLOW)
        questions = [
            inquirer.List('language',
                          message=f"{Fore.CYAN}Vui lòng chọn / Please select:{Style.RESET_ALL}",
                          choices=[("1. Tiếng Việt", 'vi'), ("2. English", 'en')],
                          carousel=True)
        ]
        answer = inquirer.prompt(questions)
        if answer and answer['language'] in ['vi', 'en']:
            return answer['language']
        print(f"{Fore.RED}❌ {'Lựa chọn không hợp lệ / Invalid choice':^76}{Style.RESET_ALL}")

def main():
    _clear()
    display_banner()
    language = select_language()

    while True:
        _clear()
        display_banner()
        print_border("MENU CHÍNH / MAIN MENU", Fore.YELLOW)

        available_scripts = get_available_scripts(language)
        questions = [
            inquirer.List('script',
                          message=f"{Fore.CYAN}{'Chọn script để chạy / Select script to run'}{Style.RESET_ALL}",
                          choices=[script["name"] for script in available_scripts],
                          carousel=True)
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            continue

        selected_script_name = answers['script']
        selected_script_value = next(script["value"] for script in available_scripts if script["name"] == selected_script_name)

        script_func = SCRIPT_MAP.get(selected_script_value)
        if script_func is None:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(f"{'Chưa triển khai / Not implemented'}: {selected_script_name}", Fore.RED)
            input(f"{Fore.YELLOW}⏎ {'Nhấn Enter để tiếp tục... / Press Enter to continue...'}{Style.RESET_ALL:^76}")
            continue

        try:
            print(f"{Fore.CYAN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(f"ĐANG CHẠY / RUNNING: {selected_script_name}", Fore.CYAN)
            run_script(script_func, language)
            print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(f"{'Hoàn thành / Completed'} {selected_script_name}", Fore.GREEN)
            input(f"{Fore.YELLOW}⏎ {'Nhấn Enter để tiếp tục... / Press Enter to continue...'}{Style.RESET_ALL:^76}")
        except Exception as e:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(f"{'Lỗi / Error'}: {str(e)}", Fore.RED)
            input(f"{Fore.YELLOW}⏎ {'Nhấn Enter để tiếp tục... / Press Enter to continue...'}{Style.RESET_ALL:^76}")

if __name__ == "__main__":
    main()
