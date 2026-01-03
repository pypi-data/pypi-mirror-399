# Coin City Client

**Version:** 0.1.0  
**Author:** Viren Sahti  
**License:** Proprietary © 2026  

Coin City Client (`coincity`) is a Python terminal-based client for playing the Coin City game. It allows users to manage their city, build structures, spin for rewards, trade coins, and interact with other players on the official Coin City server.

---

## Features

- **Account Management:** Register, login, change username or password, and delete your account safely.
- **City Building:** Upgrade buildings like House, Bank, Tower, Market, Library, Barracks, and Fortress.
- **Spins & Rewards:** Spin for coins, shields, random upgrades, and buried treasures.
- **Player Interaction:** Attack other players’ buildings, transfer coins, and monitor your rank.
- **Admin Panel:** For admins and owners, perform actions like banning users, giving coins, and resetting accounts.
- **Cross-Platform:** Works on Windows, Linux, and macOS terminals.
- **Async & Responsive:** Uses asyncio with a spinner animation for a smooth user experience.
- **Local Config & Logging:** Stores configuration and logs locally in your OS data directory.

---

## Overview

Coin City Client connects to the official Coin City game server to manage your player profile. Your username and password are securely stored on the server, and all actions like building, spinning, and transferring coins are performed through authenticated requests. The client also includes local logging for debugging and tracking your actions.

---

## Security & Privacy Notes

- **Secure Authentication:** Passwords are hashed on the server; tokens are used locally for session management.
- **IP Tracking:** Your IP may be recorded to prevent abuse, as per game rules.
- **Local Data Storage:** Configuration and logs are stored in your OS’s standard application data directory.
- **Disclaimer:** Use this client responsibly. The author is not responsible for account bans, server issues, or misuse.

---

## Getting Started

1. Install the package via `pip install .` from the repository.  
2. Run the client in your terminal with:

   ```bash
   coincity