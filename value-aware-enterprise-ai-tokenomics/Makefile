.PHONY: test verify

test:
	node --test studies/ovar/pilot/tests/pilot_v1.0.test.mjs
	node --test studies/ovar/calibration/tests/candidate_v1.0.test.mjs
	node --test studies/ovar/calibration/tests/reference_labels_v1.0.test.mjs
	node --test studies/ovar/calibration/tests/calibration_policies_v1.0.test.mjs

verify: test
	python3 scripts/verify_repository.py
