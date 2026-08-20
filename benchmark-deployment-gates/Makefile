.PHONY: extract analyze verify clean

extract:
	python3 scripts/extract_raer_results.py
	python3 scripts/extract_ovar_results.py
	python3 scripts/extract_vdcm_results.py

analyze:
	python3 scripts/rank_reversal_analysis.py
	python3 scripts/threshold_sensitivity.py

verify:
	python3 scripts/verify_integrity.py

clean:
	rm -rf studies/cross-study/data/*.json
	rm -rf studies/cross-study/data/*.csv
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
