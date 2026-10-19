# cut-stock-proof

Prove a bounded minimum-bar plan with explicit between-piece kerf and a search budget.

For Small workshop material planners. Greedy allocation can waste a board, while a search cutoff must not be presented as proven optimal.

## Quickstart

Python3.10+; zero runtime dependencies. Wheel builds require setuptools from the normal Python registry.

```sh
git clone https://github.com/nripankadas07/cut-stock-proof.git
cd cut-stock-proof
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/cut-stock-proof example.json
```

Exit0: six pieces6,5,3,2,2,2 in stock10 need two bars; the reported first-fit upper bound is three.

Example generators create only an explicitly named new file and refuse overwrite. Reports never modify the input. Windows equivalents use `.venv\Scripts\python.exe` and the installed `.exe`; Windows/macOS have not been executed by this release's Linux CI.

## Contract

Strict JSON stock_length, kerf, pieces. Integer lengths1..1000000, kerf0..1000000;1..24 expanded pieces with unique printable IDs and optional quantity. Unlimited identical stock lengths. Kerf is charged only between adjacent pieces, never at ends. Transform length+kerf into bins of stock+kerf; first-fit decreasing upper bound, valid total-capacity lower bound and exhaustive branch search with equal-free-space symmetry pruning. An optimal claim requires reaching the lower bound or completing search. Oversized pieces return infeasible/exit1; budget exhaustion returns exit2 without a plan or optimality claim.

JSON reports go to stdout. Exit0 means the documented successful result, exit1 a valid finding/incomplete/rejected result, exit2 invalid/unsupported input, I/O or budget failure with stderr and no partial report. Ranges are half-open.

## Limits

64 KiB JSON,250000 search nodes maximum. One stock length, no stock availability/cost objective,2D layouts, end trim, grain, saw sequencing or machine control. The mathematical kerf convention must match the intended planning task; this is not manufacturing certification.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/cut-stock-proof-check
/tmp/cut-stock-proof-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/cut-stock-proof-check/bin/python
```

[Validation](VALIDATION.md), [research](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md), [security](SECURITY.md), [MIT license](LICENSE).

Original implementation, prose and invented fixtures developed with AI assistance. No measured performance-superiority or verified production-adoption claim.
