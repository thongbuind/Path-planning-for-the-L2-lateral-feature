"""Local workbench server: the web UI and the run API over execution.supervisor.

Knows no system under test: the worker commands come from its configuration. It must not
import interfaces, planner, adapters, sim, eval or benchmark (tests/test_import_rules.py).
"""
