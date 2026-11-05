# Reviewed upstream reference

Repository: https://github.com/je-suis-tm/quant-trading

Revision: `611b73f2c3f577ac5b28aaa19ac8c43d3236c7a5`

Original path: `London Breakout backtest.py`

Source URL: https://raw.githubusercontent.com/je-suis-tm/quant-trading/611b73f2c3f577ac5b28aaa19ac8c43d3236c7a5/London%20Breakout%20backtest.py

SHA-256: `8b5a0f672c2c5a44fb5a72564fcb0b20a5bd2b0d3d9da3e2f4a52b2d047f8e3a`

Author/project attribution: je-suis-tm / quant-trading. Original Apache-2.0 license is retained in LICENSE. The reference file is copied byte-for-byte from our pinned research snapshot. No original comments or code were removed. No upstream NOTICE file was supplied in that research snapshot; do not infer a project-wide license for our application.

Local adaptation: src/tradinglab/upstream_london.py independently ports the reviewed signal loop into Python lists, retaining threshold, clock, branching and cumsum semantics. src/tradinglab/upstream_verification.py loads only the two reviewed upstream function definitions via AST after a hash check, with pandas supplied explicitly. It does not import the original script or execute os.chdir('d:/'), plotting or main/file operations.

Known behavior is deliberately preserved, including stale cumsum values after resetting some rejected signals, a fixed 0.01 absolute-price risk interval, no protection checks in the initial 03:01–03:29 branch, fixed UTC-5 input clock, and source-row signal timing. These are reproduction semantics, not production recommendations. A revised gold strategy must use another version name and document deviations.
