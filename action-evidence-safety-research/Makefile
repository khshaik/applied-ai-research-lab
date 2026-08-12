.PHONY: test verify

test:
	python3 studies/raer/evaluation/test_raer_benchmark.py
	python3 studies/raer/evaluation/v2/test_raer_v2_design.py

verify: test
	python3 scripts/verify_repository.py

