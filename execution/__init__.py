"""Execution core shared by every system under test (SUT): run identity, canonical data,
run bundles and the supervision of worker processes.

Standard library only. It knows nothing about the path planner: it must not import
interfaces, planner, adapters, sim, eval, benchmark or workbench (tests/test_import_rules.py).
A SUT package plugs in by providing a worker command and the values it hashes.
"""
