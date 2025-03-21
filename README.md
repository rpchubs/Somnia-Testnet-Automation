# ⚙️ Somnia Testnet Automation Scripts

Automate your journey on **Somnia Testnet** with ease! This project is a Python-based CLI toolkit that streamlines faucet claiming, token minting, swapping, contract deployment, NFT interaction, and memecoin trading. Works seamlessly across Linux/macOS and Windows!

---

## 🚀 Features

- 🔑 **Multi-Account Automation**: Load multiple private keys via `pvkey.txt`
- 🌐 **Proxy Support**: Rotate through proxies using `proxies.txt`
- 💬 **Bilingual UI**: Choose between English or Vietnamese interface
- ⚡ **Asynchronous Execution**: Efficient and non-blocking task execution
- 📜 **Comprehensive Logging**: Outputs explorer links, success, and error details

---

## 📦 Included Scripts (Pick from the menu!)

1. Faucet token $STT  
2. Mint $PONG / $PING  
3. Send TX to random or file-based addresses  
4. Deploy & Send ERC-20 Token  
5. Deploy NFT  
6. Mint CMS NFT  
7. Mint sUSDT  
8. Swap PONG <-> PING  
9. Buy/Sell Memecoins (SOMI, SMSM, SMI)

---

## 🧩 Installation Guide

### 🐧 Linux / 🍏 macOS

#### 1️⃣ Clone the repository
This downloads the automation scripts to your computer.
```bash
git clone https://github.com/rpchubs/Somnia-Testnet-Automation.git
cd Somnia-Testnet-Automation
```

#### 2️⃣ Install required dependencies
This ensures all necessary Python libraries are installed.
```bash
pip install -r requirements.txt
```

#### 3️⃣ Prepare input files
These files contain required details for execution:
```bash
nano pvkey.txt           # Add your private keys (one per line)
nano address.txt         # (Optional) Addresses for send TX
nano addressERC20.txt    # (Optional) Addresses for sending tokens
nano addressFaucet.txt   # (Optional) Addresses for faucet requests
nano proxies.txt         # (Optional) Add proxies here
nano contractERC20.txt   # (Optional) Deployed contract addresses
```

#### 4️⃣ Run the bot
Launch the automation script.
```bash
python main.py
```

### 🪟 Windows

#### 1️⃣ Install Python 3.8+
Download and install [Python 3.8+](https://www.python.org/downloads/).

#### 2️⃣ Open Command Prompt or PowerShell
Press `Win + R`, type `cmd`, and press Enter.

#### 3️⃣ Clone the repository
```cmd
git clone https://github.com/rpchubs/Somnia-Testnet-Automation.git
cd Somnia-Testnet-Automation
```

#### 4️⃣ Install dependencies
```cmd
pip install -r requirements.txt
```

#### 5️⃣ Prepare input files
Edit the necessary configuration files using Notepad.
```cmd
notepad pvkey.txt
notepad address.txt
notepad proxies.txt
```

#### 6️⃣ Run the bot
```cmd
python main.py
```

---

## ⚙️ Configuration: Threads

File: `config.json`

```json
{
  "threads": {
    "maxWorkers": 100
  }
}
```

> 🎯 **maxWorkers**: Set how many concurrent tasks (wallets) run at once. Adjust based on your system performance (recommended: 50–150).

---

## 🌍 Proxy Format Guide

In `proxies.txt`, each line must follow this format:

```
http://user:password@ip:port
```

✅ Example:
```
http://proxyuser:proxypass@123.45.67.89:8000
```

> 🧠 Proxies are optional but **highly recommended** for operations like faucet to avoid rate limits.

---

## 🙋‍♂️ Community & Support

Join the team or get help here:

- 💬 [RPC Community Chat](https://t.me/chat_RPC_Community)  
- 📣 [RPC Hubs Channel](https://t.me/RPC_Hubs)  

---

## ❤️ Made with love by the RPC Hubs Team