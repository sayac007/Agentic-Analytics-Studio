"""Synthetic source-layout checks; actual private observations never enter CI."""
import copy
import csv
import io
import json
import unittest
from unittest.mock import patch

from source_acquisition.normalize import credit, cpi, coverage
from source_acquisition.fetch_sources import fetch_review


def credit_fixture(**changes):
    row={'KEY':'MIR.M.DE.B.A2B.A.R.A.2250.EUR.N','FREQ':'M','REF_AREA':'DE','BS_ITEM':'A2B',
         'MATURITY_NOT_IRATE':'A','DATA_TYPE_MIR':'R','IR_BUS_COV':'N','BS_COUNT_SECTOR':'2250',
         'CURRENCY_TRANS':'EUR','UNIT':'PCPA','UNIT_MULT':'0','TIME_PERIOD':'2018-01','OBS_VALUE':'3.125','OBS_STATUS':'A'}
    row.update(changes);f=io.StringIO();w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerow(row);return f.getvalue().encode()


def cpi_fixture():
    dims={'statistic':{'61111':0},'DINSG':{'DG':0},'content':{'PREIS1$QMU':0,'PREIS1$CH0004':1,'PREIS1$CH0005':2},'MONAT':{'MONAT01':0,'MONAT02':1},'JAHR':{'2018':0}}
    d={'data':[{'id':list(dims),'size':[len(v) for v in dims.values()],
        'dimension':{k:{'category':{'index':v}} for k,v in dims.items()},'value':[101,102,7,8,9,10],'status':['e']*6}]}
    s={'table':{'code':'61111-0002'},'contents':{'PREIS1':{'functions':{'QMU':{'label':{'de':'2020=100'}}}}}}
    q={'signsReplacingValue':['-','.'],'signsWithValue':['e','p','r']}
    return d,s,q


class VerifiedSourceTests(unittest.TestCase):
    def test_credit_is_aar_not_aprc_and_native_units(self):
        row=credit(credit_fixture())[0];self.assertEqual(row['value'],3.125);self.assertEqual(row['unit'],'percent_per_annum')
        for changes in [{'DATA_TYPE_MIR':'C'},{'UNIT':'USD'},{'UNIT_MULT':'2'},{'OBS_VALUE':'NaN'},{'REF_AREA':'FR'}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):credit(credit_fixture(**changes))
        with self.assertRaises(ValueError):credit(b'<html>Announcement, not CSV</html>')
        self.assertIsNone(credit(credit_fixture(OBS_VALUE='',OBS_STATUS='M'))[0]['value'])

    def test_cpi_selects_index_not_change_and_preserves_missing_status(self):
        d,s,q=cpi_fixture()
        rows=cpi(*(json.dumps(v).encode() for v in (d,s,q)))
        self.assertEqual([r['value'] for r in rows],[101,102])
        d['data'][0]['value'][1]=0;d['data'][0]['status'][1]='-'
        rows=cpi(*(json.dumps(v).encode() for v in (d,s,q)))
        self.assertIsNone(rows[1]['value']);self.assertEqual(coverage(rows)['present'],1)
        wrong=copy.deepcopy(s);wrong['contents']['PREIS1']['functions']['QMU']['label']['de']='2015=100'
        with self.assertRaises(ValueError):cpi(*(json.dumps(v).encode() for v in (d,wrong,q)))

    def test_duplicate_dimensions_and_wrong_country_are_refused(self):
        for key,value in [('DINSG',{'FR':0}),('statistic',{'61121':0})]:
            d,s,q=cpi_fixture();d['data'][0]['dimension'][key]['category']['index']=value
            with self.subTest(key=key),self.assertRaises(ValueError):cpi(*(json.dumps(v).encode() for v in (d,s,q)))
        d,s,q=cpi_fixture();d['data'][0]['value'].pop()
        with self.assertRaises(ValueError):cpi(*(json.dumps(v).encode() for v in (d,s,q)))

    def test_failed_request_is_not_timestamped_or_hashed_as_data(self):
        with patch('urllib.request.urlopen',side_effect=OSError('network failure')):
            row,raw=fetch_review(('ecb','fixture','https://www.ecb.europa.eu/fixture'))
        self.assertIsNone(raw);self.assertIsNone(row['accessed_at_utc']);self.assertIsNone(row['sha256'])
        self.assertTrue(row['attempted_at_utc'].endswith('+00:00'))
        self.assertIn('network failure',row['error'])


if __name__=='__main__':unittest.main()

class RightsBeforeAcquisitionTests(unittest.TestCase):
    def test_no_numeric_fetch_when_primary_policy_is_missing(self):
        import tempfile
        from pathlib import Path
        from source_acquisition.fetch_sources import run, REQUESTS
        calls=[]
        def denied(item):
            calls.append(item)
            return {'source':item[0],'role':item[1],'url':item[2],'status':403,
                    'raw_path':None,'sha256':None,'error':'synthetic refusal'},None
        with tempfile.TemporaryDirectory() as td, patch('source_acquisition.fetch_sources.fetch_review',side_effect=denied):
            with self.assertRaisesRegex(ValueError,'Missing primary rights'):
                run(Path(td)/'private',acquire=True)
        self.assertEqual(len(calls),len(REQUESTS))
        self.assertFalse(any(role in ('native_csv','verified_base_data') for _,role,_ in calls))
