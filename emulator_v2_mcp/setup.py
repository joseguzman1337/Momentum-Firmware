from setuptools import setup, find_packages

setup(
    name="flipper-zero-emulator-v2",
    version="2.1.0",
    description="Flipper Zero Hardware & Firmware Emulator with Model Context Protocol (MCP) Server",
    author="Flipper Emulator Team",
    packages=find_packages(),
    py_modules=["integration_server", "flipper_mcp_server", "main"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "flipper-emulator=main:main",
            "flipper-mcp-server=flipper_mcp_server:main",
            "momentum-emulator-v2=main:main",
            "momentum-emulator-v2-mcp=integration_server:main",
        ],
    },
)
