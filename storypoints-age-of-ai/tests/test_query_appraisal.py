import csv, json
from pathlib import Path
import tempfile
import pytest
from gate2.query_appraisal import (AppraisalError, appraise,
                                   deterministic_sample_positions,
                                   required_sample_size)

REGISTRY = {"sentinels": [
    {"sentinel_id":"P","doi":"10.1/P","role":"positive"},
    {"sentinel_id":"N","doi":"10.1/N","role":"negative_boundary"}],
    "status":"development_pilot", "version":"test", "queries":[],
    "sampled_precision_rule":{"required_fields":["source_id","decision","reason"],
    "allowed_decisions":["likely_relevant","likely_irrelevant","uncertain"],
    "development_diagnostic_minimum_sample":1,
    "freeze_sample_bands":[
        {"population_min":0,"population_max":50,"required_sample":"all"},
        {"population_min":51,"population_max":1000,"required_sample":50},
        {"population_min":1001,"population_max":None,"required_sample":100}],
    "acceptance_bands":{"operational_minimum_relevant_plus_uncertain":0.10,
    "conditional_minimum_relevant_plus_uncertain":0.05,
    "conditional_requires_documented_capacity_and_coverage_approval":True}}}

def fixture(tmp, *, complete=False, total=1, record_count=1):
    (tmp/'manifest.json').write_text(json.dumps({"status":"development_pilot","source":"openalex","query_id":"Q",
        "complete_pagination":complete,"total_reported":total,"records_retrieved":record_count}))
    with (tmp/'records.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['source_id','doi']); w.writeheader()
        for i in range(record_count):
            w.writerow({'source_id':'x' if i == 0 else f'x{i}',
                        'doi':'https://doi.org/10.1/P' if i == 0 else ''})

def test_incomplete_export_can_pass_diagnostic_but_never_freeze():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); fixture(p)
        result=appraise(p,REGISTRY,[{'source_id':'x','decision':'likely_relevant','reason':'in scope'}])
        assert result['positive_sentinel_recall_pass'] and result['negative_boundary_pass']
        assert result['sample_precision_point_estimate']==1
        assert result['development_diagnostic_pass']
        assert not result['freeze_ready'] and not result['query_appraisal_pass']

def test_complete_small_export_requires_all_records_and_can_freeze():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); fixture(p,complete=True,total=2,record_count=2)
        one=[{'source_id':'x','decision':'likely_relevant','reason':'in scope'}]
        result=appraise(p,REGISTRY,one)
        assert result['required_sample_size_for_freeze']==2
        assert not result['sample_minimum_met'] and not result['freeze_ready']
        both=one+[{'source_id':'x1','decision':'likely_irrelevant','reason':'noise'}]
        result=appraise(p,REGISTRY,both)
        assert result['sample_minimum_met'] and result['freeze_ready']
        assert result['development_diagnostic_pass']
        assert result['development_diagnostic_required_for_population']==1

def test_appendix_sample_bands_and_incomplete_projected_total_are_enforced():
    assert [required_sample_size(n) for n in (0,50,51,1000,1001)] == [0,50,50,50,100]
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); fixture(p,complete=False,total=134,record_count=100)
        decisions=[{'source_id':f'x{i}' if i else 'x','decision':'likely_relevant','reason':'diagnostic'}
                   for i in range(20)]
        result=appraise(p,REGISTRY,decisions)
        assert result['population_size_for_sample']==134
        assert result['population_size_basis']=='incomplete_export_reported_total_projection'
        assert result['required_sample_size_for_freeze']==50
        assert result['development_diagnostic_pass'] and not result['sample_minimum_met']
        assert not result['freeze_ready']

def test_deterministic_sample_has_boundary_hash_and_middle_coverage():
    positions,digest=deterministic_sample_positions(134,'openalex','S3','0.3')
    assert len(positions)==50 and positions[:10]==list(range(10))
    assert positions[-10:]==list(range(124,134))
    assert len(digest)==64
    assert deterministic_sample_positions(134,'openalex','S3','0.3')==(positions,digest)
    large,_=deterministic_sample_positions(1200,'openalex','S5S','0.3')
    assert len(large)==100 and set(range(595,605)).issubset(large)

def test_burden_acceptance_bands_fail_closed():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); fixture(p,complete=True,total=20,record_count=20)
        ids=['x']+[f'x{i}' for i in range(1,20)]
        decisions=[{'source_id':rid,'decision':'likely_irrelevant','reason':'noise'} for rid in ids]
        result=appraise(p,REGISTRY,decisions)
        assert result['burden_acceptance_band']=='revise_or_split'
        assert not result['freeze_ready']
        decisions[0]['decision']='uncertain'
        result=appraise(p,REGISTRY,decisions)
        assert result['burden_acceptance_band']=='conditional_review_required'
        assert not result['freeze_ready']

def test_registry_bands_cannot_drift_from_appendix():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); fixture(p)
        bad=json.loads(json.dumps(REGISTRY)); bad['sampled_precision_rule']['freeze_sample_bands'][1]['required_sample']=20
        with pytest.raises(AppraisalError,match='Appendix 4.2'):
            appraise(p,bad,[{'source_id':'x','decision':'likely_relevant','reason':'x'}])

def test_bad_sample_id_fails_closed():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); fixture(p)
        with pytest.raises(AppraisalError,match='absent'):
            appraise(p,REGISTRY,[{'source_id':'missing','decision':'likely_relevant','reason':'x'}])

def test_checked_in_oa_s3r_complete_appraisal_rederives_exactly():
    root=Path(__file__).parents[1]
    registry=json.loads((root/'gate2/open_index_pilot_queries.json').read_text())
    decision_artifact=json.loads((root/'gate2/output/development/query_appraisals/OA-S3R-20260815-query-decisions-v2.json').read_text())
    result=appraise(root/'gate2/output/development/openalex/OA-S3R-20260815-pilot2-complete',
                    registry,decision_artifact['decisions'])
    checked=json.loads((root/'gate2/output/development/query_appraisals/OA-S3R-20260815-query-appraisal-v2.json').read_text())
    assert result == checked
    assert result['freeze_ready'] and result['sample_size']==50
    assert result['relevant_plus_uncertain_count']==13

def test_v03_requires_family_scoped_positive_and_neutral_sentinels():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)
        (p/'manifest.json').write_text(json.dumps({
            'status':'development_pilot','source':'openalex','query_id':'OA-S3',
            'query':'exact query','complete_pagination':True,'total_reported':2,
            'records_retrieved':2}))
        with (p/'records.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['source_id','doi','title']); w.writeheader()
            w.writerow({'source_id':'p','doi':'10.1/P','title':'Positive'})
            w.writerow({'source_id':'d','doi':'','title':'Disconfirming Story Points'})
        registry=json.loads(json.dumps(REGISTRY))
        registry.update({'version':'0.3','sentinel_control_version':'family_scoped_v0.3',
                         'queries':[{'source':'openalex','query_id':'OA-S3','family_id':'S3','query':'exact query'}],
                         'sentinels':[
                             {'sentinel_id':'P','family_id':'S3','role':'scope_positive','doi':'10.1/P','title':'Positive','testable_sources':['openalex']},
                             {'sentinel_id':'D','family_id':'S3','role':'neutral_disconfirming','doi':'10.1/D','title':'Disconfirming Story Points','testable_sources':['openalex']},
                             {'sentinel_id':'B','family_id':'S3','role':'negative_boundary','doi':'10.1/B','title':'Boundary','testable_sources':['openalex']} ]})
        decisions=[{'source_id':'p','decision':'likely_relevant','reason':'scope'},
                   {'source_id':'d','decision':'likely_relevant','reason':'constraint'}]
        result=appraise(p,registry,decisions)
        assert result['sentinel_class_complete']
        assert result['positive_sentinel_recall_pass']
        assert result['neutral_disconfirming_recall_pass']
        assert result['negative_boundary_pass'] and result['freeze_ready']
        registry['sentinels'][-1]['title']='Disconfirming Story Points'
        result=appraise(p,registry,decisions)
        assert not result['negative_boundary_pass'] and result['freeze_ready']
        registry['sentinels']=[row for row in registry['sentinels'] if row['role']!='neutral_disconfirming']
        result=appraise(p,registry,decisions)
        assert not result['sentinel_class_complete'] and not result['freeze_ready']

def test_v03_rejects_manifest_query_drift():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); fixture(p,complete=True,total=1,record_count=1)
        manifest=json.loads((p/'manifest.json').read_text()); manifest['query']='changed'
        (p/'manifest.json').write_text(json.dumps(manifest))
        registry=json.loads(json.dumps(REGISTRY))
        registry.update({'version':'0.3','sentinel_control_version':'family_scoped_v0.3',
                         'queries':[{'source':'openalex','query_id':'Q','family_id':'S3','query':'registered'}]})
        with pytest.raises(AppraisalError,match='does not match'):
            appraise(p,registry,[{'source_id':'x','decision':'likely_relevant','reason':'x'}])

def test_checked_in_v03_appraisals_rederive_exactly():
    root=Path(__file__).parents[1]
    registry=json.loads((root/'gate2/open_index_pilot_queries_v0.3.json').read_text())
    cases=[
        ('gate2/output/development/openalex/OA-S3R3-20260815-pilot1',
         'gate2/output/development/query_appraisals/OA-S3R3-20260815-query-decisions-v1.json',
         'gate2/output/development/query_appraisals/OA-S3R3-20260815-query-appraisal-v1.json'),
        ('gate2/output/development/semantic_scholar/S2-S3R3-20260815-pilot1',
         'gate2/output/development/query_appraisals/S2-S3R-20260815-query-decisions-v1.json',
         'gate2/output/development/query_appraisals/S2-S3R3-20260815-query-appraisal-v1.json')]
    for export,decisions,result_path in cases:
        rows=json.loads((root/decisions).read_text())['decisions']
        assert appraise(root/export,registry,rows)==json.loads((root/result_path).read_text())


def test_checked_in_s5t_openalex_appraisal_rederives_exactly():
    root=Path(__file__).parents[1]
    registry=json.loads((root/'research/studies/vdcm/evidence-map/registries/s5t_open_index_queries_v0.4.json').read_text())
    decisions=json.loads((root/'gate2/output/development/query_appraisals/OA-S5TR4-20260816-query-decisions-v1.json').read_text())['decisions']
    result=appraise(root/'gate2/output/development/openalex/OA-S5TR4-20260816-pilot1',registry,decisions)
    checked=json.loads((root/'gate2/output/development/query_appraisals/OA-S5TR4-20260816-query-appraisal-v1.json').read_text())
    assert result==checked
    assert result['freeze_ready'] and result['sample_size']==50
    assert result['neutral_disconfirming_recall_pass']


def test_checked_in_s5s_openalex_appraisal_rederives_exactly():
    root=Path(__file__).parents[1]
    registry=json.loads((root/'research/studies/vdcm/evidence-map/registries/s5s_open_index_queries_v0.7.json').read_text())
    decisions=json.loads((root/'gate2/output/development/query_appraisals/OA-S5SR7-20260816-query-decisions-v1.json').read_text())['decisions']
    result=appraise(root/'gate2/output/development/openalex/OA-S5SR7-20260816-pilot1',registry,decisions)
    checked=json.loads((root/'gate2/output/development/query_appraisals/OA-S5SR7-20260816-query-appraisal-v1.json').read_text())
    assert result==checked
    assert result['freeze_ready'] and result['sample_size']==19
    assert result['neutral_disconfirming_recall_pass']


def test_checked_in_s6_openalex_appraisal_rederives_exactly():
    root=Path(__file__).parents[1]
    registry=json.loads((root/'research/studies/vdcm/evidence-map/registries/s6_open_index_queries_v0.8.json').read_text())
    decision_artifact=json.loads((root/'gate2/output/development/query_appraisals/OA-S6R8-20260816-query-decisions-v1.json').read_text())
    positions,seed=deterministic_sample_positions(231,'openalex','S6','0.8')
    assert positions==decision_artifact['sample_positions_zero_based']
    assert seed==decision_artifact['sampling_seed_sha256']
    with (root/'gate2/output/development/openalex/OA-S6R8-20260816-pilot1/records.csv').open() as handle:
        records=list(csv.DictReader(handle))
    assert [records[index]['source_id'] for index in positions]==[
        row['source_id'] for row in decision_artifact['decisions']]
    result=appraise(root/'gate2/output/development/openalex/OA-S6R8-20260816-pilot1',
                    registry,decision_artifact['decisions'])
    checked=json.loads((root/'gate2/output/development/query_appraisals/OA-S6R8-20260816-query-appraisal-v1.json').read_text())
    assert result==checked
    assert result['freeze_ready'] and result['sample_size']==50
    assert result['positive_sentinel_recall_pass']
    assert result['neutral_disconfirming_recall_pass']
    assert not result['negative_boundary_pass']
