# src/gsp_core/protocol/commands.py

"""
8-bit command-ID allocation scheme:
  0x00–0x0F: Core/system control
  0x10–0x1F: Bootloader flash operations
  0x20–0x2F: Data-transfer / chunking
  0x30–0x3F: Message/IPC commands
  0x40–0x4F: Diagnostics & health
  0x50–0x5F: Configuration & settings
  0x60–0x6F: Security & auth
  0x70–0x7F: Radio / transport control
  0x80–0x8F: App-defined #1
  0x90–0x9F: App-defined #2
  0xA0–0xAF: App-defined #3
  0xB0–0xBF: Reserved
  0xC0–0xFF: Reserved for future use
"""

# ─── 0x10–0x1F: Bootloader flash operations ─────────────────────────────────
CMD_ERASE_FLASH   = 0x10
CMD_WRITE_CHUNK   = 0x11
CMD_VERIFY_CHUNK  = 0x12
CMD_RESET_AND_RUN = 0x13
CMD_ABORT         = 0x14

# ─── 0x30–0x3F: Message/IPC commands ───────────────────────────────────────
CMD_SEND_MESSAGE  = 0x30

# (add more commands as needed…)
