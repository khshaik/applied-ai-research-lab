.PHONY: test verify manuscript-check manuscript-release-check prelock

test:
	@if [ -f PUBLIC_RELEASE_MANIFEST.json ]; then \
		python3 -m pytest -q \
			--ignore=tests/test_fulltext_consensus_audit.py \
			--ignore=tests/test_fulltext_consensus_rereview.py \
			--ignore=tests/test_fulltext_extraction.py \
			--ignore=tests/test_fulltext_finalize.py \
			--ignore=tests/test_fulltext_retrieval.py \
			--ignore=tests/test_fulltext_screening.py \
			--ignore=tests/test_quality_appraisal.py \
			--ignore=tests/test_quality_appraisal_finalize.py \
			--ignore=tests/test_quality_appraisal_reconcile.py; \
	else \
		python3 -m simulation.test_runner --quiet; \
	fi

verify: test
	@if [ -f PUBLIC_RELEASE_MANIFEST.json ]; then \
		python3 scripts/verify_public_release.py .; \
	else \
		python3 scripts/verify_repository.py; \
	fi
	python3 scripts/verify_manuscript.py --json

manuscript-check:
	python3 scripts/verify_manuscript.py --json

manuscript-release-check:
	python3 scripts/verify_manuscript.py --release --json

prelock:
	python3 -m simulation.prelock --json
