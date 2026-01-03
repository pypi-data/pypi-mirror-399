# Codebase Health Report

**Generated:** 2025-12-31 12:09:32
**Date:** 2025-12-31
**Time:** 12:09:32

---

# Codebase Health Report

**Generated:** 2025-12-31T06:39:14.155020+00:00
**Directory:** `/Users/mthangaraj/my_projects/sage/plint`
**Project Type:** python
**Files Scanned:** 29

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 2 | 🛑 Block |
| High | 13 | ⚠️ Fix soon |
| Medium | 202 | 📋 Backlog |
| Low | 0 | ✅ |

## 🛑 Critical Issues (Action Required)

| Scanner | File | Line | Message | Owner |
|---------|------|------|---------|-------|
| code_quality | `analyzer.py` | 32 | except Exception without re-raise | developer |
| code_quality | `server.py` | 40 | except Exception without re-raise | developer |

## ⚠️ High Priority

| Scanner | File | Line | Message | Owner |
|---------|------|------|---------|-------|
| code_quality | `analyzer.py` | 33 | print() statement found | developer |
| complexity | `reporting.py` | 1 | File complexity 24 (threshold: 12, LOC: 130) | architect |
| code_quality | `server.py` | 11 | Missing return type hint: get_analyzer | developer |
| code_quality | `server.py` | 46 | Missing return type hint: run | developer |
| code_quality | `tokenizer.py` | 11 | print() statement found | developer |
| code_quality | `e2e_verify.py` | 14 | Missing return type hint: setUpClass | developer |
| code_quality | `e2e_verify.py` | 19 | Missing return type hint: test_001_core_framework | developer |
| code_quality | `e2e_verify.py` | 32 | Missing return type hint: test_002_core_metrics | developer |
| code_quality | `e2e_verify.py` | 46 | Missing return type hint: test_003_advanced_metrics | developer |
| code_quality | `e2e_verify.py` | 62 | print() statement found | developer |
| code_quality | `e2e_verify.py` | 63 | print() statement found | developer |
| code_quality | `e2e_verify.py` | 67 | Missing return type hint: test_004_complex_analytics | developer |
| code_quality | `e2e_verify.py` | 90 | Missing return type hint: test_005_reporting | developer |

## By Owner

### architect (4 issues: 0 critical, 1 high)

- ⚠️ `reporting.py:1` - File complexity 24 (threshold: 12, LOC: 130)
- • `classifier.py:18:18` - `classify` complexity 20 > 12
- • `reporting.py:73:73` - `generate_table_report` complexity 14 > 12
- • `reporting.py:9:9` - `generate_markdown_report` complexity 15 > 12

### developer (147 issues: 2 critical, 12 high)

- 🛑 `analyzer.py:32` - except Exception without re-raise
- 🛑 `server.py:40` - except Exception without re-raise
- ⚠️ `analyzer.py:33` - print() statement found
- ⚠️ `server.py:11` - Missing return type hint: get_analyzer
- ⚠️ `server.py:46` - Missing return type hint: run
- ⚠️ `tokenizer.py:11` - print() statement found
- ⚠️ `e2e_verify.py:14` - Missing return type hint: setUpClass
- ⚠️ `e2e_verify.py:19` - Missing return type hint: test_001_core_framework
- *... and 139 more*

### docs_curator (66 issues: 0 critical, 0 high)

- • `ci.yml:1` - YAML file missing header comment
- • `README.md:124` - Redundant init comment
- • `__init__.py:1` - Missing module docstring
- • `__main__.py:1` - Missing module docstring
- • `analyzer.py:1` - Missing module docstring
- • `analyzer.py:15` - Class `Analyzer` missing docstring
- • `analyzer.py:27` - Redundant init comment
- • `analyzer.py:37` - Function `analyze` missing docstring
- *... and 58 more*

## Recommended Actions

1. 🛑 **BLOCK:** Fix critical issues before any deployment
2. Activate `developer` → Fix 147 code issues
3. Activate `architect` → Review 4 architectural issues
4. Activate `pr_reviewer` → Validate documentation (66 issues)
