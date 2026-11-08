#!/usr/bin/env python3
"""Build an editable, macro-free IPD workbook with cached formula results."""
from __future__ import annotations
import bisect, collections, csv, datetime as dt, json, sys, zipfile
from pathlib import Path
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name as col, xl_rowcol_to_cell as cell
from wbs_data import TASKS, SOURCES, GATE_INFO

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'; OUT.mkdir(exist_ok=True)
START=dt.date(2026,11,9); STATUS=START; TARGET=dt.date(2028,3,31)
FIRST=5; SLOTS=400; LAST=FIRST+SLOTS; WEEKS=104
CALSTART=dt.date(START.year-1,1,1); CALDAYS=4383
SCOPES=[('BASE',1,'基础产品包/治理活动'),('APP',1,'配套手机App'),('CLOUD',1,'配套云服务'),('GNSS',1,'独立卫星定位'),('NFC',0,'按实际用途裁剪'),('LTE',0,'蜂窝/eSIM'),('WIFI',0,'Wi-Fi'),('ECG',0,'ECG功能；不自动等同医疗用途'),('MED',0,'医疗用途/诊疗宣称；须专项注册计划'),('CN',1,'中国大陆市场（示例）'),('EU',0,'欧盟市场'),('US',0,'美国市场'),('RETIRE',0,'退出/退市工作包，按触发时点启用'),('OTHER',0,'其他市场：须新增认证任务'),('LTE_CN',0,'自动：LTE且CN')]
SWITCH={s:v for s,v,_ in SCOPES}
PHASES=list(dict.fromkeys(t['phase'] for t in TASKS))
ROLES={'PM':'整机项目经理/PDT执行统筹','PDT负责人':'项目端到端交付负责人','IPMT':'投资与产品组合决策组织','技术评审组':'跨领域技术与质量评审组织','产品经理':'产品定义与商业结果','系统架构':'系统方案与跨域接口','ID/UX':'工业设计、CMF与交互体验','结构':'结构、密封、光学窗口与模具','硬件':'电子、电源与电池设计','RF':'天线、射频、GNSS与蜂窝','固件':'BSP、驱动、系统、OTA与固件版本','算法':'运动健康算法与证据','App':'手机应用、兼容及分发','云端':'后端服务、运维与数据可靠性','测试':'需求验证、系统测试及回归','可靠性':'环境、机械、防水和寿命验证','QA':'质量策划、独立监督与放行','法规认证':'市场准入、标准与认证配置','安全隐私':'安全设计、隐私与漏洞响应','NPI':'工艺、产测、校准和量产导入','采购':'物料、供应商、产能与物流','财务':'商业计划、投资预算与成本','服务':'售后、维修、备件与客服','市场':'渠道、上市与营销执行'}

ids={t['key']:1001+i for i,t in enumerate(TASKS)}
stream_counts=collections.defaultdict(int); phase_streams={}
for t in TASKS:
    streams=phase_streams.setdefault(t['phase'],[])
    if t['stream'] not in streams: streams.append(t['stream'])
    stream_counts[(t['phase'],t['stream'])]+=1
    t['id']=ids[t['key']]
    t['wbs']=f"{t['phase'][0]}.{streams.index(t['stream'])+1:02d}.{stream_counts[(t['phase'],t['stream'])]:02d}"
    t['pred']=[ids[k] for k in t['deps']]

def calendar(start=START, holidays=(), makeup=(), weekend='0000011'):
    origin=dt.date(start.year-1,1,1); days=[]; works=[]; rank={}; before={}; n=0
    for i in range(CALDAYS):
        d=origin+dt.timedelta(days=i)
        work=d in makeup or (d not in holidays and weekend[d.weekday()]=='0')
        before[d]=n
        if work: n+=1; works.append(d)
        rank[d]=n; days.append((d,work,n))
    return days,works,before,rank

def schedule(tasks=TASKS,start=START,switch=None,holidays=(),makeup=(),weekend='0000011'):
    sw=dict(SWITCH if switch is None else switch); sw['LTE_CN']=int(sw.get('LTE',0)==1 and sw.get('CN',0)==1)
    days,works,before,rank=calendar(start,holidays,makeup,weekend)
    res={}; p=before[start]
    for t in tasks:
        if len(t['pred'])>4: raise ValueError(f"Too many predecessors: {t['key']}")
        bounds=[]
        for pred in t['pred']:
            if pred not in res: raise ValueError(f"Missing or non-topological predecessor: {t['key']} {pred}")
            bounds.append(res[pred]['boundary'])
        ready=max([p]+bounds)
        active=sw.get(t['scope'],0)==1
        if t.get('override')=='保留': active=True
        if t.get('override')=='不适用': active=False
        if active:
            ready=max(p,ready+t.get('lag',0),before.get(t.get('constraint',start),p))
            endord=ready+max(t['days'],1)-1
            res[t['id']]={'active':1,'start':works[ready], 'finish':works[endord], 'boundary':ready+t['days'],'startord':ready}
        else: res[t['id']]={'active':0,'start':None,'finish':None,'boundary':ready,'startord':ready}
    return res,(days,works,before,rank)

RES,CAL=schedule(); days,workdates,before,rank=CAL
def serial(d): return (d-dt.date(1899,12,30)).days if d else ''
def valdate(d): return serial(d)
def fmtdate(d): return d.isoformat() if d else ''
def task_by_key(k): return next(t for t in TASKS if t['key']==k)
def row_for_key(k): return FIRST+next(i for i,t in enumerate(TASKS) if t['key']==k)

wb=xlsxwriter.Workbook(str(OUT/'智能手表_IPD_WBS_可定制模板.xlsx'),{'use_future_functions':True})
wb.set_properties({'title':'智能手表 IPD WBS 可定制计划','subject':'公开IPD实践 + 智能手表项目裁剪模板','author':'项目管理工作模板','comments':'无宏；全部任务和工期均为可修改建议，非任何公司的完整内部流程。'})
wb.set_calc_mode('auto')
wb.define_name('ScopeCodes',"='01项目配置'!$E$6:$E$20")
NAVY='#16324F'; TEAL='#007F86'; BLUE='#1565C0'; LIGHT='#EAF4FC'; GRAY='#F2F5F8'; RED='#B42318'; WHITE='#FFFFFF'
formats={}
def f(name,**kw):
    if name not in formats: formats[name]=wb.add_format({'font_name':'Microsoft YaHei','font_size':10,'valign':'top',**kw})
    return formats[name]
TITLE=f('title',font_size=21,bold=True,font_color=WHITE,bg_color=NAVY,valign='vcenter')
SUB=f('sub',font_color='#52677D',text_wrap=True)
HEAD=f('head',bold=True,font_color=WHITE,bg_color=TEAL,text_wrap=True,valign='vcenter',border=1,border_color=WHITE)
TEXT=f('text',text_wrap=True,bottom=1,bottom_color='#E4EAF0')
INPUT=f('input',font_color=BLUE,bg_color=LIGHT,text_wrap=True,bottom=1,bottom_color='#D1E4F3')
NUM=f('num',font_color=BLUE,bg_color=LIGHT,num_format='0.0',bottom=1,bottom_color='#D1E4F3')
INT=f('int',font_color=BLUE,bg_color=LIGHT,num_format='0',bottom=1,bottom_color='#D1E4F3')
DATE=f('date',num_format='yyyy-mm-dd',bg_color=GRAY)
DIN=f('date_input',num_format='yyyy-mm-dd',font_color=BLUE,bg_color=LIGHT)
PCT=f('pct_input',num_format='0%',font_color=BLUE,bg_color=LIGHT)
FORM=f('formula',bg_color=GRAY,text_wrap=True)
MONEY=f('money',num_format='#,##0.00',font_color=BLUE,bg_color=LIGHT)
LINK=f('link',font_color=BLUE,underline=True,text_wrap=True)
GOOD=f('good',font_color='#17633D',bg_color='#E6F4EA')
BAD=f('bad',font_color=RED,bg_color='#FDE9E7')
WARN=f('warn',font_color='#925600',bg_color='#FFF0C2')
MILE=f('mile',font_color=NAVY,bold=True,bg_color='#D7E8F7',text_wrap=True)
SMALL=f('small',font_size=9,font_color='#617487',text_wrap=True)
WORK=f('work',num_format='0',bg_color=GRAY)

SHEETS=['00使用说明','01项目配置','02IPD流程','03WBS','04评审门禁','05周甘特','06项目看板','07风险台账','08变更台账','09职责资源','10认证矩阵','11需求追踪','12来源依据','13工作日历']
ws={n:wb.add_worksheet(n) for n in SHEETS}
def banner(s,title,note,lastcol=7):
    s.hide_gridlines(2);s.set_zoom(85);s.set_tab_color(TEAL)
    s.merge_range(0,0,0,lastcol,title,TITLE);s.set_row(0,40)
    s.merge_range(1,0,1,lastcol,note,SUB);s.set_row(1,34)
    for j,(label,target) in enumerate([('使用说明','00使用说明'),('项目配置','01项目配置'),('WBS主表','03WBS'),('项目看板','06项目看板')]):
        s.write_url(2,j,f"internal:'{target}'!A1",LINK,label)
    s.freeze_panes(5,0);s.set_landscape();s.fit_to_pages(1,0);s.set_paper(9)
    s.set_footer('&L智能手表 IPD｜可定制模板&R第 &P 页 / &N 页')
def headers(s,labels):
    for j,label in enumerate(labels): s.write(4,j,label,HEAD)
    s.set_row(4,32)
def write_rows(s,labels,rows,widths=None):
    headers(s,labels)
    for i,row in enumerate(rows,FIRST):
        for j,v in enumerate(row): s.write(i,j,v,TEXT)
        s.set_row(i,58)
    if rows: s.autofilter(4,0,FIRST+len(rows)-1,len(labels)-1)
    for j,w in enumerate(widths or [18]*len(labels)): s.set_column(j,j,w)
    s.print_area(0,0,FIRST+len(rows),len(labels)-1)
def formula(s,r,c,expr,cached='',style=FORM): s.write_formula(r,c,expr,style,cached)

# Configuration: dates are real Excel dates. Exception lists are keyed by date.
s=ws['01项目配置'];banner(s,'项目配置 / 功能裁剪 / 日历例外','蓝色单元格可编辑。默认：中国大陆蓝牙运动健康手表 + App/云 + GNSS；全部为示例。',12)
s.set_column('A:A',23);s.set_column('B:B',23);s.set_column('C:C',43);s.set_column('D:D',3);s.set_column('E:E',15);s.set_column('F:F',11);s.set_column('G:G',44);s.set_column('H:H',3);s.set_column('I:I',15);s.set_column('J:J',28);s.set_column('K:K',3);s.set_column('L:L',15);s.set_column('M:M',28)
config=[('项目名称','智能手表示例项目','替换为项目代号/型号'),('项目启动日',START,'排期起点；改变日期自动重排，基线保持不变'),('状态日期',STATUS,'用于判断逾期；请按周更新'),('目标GA日期',TARGET,'仅作差异对照，不会倒推或强压任务工期'),('每周休息模式','0000011','从周一到周日：0工作，1休息；默认周末休息'),('甘特起始周',START,'自动取启动日所在周的周一'),('甘特周数',WEEKS,'固定展示104周，横向滚动；超范围在看板提示'),('模板基线日期',dt.date(2026,11,8),'示例基线；批准计划后按说明手工更新V/W列'),('排期规则','FS + 非负工作日间隔','前置完成后开始；0工期评审不额外占一天'),('续航目标','待项目批准','使用场景、采样、亮度、连接、定位必须同时定义'),('防水目标/场景','待项目批准','等级、方法、动态使用、老化复测和保修边界需一并定义'),('PVT良率/产能目标','待制造与QA批准','按工位/直通/最终良率分别定义，不使用统一默认阈值'),('样本量/统计置信','见已批DVP&R','由风险、用途、试验方法和量产要求确定'),('软件/安全支持期','待项目批准','生命周期观察窗口不等于承诺支持期'),('资源排平','未自动排平','排期按逻辑依赖；需结合09职责资源确认人力/设备'),('日期覆盖',f'{CALSTART} 至 {CALSTART+dt.timedelta(days=CALDAYS-1)}','日历从启动年份前一年起连续4383天；异常日期会提示')]
for i,(k,v,n) in enumerate(config,4):
    s.write(i,0,k,TEXT);s.write(i,2,n,SMALL)
    if isinstance(v,dt.date): s.write_number(i,1,serial(v),DIN)
    else: s.write(i,1,v,INPUT)
formula(s,9,1,"=B6-WEEKDAY(B6,2)+1",serial(START),DATE)
s.write_row(4,4,['范围码','开关 1/0','说明'],HEAD)
scope_rows={}
for i,(code,on,desc) in enumerate(SCOPES,5):
    scope_rows[code]=i+1;s.write(i,4,code,TEXT);s.write(i,5,on,INT);s.write(i,6,desc,SMALL);s.set_row(i,32)
formula(s,scope_rows['LTE_CN']-1,5,f'=--AND(F{scope_rows["LTE"]}=1,F{scope_rows["CN"]}=1)',0,WORK)
s.data_validation(5,5,5+len(SCOPES)-2,5,{'validate':'integer','criteria':'between','minimum':0,'maximum':1,'input_message':'1启用；0停用。BASE建议保持1。','error_type':'stop'})
s.data_validation(8,1,8,1,{'validate':'list','source':['0000011','0000001','0000000']})
s.write_row(4,8,['额外休息日','备注'],HEAD);s.write_row(4,11,['额外工作日/补班','备注'],HEAD)
for r in range(5,205):
    for c in [8,11]:s.write_blank(r,c,None,DIN)
    for c in [9,12]:s.write_blank(r,c,None,INPUT)
s.data_validation(5,8,204,8,{'validate':'date','criteria':'between','minimum':dt.datetime(2020,1,1),'maximum':dt.datetime(2050,12,31)})
s.data_validation(5,11,204,11,{'validate':'date','criteria':'between','minimum':dt.datetime(2020,1,1),'maximum':dt.datetime(2050,12,31)})
s.merge_range(23,0,25,6,'节假日尚未填入。请按项目所在地及工厂日历维护右侧日期清单；周末补班填入“额外工作日”。同一天同时填入两表时按补班处理，看板会提示冲突。日期清单在改变启动日后仍按实际日期匹配。',WARN)
s.print_area(0,0,26,12)

# Working calendar ranks allow Chinese make-up working weekends.
s=ws['13工作日历'];banner(s,'工作日历 / 排期计算依据','由01项目配置的每周模式、额外休息日和补班日期生成。该页为公式区，请通过配置表修改日历。',6)
headers(s,['日期','星期','常规工作日','例外类型','实际工作日 1/0','累计工作日序号','当日之前工作日数'])
s.set_column('A:A',16);s.set_column('B:D',20);s.set_column('E:G',22)
for i,(d,iswork,n) in enumerate(days,FIRST):
    er=i+1; raw=int(d.weekday()<5);prev=n-int(iswork)
    expr="=DATE(YEAR('01项目配置'!$B$6)-1,1,1)" if i==FIRST else f'=A{er-1}+1'
    formula(s,i,0,expr,serial(d),DATE)
    formula(s,i,1,f'=WEEKDAY(A{er},2)',d.weekday()+1,WORK)
    formula(s,i,2,f'=--(MID(\'01项目配置\'!$B$9,B{er},1)="0")',raw,WORK)
    formula(s,i,3,f'=IF(COUNTIF(\'01项目配置\'!$L$6:$L$205,A{er})>0,"补班",IF(COUNTIF(\'01项目配置\'!$I$6:$I$205,A{er})>0,"休息","常规"))','常规',FORM)
    formula(s,i,4,f'=IF(D{er}="补班",1,IF(D{er}="休息",0,C{er}))',int(iswork),WORK)
    formula(s,i,5,(f'=F{er-1}+E{er}' if i>FIRST else f'=E{er}'),n,WORK)
    formula(s,i,6,f'=F{er}-E{er}',prev,WORK)
s.autofilter(4,0,FIRST+CALDAYS-1,6)
CA=f"'13工作日历'!$A$6:$A${FIRST+CALDAYS}"
CF=f"'13工作日历'!$F$6:$F${FIRST+CALDAYS}"
CG=f"'13工作日历'!$G$6:$G${FIRST+CALDAYS}"
PR=f"INDEX({CG},MATCH('01项目配置'!$B$6,{CA},0))"

# WBS core sheet: 400 prepared rows, four FS predecessors, visible user fields.
s=ws['03WBS'];banner(s,'智能手表 IPD · WBS 主计划','蓝色可编辑，灰色自动计算。按“启用=1”筛选。前置任务须在后继行之前；可筛选，调整顺序时需保持这一规则。',35)
labels=['任务ID','WBS编码','IPD阶段','工作流','任务 / 工作包','类型','范围码','裁剪设置','启用 1/0','R 负责人','A 批准人','C 协作/咨询','工期 工作日','前置ID 1','前置ID 2','前置ID 3','前置ID 4','FS间隔 工作日','最早开始约束','计划开始','计划完成','基线开始','基线完成','完成率','实际开始','实际完成','交付物','验收标准 / 完成定义','关联评审','证据 / 文档链接','风险 / 备注','状态','完成偏差 工作日','输入校验','费用预算 元','计划投入 FTE','_完成边界序号','_前置边界1','_前置边界2','_前置边界3','_前置边界4','估算投入 人日','_开始序号']
headers(s,labels)
widths=[11,13,17,19,47,12,12,13,11,15,15,24,14,13,13,13,13,14,16,16,16,16,16,12,16,16,38,53,16,28,50,18,18,28,17,15]
for j,w in enumerate(widths):s.set_column(j,j,w)
s.set_column(36,40,12,None,{'hidden':True});s.set_column(41,41,17);s.set_column(42,42,12,None,{'hidden':True})
s.freeze_panes(FIRST,5);s.set_zoom(75)
RANGE=lambda c:f"'03WBS'!${col(c)}$6:${col(c)}${LAST}"
IDR=f'$A$6:$A${LAST}';SCOPE=f"'01项目配置'!$E$6:$F${5+len(SCOPES)}"
for i in range(SLOTS):
    r=FIRST+i;er=r+1;t=TASKS[i] if i<len(TASKS) else None;rr=RES[t['id']] if t else None
    for c in list(range(0,8))+list(range(9,19))+list(range(21,31))+[34,35]:s.write_blank(r,c,None,INPUT)
    for c in [18,21,22,24,25]:s.write_blank(r,c,None,DIN)
    s.write_blank(r,23,None,PCT);s.write_blank(r,34,None,MONEY);s.write_blank(r,35,None,NUM)
    if t:
        values={0:t['id'],1:t['wbs'],2:t['phase'],3:t['stream'],4:t['name'],5:t['kind'],6:t['scope'],7:'自动',9:t['owner'],10:t['approver'],11:t['consult'],12:t['days'],17:0,23:0,26:t['output'],27:t['accept'],28:t['gate'],30:t['note'],35:0 if t['days']==0 else 1}
        for c,v in values.items():s.write(r,c,v,PCT if c==23 else INPUT)
        for j,p in enumerate(t['pred']):s.write_number(r,13+j,p,INT)
        for c,k in [(21,'start'),(22,'finish')]:
            if rr[k]:s.write_number(r,c,serial(rr[k]),DIN)
        s.set_row(r,60 if t['kind']=='任务' else 66)
    # Inputs are validated before scheduling. Prior-row references make cycles impossible.
    predchecks=[]
    for c in range(13,17):
        a=col(c)+str(er)
        if r==FIRST:predchecks.append(f'IF({a}<>"","前置须位于上方","")')
        else:predchecks.append(f'IF({a}="","",IF(COUNTIF($A$6:$A${er-1},{a})<>1,"前置缺失/重复/位于下方",IF(IFERROR(INDEX($AH$6:$AH${er-1},MATCH({a},$A$6:$A${er-1},0)),"")<>"通过","上游校验异常","")))')
    check=f'=IF(A{er}="","",IF(COUNTIF({IDR},A{er})<>1,"任务ID重复",IF(OR(E{er}="",J{er}="",K{er}="",AA{er}="",AB{er}=""),"关键字段缺失",IF(COUNTIF(\'01项目配置\'!$E$6:$E${5+len(SCOPES)},G{er})<>1,"范围码错误",IF(OR(M{er}="",M{er}<0,R{er}<0,X{er}<0,X{er}>1),"工期/间隔/进度错误",IF(AND(S{er}<>"",OR(S{er}<MIN({CA}),S{er}>MAX({CA}))),"约束日期超出日历",IF(AND(Y{er}<>"",Z{er}<>"",Z{er}<Y{er}),"实际完成早于开始",IF(AND(Z{er}<>"",X{er}<>1),"实际完成与进度矛盾",IF(CONCATENATE({",".join(predchecks)})<>"","前置须唯一且位于上方","通过")))))))))'
    formula(s,r,33,check,'通过' if t else '')
    active=f'=IF(A{er}="","",IF(H{er}="保留",1,IF(H{er}="不适用",0,IFERROR(VLOOKUP(G{er},{SCOPE},2,FALSE),0))))'
    formula(s,r,8,active,rr['active'] if t else '',WORK)
    for j in range(4):
        pc=f'{col(13+j)}{er}'
        expr=f'=IF(A{er}="","",{PR})' if r==FIRST else f'=IF(A{er}="","",IF({pc}="",{PR},IFERROR(INDEX($AK$6:$AK${er-1},MATCH({pc},$A$6:$A${er-1},0)),{PR})))'
        cached=RES[t['pred'][j]]['boundary'] if t and j<len(t['pred']) else before[START] if t else ''
        formula(s,r,37+j,expr,cached,WORK)
    startord=f'=IF(A{er}="","",IF(AH{er}<>"通过",{PR},IF(I{er}=0,MAX(AL{er}:AO{er}),MAX({PR},MAX(AL{er}:AO{er})+R{er},IF(S{er}="",{PR},IFERROR(INDEX({CG},MATCH(S{er},{CA},0)),{PR}))))))'
    formula(s,r,42,startord,rr['startord'] if t else '',WORK)
    formula(s,r,19,f'=IF(OR(A{er}="",I{er}=0,AH{er}<>"通过"),"",IFERROR(INDEX({CA},MATCH(AQ{er}+1,{CF},0)),""))',valdate(rr['start']) if t else '',DATE)
    formula(s,r,20,f'=IF(T{er}="","",IF(M{er}=0,T{er},IFERROR(INDEX({CA},MATCH(AQ{er}+M{er},{CF},0)),"")))',valdate(rr['finish']) if t else '',DATE)
    formula(s,r,36,f'=IF(A{er}="","",IF(I{er}=0,AQ{er},AQ{er}+M{er}))',rr['boundary'] if t else '',WORK)
    status=f'=IF(A{er}="","",IF(AH{er}<>"通过","输入需修正",IF(I{er}=0,"不适用",IF(OR(T{er}="",U{er}=""),"日历范围不足",IF(X{er}=1,"已完成",IF(U{er}<\'01项目配置\'!$B$7,"逾期",IF(Y{er}<>"","进行中",IF(T{er}<=\'01项目配置\'!$B$7,"应已开始","未开始"))))))))'
    cache=('不适用' if not rr['active'] else '应已开始' if rr['start']<=STATUS else '未开始') if t else ''
    formula(s,r,31,status,cache)
    formula(s,r,32,f'=IF(OR(U{er}="",W{er}=""),"",IFERROR(INDEX({CG},MATCH(U{er},{CA},0))-INDEX({CG},MATCH(W{er},{CA},0)),""))',0 if t and rr['active'] else '',WORK)
    formula(s,r,41,f'=IF(A{er}="","",IF(I{er}=1,M{er}*AJ{er},0))',t['days'] if t and rr['active'] else 0 if t else '',WORK)
s.add_table(4,0,LAST-1,42,{'name':'SmartwatchWBS','style':'Table Style Light 9','autofilter':True,'columns':[{'header':x,'header_format':HEAD} for x in labels]})
s.data_validation(FIRST,5,LAST-1,5,{'validate':'list','source':['任务','评审','里程碑']})
s.data_validation(FIRST,6,LAST-1,6,{'validate':'list','source':'=ScopeCodes'})
s.data_validation(FIRST,2,LAST-1,2,{'validate':'list','source':PHASES})
s.data_validation(FIRST,7,LAST-1,7,{'validate':'list','source':['自动','保留','不适用']})
for c in [12,17]:s.data_validation(FIRST,c,LAST-1,c,{'validate':'integer','criteria':'between','minimum':0,'maximum':3000})
s.data_validation(FIRST,23,LAST-1,23,{'validate':'decimal','criteria':'between','minimum':0,'maximum':1})
s.data_validation(FIRST,35,LAST-1,35,{'validate':'decimal','criteria':'between','minimum':0,'maximum':100})
s.conditional_format(FIRST,0,LAST-1,35,{'type':'formula','criteria':'=$I6=0','format':f('inactive',font_color='#9CA8B5',bg_color='#F4F6F8')})
s.conditional_format(FIRST,33,LAST-1,33,{'type':'formula','criteria':'=AND($A6<>"",$AH6<>"通过")','format':BAD})
s.conditional_format(FIRST,31,LAST-1,31,{'type':'text','criteria':'containing','value':'逾期','format':BAD})
s.conditional_format(FIRST,23,LAST-1,23,{'type':'data_bar','bar_color':TEAL})
s.conditional_format(FIRST,32,LAST-1,32,{'type':'cell','criteria':'>','value':0,'format':WARN})
s.print_area(0,0,FIRST+len(TASKS)-1,27);s.repeat_rows(4);s.set_h_pagebreaks([FIRST+i for i in range(12,len(TASKS),12)])

# Gate register: manual decisions remain separate from schedule.
s=ws['04评审门禁'];banner(s,'评审门禁 / 决策与证据','排期到达、任务100%均不代表获批。DCP由IPMT决策；TR由技术组织评审；Build退出由项目约定组织验收。',13)
glabels=['评审/节点','性质','WBS任务ID','计划日期','签批责任组织','关键输入证据','建议准入 / 退出条件','人工结论','实际签批日','纪要 / 证据链接','未决事项 / 条件','责任人','关闭期限','提示']
headers(s,glabels)
for j,w in enumerate([15,17,13,16,18,51,60,18,16,30,45,15,16,25]):s.set_column(j,j,w)
for i,(k,typ,acct,inputs,criteria) in enumerate(GATE_INFO,FIRST):
    t=task_by_key(k);r=row_for_key(k);er=i+1;rr=RES[t['id']]
    s.write(i,0,t['gate'],MILE);s.write(i,1,typ,TEXT);s.write(i,2,t['id'],TEXT)
    formula(s,i,3,f'=IFERROR(IF(INDEX({RANGE(8)},MATCH(C{er},{RANGE(0)},0))=0,"",INDEX({RANGE(19)},MATCH(C{er},{RANGE(0)},0))),"")',serial(rr['start']),DATE)
    s.write(i,4,acct,TEXT);s.write(i,5,inputs,TEXT);s.write(i,6,criteria,TEXT);s.write(i,7,'未评审',INPUT)
    for c in [8,12]:s.write_blank(i,c,None,DIN)
    for c in [9,10,11]:s.write_blank(i,c,None,INPUT)
    formula(s,i,13,f'=IF(D{er}="","不适用",IF(OR(H{er}="Hold",H{er}="No-Go"),"禁止放行",IF(H{er}="未评审","待人工评审",IF(OR(I{er}="",J{er}=""),"签批证据缺失",IF(H{er}="Conditional Go","条件待跟踪","已记录Go，请核验证据")))))','待人工评审' if rr['active'] else '不适用')
    s.set_row(i,96)
s.data_validation(FIRST,7,FIRST+len(GATE_INFO)-1,7,{'validate':'list','source':['未评审','Go','Conditional Go','Hold','No-Go']})
s.autofilter(4,0,FIRST+len(GATE_INFO)-1,13)

# Gantt is driven by WBS IDs. It shows milestone diamonds, actual progress in a separate column.
s=ws['05周甘特'];banner(s,'周甘特 / 104周滚动视图','每列一周；◆为0工期节点。完成率、基线及实际日期见WBS。更改01项目配置的启动日后自动重排。',12)
s.set_column('A:A',11);s.set_column('B:B',16);s.set_column('C:C',46);s.set_column('D:E',15);s.set_column('F:F',11);s.set_column(6,6+WEEKS-1,3.7)
for j,v in enumerate(['ID','阶段','任务','开始','完成','完成率']):s.write(4,j,v,HEAD)
for w in range(WEEKS):
    d=START+dt.timedelta(weeks=w)
    formula(s,4,6+w,f"='01项目配置'!$B$10+{7*w}",serial(d),f('weekhead',num_format='mm/dd',bold=True,font_color=WHITE,bg_color=TEAL,rotation=90))
s.set_row(4,48);s.freeze_panes(FIRST,3);s.set_zoom(75)
for i in range(SLOTS):
    r=FIRST+i;er=r+1;t=TASKS[i] if i<len(TASKS) else None;rr=RES[t['id']] if t else None
    for c,src in [(0,0),(1,2),(2,4),(3,19),(4,20),(5,23)]:
        expr=f'=IF(OR(\'03WBS\'!A{er}="",\'03WBS\'!I{er}=0),"",\'03WBS\'!{col(src)}{er})'
        cached=(t['id'] if c==0 else t['phase'] if c==1 else t['name'] if c==2 else serial(rr['start']) if c==3 else serial(rr['finish']) if c==4 else 0) if t and rr['active'] else ''
        formula(s,r,c,expr,cached,DATE if c in [3,4] else f('pctgrey',num_format='0%',bg_color=GRAY) if c==5 else TEXT)
    for w in range(WEEKS):
        wc=col(6+w);d=START+dt.timedelta(weeks=w)
        expr=f'=IF(OR($D{er}="",$E{er}=""),"",IF(AND($D{er}<={wc}$5+6,$E{er}>={wc}$5),IF(\'03WBS\'!$M{er}=0,"◆","■"),""))'
        cached='◆' if t and rr['active'] and t['days']==0 and rr['start']<=d+dt.timedelta(days=6) and rr['finish']>=d else '■' if t and rr['active'] and rr['start']<=d+dt.timedelta(days=6) and rr['finish']>=d else ''
        formula(s,r,6+w,expr,cached,f('ganttcell',font_color=TEAL,align='center',font_size=10))
    if t:s.set_row(r,28)
s.conditional_format(FIRST,6,LAST-1,6+WEEKS-1,{'type':'cell','criteria':'==','value':'"■"','format':f('bar',bg_color='#A7DCDE',font_color=TEAL,align='center')})
s.conditional_format(FIRST,6,LAST-1,6+WEEKS-1,{'type':'cell','criteria':'==','value':'"◆"','format':f('diamond',bg_color='#FCE2AD',font_color='#9B6400',align='center',bold=True)})
s.autofilter(4,0,LAST-1,5);s.print_area(0,0,FIRST+len(TASKS)-1,32)

# Phase/process model: concise paraphrases, local mappings explicitly labelled.
s=ws['02IPD流程'];banner(s,'IPD流程骨架 / 智能手表裁剪映射','依据公开IPD实践编制；各公司节点名称、位置和TR粒度可不同。下列阶段输出和Build映射为本模板建议。',7)
process=[
 ('前置授权','机会与产品路标/Charter','IPMT/产品经理','机会、路标、概念预算','Charter','概念投入获授权','不属于六阶段主干','S01/S03'),
 ('概念','判断客户价值、技术可行性及投资吸引力','PDT/产品/研发/财务','初版产品包需求、概念、商业计划','TR1 / CDCP','决定计划阶段投入','可做原理验证；不等同EVT','S01/S02/S03'),
 ('计划','形成可承诺的产品、方案、资源及商业基线','PDT跨职能团队','SRS、架构、WBS、DVP&R、预算与资源承诺','TR2 / TR3 / PDCP','批准开发投资及项目承诺','确定EVT/DVT/PVT目标和样本','S02/S03；具体输出为建议'),
 ('开发','实现完整产品包并建立正式验证条件','研发/采购/NPI/质量/市场/服务','设计、代码、样机、SIT、配置基线','TR4 / EVT退出 / TR5','集成版本达到正式验证入口','EVT + DVT样机构建；软件持续迭代','TR与Build对应为本模板映射'),
 ('验证','验证设计、用户价值、准入及制造过程','测试/质量/法规/NPI/产品','DVT、Beta、认证、PVT、RC与服务证据','DVT退出 / PVT退出 / TR6 / ADCP','技术与商业准备均获授权','DVT验证 + PVT生产验证','S02；具体工作包为建议'),
 ('发布','量产爬坡、销售供货及支持能力就绪','供应链/制造/质量/市场/服务','受控量产包、首批放行、正式版本、渠道','MP / GA','客户可获得产品及承诺服务','MP首批；GA为商业可获得节点','S02；MP与GA关系为建议'),
 ('生命周期','经营与质量监控、维护、降本及退出','LMT/产品/质量/服务/研发','经营复盘、CAPA、维护版本、EOL/EOS','上市后复盘 / EOL DCP','持续满足用户与法定义务','观察窗口不代表产品寿命或支持期','S01/S02/S03'),
]
write_rows(s,['阶段','目的','责任组织','主要输出（建议）','评审/里程碑（建议映射）','退出目标','智能手表Build关系','依据/边界'],process,[15,40,31,54,36,42,45,35])
s.merge_range(15,0,17,7,'DCP：投资与商业决策，可Go / Conditional Go / Hold / No-Go。TR：技术成熟度与产品质量评审。EVT/DVT/PVT：样机及制造验证活动。本模板保留三者独立记录；需先明确各节点证据，再由公司签批裁剪和授权规则。',WARN)

# Risk / change management starter registers.
risks=[
 ('技术','金属外观与人体加载导致天线性能不足','RF','概念/计划','天线净空、人体仿真及EVT摸底','TR3/EVT退出'),
 ('质量','密封、公差或声学膜老化导致进液','结构','计划/开发','公差链、胶路、气密与老化后防水验证','DVT退出'),
 ('性能','PPG串光、肤色或运动伪影导致精度不足','算法','概念/验证','光路设计、分层数据和独立验证','DVT退出'),
 ('性能','典型场景续航未达到承诺','硬件','全阶段','锁定使用模型，预算到模块，逐Build回归','TR5/DVT退出'),
 ('安全','充电异常、电池热或皮肤温升风险','硬件','全阶段','保护、异常工况、热与电池验证','TR6'),
 ('供应','屏幕/SoC/传感器/电池单一来源或交期延迟','采购','计划/开发','长期料清单、备选验证、交付承诺','PDCP/PVT退出'),
 ('进度','开模或修模轮次不足','结构','开发','T0/T1/T2测量与预留整改窗口','DVT退出'),
 ('质量','App/固件/云/算法版本不兼容','系统架构','开发/发布','版本矩阵、端到端回归及配置审计','TR5/GA'),
 ('安全','OTA掉电、跨版本迁移或回滚失败','固件','开发/验证','签名验证、断电恢复与版本组合测试','TR6'),
 ('法规','送检配置与量产BOM/天线/固件不一致','法规认证','验证/发布','送样配置冻结，ECO触发再评估','ADCP'),
 ('法规','医疗宣称触发额外注册或临床工作','法规认证','概念/计划','用途分类确认，建立专项注册/临床计划','CDCP/PDCP'),
 ('安全隐私','健康/位置数据权限、跨境或第三方SDK违规','安全隐私','全阶段','数据地图、最小权限、合同与区域审查','TR6'),
 ('法规','欧盟网络安全/CRA适用日期判断错误','法规认证','计划/发布','按实际投放日核对现行法源及支持义务','ADCP'),
 ('制造','产测漏测、校准相关性差或误判率高','NPI','开发/验证','DFT、量测分析、实验室相关性及追溯','PVT退出'),
 ('制造','良率和产能不足以支撑首销','NPI','验证/发布','PVT数据、瓶颈、工位能力及备线','PVT退出'),
 ('体验','表带、背壳及重量引发不适或皮肤问题','ID/UX','概念/验证','人体工学、材料风险评估与试戴','DVT退出'),
 ('生态','运营商、NFC合作方或App审核依赖拖期','产品经理','计划/验证','提前预约、明确接口及样机准入','ADCP'),
 ('服务','售后维修破坏防水或用户数据保护','服务','验证/生命周期','维修工艺、防水复验和数据处置SOP','GA'),
 ('资源','共享实验室、设备或关键人员冲突','PM','全阶段','按关键窗口预约资源并进行人工排平','PDCP/周例会'),
 ('经营','销量、成本与售后率偏离商业计划','财务','全阶段','敏感性分析及上市后复盘','各DCP/上市后复盘')]
s=ws['07风险台账'];banner(s,'风险台账 / 20项智能手表示例','风险描述及应对为启动清单。概率和影响默认空白，需项目团队评分；风险分数=概率×影响。',11)
headers(s,['风险ID','类别','风险事件','责任角色','重点阶段','概率 1-5','影响 1-5','风险分','应对 / 缓解措施','关联节点','状态','证据 / 关闭条件'])
for j,w in enumerate([13,17,60,17,18,13,13,12,64,24,16,45]):s.set_column(j,j,w)
for r in range(FIRST,FIRST+80):
    vals=[f'R{r-FIRST+1:03d}',*risks[r-FIRST][:4],'','', '',risks[r-FIRST][4],risks[r-FIRST][5],'待评估',''] if r-FIRST<len(risks) else ['']*12
    for c,v in enumerate(vals):s.write(r,c,v,INPUT)
    formula(s,r,7,f'=IF(OR(F{r+1}="",G{r+1}=""),"",F{r+1}*G{r+1})','',WORK)
    s.set_row(r,64)
s.data_validation(FIRST,5,FIRST+79,6,{'validate':'integer','criteria':'between','minimum':1,'maximum':5})
s.data_validation(FIRST,10,FIRST+79,10,{'validate':'list','source':['待评估','开放','处理中','监控','关闭']})
s.autofilter(4,0,FIRST+79,11)

s=ws['08变更台账'];banner(s,'变更台账 / ECR-ECO 与重基线','建议冻结后所有需求、BOM、天线、算法、软件、工艺及市场变化均进行影响评估，按公司权限签批。',12)
ch=['变更ID','提出日期','变更对象/版本','变更原因与内容','涉及需求/WBS ID','范围/体验影响','成本/资源影响','工期/依赖影响','认证/质量/安全影响','决策/批准人','实施版本/日期','回归及证据','基线更新记录']
headers(s,ch)
for j,w in enumerate([15,16,28,50,25,38,35,35,50,30,28,45,40]):s.set_column(j,j,w)
for r in range(FIRST,FIRST+80):
    for c in range(len(ch)):s.write_blank(r,c,None,DIN if c==1 else INPUT)
    s.set_row(r,45)
s.merge_range(FIRST+82,0,FIRST+84,12,'建议变更链路：提出ECR → 评估产品包/进度/成本/资源/质量/法规/服务影响 → 授权决策 → ECO实施及配置发布 → 回归与证据归档 → 必要时批准重基线。评审被Hold/No-Go后，由PM同步调整WBS；模板不会自动阻断生产系统。',WARN)

# RACI and capacity inputs.
s=ws['09职责资源'];banner(s,'职责 / 资源需求 / 人工排平','WBS中R为执行负责人，A为该工作包批准人，C为咨询协作；I默认PDT及受影响职能。将角色替换成具体姓名。',7)
headers(s,['角色','主要职责','具体姓名/团队','可投入 FTE','启用任务数','示例估算投入 人日','资源备注 / 冲突窗口','需通知 I'])
for j,w in enumerate([18,52,28,18,18,25,55,35]):s.set_column(j,j,w)
for i,(role,desc) in enumerate(ROLES.items(),FIRST):
    er=i+1;s.write(i,0,role,TEXT);s.write(i,1,desc,TEXT);s.write_blank(i,2,None,INPUT);s.write_blank(i,3,None,NUM)
    tt=[t for t in TASKS if t['owner']==role and RES[t['id']]['active']]
    formula(s,i,4,f'=COUNTIFS({RANGE(9)},A{er},{RANGE(8)},1)',len(tt),WORK)
    formula(s,i,5,f'=SUMIF({RANGE(9)},A{er},{RANGE(41)})',sum(t['days'] for t in tt),WORK)
    s.write_blank(i,6,None,INPUT);s.write(i,7,'PDT及受影响领域代表',INPUT);s.set_row(i,55)
s.merge_range(FIRST+len(ROLES)+2,0,FIRST+len(ROLES)+5,7,'人日=启用任务工期×计划投入FTE，只代表粗估需求；默认任务FTE=1、评审FTE=0，需按实际改写。此处未计入协作人员或费用，不等于工作量承诺，也未执行资源自动排平。DCP的A为IPMT；技术评审的A为技术组织；项目经理不能用排期日期替代上述签批。',WARN)

# Compliance applicability matrix. These rows are not automatically certified.
compliance=[
 ('BT','所有蓝牙产品','BASE','Bluetooth SIG产品资格','btsig','S04','品牌主体、设计引用/测试、产品名型号、上市时间','供应商资格不自动等于自有品牌产品资格'),
 ('BAT-TR','含锂电产品运输','BASE','UN38.3与运输资料','un383','S11','电芯/电池包型号、试验摘要、运输配置与包装','不是通用安全认证证书'),
 ('CN-RF','中国大陆无线功能','CN','无线电型号核准/适用豁免','cnradio','S05/S06','频段、功率、天线、微功率目录和整机配置','蓝牙不应被一概认作豁免'),
 ('CN-CCC','中国整机/电池/配件','CN','CCC目录及范围判断','cnccc','S07','整机类别、电池与随附电源的产品界定','按现行目录与认证规则判断'),
 ('CN-DATA','中国用户/数据场景','CN','隐私/App/数据要求','cnprivacy','需按实际业务补充现行法源','健康、位置、权限、注销、SDK及跨境','待法规/隐私负责人确认'),
 ('CN-NET','中国蜂窝产品','LTE_CN','进网及运营商适用准入','cnnetwork','需补充现行MIIT目录与运营商要求','蜂窝终端类别、频段、运营商服务','只在LTE且CN启用'),
 ('EU-RED','欧盟无线产品','EU','RED/EMC/安全/RF暴露','eured','S08','产品分类、频段、标准清单、评定路径、技术文档/DoC','标准版本应在送检前再次确认'),
 ('EU-CYBER','欧盟适用无线/数字产品','EU','RED网络安全/CRA衔接','eucyber','S08/S09','实际投放日期、数据功能、支持期及报告义务','2027-12-11为相关废止/主要义务衔接日期，不是2026年已取消'),
 ('EU-MAT','欧盟材料/电池/废弃物/包装','EU','RoHS/REACH/电池/WEEE/包装义务','eumat','须补充各制度现行法源','材料检测/供应链声明、经济运营者、注册/标识等','全部按产品、市场和日期适用性确认'),
 ('US-FCC','美国射频产品','US','FCC设备授权/RF暴露/标签','usfcc','S10','整机配置、授权路径、模块集成条件和实验室资格','法规动态，须在立项及送检时复核'),
 ('US-DATA','美国目标州及用户','US','隐私/健康用途与宣称','usprivacy','S12；州隐私要求另补','目标州、目标人群、数据种类和健康宣称','不因有无ECG单独决定医疗器械属性'),
 ('CELL','启用蜂窝功能','LTE','运营商/GCF/PTCRB等适用准入','operator','由目标运营商及认证组织确认','频段、地区、服务能力及要求的证据','这些项目不是全球所有蜂窝手表均必选'),
 ('MED','医疗用途或诊疗宣称','MED','目标市场分类、注册/许可和临床证据','medapproval','S12仅支撑美国一般健康边界；其他法源另补','用途、类别、QMS、临床/性能证据、标签及许可','须另建经批准专项计划，不能采用模板占位工期'),
 ('OTHER','其他目标市场','OTHER','按市场新增合规工作包','regplan','待补充','应新增具体准入、法源、任务、证据及依赖','当前模板不包含其他市场的完整准入清单')]
s=ws['10认证矩阵'];banner(s,'认证与合规适用性矩阵','每项均须确认适用性、市场和产品配置。排期与功能开关只控制计划范围，不产生认证/合规结论。',11)
headers(s,['项目码','适用对象','范围码','候选事项','关联WBS ID','参考来源','需确认的关键边界','注意 / 待补证据','启用 1/0','人工适用性结论','证据 / 有效期 / 实验室','责任人'])
for j,w in enumerate([15,32,13,39,15,45,60,57,13,24,47,18]):s.set_column(j,j,w)
for r,row in enumerate(compliance,FIRST):
    er=r+1;code,obj,scope,item,key,src,bound,note=row
    for c,v in enumerate([code,obj,scope,item,ids[key],src,bound,note]):s.write(r,c,v,TEXT)
    formula(s,r,8,f'=IFERROR(VLOOKUP(C{er},{SCOPE},2,FALSE),0)',SWITCH[scope],WORK)
    s.write(r,9,'待确认',INPUT);s.write_blank(r,10,None,INPUT);s.write(r,11,'法规认证',INPUT);s.set_row(r,105)
s.data_validation(FIRST,9,FIRST+len(compliance)-1,9,{'validate':'list','source':['待确认','适用-未完成','适用-已完成','不适用-已批准']})
s.autofilter(4,0,FIRST+len(compliance)-1,11)

s=ws['11需求追踪'];banner(s,'需求追踪矩阵 / 需求到验证证据','以下为智能手表需求类别样例；具体数值和判据必须来自已批准PRD/SRS。可继续增加需求，WBS保持工作包粒度。',10)
reqs=[('续航/充电','典型及重度模型、温升、低电量与寿命','powerfw','dvtendurance'),('连接/兼容','配对、重连、通话/通知、支持手机OS','ble','dvtapp'),('运动健康','人群分层、参考方法、误差及适用限制','alg','dvtalg'),('防水/声学','场景、方法、等级、老化与装配变差','md','dvtwater'),('佩戴/材料','尺寸、表带、接触材质、汗液与耐久','cmf','dvtsurface'),('定位','TTFF、轨迹、复杂环境及功耗','gnssdev','dvtgnss'),('NFC','按选定生态定义功能及安全目标','nfcdev','dvtnfc'),('蜂窝/eSIM','频段、运营商、弱场及异常恢复','ltedev','dvtlte'),('ECG','信号质量、参考方法和用途边界','ecgdev','dvtecg'),('软件升级','签名、掉电恢复、回滚及数据迁移','ota','dvtota'),('安全与隐私','权限、密钥、数据、漏洞与支持期','secimpl','dvtsec'),('制造与追溯','工位覆盖、校准、气密、SN及版本','jigs','msa'),('服务与保修','返修防水、用户数据和备件','service','service')]
headers(s,['需求ID','类别','需求/规格要点','批准指标/判据','需求责任人','实现WBS ID','验证WBS ID','用例/方法ID','证据链接','结论','基线/变更ID'])
for j,w in enumerate([17,20,58,52,18,17,17,28,38,21,25]):s.set_column(j,j,w)
for r in range(FIRST,FIRST+100):
    for c in range(11):s.write_blank(r,c,None,INPUT)
    if r-FIRST<len(reqs):
        category,detail,dev,test=reqs[r-FIRST]
        for c,v in {0:f'SRS-{r-FIRST+1:03d}',1:category,2:detail,3:'待PRD/SRS批准',4:'系统架构',5:ids[dev],6:ids[test],9:'未验证'}.items():s.write(r,c,v,INPUT)
    s.set_row(r,55)
s.data_validation(FIRST,9,FIRST+99,9,{'validate':'list','source':['未验证','通过','不通过','不适用-已批准']});s.autofilter(4,0,FIRST+99,10)

s=ws['12来源依据'];banner(s,'公开来源 / 引用范围 / 模板假设','检索核验日期：2026-11-08。使用官方或原始实践资料；历史案例支撑框架，不替代公司流程或现行法规。',7)
source_rows=[(sid,pub,title,date,url,claims,limits,'2026-11-08') for sid,pub,title,date,url,claims,limits in SOURCES]
write_rows(s,['来源ID','发布方','资料标题','日期/版本','原始链接','支持的内容','使用边界','核验日期'],source_rows,[13,25,60,37,70,65,65,18])
for i,src in enumerate(SOURCES,FIRST):s.write_url(i,4,src[4],LINK,src[4]);s.set_row(i,108)

# Dashboard includes formula-driven warnings instead of a false automatic release.
s=ws['06项目看板'];banner(s,'项目看板 / 计划与管理状态','日期来自工作包依赖；批准状态来自04评审门禁；认证结论来自10认证矩阵。三者分别检查。',9)
s.set_column('A:A',26);s.set_column('B:B',25);s.set_column('C:C',5);s.set_column('D:J',20)
ga=RES[ids['ga']]['start'];latest=max(v['finish'] for v in RES.values() if v['active']);active_count=sum(v['active'] for v in RES.values())
ga_lookup=f'INDEX({RANGE(19)},MATCH({ids["ga"]},{RANGE(0)},0))'
metrics=[('启用工作包数',f'=COUNTIF({RANGE(8)},1)',active_count),('模板工作包总数',f'=COUNT({RANGE(0)})',len(TASKS)),('预测GA',f'={ga_lookup}',serial(ga)),('目标GA',"='01项目配置'!B8",serial(TARGET)),('GA日期差 日历天',f'=IF(OR({ga_lookup}="",\'01项目配置\'!B8=""),"",{ga_lookup}-\'01项目配置\'!B8)',(ga-TARGET).days),('已完成工作包数',f'=COUNTIFS({RANGE(8)},1,{RANGE(23)},1)',0),('逾期工作包数',f'=COUNTIF({RANGE(31)},"逾期")',0),('输入校验异常数',f'=COUNTIFS({RANGE(0)},"<>",{RANGE(33)},"<>通过")',0),('核心BASE已裁剪数',f'=COUNTIFS({RANGE(6)},"BASE",{RANGE(8)},0)',0),('已启用合规待确认数',"=COUNTIFS('10认证矩阵'!I6:I19,1,'10认证矩阵'!J6:J19,\"待确认\")",sum(SWITCH[x[2]] for x in compliance)),('Hold/No-Go门禁数',"=COUNTIF('04评审门禁'!H6:H20,\"Hold\")+COUNTIF('04评审门禁'!H6:H20,\"No-Go\")",0),('已记录Go门禁数',"=COUNTIF('04评审门禁'!H6:H20,\"Go\")",0),('周历例外冲突数',"=SUMPRODUCT(--('01项目配置'!I6:I205<>\"\"),--(COUNTIF('01项目配置'!L6:L205,'01项目配置'!I6:I205)>0))",0),('日历范围不足任务数',f'=COUNTIF({RANGE(31)},"日历范围不足")',0),('甘特范围外任务数',f'=COUNTIFS({RANGE(8)},1,{RANGE(20)},">="&\'01项目配置\'!B10+728)',sum(v['active'] and v['finish']>=START+dt.timedelta(days=728) for v in RES.values() if v['finish']))]
for r,(label,expr,cached) in enumerate(metrics,4):
    s.write(r,0,label,TEXT);formula(s,r,1,expr,cached,DATE if 'GA' in label and '日期差' not in label else FORM);s.set_row(r,30)
s.merge_range(21,0,24,9,'管理提醒：默认所有评审均“未评审”，所有认证适用性均“待确认”。启用MED后，医疗专项工期仍为占位，必须拆成实际注册与临床计划。任何核心任务被裁剪、任一门禁Hold/No-Go、认证证据缺失或日历未完善时，须先处理再批准发布。',WARN)
phasehead=27
for j,v in enumerate(['阶段','启用任务数','最早开始','最晚完成','计划人日','已完成数']):s.write(phasehead,j,v,HEAD)
for i,p in enumerate(PHASES,phasehead+1):
    er=i+1;selected=[t for t in TASKS if t['phase']==p and RES[t['id']]['active']]
    s.write(i,0,p,TEXT)
    formula(s,i,1,f'=COUNTIFS({RANGE(2)},A{er},{RANGE(8)},1)',len(selected),WORK)
    formula(s,i,2,f'=IF(B{er}=0,"",MINIFS({RANGE(19)},{RANGE(2)},A{er},{RANGE(8)},1))',serial(min(RES[t['id']]['start'] for t in selected)) if selected else '',DATE)
    formula(s,i,3,f'=IF(B{er}=0,"",MAXIFS({RANGE(20)},{RANGE(2)},A{er},{RANGE(8)},1))',serial(max(RES[t['id']]['finish'] for t in selected)) if selected else '',DATE)
    formula(s,i,4,f'=SUMIFS({RANGE(41)},{RANGE(2)},A{er})',sum(t['days'] for t in selected),WORK)
    formula(s,i,5,f'=COUNTIFS({RANGE(2)},A{er},{RANGE(8)},1,{RANGE(23)},1)',0,WORK)
s.merge_range(38,0,40,9,'前置立项为进入概念阶段的授权；跨阶段管理为可续建的例会/风险/变更窗口，不参与阶段日期求和。阶段可因并行策划、NPI准备或认证活动交叠。WBS按依赖排期，未自动计算关键路径、时差或资源平衡。',SMALL)
s.conditional_format(4,1,18,1,{'type':'formula','criteria':'=AND(OR(ROW()=11,ROW()=12,ROW()=13,ROW()=15,ROW()=17,ROW()=18,ROW()=19),B5>0)','format':WARN})
s.print_area(0,0,41,9)

# Readme inside workbook.
s=ws['00使用说明'];banner(s,'智能手表 IPD · 可定制 WBS','公开流程有出处，任务排期可修改，投资决策、技术成熟度及样机验证分别留证。模板版本 v1.0 · 2026-11-08',7)
instructions=[
 ('交付内容',f'{len(TASKS)}个工作包/节点、{len(GATE_INFO)}个评审/里程碑记录、400行公式容量、104周甘特、14个工作表；不含宏与外部数据连接。'),
 ('1. 配置项目','在01项目配置填写启动日、状态日期、目标GA，确认销售市场与功能开关；默认为新平台完整开发的保守示例，全部工期须由领域负责人估算，不代表行业标准周期。'),
 ('2. 维护日历','在01项目配置填写法定节假日/工厂停工日和周末补班；13工作日历自动计算。未填节假日时排期仅按默认每周工作模式。'),
 ('3. 裁剪任务','范围码控制默认启用；03WBS的“自动/保留/不适用”逐任务覆盖。停用工作包变成0工期依赖桥，祖先依赖继续传递。BASE及门禁的裁剪须在变更或评审记录中说明。'),
 ('4. 定制排期','修改工期、最多4个前置ID、FS非负工作日间隔和最早开始约束。前置必须位于后继行上方，任务ID全表唯一；支持筛选。排序或移动任务时保持前置先于后继。'),
 ('新增/拆分任务','末尾空白行已预置公式；新增任务填写唯一ID、WBS、阶段、工作流、类型、范围码、裁剪、R/A、工期、间隔、进度、交付物、判据及FTE。若需插入现有门禁之前，请在主表内部插入整行并从相邻正常行复制公式；随后同步检查其他表和图表范围。'),
 ('删除/依赖扩展','建议用“不适用”停用，保留ID、基线和追溯。多于4个前置可新增0工期汇总节点分组汇入；本版仅支持FS，需SS/FF时应拆出可验证的中间交付节点或在专业排程工具中扩展。'),
 ('5. 批准基线','示例V/W列已保存初始计划。公司批准PDCP或ECO重基线后，在完整未筛选表中复制T/U两列，选择性粘贴“值”到V/W，记录基线版本/日期并保留旧文件；不要把公式粘入基线列。'),
 ('6. 周度跟踪','更新完成率、实际开始/完成、风险和证据链接。状态日期驱动逾期提示；实际日期用于记录，不自动改变剩余计划。预测变化时由PM调整剩余任务的工期、依赖或约束，并保留基线。'),
 ('7. 评审与签批','04评审门禁由有授权组织填写Go/Conditional Go/Hold/No-Go、实际日期和纪要。排期及完成率不触发自动批准；Hold/No-Go后须由PM执行停工/改向与计划同步。'),
 ('8. 认证与需求','10认证矩阵逐项判断适用性与证据；11需求追踪把PRD/SRS连到实现、测试及报告。市场“其他”启用时需新增对应准入任务。'),
 ('9. 资源与费用','09职责资源填写具体姓名与可用FTE；WBS的工期×FTE用于粗估人日，费用另填。默认FTE是占位，计划没有自动资源排平，也没有输出关键路径。'),
 ('医疗专项边界','ECG不自动等于医疗器械，关键是用途/宣称及市场。MED默认关闭；专项执行与许可核验的60工作日是演示占位，须替换为获批的真实注册/临床计划，实际许可是放行前提。'),
 ('生命周期边界','首销监控和维护任务为首轮观察窗口，可重复创建；不代表产品寿命或安全支持期。RETIRE默认关闭，启用时按实际EOL触发点设置最早开始约束。'),
 ('兼容与公式','建议Excel 2019/365或支持MINIFS/MAXIFS的新版WPS。文件包含公式及初始缓存值，打开后启用自动计算；如显示旧值可执行完整重算。已用LibreOffice Calc进行重算及场景检查，未在Microsoft Excel/WPS客户端实机验证。'),
 ('方法论出处','IBM官方研究说明IPD范围，Huawei官方白皮书公开阶段/评审图示，PMI原始实践说明IPMT/PDT。完整链接与引用边界见12来源依据；本文件为项目裁剪方案，非官方统一标准或公司内部流程原件。'),
 ('字段及颜色','蓝色=可编辑输入；灰色=公式；任务ID用于依赖、WBS编码用于层级，不要混用。R执行、A批准、C咨询，I默认PDT及受影响领域。计划日期单位为工作日，偏差列按自定义工作日历计算。'),
 ('适用限制','400行公式容量、4个FS前置、104周甘特；日历约12年。扩展容量、插入/删除行或结构化排序后需复核公式、甘特、评审、看板与认证链接。任何人工签批/合规结论均不能由模板代替。')]
headers(s,['操作项','说明'])
s.set_column('A:A',27);s.set_column('B:H',18)
for r,(k,v) in enumerate(instructions,FIRST):s.write(r,0,k,HEAD);s.merge_range(r,1,r,7,v,TEXT);s.set_row(r,75 if len(v)>145 else 60)
s.print_area(0,0,FIRST+len(instructions)-1,7)
wb.close()

# CSV and structured task library preserve editable data independently of Excel.
with (OUT/'智能手表_IPD_WBS_数据.csv').open('w',encoding='utf-8-sig',newline='') as fp:
    writer=csv.writer(fp);writer.writerow(['任务ID','WBS','阶段','工作流','工作包','类型','范围码','默认启用','R','A','工期工作日','前置任务ID','计划开始','计划完成','交付物','验收标准','关联评审','备注'])
    for t in TASKS:
        r=RES[t['id']];writer.writerow([t['id'],t['wbs'],t['phase'],t['stream'],t['name'],t['kind'],t['scope'],r['active'],t['owner'],t['approver'],t['days'],','.join(map(str,t['pred'])),fmtdate(r['start']),fmtdate(r['finish']),t['output'],t['accept'],t['gate'],t['note']])
(ROOT/'data'/'task_library.json').write_text(json.dumps(TASKS,ensure_ascii=False,indent=2),encoding='utf-8')
meta={'task_count':len(TASKS),'enabled':active_count,'gate_count':len(GATE_INFO),'predicted_ga':fmtdate(ga),'target_ga':fmtdate(TARGET),'last_date':fmtdate(latest),'phase_dates':{p:{'start':fmtdate(min(RES[t['id']]['start'] for t in TASKS if t['phase']==p and RES[t['id']]['active'])),'finish':fmtdate(max(RES[t['id']]['finish'] for t in TASKS if t['phase']==p and RES[t['id']]['active']))} for p in PHASES}}
(OUT/'计划摘要.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2))
