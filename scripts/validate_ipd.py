"""Verify workbook structure and recalculate independent scheduling scenarios in Calc."""
import copy, datetime as dt, json, subprocess, warnings
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.formula.tokenizer import Tokenizer
warnings.filterwarnings('ignore',category=UserWarning,module='openpyxl')
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'deliverables/智能手表_IPD_WBS_可定制模板.xlsx'
TASKS=json.loads((ROOT/'data/task_library.json').read_text())
V=ROOT/'.verification';(V/'scenarios').mkdir(parents=True,exist_ok=True);(V/'results').mkdir(exist_ok=True)
W=load_workbook(SOURCE)
scope_rows={W['01项目配置'].cell(r,5).value:r for r in range(6,21)}
rows={W['03WBS'].cell(r,1).value:r for r in range(6,406) if W['03WBS'].cell(r,1).value}
keyrows={t['key']:rows[t['id']] for t in TASKS}
formula_count=0
for s in W:
    for row in s:
        for c in row:
            if c.data_type=='f':
                formula_count+=1;balance=0
                for tok in Tokenizer(c.value).items:
                    if tok.type in ['FUNC','PAREN'] and tok.subtype=='OPEN':balance+=1
                    if tok.type in ['FUNC','PAREN'] and tok.subtype=='CLOSE':balance-=1
                    assert balance>=0,(s.title,c.coordinate)
                assert balance==0,(s.title,c.coordinate)
assert len(W.sheetnames)==14
assert len({t['id'] for t in TASKS})==len(TASKS)
assert len({t['wbs'] for t in TASKS})==len(TASKS)
assert all(t['output'] and t['accept'] and t['owner'] and t['approver'] for t in TASKS)

def justdate(v):
    if isinstance(v,dt.datetime):return v.date()
    if isinstance(v,dt.date):return v
    return None

def independent(w):
    conf=w['01项目配置'];sheet=w['03WBS'];start=justdate(conf['B6'].value)
    switches={conf.cell(r,5).value:int(conf.cell(r,6).value or 0) for r in range(6,20)}
    switches['LTE_CN']=int(switches['LTE']==1 and switches['CN']==1)
    holidays={justdate(conf.cell(r,9).value) for r in range(6,206)}-{None}
    makeup={justdate(conf.cell(r,12).value) for r in range(6,206)}-{None}
    week=conf['B9'].value
    def work(d):return d in makeup or (d not in holidays and week[d.weekday()]=='0')
    def normalize(d):
        while not work(d):d+=dt.timedelta(days=1)
        return d
    def add(d,n):
        assert n>=0
        while n:
            d+=dt.timedelta(days=1)
            if work(d):n-=1
        return d
    ready0=normalize(start);out={}
    for t in TASKS:
        r=rows[t['id']];pred=[sheet.cell(r,c).value for c in range(14,18) if sheet.cell(r,c).value]
        ready=max([ready0]+[out[p]['boundary'] for p in pred])
        on=switches[sheet.cell(r,7).value]==1
        mode=sheet.cell(r,8).value
        if mode=='保留':on=True
        if mode=='不适用':on=False
        dur=sheet.cell(r,13).value
        if on:
            ready=add(ready,int(sheet.cell(r,18).value or 0))
            constraint=justdate(sheet.cell(r,19).value)
            if constraint:ready=normalize(max(ready,constraint))
            finish=add(ready,max(dur-1,0));boundary=add(ready,dur)
            out[t['id']]={'active':1,'start':ready,'finish':finish,'boundary':boundary}
        else:out[t['id']]={'active':0,'start':None,'finish':None,'boundary':ready}
    return out

def save_case(name,mutate=None):
    w=load_workbook(SOURCE)
    if mutate:mutate(w)
    w.save(V/'scenarios'/f'{name}.xlsx')
    return w

def full(w):
    c=w['01项目配置'];s=w['03WBS'];c['B6']=dt.datetime(2027,2,1);c['B7']=dt.datetime(2027,2,1)
    for k in ['NFC','LTE','WIFI','ECG','MED','EU','US','RETIRE']:c.cell(scope_rows[k],6,1)
    c['I6']=dt.datetime(2027,2,2);c['I7']=dt.datetime(2027,2,3);c['L6']=dt.datetime(2027,2,6)
    s.cell(keyrows['opportunity'],13,8)
    s.cell(keyrows['voc'],18,2);s.cell(keyrows['voc'],19,dt.datetime(2027,3,1))
    s.cell(keyrows['nfcdev'],8,'不适用')
    s.cell(keyrows['eolplan'],19,dt.datetime(2030,1,1))
    for r in range(6,21):
        if w['04评审门禁'].cell(r,1).value=='ADCP':w['04评审门禁'].cell(r,8,'Hold')

def lean(w):
    c=w['01项目配置'];s=w['03WBS'];c['B6']=dt.datetime(2026,11,15);c['B7']=dt.datetime(2026,11,15)
    for k in ['APP','CLOUD','GNSS']:c.cell(scope_rows[k],6,0)
    c['I6']=dt.datetime(2026,11,16);c['L6']=dt.datetime(2026,11,21)
    s.cell(keyrows['gnssdev'],8,'保留');s.cell(keyrows['bench'],8,'不适用')

def invalid(w):w['03WBS'].cell(keyrows['charter'],14,999999)

cases={'baseline':save_case('baseline'),'full':save_case('full',full),'lean':save_case('lean',lean),'invalid':save_case('invalid',invalid)}
cmd=['libreoffice','-env:UserInstallation=file:///tmp/smartwatch-ipd-tests','--headless','--convert-to','xlsx','--outdir',str(V/'results')]+[str(V/'scenarios'/f'{n}.xlsx') for n in cases]
subprocess.run(cmd,check=True,timeout=240,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
report=[]
for name,original in cases.items():
    calc=load_workbook(V/'results'/f'{name}.xlsx',data_only=True)
    errors=[(s.title,c.coordinate,c.value) for s in calc for row in s for c in row if c.data_type=='e']
    assert not errors,(name,errors[:10])
    if name=='invalid':
        assert calc['03WBS'].cell(keyrows['charter'],34).value!='通过'
        assert calc['03WBS'].cell(keyrows['ga'],34).value!='通过'
        assert justdate(calc['03WBS'].cell(keyrows['ga'],20).value) is None
        assert calc['06项目看板']['B12'].value>0
        report.append({'scenario':name,'result':'通过','checks':'无效前置检出、错误向后继传播、GA日期清空、看板提示'})
        continue
    expected=independent(original)
    for t in TASKS:
        r=rows[t['id']];v=expected[t['id']]
        assert calc['03WBS'].cell(r,9).value==v['active'],(name,t['key'],'active')
        for c,k in [(20,'start'),(21,'finish')]:
            actual=justdate(calc['03WBS'].cell(r,c).value)
            assert actual==v[k],(name,t['key'],k,actual,v[k])
        for c in [22,23]:
            assert calc['03WBS'].cell(r,c).value==original['03WBS'].cell(r,c).value,(name,t['key'],'baseline changed')
        assert calc['03WBS'].cell(r,34).value=='通过',(name,t['key'],'invalid')
    if name=='full':assert calc['06项目看板']['B15'].value==1
    if name=='baseline':
        cached=load_workbook(SOURCE,data_only=True)
        differences=[]
        for s in cached:
            for row in s:
                for c in row:
                    a,b=c.value,calc[s.title][c.coordinate].value
                    if a in [None,''] and b in [None,'']:continue
                    if a!=b:differences.append((s.title,c.coordinate,str(a),str(b)))
        assert not differences,differences[:20]
    gate=next(t for t in TASKS if t['key']=='ga')
    report.append({'scenario':name,'result':'通过','tasks_compared':len(TASKS),'predicted_GA':str(expected[gate['id']]['start']),'formula_errors':len(errors)})
result={'engine':'LibreOffice Calc 26.2','sheets':14,'tasks':len(TASKS),'formula_count':formula_count,'scenarios':report,'scope':'独立逐日排期算法对照、400行公式结构、全表缓存一致性、基线保持、错误传播；未在Microsoft Excel/WPS客户端实机测试'}
(ROOT/'deliverables/验证报告.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
