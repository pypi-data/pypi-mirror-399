#!/usr/bin/env python3
import asyncio
import json
import os
import sys
import time
import getpass
import random
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

def get_data_dir(appname="coincity"):
    if sys.platform.startswith("win"):
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or Path.home() / "AppData" / "Local"
        return Path(base) / appname
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / appname
    return Path(os.getenv("XDG_DATA_HOME") or Path.home() / ".local" / "share") / appname

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = get_data_dir("coincity")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONF_FILE = DATA_DIR / "config.json"
LOG_FILE = DATA_DIR / "client.log"
DEFAULT_HOST = "92.118.206.166"
DEFAULT_PORT = 30515
NETWORK_TIMEOUT = 6.0
RETRY_LIMIT = 5
RETRY_BASE_DELAY = 0.4
SPINNER_CHARS = ["|", "/", "-", "\\"]
BUILDINGS = ["House", "Bank", "Tower", "Market", "Library", "Barracks", "Fortress"]
MAX_SPIN_BUY = 10

logger = logging.getLogger("coincity_client")
logger.setLevel(logging.DEBUG)
rhandler = logging.handlers.RotatingFileHandler(str(LOG_FILE), maxBytes=5_000_000, backupCount=3, encoding="utf-8")
shandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
rhandler.setFormatter(formatter)
shandler.setFormatter(formatter)
logger.addHandler(rhandler)
logger.addHandler(shandler)

class Config:
    def __init__(self, path: Path):
        self.path = path
        self.data = {}
        self.load()
    def load(self):
        try:
            if self.path.exists():
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            else:
                self.data = {}
        except Exception:
            self.data = {}
    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass
    def get(self, key, default=None):
        return self.data.get(key, default)
    def set(self, key, value):
        self.data[key] = value
        self.save()
    def pop(self, key):
        if key in self.data:
            self.data.pop(key)
            self.save()

class Screen:
    ESC = "\033["
    BOLD = ESC + "1m"
    RESET = ESC + "0m"
    RED = ESC + "31m"
    GREEN = ESC + "32m"
    YELLOW = ESC + "33m"
    BLUE = ESC + "34m"
    MAGENTA = ESC + "35m"
    CYAN = ESC + "36m"
    WHITE = ESC + "37m"
    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")
    @staticmethod
    def banner(title: str):
        try:
            width = os.get_terminal_size().columns
        except Exception:
            width = 80
        w = max(40, width, len(title) + 10)
        line = "=" * w
        print(Screen.CYAN + line + Screen.RESET)
        print(Screen.MAGENTA + title.center(w) + Screen.RESET)
        print(Screen.CYAN + line + Screen.RESET)
    @staticmethod
    def status(user: Optional[str]):
        u = user or "Not logged in"
        print(Screen.BOLD + Screen.MAGENTA + f"User: {u}" + Screen.RESET)
    @staticmethod
    def coins(n: int):
        try:
            return f"{int(n):,}".replace(",", ".") + "¢"
        except Exception:
            return str(n)
    @staticmethod
    def pause(prompt="Press Enter to continue..."):
        try:
            input(prompt)
        except Exception:
            pass

class Spinner:
    def __init__(self, label: str = ""):
        self.label = label
        self._running = False
        self._task = None
    async def _spin(self):
        i = 0
        while self._running:
            sys.stdout.write("\r" + self.label + " " + SPINNER_CHARS[i % len(SPINNER_CHARS)])
            sys.stdout.flush()
            i += 1
            await asyncio.sleep(0.08)
        sys.stdout.write("\r" + " " * (len(self.label) + 4) + "\r")
        sys.stdout.flush()
    async def __aenter__(self):
        self._running = True
        self._task = asyncio.create_task(self._spin())
        return self
    async def __aexit__(self, exc_type, exc, tb):
        self._running = False
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=1.0)
            except Exception:
                pass

class Network:
    def __init__(self, host: str, port: int, timeout=NETWORK_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._lock = asyncio.Lock()
        self._seq = 0
    async def _open(self):
        last_exc = None
        for attempt in range(1, RETRY_LIMIT + 1):
            try:
                reader, writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), timeout=self.timeout)
                return reader, writer
            except Exception as e:
                last_exc = e
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1)) + random.random() * 0.1
                await asyncio.sleep(delay)
        raise ConnectionError("Unable to connect") from last_exc
    async def request(self, payload: Dict[str, Any], timeout: float = NETWORK_TIMEOUT) -> Dict[str, Any]:
        async with self._lock:
            self._seq += 1
            payload = dict(payload)
            payload["_seq"] = self._seq
            reader = None
            writer = None
            try:
                reader, writer = await self._open()
                data = (json.dumps(payload) + "\n").encode("utf-8")
                writer.write(data)
                await asyncio.wait_for(writer.drain(), timeout=timeout)
                line = await asyncio.wait_for(reader.readline(), timeout=timeout)
                if not line:
                    raise ConnectionError("No response")
                resp = json.loads(line.decode("utf-8").strip())
                return resp
            finally:
                try:
                    if writer:
                        writer.close()
                        await writer.wait_closed()
                except Exception:
                    pass

class Input:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
    async def ainput(self, prompt: str = ""):
        return await self.loop.run_in_executor(None, lambda: input(prompt))
    async def agetpass(self, prompt: str = ""):
        return await self.loop.run_in_executor(None, lambda: getpass.getpass(prompt))

class Client:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.net = Network(DEFAULT_HOST, DEFAULT_PORT)
        self.input = Input()
        self.username = cfg.get("username")
        self.token = cfg.get("token")
        self.last_info = None
    def _save_auth(self, username: str, token: str):
        self.username = username
        self.token = token
        self.cfg.set("username", username)
        self.cfg.set("token", token)
    def _clear_auth(self):
        self.username = None
        self.token = None
        self.cfg.pop("username")
        self.cfg.pop("token")
    async def check_server(self):
        try:
            await self.net.request({"cmd": "ping"})
            return True
        except Exception:
            return False
    async def register(self):
        Screen.clear()
        Screen.banner("REGISTER")
        ok = await self.check_server()
        if not ok:
            print(Screen.RED + "Server unreachable" + Screen.RESET)
            await asyncio.sleep(0.6)
            return
        print("When you create an account, the following happens:")
        print("- Your username and password are securely stored on the server (hashed).")
        print("- Your IP may be recorded to prevent abuse.")
        print("- A player profile is created with coins, spins, shields, and buildings.")
        print("- By registering you agree to the game rules.")
        print()
        while True:
            uname = (await self.input.ainput("Choose username (or 'cancel'): ")).strip()
            if not uname or uname.lower() == "cancel":
                return
            passwd = await self.input.agetpass("Password (min 8): ")
            confirm = await self.input.agetpass("Repeat password: ")
            if passwd != confirm:
                print(Screen.RED + "Passwords do not match" + Screen.RESET)
                continue
            if len(passwd) < 8:
                print(Screen.YELLOW + "Password too short, min 8 chars" + Screen.RESET)
                continue
            async with Spinner("Registering"):
                try:
                    resp = await self.net.request({"cmd": "register", "username": uname, "password": passwd})
                except Exception as e:
                    print(Screen.RED + "Register error: " + str(e) + Screen.RESET)
                    return
            if not resp.get("ok"):
                err = resp.get("error")
                print(Screen.RED + f"Register failed: {err}" + Screen.RESET)
                retry = (await self.input.ainput("Try again? (y/n): ")).strip().lower()
                if retry != "y":
                    return
                continue
            async with Spinner("Logging in"):
                try:
                    login_r = await self.net.request({"cmd": "login", "username": uname, "password": passwd})
                except Exception:
                    print(Screen.YELLOW + "Auto-login failed" + Screen.RESET)
                    return
            if login_r.get("ok") and login_r.get("token"):
                self._save_auth(uname, login_r.get("token"))
                print(Screen.GREEN + "Auto-logged in" + Screen.RESET)
                await asyncio.sleep(0.6)
                return
            else:
                print(Screen.YELLOW + "Auto-login failed" + Screen.RESET)
                return
    async def login(self):
        Screen.clear()
        Screen.banner("LOGIN")
        ok = await self.check_server()
        if not ok:
            print(Screen.RED + "Server unreachable" + Screen.RESET)
            await asyncio.sleep(0.6)
            return
        uname = (await self.input.ainput("Username (or 'cancel'): ")).strip()
        if not uname or uname.lower() == "cancel":
            return
        passwd = await self.input.agetpass("Password: ")
        async with Spinner("Logging in"):
            try:
                resp = await self.net.request({"cmd": "login", "username": uname, "password": passwd})
            except Exception as e:
                print(Screen.RED + "Login failed: " + str(e) + Screen.RESET)
                await asyncio.sleep(0.6)
                return
        if not resp.get("ok"):
            err = resp.get("error")
            if err == "ip_banned":
                print(Screen.RED + "Your IP is banned" + Screen.RESET)
            else:
                print(Screen.RED + f"Login failed: {err}" + Screen.RESET)
            await asyncio.sleep(0.9)
            return
        token = resp.get("token")
        if not token:
            print(Screen.RED + "No token returned" + Screen.RESET)
            await asyncio.sleep(0.6)
            return
        self._save_auth(uname, token)
        print(Screen.GREEN + "Logged in successfully" + Screen.RESET)
        await asyncio.sleep(0.4)
    async def logout(self):
        if self.token:
            try:
                await self.net.request({"cmd": "logout", "token": self.token})
            except Exception:
                pass
        self._clear_auth()
        print(Screen.GREEN + "Logged out locally" + Screen.RESET)
        await asyncio.sleep(0.4)
    async def fetch_info(self):
        if not self.token:
            print(Screen.YELLOW + "You must log in first" + Screen.RESET)
            return None
        async with Spinner("Fetching info"):
            try:
                resp = await self.net.request({"cmd": "info", "token": self.token})
            except Exception as e:
                print(Screen.RED + "Failed to fetch info: " + str(e) + Screen.RESET)
                return None
        if not resp.get("ok"):
            print(Screen.RED + f"Failed: {resp.get('error')}" + Screen.RESET)
            return None
        self.last_info = resp
        return resp
    async def show_info(self):
        info = await self.fetch_info()
        if not info:
            return
        Screen.clear()
        Screen.banner("MY INFO")
        user = info.get("user", {})
        state = info.get("state", {})
        buildings = info.get("buildings", [])
        print(Screen.GREEN + f"Player: {user.get('username')}  —  Rank: {user.get('rank')}" + Screen.RESET)
        status = state.get("status", "village")
        status_txt = status.upper()
        status_color = Screen.GREEN if status == "empire" else (Screen.YELLOW if status == "city" else Screen.CYAN)
        try:
            width = os.get_terminal_size().columns
        except Exception:
            width = 80
        print(status_color + status_txt.center(width) + Screen.RESET)
        print()
        print(Screen.YELLOW + f"Coins: {Screen.coins(state.get('coins',0))}    Spins: {state.get('spins',0)}    Shields: {state.get('shields',0)}" + Screen.RESET)
        print(Screen.YELLOW + f"Village level: {state.get('village_level',0)}    Buried treasures: {state.get('buried_treasure_found',0)}" + Screen.RESET)
        print()
        print(Screen.CYAN + "Buildings:" + Screen.RESET)
        for b in buildings:
            lvl = int(b.get("level", 0))
            bar_len = min(30, max(1, lvl // 4))
            bar = "█" * bar_len + " " * (30 - bar_len)
            print(Screen.GREEN + f" {b.get('name'):10} " + Screen.WHITE + f" Lv {lvl:3} " + Screen.BLUE + f"[{bar}]" + Screen.RESET)
        Screen.pause()
    async def build(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        Screen.clear()
        Screen.banner("BUILD")
        print("Buildings: " + ", ".join(BUILDINGS))
        choice = (await self.input.ainput("Which building to upgrade: ")).strip().title()
        if choice not in BUILDINGS:
            print(Screen.RED + "Invalid building" + Screen.RESET)
            await asyncio.sleep(0.4)
            return
        async with Spinner("Upgrading"):
            try:
                resp = await self.net.request({"cmd": "build", "token": self.token, "building": choice})
            except Exception as e:
                print(Screen.RED + "Build failed: " + str(e) + Screen.RESET)
                return
        if not resp.get("ok"):
            print(Screen.RED + f"Build failed: {resp.get('error')}" + Screen.RESET)
            return
        if resp.get("became_empire"):
            print(Screen.GREEN + f"Built {choice}. New level {resp.get('new_level')}. You ascended to EMPIRE!" + Screen.RESET)
        else:
            print(Screen.GREEN + f"Built {choice}. New level {resp.get('new_level')}." + Screen.RESET)
        nb = resp.get("new_balance")
        if nb is not None:
            print(Screen.YELLOW + "New balance: " + Screen.coins(nb) + Screen.RESET)
        await asyncio.sleep(0.8)
    async def spin(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        async with Spinner("Spinning"):
            try:
                resp = await self.net.request({"cmd": "spin", "token": self.token})
            except Exception as e:
                print(Screen.RED + "Spin failed: " + str(e) + Screen.RESET)
                return
        if not resp.get("ok"):
            print(Screen.RED + f"Spin failed: {resp.get('error')}" + Screen.RESET)
            return
        outcome = resp.get("outcome")
        if outcome == "coins":
            amt = resp.get("amount", 0)
            print(Screen.GREEN + "You won coins: " + Screen.coins(amt) + Screen.RESET)
            print(Screen.CYAN + "New balance: " + Screen.coins(resp.get("new_balance", 0)) + Screen.RESET)
        elif outcome == "upgrade":
            if resp.get("result") == "not_enough_coins":
                print(Screen.YELLOW + "Upgrade rolled but not enough coins. Required: " + Screen.coins(resp.get("required", 0)) + Screen.RESET)
            else:
                print(Screen.GREEN + f"Random upgrade: {resp.get('building')} -> level {resp.get('new_level')}" + Screen.RESET)
                print(Screen.CYAN + "New balance: " + Screen.coins(resp.get("new_balance", 0)) + Screen.RESET)
        elif outcome == "attack":
            result = resp.get("result")
            if result == "no_target_available":
                print(Screen.YELLOW + "No target available to attack." + Screen.RESET)
            elif result == "choose_building":
                await self._handle_attack_choice(resp)
            else:
                print(Screen.YELLOW + "Attack result: " + str(result) + Screen.RESET)
        elif outcome == "shield":
            if resp.get("result") == "already_max":
                print(Screen.YELLOW + "You already have maximum shields." + Screen.RESET)
            else:
                print(Screen.GREEN + "Gained a shield. Shields now: " + str(resp.get("new_shields")) + Screen.RESET)
        elif outcome == "buried_treasure":
            amt = resp.get("amount", 0)
            print(Screen.MAGENTA + "BURIED TREASURE! You found " + Screen.coins(amt) + Screen.RESET)
            print(Screen.CYAN + "New balance: " + Screen.coins(resp.get("new_balance", 0)) + Screen.RESET)
        elif outcome == "nothing":
            print(Screen.YELLOW + "Spin resulted in nothing." + Screen.RESET)
        else:
            print(Screen.RED + "Unknown spin outcome: " + str(resp) + Screen.RESET)
        await asyncio.sleep(0.8)
    async def _handle_attack_choice(self, resp):
        target = resp.get("target")
        t_buildings = resp.get("target_buildings") or []
        if not target or not t_buildings:
            print(Screen.RED + "No valid target or buildings" + Screen.RESET)
            return
        Screen.clear()
        Screen.banner("ATTACK CHOICE")
        print(Screen.MAGENTA + f"Attack opportunity vs: {target}" + Screen.RESET)
        for i, b in enumerate(t_buildings, start=1):
            print(Screen.GREEN + f" [{i}] {b['name']} - level {b['level']}" + Screen.RESET)
        choice = (await self.input.ainput("Choose building number to attack (or 'c' cancel): ")).strip()
        if choice.lower() == "c":
            print(Screen.YELLOW + "Attack cancelled" + Screen.RESET)
            return
        if not choice.isdigit():
            print(Screen.RED + "Invalid choice" + Screen.RESET)
            return
        idx = int(choice) - 1
        if idx < 0 or idx >= len(t_buildings):
            print(Screen.RED + "Out of range" + Screen.RESET)
            return
        building = t_buildings[idx]["name"]
        async with Spinner("Attacking"):
            try:
                aresp = await self.net.request({"cmd": "attack", "token": self.token, "target": target, "building": building})
            except Exception as e:
                print(Screen.RED + "Attack failed: " + str(e) + Screen.RESET)
                return
        if not aresp.get("ok"):
            print(Screen.RED + f"Attack error: {aresp.get('error')}" + Screen.RESET)
            return
        if aresp.get("result") == "shield_consumed":
            print(Screen.YELLOW + f"Target had a shield. Shield consumed on {target}." + Screen.RESET)
        elif aresp.get("result") == "succeeded":
            print(Screen.GREEN + f"Attack succeeded on {target}. {building}: {aresp.get('old_level')} -> {aresp.get('new_level')}" + Screen.RESET)
            print(Screen.YELLOW + "Reward: " + Screen.coins(aresp.get("reward", 0)) + Screen.RESET)
            print(Screen.CYAN + "Your new balance: " + Screen.coins(aresp.get("attacker_new_balance", 0)) + Screen.RESET)
        else:
            print(Screen.YELLOW + "Attack result: " + str(aresp.get("result")) + Screen.RESET)
        await asyncio.sleep(0.6)
    async def buy_spins(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        Screen.clear()
        Screen.banner("BUY SPINS")
        amt = (await self.input.ainput(f"How many spins to buy? (1-{MAX_SPIN_BUY}): ")).strip()
        if not amt.isdigit():
            print(Screen.RED + "Invalid amount" + Screen.RESET)
            return
        amt_i = int(amt)
        if amt_i < 1 or amt_i > MAX_SPIN_BUY:
            print(Screen.RED + "Amount out of range" + Screen.RESET)
            return
        async with Spinner("Buying spins"):
            try:
                resp = await self.net.request({"cmd": "buy_spin", "token": self.token, "amount": amt_i})
            except Exception as e:
                print(Screen.RED + "Buy failed: " + str(e) + Screen.RESET)
                return
        if not resp.get("ok"):
            print(Screen.RED + f"Buy spins failed: {resp.get('error')}" + Screen.RESET)
            return
        print(Screen.GREEN + f"Bought {amt_i} spins. Spins: {resp.get('spins')}  Balance: {Screen.coins(resp.get('new_balance',0))}" + Screen.RESET)
        await asyncio.sleep(0.6)
    async def transfer(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        t = (await self.input.ainput("Send to username: ")).strip()
        if not t:
            print(Screen.YELLOW + "Cancelled" + Screen.RESET)
            return
        amt = (await self.input.ainput("Amount (integer coins): ")).strip().replace(".", "")
        if not amt.isdigit():
            print(Screen.RED + "Invalid amount" + Screen.RESET)
            return
        amt_i = int(amt)
        async with Spinner("Transferring"):
            try:
                resp = await self.net.request({"cmd": "transfer", "token": self.token, "target": t, "amount": amt_i})
            except Exception as e:
                print(Screen.RED + "Transfer failed: " + str(e) + Screen.RESET)
                return
        if not resp.get("ok"):
            print(Screen.RED + f"Transfer failed: {resp.get('error')}" + Screen.RESET)
            return
        print(Screen.GREEN + f"Transferred {Screen.coins(amt_i)} to {resp.get('to')}. Your new balance: {Screen.coins(resp.get('new_balance',0))}" + Screen.RESET)
        await asyncio.sleep(0.6)
    async def admin_panel(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        async with Spinner("Checking rank"):
            try:
                info = await self.net.request({"cmd": "info", "token": self.token})
            except Exception as e:
                print(Screen.RED + "Cannot check rank: " + str(e) + Screen.RESET)
                return
        rank = info.get("user", {}).get("rank", "user")
        if rank == "user":
            print(Screen.YELLOW + "You are not an admin or owner" + Screen.RESET)
            await asyncio.sleep(0.6)
            return
        while True:
            Screen.clear()
            Screen.banner(f"{rank.capitalize()} Panel")
            lines = ["1) Ban user","2) Unban user","3) Give coins","4) Remove coins","5) Show user"]
            if rank == "owner":
                lines += ["6) Grant admin","7) Revoke admin","8) Reset user","9) Delete user","10) Reset password","11) Change username (admin)","12) Logout all users"]
            lines += ["0) Back"]
            for l in lines:
                print(l)
            choice = (await self.input.ainput("Choice: ")).strip()
            if choice == "0":
                return
            action_map = {"1":"ban_user","2":"unban_user","3":"give_coins","4":"remove_coins","5":"show","6":"grantadmin","7":"revokeadmin","8":"resetuser","9":"deleteuser","10":"resetpassword","11":"usernamechange","12":"logoutall"}
            if choice not in action_map:
                print(Screen.YELLOW + "Unknown choice" + Screen.RESET)
                await asyncio.sleep(0.4)
                continue
            action = action_map[choice]
            extra = {}
            if action == "ban_user":
                target = (await self.input.ainput("Target username or id: ")).strip()
                days = (await self.input.ainput("Days to ban: ")).strip()
                extra = {"target": target, "days": int(days) if days.isdigit() else 0}
            elif action == "unban_user":
                target = (await self.input.ainput("Target username or id: ")).strip()
                extra = {"target": target}
            elif action in ("give_coins","remove_coins"):
                target = (await self.input.ainput("Target username or id: ")).strip()
                amount = (await self.input.ainput("Amount: ")).strip().replace(".", "")
                if not amount.isdigit():
                    print(Screen.RED + "Invalid amount" + Screen.RESET)
                    await asyncio.sleep(0.6)
                    continue
                extra = {"target": target, "amount": int(amount)}
            elif action in ("grantadmin","revokeadmin","resetuser","deleteuser","show","usernamechange"):
                target = (await self.input.ainput("Target username or id: ")).strip()
                extra = {"target": target}
                if action == "usernamechange":
                    new_name = (await self.input.ainput("New username: ")).strip()
                    extra["new"] = new_name
            elif action == "resetpassword":
                target = (await self.input.ainput("Target username or id: ")).strip()
                new_pass = (await self.input.agetpass("New password: ")).strip()
                extra = {"target": target, "new_password": new_pass}
            elif action == "logoutall":
                extra = {}
            async with Spinner("Processing"):
                try:
                    resp = await self.net.request({"cmd": "admin", "token": self.token, "action": action, **extra})
                except Exception as e:
                    print(Screen.RED + "Admin action failed: " + str(e) + Screen.RESET)
                    await asyncio.sleep(0.6)
                    continue
            print((Screen.GREEN if resp.get("ok") else Screen.RED) + str(resp) + Screen.RESET)
            Screen.pause()
    async def show_user(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        username = (await self.input.ainput("Show which username: ")).strip()
        if not username:
            return
        async with Spinner("Fetching user"):
            try:
                resp = await self.net.request({"cmd": "admin", "token": self.token, "action": "show", "target": username})
            except Exception as e:
                print(Screen.RED + "Show failed: " + str(e) + Screen.RESET)
                return
        if not resp.get("ok"):
            print(Screen.RED + f"Show failed: {resp.get('error')}" + Screen.RESET)
            await asyncio.sleep(0.6)
            return
        state = resp.get("state", {})
        buildings = resp.get("buildings", [])
        Screen.clear()
        Screen.banner("USER SHOW")
        print(Screen.MAGENTA + f"User: {resp.get('user')}" + Screen.RESET)
        print(Screen.YELLOW + f"Coins: {Screen.coins(state.get('coins',0))}  Spins: {state.get('spins',0)}  Shields: {state.get('shields',0)}" + Screen.RESET)
        print(Screen.CYAN + "Buildings:" + Screen.RESET)
        for b in buildings:
            print(Screen.GREEN + f" - {b.get('name')}: level {b.get('level')}" + Screen.RESET)
        Screen.pause()
    async def delete_account(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        confirm = (await self.input.ainput("Are you sure you want to DELETE your account? This is irreversible. (type 'DELETE' to confirm): ")).strip()
        if confirm != "DELETE":
            print(Screen.YELLOW + "Cancelled" + Screen.RESET)
            return
        pwd = await self.input.agetpass("Enter your password to confirm deletion: ")
        async with Spinner("Deleting account"):
            try:
                resp = await self.net.request({"cmd": "delete_account", "token": self.token, "password": pwd})
            except Exception as e:
                print(Screen.RED + "Delete failed: " + str(e) + Screen.RESET)
                return
        if not resp.get("ok"):
            print(Screen.RED + f"Delete failed: {resp.get('error')}" + Screen.RESET)
            return
        self._clear_auth()
        print(Screen.GREEN + "Your account was deleted. Goodbye." + Screen.RESET)
        await asyncio.sleep(1.0)
    async def change_username(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        new = (await self.input.ainput("New username: ")).strip()
        if not new:
            print(Screen.YELLOW + "Cancelled" + Screen.RESET)
            return
        async with Spinner("Changing username"):
            try:
                resp = await self.net.request({"cmd": "change_username", "token": self.token, "new_username": new})
            except Exception as e:
                print(Screen.RED + "Change failed: " + str(e) + Screen.RESET)
                return
        if not resp.get("ok"):
            print(Screen.RED + f"Change failed: {resp.get('error')}" + Screen.RESET)
            return
        self._clear_auth()
        print(Screen.GREEN + "Username changed. You have been logged out. Please log in with your new username." + Screen.RESET)
        await asyncio.sleep(1.0)
    async def change_password(self):
        if not self.token:
            print(Screen.YELLOW + "Login first" + Screen.RESET)
            return
        old = await self.input.agetpass("Current password: ")
        new = await self.input.agetpass("New password (min 8): ")
        confirm = await self.input.agetpass("Repeat new password: ")
        if new != confirm:
            print(Screen.RED + "New passwords do not match" + Screen.RESET)
            return
        if len(new) < 8:
            print(Screen.YELLOW + "New password too short" + Screen.RESET)
            return
        async with Spinner("Changing password"):
            try:
                resp = await self.net.request({"cmd": "change_password", "token": self.token, "old_password": old, "new_password": new})
            except Exception as e:
                print(Screen.RED + "Change password failed: " + str(e) + Screen.RESET)
                return
        if not resp.get("ok"):
            print(Screen.RED + f"Change failed: {resp.get('error')}" + Screen.RESET)
            return
        self._clear_auth()
        print(Screen.GREEN + "Password changed. You have been logged out. Please log in again." + Screen.RESET)
        await asyncio.sleep(1.0)
    async def account_menu(self):
        while True:
            Screen.clear()
            Screen.banner("ACCOUNT")
            print("1) Change username")
            print("2) Change password")
            print("3) Delete account")
            print("0) Back")
            choice = (await self.input.ainput("Choice: ")).strip()
            if choice == "0":
                return
            if choice == "1":
                await self.change_username()
            elif choice == "2":
                await self.change_password()
            elif choice == "3":
                await self.delete_account()
            else:
                print(Screen.YELLOW + "Unknown choice" + Screen.RESET)
                await asyncio.sleep(0.3)
    async def main_menu(self):
        while True:
            Screen.clear()
            Screen.banner("COIN CITY CLIENT")
            Screen.status(self.username)
            print("1) Login")
            print("2) Register")
            print("3) Show my info")
            print("4) Build")
            print("5) Spin")
            print("6) Buy spins")
            print("7) Transfer coins")
            print("8) Admin panel")
            print("9) Account")
            print("10) Logout")
            print("0) Quit")
            choice = (await self.input.ainput("Choice: ")).strip()
            if choice == "0":
                print(Screen.GREEN + "Goodbye." + Screen.RESET)
                await asyncio.sleep(0.2)
                return
            if choice == "1":
                await self.login()
            elif choice == "2":
                await self.register()
            elif choice == "3":
                await self.show_info()
            elif choice == "4":
                await self.build()
            elif choice == "5":
                await self.spin()
            elif choice == "6":
                await self.buy_spins()
            elif choice == "7":
                await self.transfer()
            elif choice == "8":
                await self.admin_panel()
            elif choice == "9":
                await self.account_menu()
            elif choice == "10":
                await self.logout()
            else:
                print(Screen.YELLOW + "Unknown choice" + Screen.RESET)
                await asyncio.sleep(0.3)

async def main():
    cfg = Config(CONF_FILE)
    client = Client(cfg)
    try:
        await client.main_menu()
    except KeyboardInterrupt:
        print("\n" + Screen.GREEN + "Exited." + Screen.RESET)
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        await asyncio.sleep(0.01)

def main_sync():
    import asyncio
    asyncio.run(main())
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        print("Fatal error:", e)
        sys.exit(1)