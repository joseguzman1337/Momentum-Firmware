# Contributing to Momentum Firmware

Welcome to Momentum. We are pushing the boundaries of what the Flipper Zero can do.

## 🤖 AI Usage Policy: "AI-First"

**ANY AND ALL USE OF AI IS FULLY PERMITTED, ENCOURAGED, AND EXPECTED.**

We explicitly welcome the use of Generative AI tools (LLMs, Copilots, Agents) for any aspect of this project. Whether you are using AI to generate C code, refactor legacy modules, draft documentation, or debug hard faults, your contributions are valid here.

**You are a human with access to powerful tools—please leverage them to drive maximum efficiency and innovation.**

### Acceptable & Encouraged AI Workflows
* **Generation:** Use LLMs to generate boilerplate for new apps, write FuriHAL drivers, or compose Pull Request descriptions.
* **Optimization:** Use AI to analyze `furi` message queues, stack usage, and memory leaks to optimize for the Flipper's limited constraints.
* **Validation:** Use **RAG (Retrieval-Augmented Generation)** pipelines to cross-reference your code against the STM32WB55 datasheet and Flipper API docs.
* **Automation:** Deploy autonomous agents to test `fbt` build scripts and validate Asset Pack manifests.

---

## 🛠 Architectural Standards

Momentum is a high-performance custom firmware. We do not just "allow" advanced tools; we build *with* them.

### 1. Firmware & Embedded Engineering
* **Code Style:** We generally follow the existing Flipper Zero C coding style. If your AI generates code, ensure it aligns with our formatting (clang-format).
* **Memory Management:** This is an embedded environment. Agents should be instructed to prioritize `malloc`/`free` safety and avoid stack overflows.
* **Performance:** Code must be non-blocking. Use the Furi OS primitives (mutexes, semaphores, message queues) correctly.

### 2. Architecture: RAG, Agents, and MCP
We encourage the use of advanced AI architecture to improve the firmware ecosystem.
* **RAG Implementation:** Contributions that improve how we index documentation or firmware headers for AI retrieval are highly valued.
* **Model Context Protocol (MCP):** If you are building external companion tools, we encourage using **MCP servers** to standardize how LLMs interact with the Flipper via serial/BLE.

### 3. Build System (fbt)
* **FBT Compatibility:** All submissions must compile cleanly using `./fbt`.
* **CI/CD:** Ensure your AI-generated code passes the continuous integration checks defined in our workflows.

---

## 🚀 Areas for Contribution

We are actively seeking contributions in these high-impact areas:

* **Protocol Support:** New Sub-GHz protocols, NFC parsers, and Infrared remotes.
* **Asset Packs:** Tools or scripts to automate the creation of Asset Packs (Anims/Icons) from raw image data.
* **App Ecosystem:** New FAP (Flipper Application Package) modules that extend functionality (e.g., GPIO tools, games, pentesting utilities).
* **Core Optimization:** AI-driven refactoring of the core system to free up SRAM and Flash storage.

---

## 📥 Submission Guidelines

1.  **Fork & Clone:** Fork the repository and clone it locally.
2.  **Generate:** Use your preferred AI stack to solve the issue or build the feature.
3.  **Validate:**
    * **Compile:** Run `./fbt` to ensure the firmware builds.
    * **Test:** Flash the firmware to your device and verify it works on real hardware.
    * **Sanity Check:** Ensure your agents are not hallucinating APIs that don't exist in the current Firmware version.
4.  **Pull Request:** Submit your PR.
    * *Note:* You are free to mention which AI tools you used (e.g., "Refactored via Claude 3.5 Sonnet").
    * **Closing:** Simply state what your PR achieves and how it improves the firmware.

---

**Join us in building the ultimate Flipper experience.**