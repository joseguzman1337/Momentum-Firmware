<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/assets/logo_dark.png">
    <source media="(prefers-color-scheme: light)" srcset=".github/assets/logo_light.png">
    <img
        alt="Momentum Firmware"
        src=".github/assets/logo_dark.png">
  </picture>
</p>

<h2 align="center">
  <a href="#Install">Install</a> · <a href="#list-of-changes">Features</a> · <a href="https://discord.gg/momentum">Discord</a> · <a href="#%EF%B8%8F-support">Donate</a>
</h2>

This custom firmware is based on the [Official Firmware](https://github.com/flipperdevices/flipperzero-firmware) for [Flipper Zero](https://flipperzero.one/), and includes most of the awesome features from [Unleashed](https://github.com/DarkFlippers/unleashed-firmware). It is a direct continuation of the Xtreme firmware, built by the same (and only) developers who made that project special.

<br>
<h2 align="center">Modus Operandi</h2>

The goal of this firmware is to constantly push the bounds of what is possible with Flipper Zero, driving the innovation of many new groundbreaking features, while maintaining the easiest and most customizable user experience of any firmware. Fixing bugs promptly and ensuring a stable and compatible system is also of our utmost importance.

- <h4>Feature-rich: We include all third-party features and apps as long as they fulfill a useful purpose and they work correctly, aswell as implement ourselves many new exciting functionalities.</h4>

- <h4>Stable: We ensure the most stable experience possible by having an actual understanding of what's going on, and proactively making all tweaks and additions backwards-, and inter-, compatible.</h4>

- <h4>Customizable: You can tweak just about everything you see: add/remove apps from the menu, change the animations, replace icon graphics, change your Flipper's name, change how the main menu looks, setup different keybinds like never before, and so much more. All on-device, with no complicated configuration.</h4>

<br>

Note that mentioned below are only a few of our staple additions to the firmware. For a full list check [down here](https://github.com/joseguzman1337/Momentum-Firmware#List-of-Changes).

<br>
<h2 align="center">Momentum Settings</h2>

We offer a powerful and easy-to-use application tailor-made for our firmware, that lets you configure everything you could dream of, and more:

<img src=".github/assets/settings.png" align="left" height="160vh"/>
<img align="left" height="180vh" width="10" src="https://upload.wikimedia.org/wikipedia/commons/3/3d/1_120_transparent.png">

- <ins><b>Interface:</b></ins> Tweak every part of your Flipper, from the desktop animations, to the main menu, lockscreen behavior, file browser, etc.

- <ins><b>Protocols:</b></ins> Configure SubGhz settings, add/remove custom frequencies, extend SubGhz frequencies to 281-361, 378-481, 749-962 MHz and setup which GPIO pins are used by different external modules.

- <ins><b>Misc:</b></ins> Everything else that doesn't fit the previous categories. Change your Flipper's name, XP level, screen options, and configure the <a href="https://github.com/Z3BRO/Flipper-Zero-RGB-Backlight">RGB backlight</a>.

<br>

<br>

<h2 align="center">Animations / Asset Packs</h2>

We created our own improved Animation / Asset system that lets you create and cycle through your own `Asset Packs` with only a few button presses, allowing you to easily load custom Animations, Icons and Fonts like never before. Think of it as a Theme system that's never been easier.

<img src=".github/assets/packs-folder.png" align="left" width="200px"/>
You can easily create your own pack, or find some community-made ones on <b><a href="https://momentum-fw.dev/asset-packs">our website</a> or on Discord</b>. Check <a href="https://github.com/Next-Flip/Momentum-Firmware/blob/dev/documentation/file_formats/AssetPacks.md">here</a> for a tutorial on creating your own. Essentially, each <code>Asset Pack</code> can configure its own <code>Anims</code>, <code>Icons</code> & <code>Fonts</code>.

<br clear="left"/>

<br>

<img src=".github/assets/packs-select.png" align="left" width="200px"/>
Once you have some asset packs, upload them to your Flipper in <code>SD/asset_packs</code> (if you did this right you should see <code>SD/asset_packs/PackName/Anims</code> and/or <code>SD/asset_packs/PackName/Icons</code>). Alternatively, install directly using the website.


<br clear="left"/>

<br>

<img src=".github/assets/packs-done.png" align="left" width="200px"/>
After installing the packs to Flipper, hit the <code>Arrow Up</code> button on the main menu and go to <code>Momentum Settings > Interface > Graphics</code>. Here choose which asset pack you want and tweak the other settings how you prefer, then exit the app to reboot and enjoy your fully customized Flipper!

<br clear="left"/>

<br>

<h2 align="center">Bad Keyboard</h2>

<img src=".github/assets/badkb.png" align="left" width="250px"/>
BadUSB is a great app, but it lacks a lot of options. Bad-KB allows you to customize all USB and Bluetooth parameters for your attacks.

In Bluetooth mode it allows you to spoof the display name and MAC address of the device to whatever you want. Showing up as a portable speaker or a wireless keyboard is easily doable, allowing you to get the attention of your target without needing a cable at hand.

In USB mode it also enables additional functionality to spoof the manufacturer and product names, as well as vendor and product IDs (VID/PID).

<br>

<h2 align="center">List of changes</h2>

There are too many to name them all, this is a **non-comprehensive** list of the **most notable from an end-user perspective**. For a more detailed list, you can read through the [**changelogs**](https://github.com/Next-Flip/Momentum-Firmware/releases) and commits/code. Also, you can find a **feature comparison with other firmwares** on [our website](https://momentum-fw.dev/).

Note that this repo is always updated with the great work from our friends at [Unleashed](https://github.com/DarkFlippers/unleashed-firmware) and the latest changes from [OFW](https://github.com/flipperdevices/flipperzero-firmware). Below are mentioned only **our** changes that we can actually be credited for, so make sure to check their fantastic additions aswell. And a huge thank you to both teams!

```txt
[Added]

- Momentum App (Easy configuration of features and behavior of the firmware)
- Asset Packs (Unparalleled theming and customization)
- More UI customization, redesigns and optimizations
- Bad-Keyboard App
- BLE Spam App
- FindMy Flipper App
- NFC Maker App
- Wardriver App
- File Search across SD Card
- Additional NFC parsers and protocols
- NFC Type 4 protocol and NTAG4xx support
- Subdriving (saving GPS coordinates for Sub-GHz)
- Easy spoofing (Name, MAC address, Serial number)
- Video Game Module color configuration right from Flipper
- Enhanced RGB Backlight modes (Full customization & Rainbow mode)
- File management on device (Cut, Copy, Paste, Show, New Dir, etc.)
- Remember Infrared GPIO settings and add IR Blaster support in apps
- Advanced Security measures (Lock on Boot, reset on false pins, etc.)
- Disk Image management (Mount and view image contents, open in Mass Storage)
- Extended JavaScript API (Support for UsbDisk/Mass Storage, File operations)
```
```txt
[Updated]

- Enhanced WiFi support for easiest setup ever
- Extended keyboard with cursor movement and symbols
- File Browser with Sorting, More supported File Types
- Advanced and optimized Level System (Up to 30 levels)
- Desktop Keybind system for full key and press/hold remapping
- Storage backend with instant rename and virtual mounting for disk images
- Expanded Sub-GHz App (Duplicate detection & Ignore, Autosave, History improvements)
- Improved Error Messages (Showing source file paths)
```
```txt
[Removed]

- Unused Dummy Mode
- Broken or Superfluous apps
```

<br>

<h2 align="center">Install</h2>

There are 4 methods to install Momentum, we recommend you use the **Web Updater**, but choose whichever one you prefer:

> <details><summary><code>Web Updater (Chrome)</code></summary><ul>
>   <li>Make sure qFlipper is closed</li>
>   <li>Open the <a href="https://momentum-fw.dev/update">Web Updater</a></li>
>   <li>Click <code>Connect</code> and select your Flipper from the list</li>
>   <li>Select which update <code>Channel</code> you prefer from the dropdown</li>
>   <li>Click <code>Install</code> and wait for the update to complete</li>
> </ul></details>

> <details><summary><code>Flipper Lab/App (chrome/mobile)</code></summary><ul>
>   <li>(Desktop) Make sure qFlipper is closed</li>
>   <li>(Mobile) Make sure you have the <a href="https://docs.flipper.net/mobile-app">Flipper Mobile App</a> installed and paired</li>
>   <li>Open the <a href="https://github.com/Next-Flip/Momentum-Firmware/releases/latest">latest release page</a></li>
>   <li>Click the <code>☁️ Flipper Lab/App (chrome/mobile)</code> link</li>
>   <li>(Desktop) Click <code>Connect</code> and select your Flipper from the list</li>
>   <li>(Desktop) Click <code>Install</code> and wait for the update to complete</li>
>   <li>(Mobile) Accept the prompt to open the link in the Flipper Mobile App</li>
>   <li>(Mobile) Confirm to proceed with the install and wait for the update to complete</li>
> </ul></details>

> <details><summary><code>qFlipper Package (.tgz)</code></summary><ul>
>   <li>Download the qFlipper package (.tgz) from the <a href="https://github.com/Next-Flip/Momentum-Firmware/releases/latest">latest release page</a></li>
>   <li>Make sure the <code>WebUpdater</code> and <code>lab.flipper.net</code> are closed</li>
>   <li>Open <a href="https://flipperzero.one/update">qFlipper</a> and connect your Flipper</li>
>   <li>Click <code>Install from file</code></li>
>   <li>Select the .tgz you downloaded and wait for the update to complete</li>
> </ul></details>

> <details><summary><code>Zipped Archive (.zip)</code></summary><ul>
>   <li>Download the zipped archive (.zip) from the <a href="https://github.com/Next-Flip/Momentum-Firmware/releases/latest">latest release page</a></li>
>   <li>Extract the archive. This is now your new Firmware folder</li>
>   <li>Open <a href="https://flipperzero.one/update">qFlipper</a>, head to <code>SD/update</code> and simply move the firmware folder there</li>
>   <li>On the Flipper, hit the <code>Arrow Down</code> button, this will get you to the file menu. In there simply search for your updates folder</li>
>   <li>Inside that folder, select the Firmware you just moved onto it, and run the file thats simply called <code>Update</code></li>
> </ul></details>

<br>

<h2 align="center">🤖 AI-Powered Development Pipeline</h2>

This project leverages multiple AI coding agents working in parallel to automatically fix issues, improve code quality, and enhance security. The automation pipeline processes GitHub issues, security alerts, and code improvements 24/7.

> <details><summary><code>🔧 Codex Agent (OpenAI)</code></summary><ul>
>   <li><b>Purpose:</b> Automated issue resolution and feature implementation</li>
>   <li><b>Status:</b> Active - Processing issues sequentially</li>
>   <li><b>Configuration:</b> Auto-configured with issue auto-close via PR descriptions</li>
>   <li><b>Workflow:</b>
>     <ol>
>       <li>Reads GitHub issues from the repository</li>
>       <li>Analyzes codebase context and requirements</li>
>       <li>Implements fixes with proper commit messages</li>
>       <li>Automatically includes "Closes #N" in PR descriptions</li>
>     </ol>
>   </li>
>   <li><b>Log File:</b> <code>codex_tuned.log</code></li>
>   <li><b>Command:</b> <code>codex --full-auto exec "Fix issue #N"</code></li>
>   <li><b>Recent Achievements:</b>
>     <ul>
>       <li>✅ Storage filesystem selection (#56)</li>
>       <li>✅ Power charging current limit (#55)</li>
>       <li>✅ Archive multiple file selection (#54)</li>
>       <li>✅ JS BADUSB Bluetooth configuration (#50)</li>
>       <li>✅ Charge cap functionality (#49)</li>
>     </ul>
>   </li>
> </ul></details>

> <details><summary><code>🛡️ Claude Agent (Anthropic)</code></summary><ul>
>   <li><b>Purpose:</b> Security vulnerability remediation and code scanning</li>
>   <li><b>Status:</b> Completed - All 24 code scanning alerts addressed</li>
>   <li><b>Configuration:</b> Parallelized execution for maximum throughput</li>
>   <li><b>Workflow:</b>
>     <ol>
>       <li>Fetches code scanning alerts from GitHub Security</li>
>       <li>Analyzes each vulnerability independently</li>
>       <li>Applies security patches with proper validation</li>
>       <li>Runs 24 parallel sessions for simultaneous fixes</li>
>     </ol>
>   </li>
>   <li><b>Log Files:</b> <code>claude_alert_*.log</code> (24 files)</li>
>   <li><b>Command:</b> <code>claude -p --dangerously-skip-permissions "Fix alert #N"</code></li>
>   <li><b>Security Fixes:</b>
>     <ul>
>       <li>✅ Memory safety improvements (null pointer checks)</li>
>       <li>✅ Input validation and sanitization</li>
>       <li>✅ Path traversal vulnerability fixes</li>
>       <li>✅ Weak cryptographic key upgrades</li>
>       <li>✅ Dependabot vulnerability (brace-expansion 2.0.2)</li>
>     </ul>
>   </li>
> </ul></details>

> <details><summary><code>🚀 Jules Agent (Google)</code></summary><ul>
>   <li><b>Purpose:</b> Asynchronous coding tasks and PR generation</li>
>   <li><b>Status:</b> 34 sessions created (14 active, quota limit reached)</li>
>   <li><b>Configuration:</b> Authenticated with Google account, linked to GitHub</li>
>   <li><b>Workflow:</b>
>     <ol>
>       <li>Creates remote coding sessions for each issue</li>
>       <li>Works asynchronously in Google's cloud infrastructure</li>
>       <li>Generates PRs with proper issue linking</li>
>       <li>Supports multi-repository context and MCP integrations</li>
>     </ol>
>   </li>
>   <li><b>Quota Limits:</b>
>     <ul>
>       <li>Free tier: 15 tasks/day, 3 concurrent</li>
>       <li>Pro tier: ~100 tasks/day, ~15 concurrent</li>
>       <li>Ultra tier: ~300 tasks/day, ~60 concurrent</li>
>     </ul>
>   </li>
>   <li><b>Command:</b> <code>jules new --repo owner/repo "Fix issue #N"</code></li>
>   <li><b>Session Management:</b> <code>jules remote list --session</code></li>
> </ul></details>

> <details><summary><code>🧠 Gemini CLI Agent (Google)</code></summary><ul>
>   <li><b>Purpose:</b> Advanced problem-solving, architectural decisions, and complex refactoring</li>
>   <li><b>Status:</b> Configured with project context and checkpointing enabled</li>
>   <li><b>Configuration:</b> Context files in <code>.gemini/</code>, settings in <code>settings.json</code></li>
>   <li><b>Workflow:</b>
>     <ol>
>       <li>Loads project context from <code>.gemini/GEMINI.md</code></li>
>       <li>Filters complex/architectural issues automatically</li>
>       <li>Uses checkpointing for safe code modifications</li>
>       <li>Provides multi-step reasoning and analysis</li>
>     </ol>
>   </li>
>   <li><b>Key Features:</b>
>     <ul>
>       <li>🔍 Deep codebase understanding via context files</li>
>       <li>💾 Checkpointing with <code>/restore</code> command</li>
>       <li>🛠️ Built-in tools (file ops, shell, web search, memory)</li>
>       <li>🔌 MCP server support for custom tools</li>
>       <li>💬 Interactive REPL mode for iterative development</li>
>     </ul>
>   </li>
>   <li><b>Automation Script:</b> <code>python3 scripts/gemini_automation.py</code></li>
>   <li><b>Manual Usage:</b>
>     <ul>
>       <li>Interactive: <code>gemini</code></li>
>       <li>One-shot: <code>gemini -p "your prompt"</code></li>
>       <li>With file context: <code>gemini -p "Explain @./src/main.c"</code></li>
>     </ul>
>   </li>
>   <li><b>Slash Commands:</b>
>     <ul>
>       <li><code>/memory show</code> - View loaded context</li>
>       <li><code>/restore</code> - Rollback changes</li>
>       <li><code>/tools</code> - List available tools</li>
>       <li><code>/compress</code> - Optimize token usage</li>
>     </ul>
>   </li>
> </ul></details>

> <details><summary><code>⚡ Warp Terminal Agent</code></summary><ul>
>   <li><b>Purpose:</b> Code quality analysis, documentation, and performance optimization</li>
>   <li><b>Status:</b> Task list created, awaiting manual execution</li>
>   <li><b>Configuration:</b> Integrated with Warp Terminal's AI Agent Mode</li>
>   <li><b>Task Categories:</b>
>     <ul>
>       <li>🔍 Code Quality Analysis (memory leaks, unsafe pointers)</li>
>       <li>📚 Documentation Generation (API docs, usage examples)</li>
>       <li>🧪 Test Coverage Analysis and suggestions</li>
>       <li>⚡ Performance Optimization (profiling, bottleneck detection)</li>
>       <li>🔒 Security Hardening (file I/O, input validation)</li>
>       <li>📦 Dependency Update Checks</li>
>       <li>🏗️ Build System Optimization</li>
>       <li>📡 NFC Protocol Implementation Review</li>
>       <li>🔋 Power Management Analysis</li>
>       <li>♻️ Code Duplication Detection</li>
>     </ul>
>   </li>
>   <li><b>Usage:</b>
>     <ol>
>       <li>Open Warp Terminal</li>
>       <li>Navigate to project directory</li>
>       <li>Type <code>#</code> to activate AI Agent Mode</li>
>       <li>Copy tasks from <code>warp_agent_tasks.md</code></li>
>     </ol>
>   </li>
>   <li><b>Results Directory:</b> <code>.warp-agent-results/</code></li>
> </ul></details>

> <details><summary><code>📊 Automation Statistics</code></summary><ul>
>   <li><b>Total PRs Merged:</b> 7+ (in last 24 hours)</li>
>   <li><b>Issues Closed:</b> 5+ (auto-closed via PR merges)</li>
>   <li><b>Security Alerts Fixed:</b> 24 CodeQL alerts + 1 Dependabot</li>
>   <li><b>Code Files Modified:</b> 2,500+ files</li>
>   <li><b>Success Rate:</b> 100% (all submitted PRs merged)</li>
>   <li><b>Automation Uptime:</b> Continuous (24/7 processing)</li>
>   <li><b>Average Issue Resolution Time:</b> ~15-30 minutes per issue</li>
> </ul></details>

> <details><summary><code>🔄 Continuous Integration Workflow</code></summary><ul>
>   <li><b>Issue Detection:</b> GitHub Issues API monitors for new/open issues</li>
>   <li><b>Agent Assignment:</b>
>     <ul>
>       <li>Feature requests → Codex</li>
>       <li>Security alerts → Claude (parallelized)</li>
>       <li>Complex tasks → Jules (async cloud)</li>
>       <li>Code quality → Warp (manual review)</li>
>     </ul>
>   </li>
>   <li><b>PR Creation:</b> Automated with proper issue linking ("Closes #N")</li>
>   <li><b>Auto-Merge:</b> PRs merged automatically after creation</li>
>   <li><b>Issue Closure:</b> GitHub auto-closes issues when PRs merge</li>
>   <li><b>Monitoring:</b> Log files track all agent activities</li>
> </ul></details>

> <details><summary><code>⚙️ Setup Instructions</code></summary><ul>
>   <li><b>Prerequisites:</b>
>     <ul>
>       <li>GitHub CLI (<code>gh</code>) - authenticated</li>
>       <li>Codex CLI - <code>npm install -g @openai/codex</code></li>
>       <li>Claude CLI - <code>npm install -g @anthropic/claude</code></li>
>       <li>Jules CLI - <code>pnpm add -g @google/jules</code></li>
>       <li>Warp Terminal - Download from warp.dev</li>
>     </ul>
>   </li>
>   <li><b>Authentication:</b>
>     <ul>
>       <li>Codex: <code>codex login</code></li>
>       <li>Claude: <code>claude setup-token</code></li>
>       <li>Jules: <code>jules login</code></li>
>       <li>GitHub: <code>gh auth login</code></li>
>     </ul>
>   </li>
>   <li><b>Running Automation:</b>
>     <ul>
>       <li>Codex: See <code>codex_tuned.log</code> for active loop</li>
>       <li>Claude: See <code>claude_alert_*.log</code> for parallel sessions</li>
>       <li>Jules: <code>jules remote list --session</code> to view active tasks</li>
>       <li>Warp: Follow instructions in <code>warp_agent_tasks.md</code></li>
>     </ul>
>   </li>
> </ul></details>

<br>

<h2 align="center">Build it yourself</h2>

```bash
To download the repository:
$ git clone --recursive --jobs 8 https://github.com/joseguzman1337/Momentum-Firmware.git
$ cd Momentum-Firmware/

To flash directly to the Flipper (Needs to be connected via USB, qFlipper closed)
$ ./fbt flash_usb_full

To compile a TGZ package
$ ./fbt updater_package

To build and launch a single app:
$ ./fbt launch APPSRC=your_appid
```

<h2 align="center">Stargazers over time</h2>

[![Stargazers over time](https://starchart.cc/Next-Flip/Momentum-Firmware.svg?variant=adaptive)](https://starchart.cc/Next-Flip/Momentum-Firmware)

<h2 align="center">❤️ Support</h2>

If you enjoy the firmware please __**spread the word!**__ And if you really love it, maybe consider donating to the team? :D

> **[Ko-fi](https://ko-fi.com/willyjl)**: One-off or Recurring, No signup required

> **[PayPal](https://paypal.me/willyjl1)**: One-off, Signup required

> **BTC**: `1EnCi1HF8Jw6m2dWSUwHLbCRbVBCQSyDKm`

**Thank you <3**
