from pathlib import Path
import datetime as dt, json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'deliverables'
summary=json.loads((OUT/'计划摘要.json').read_text())
FONT='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def font(n):return ImageFont.truetype(FONT,n)
im=Image.new('RGB',(1680,1270),'#F4F7FB');d=ImageDraw.Draw(im)
navy='#16324F';teal='#007F86';muted='#567086'
d.rectangle((0,0,1680,160),fill=navy)
d.text((62,35),'智能手表 IPD · WBS 计划框架',fill='white',font=font(42))
d.text((64,102),'公开实践框架 + 智能手表工作包 + 可定制工作日计划',fill='#D0E4F2',font=font(23))
for j,(big,small) in enumerate([('168','工作包 / 节点'),('15','评审 / 里程碑记录'),('14','Excel 工作表'),('400 / 104','预置任务行 / 甘特周数')]):
    x=62+j*398;d.rounded_rectangle((x,184,x+366,274),radius=12,fill='white')
    d.text((x+18,193),big,fill=teal,font=font(32));d.text((x+18,238),small,fill=muted,font=font(18))
d.text((62,305),'六阶段主干 · 前置 Charter 授权 · 横向跨职能协同',fill=navy,font=font(26))
cards=[('01 概念','客户价值与技术可行性','TR1 / CDCP'),('02 计划','方案、资源与商业基线','TR2 / TR3 / PDCP'),('03 开发','完整产品包与集成','TR4 / EVT退出 / TR5'),('04 验证','设计、准入与制造验证','DVT / PVT / TR6 / ADCP'),('05 发布','量产、交付与上市','MP / GA'),('06 生命周期','质量、维护与经营复盘','维护 / 复盘 / 退出')]
for j,(title,desc,gates) in enumerate(cards):
    x=62+j*263
    d.rounded_rectangle((x,353,x+243,494),radius=12,fill='white',outline='#D4E1EC',width=2)
    d.rectangle((x+1,354,x+242,361),fill=teal)
    d.text((x+16,376),title,fill=navy,font=font(27))
    d.text((x+16,421),desc,fill=muted,font=font(18))
    d.text((x+12,460),gates,fill=teal,font=font(15))
    if j<5:
        d.line((x+246,422,x+259,422),fill=teal,width=3);d.polygon([(x+260,422),(x+253,417),(x+253,427)],fill=teal)
d.rounded_rectangle((62,513,1618,570),radius=10,fill='#E0EDF5')
d.text((83,528),'投资决策 DCP、技术评审 TR、样机验证 EVT/DVT/PVT 分别留证；排期日期不自动产生放行结论。',fill=navy,font=font(22))
d.text((62,602),'示例阶段视图',fill=navy,font=font(28))
d.text((309,609),'示例配置：中国大陆 · 蓝牙 / App / 云 / GNSS · 新平台完整开发',fill=muted,font=font(19))
phase=summary['phase_dates'];start=dt.date(2026,11,9);end=dt.date.fromisoformat(summary['last_date'])+dt.timedelta(days=8)
left,right=322,1582;top=704;bottom=1082
def x(dte):return left+(dte-start).days/(end-start).days*(right-left)
month=dt.date(2026,12,1)
while month<=end:
    xx=x(month);d.line((xx,680,xx,bottom),fill='#D5E0E8',width=1)
    if month.month in [1,4,7,10]:d.text((xx-28,657),month.strftime('%Y/%m'),fill=muted,font=font(17))
    month=dt.date(month.year+int(month.month==12),month.month%12+1,1)
colors=['#61788C','#316A9C','#007F86','#31A8BC','#7268AF','#D79238','#448763']
for i,(p,v) in enumerate(list(phase.items())[:7]):
    yy=top+i*52
    d.text((65,yy+3),p,fill=navy,font=font(23))
    a=dt.date.fromisoformat(v['start']);b=dt.date.fromisoformat(v['finish'])
    d.rounded_rectangle((x(a),yy,x(b)+2,yy+27),radius=6,fill=colors[i])
    label=f"{a:%m/%d}—{b:%m/%d}"
    d.text((max(left,x(a)),yy+28),label,fill=muted,font=font(14))
ga=dt.date.fromisoformat(summary['predicted_ga']);gx=x(ga)
d.line((gx,680,gx,bottom+8),fill='#B42318',width=2)
d.text((gx-70,1110),'示例GA '+ga.isoformat(),fill='#B42318',font=font(20))
d.text((62,1162),'可调：功能 / 市场、工期、前置、日期约束、责任、投入、交付物、判据、节假日与补班。',fill=navy,font=font(21))
d.text((62,1203),'示例尚未录入法定节假日，未做资源排平。工期、验收目标与认证适用性须按项目确认。',fill=muted,font=font(19))
im.save(OUT/'智能手表_IPD流程与计划概览.png')
im.save(OUT/'智能手表_IPD流程与计划概览.pdf','PDF',resolution=145)
print(OUT/'智能手表_IPD流程与计划概览.png')
