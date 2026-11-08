"""Smartwatch IPD work packages. All durations and exit criteria are editable proposals."""
TASKS = []
def a(key, phase, stream, name, days, deps='', scope='BASE', owner='PM', approver='PDT负责人', output='', accept='', kind='任务', gate='', note='', consult='相关领域代表'):
    TASKS.append(dict(key=key, phase=phase, stream=stream, name=name, days=days,
                      deps=deps.split() if deps else [], scope=scope, owner=owner,
                      approver=approver, output=output, accept=accept, kind=kind,
                      gate=gate, note=note, consult=consult))

P='0 前置立项'
a('opportunity',P,'战略与立项','机会点、目标客户及产品路标匹配',5,owner='产品经理',output='机会说明/路标关联',accept='客户、价格带、上市窗口及机会假设可核验')
a('charter',P,'战略与立项','Charter 任务书与概念阶段授权',2,'opportunity',owner='产品经理',approver='IPMT',output='批准的Charter/概念预算',accept='明确PDT负责人、范围、投入上限及退出条件',kind='评审',gate='Charter')

P='1 概念'
a('voc',P,'市场与商业','VOC、使用场景与痛点调研',10,'charter',owner='产品经理',output='VOC/场景清单',accept='覆盖目标人群、佩戴场景及购买决策因素')
a('bench',P,'市场与商业','竞品拆解与体验/价格基准',8,'charter',owner='产品经理',output='竞品矩阵',accept='覆盖续航、屏幕、运动健康、连接及售后差异')
a('claim',P,'产品定义','功能边界、健康/医疗宣称和目标市场初判',5,'voc',owner='法规认证',approver='产品经理',output='功能与市场适用矩阵',accept='区分一般健康与诊疗用途，列明市场和监管路径待确认项')
a('prd0',P,'产品定义','产品包需求与初版 PRD',8,'voc bench claim',owner='产品经理',output='PRD v0/产品包需求',accept='覆盖产品、配件、App、云、包装、服务及可测目标')
a('id0',P,'工业与结构','ID、人体工学与佩戴概念',10,'voc bench',owner='ID/UX',output='ID概念/佩戴模型',accept='尺寸、重量、表带、人群适配和充电方式有候选方案')
a('platform',P,'系统工程','SoC/OS/存储及平台复用评估',8,'prd0',owner='系统架构',output='平台选型建议',accept='确认SDK授权、内存余量、维护周期及平台限制')
a('sensor0',P,'运动健康','PPG/IMU/温度等传感方案可行性',7,'prd0',owner='算法',output='传感器/算法可行性报告',accept='识别肤色、运动伪影、光路、佩戴和数据依赖')
a('rf0',P,'射频与天线','蓝牙天线与整机堆叠可行性',7,'prd0 id0',owner='RF',output='射频风险清单',accept='金属表壳、人体遮挡及天线净空存在可实施方案')
a('power0',P,'电源与电池','电池容量、功耗及热预算初估',7,'platform id0',owner='硬件',output='能量/热预算',accept='按目标使用模型估算续航并保留设计余量')
a('supply0',P,'采购与供应链','关键料供应、交期与可替代性初评',7,'platform sensor0',owner='采购',output='关键料风险/询价',accept='屏幕、SoC、传感器、电池等长交期和单一来源已识别')
a('biz0',P,'市场与商业','销量、ASP、BOM及损益敏感性分析',6,'prd0 supply0',owner='财务',output='初版商业计划',accept='收入成本、毛利、NRE、保修和敏感性假设有责任人')
a('quality0',P,'质量与可靠性','质量、可靠性及安全目标初稿',5,'prd0 claim',owner='QA',output='质量目标/重大风险',accept='定义任务剖面、关键失效及试验策略待确认项')
a('tr1',P,'技术评审','TR1：需求与产品概念评审',0,'prd0 platform power0 quality0',owner='系统架构',approver='技术评审组',output='TR1纪要/问题清单',accept='需求和概念技术可行，关键风险及验证计划明确',kind='评审',gate='TR1')
a('cdcp',P,'投资决策','CDCP：概念投资决策',0,'tr1 biz0 rf0 id0',owner='PM',approver='IPMT',output='CDCP决议/计划阶段授权',accept='商业机会成立，风险可承受，批准下一阶段投入',kind='评审',gate='CDCP')

P='2 计划'
a('pdt',P,'项目策划','PDT组建、角色授权与供应商接口',3,'cdcp',output='PDT/RACI/沟通机制',accept='职能代表、决策权限及ODM/OEM边界确认')
a('srs',P,'需求与系统','PRD基线、SRS与需求分解',10,'cdcp',owner='系统架构',approver='产品经理',output='PRD/SRS/需求追踪矩阵',accept='功能、性能、边界、优先级、验收方式和责任人完整')
a('ux',P,'工业与结构','交互架构、UI与无障碍方案',15,'srs',owner='ID/UX',output='UX规范/可交互原型',accept='核心路径、异常提示、语言及可访问性经过评审')
a('idfreeze',P,'工业与结构','ID定案、CMF、表带及人体工学评审',12,'srs id0',owner='ID/UX',output='ID/CMF基线',accept='装配、皮肤接触、佩戴舒适与外观验收方法确认')
a('stack',P,'工业与结构','整机堆叠、光路与防水声学架构',12,'idfreeze platform',owner='结构',output='堆叠/密封/声学方案',accept='光窗、天线、麦克风、扬声器、泄压及维修路径协调')
a('arch',P,'需求与系统','系统架构、接口与软硬件版本策略',12,'srs platform',owner='系统架构',output='架构/接口/版本基线',accept='明确端、App、云、算法和硬件接口及兼容矩阵')
a('gnssplan',P,'功能选配','GNSS频段、定位场景与天线共存策划',5,'arch stack','GNSS','RF',output='GNSS设计/验证范围',accept='定义TTFF、轨迹、城市峡谷及运动场景目标')
a('nfcplan',P,'功能选配','NFC用途、密钥责任与生态接入策划',8,'arch','NFC','系统架构',output='NFC用途与合作计划',accept='门禁、公交或支付按选定用途界定，确认商务与安全边界')
a('lteplan',P,'功能选配','LTE/eSIM频段、运营商及平台接入策划',10,'arch','LTE','RF',output='蜂窝与运营商准入计划',accept='明确地区频段、VoLTE/紧急功能适用性及外部依赖')
a('wifiplan',P,'功能选配','Wi-Fi频段、共存与场景策划',5,'arch','WIFI','RF',output='Wi-Fi规格',accept='频段、吞吐、功耗、共存和市场限制明确')
a('ecgplan',P,'功能选配','ECG电极、算法和用途边界策划',8,'srs stack','ECG','算法',output='ECG规格与验证方案',accept='确认电极接触、信号质量与健康/医疗用途边界')
a('medroute',P,'法规与认证','医疗用途分类、注册路径与专项项目计划',15,'claim srs','MED','法规认证',output='分类意见/注册及临床专项计划',accept='由法规负责人确认地区路径、QMS、证据、预算和真实周期',note='此工作包只做路线策划；启用医疗功能后须另建经批准的详细注册/临床子计划，模板工期不代表审批周期')
a('testplan',P,'质量与可靠性','DVP&R与整机验证总体计划',10,'srs arch',owner='测试',approver='QA',output='DVP&R/样本与设备计划',accept='需求到用例追踪，试验条件、样本量、判据和复测规则获批')
a('qualplan',P,'质量与可靠性','DFMEA、可靠性任务剖面与安全风险分析',8,'srs stack',owner='QA',output='DFMEA/可靠性计划',accept='覆盖进液、电池热、皮肤接触、跌落及误测危害')
a('regplan',P,'法规与认证','目标市场认证适用性、标准版本与送样计划',8,'claim arch',owner='法规认证',output='认证矩阵/报价/实验室计划',accept='每项有适用性结论、法源、样机配置、责任人与周期')
a('secplan',P,'安全与隐私','威胁建模、数据地图及隐私需求',8,'arch claim',owner='安全隐私',output='威胁模型/数据与安全要求',accept='覆盖配对、密钥、健康/位置数据、未成年人适用性及云边界')
a('swplan',P,'软件与平台','软件迭代、持续集成及配置管理计划',5,'arch',owner='固件',output='发布列车/CI/配置规则',accept='统一需求、代码、硬件、算法、App和云版本标识')
a('appplan',P,'App与云','App/手机OS兼容与商店发布计划',6,'arch','APP','App',output='App兼容矩阵/上架计划',accept='目标iOS/Android版本、权限和商店政策复核计划明确')
a('cloudplan',P,'App与云','云容量、运维、数据驻留与第三方服务策划',7,'arch secplan','CLOUD','云端',output='云架构/SLA/成本预算',accept='明确区域、备份、恢复、可观测性及供应商责任')
a('npi',P,'制造与供应链','NPI、DFM/DFA/DFT及工厂能力策划',8,'stack arch',owner='NPI',output='制造方案/工装设备清单',accept='产测、校准、气密和追溯方案具备可行性')
a('toolplan',P,'制造与供应链','模具、工装及治具交期与投资策划',6,'stack npi',owner='结构',output='模具/治具计划与预算',accept='识别T0/T1/T2、修模及备份节拍')
a('supplier',P,'制造与供应链','供应商定点、质量协议与备选料策略',10,'supply0 regplan',owner='采购',output='AVL/供应商质量协议',accept='关键规格、PCN/EOL、产能和交付责任确认')
a('finance',P,'项目策划','最终商业计划、预算与目标成本分解',6,'biz0 supplier toolplan',owner='财务',output='商业计划/NRE/OPEX/目标BOM',accept='假设更新，分阶段投资、量产成本及盈亏风险确认')
a('wbsplan',P,'项目策划','WBS、依赖、资源及风险基线编制',6,'pdt testplan npi',output='批准候选计划/风险台账',accept='责任到人、交付物明确，长交期和认证路径进入主计划')
a('tr2',P,'技术评审','TR2：产品规格与需求可验证性评审',0,'srs testplan regplan secplan',owner='系统架构',approver='技术评审组',output='TR2纪要/SRS基线',accept='产品规格完整、可测，未决要求具有关闭计划',kind='评审',gate='TR2')
a('tr3',P,'技术评审','TR3：总体方案与开发准备评审',0,'tr2 stack arch qualplan',owner='系统架构',approver='技术评审组',output='TR3纪要/架构基线',accept='跨域接口、风险和制造验证方案确认',kind='评审',gate='TR3')
a('planextra',P,'项目策划','选配功能与端云计划汇总关闭',3,'lteplan nfcplan ecgplan medroute',output='选配子计划/外部依赖清单',accept='启用功能有独立里程碑与责任人；不适用项留裁剪依据')
a('planextra2',P,'项目策划','平台、定位及App/云计划一致性检查',2,'gnssplan wifiplan appplan cloudplan',output='跨域计划一致性记录',accept='选配与平台接口、资源、迭代节奏一致')
a('pdcp',P,'投资决策','PDCP：计划投资决策与项目承诺',0,'tr3 finance wbsplan planextra',owner='PM',approver='IPMT',output='PDCP决议/项目合同/计划基线',accept='范围、资源、进度、成本、质量和风险经授权承诺',kind='评审',gate='PDCP',note='planextra2、ux、toolplan等也通过开发入口任务控制，评审资料须整体核验')

P='3 开发'
a('kick',P,'开发统筹','开发基线发布与跨域启动',2,'pdcp planextra2 ux swplan',output='开发基线/迭代计划',accept='各领域使用相同产品配置及接口版本')
a('sch',P,'硬件与射频','原理图、电源时序及保护电路设计',15,'kick',owner='硬件',output='原理图/设计计算',accept='完成接口、功耗、保护和关键器件降额评审')
a('rfdesign',P,'硬件与射频','蓝牙射频、天线及人体加载仿真',15,'kick stack',owner='RF',output='天线/RF设计',accept='匹配、净空、共存与人体场景有设计依据')
a('pcb',P,'硬件与射频','PCB Layout、SI/PI/EMC及可制造性评审',15,'sch rfdesign',owner='硬件',output='PCB/Gerber/评审记录',accept='高速、射频、模拟地、充电回路和生产可测性检查通过')
a('md',P,'结构与模具','结构详设、密封、声学及表带快拆设计',20,'kick stack',owner='结构',output='3D/2D图纸/公差链',accept='密封压缩量、公差、胶路、跌落和装配可控')
a('optical',P,'结构与模具','PPG光学窗口、遮光与接触压力设计',12,'md sensor0',owner='结构',output='光路/光学材料/接触方案',accept='抑制串光、漏光，兼顾肤色与佩戴适应性')
a('cmf',P,'结构与模具','CMF、接触材料和供应商工艺验证',15,'md',owner='ID/UX',output='CMF封样/材料规范',accept='外观、汗液、腐蚀、涂层及皮肤接触风险可验证')
a('mold',P,'结构与模具','模具开模、T0/T1与尺寸测量',30,'md toolplan',owner='结构',output='T1样件/尺寸报告',accept='关键尺寸与装配缺陷形成闭环计划',note='开模作为PDCP后投入；提前开模应单独批准风险投资')
a('evtmat',P,'硬件与射频','EVT物料、PCB制板与SMT准备',15,'pcb supplier',owner='采购',output='EVT齐套表/PCBA',accept='关键物料追溯、替代料和焊接质量确认')
a('bsp',P,'固件与系统','BSP、驱动与板级Bring-up',20,'evtmat',owner='固件',output='驱动/Bring-up记录',accept='显示、触控、传感器、存储、通信和电源基本工作')
a('boot',P,'固件与系统','启动链、签名、密钥与工厂烧录架构实现',15,'kick secplan',owner='固件',output='安全启动/密钥方案',accept='调试权限、密钥注入和恢复路径经过评审')
a('fwcore',P,'固件与系统','系统服务、UI、通知、表盘与基础应用',30,'kick ux',owner='固件',output='固件功能版本',accept='基础用户路径、异常恢复及配置符合规格')
a('ble',P,'固件与系统','蓝牙协议、连接、通话/音频按需实现',20,'bsp',owner='固件',output='蓝牙/音频功能',accept='配对、重连、权限、干扰与典型手机兼容可测试')
a('powerfw',P,'固件与系统','低功耗、充电策略与热保护实现',20,'bsp power0',owner='固件',output='功耗控制/充电策略',accept='覆盖休眠、唤醒、边充边用、低电量及温度保护')
a('ota',P,'固件与系统','OTA、差分/全量升级与失败恢复实现',15,'boot fwcore',owner='固件',output='OTA链路/恢复机制',accept='升级签名、掉电保护、兼容性及回滚规则明确')
a('alg',P,'运动健康','心率/血氧/睡眠/运动算法集成与版本管理',25,'kick sensor0',owner='算法',output='算法版本/接口/评估脚本',accept='数据来源、算法版本、场景限制和可复现性明确')
a('dataset',P,'运动健康','算法验证数据、招募与授权准备',20,'kick testplan secplan',owner='算法',output='人群与场景数据计划',accept='覆盖肤色、年龄、佩戴、运动强度，数据取得合法授权')
a('appdev',P,'App与云','App绑定、设置、数据展示与账号功能开发',35,'kick appplan','APP','App',output='App Alpha',accept='端到端数据语义、权限、离线、注销及错误提示可用')
a('clouddev',P,'App与云','云服务、API、数据处理及可观测性开发',30,'kick cloudplan','CLOUD','云端',output='云服务/接口/监控',accept='鉴权、数据隔离、限流、备份及审计具备测试条件')
a('appint',P,'App与云','手表—App—云接口联调',15,'appdev clouddev ble','APP','App',output='端到端联调记录',accept='同步、时区、单位、账号迁移与异常重试可验证')
a('gnssdev',P,'选配开发','GNSS硬件、驱动、星历与定位算法实现',20,'bsp gnssplan','GNSS','RF',output='GNSS功能版本',accept='定位、轨迹、授时、天线匹配及功耗进入验证')
a('nfcdev',P,'选配开发','NFC天线、固件、密钥及生态联调',25,'bsp nfcplan','NFC','固件',output='NFC功能/生态联调记录',accept='按选定用途完成读卡/刷卡、异常及安全路径联调')
a('ltedev',P,'选配开发','蜂窝射频、协议、eSIM及运营商联调',35,'bsp lteplan','LTE','RF',output='蜂窝/eSIM Alpha',accept='入网、重选、通话/数据及eSIM生命周期进入验证')
a('wifidev',P,'选配开发','Wi-Fi驱动、网络配置与蓝牙共存',20,'bsp wifiplan','WIFI','固件',output='Wi-Fi功能版本',accept='网络异常、重连、吞吐、功耗及共存进入验证')
a('ecgdev',P,'选配开发','ECG模拟前端、电极与算法实现',25,'bsp ecgplan','ECG','算法',output='ECG功能与信号质量记录',accept='静电、接触、电噪声及用途边界符合设计约束')
a('medsub',P,'选配开发','医疗专项子计划执行与设计控制证据',60,'medroute kick','MED','法规认证',output='专项计划证据索引',accept='按经批准的注册/临床计划逐项完成，实际周期另行细化',note='60工作日仅为占位演示，绝不能作为注册、临床或获批周期承诺')
a('tr4',P,'技术评审','TR4：详细设计与设计实现准备评审',0,'pcb md boot npi',owner='系统架构',approver='技术评审组',output='TR4纪要/详设基线',accept='硬件、结构、软件关键详设及DFX风险完成评审',kind='评审',gate='TR4')
a('evtbuild',P,'EVT','EVT整机组装与配置追溯',7,'tr4 mold bsp optical',owner='NPI',output='EVT样机/Build报告',accept='每台SN对应BOM、硬件、固件、工艺及异常记录')
a('evtfun',P,'EVT','EVT功能、接口与软硬件集成摸底',12,'evtbuild fwcore ble alg',owner='测试',output='EVT功能报告',accept='核心链路可运行，阻塞问题明确复现并分级')
a('evtphy',P,'EVT','EVT防水、跌落、声学与光学摸底',12,'evtbuild cmf',owner='可靠性',output='EVT物理验证报告',accept='密封、跌落、传感和声学薄弱点识别')
a('evtpower',P,'EVT','EVT功耗、续航、充电温升与RF摸底',12,'evtbuild powerfw rfdesign',owner='硬件',output='EVT功耗/RF/热报告',accept='与设计预算对照，瓶颈和整改方向明确')
a('evtoptions',P,'EVT','EVT选配功能集成摸底',10,'gnssdev nfcdev ltedev ecgdev',owner='测试',output='选配EVT报告',accept='所有启用功能具有可复现的冒烟结果')
a('evtclose',P,'EVT','EVT问题归因、方案整改与复测',12,'evtfun evtphy evtpower evtoptions',owner='系统架构',output='EVT闭环清单',accept='架构性风险关闭或有获批的后续验证方案')
a('evtexit',P,'EVT','EVT退出/原型验证检查',0,'evtclose appint wifidev',owner='QA',approver='技术评审组',output='EVT退出纪要',accept='允许转DVT的风险清单、版本及样机需求确认',kind='评审',gate='EVT退出')
a('dvtpcb',P,'DVT准备','DVT硬件/射频改板与制板',20,'evtexit',owner='硬件',output='DVT PCBA/设计变更',accept='EVT根因修改完成且版本可追溯')
a('dvtmd',P,'DVT准备','DVT修模、T2、密封和公差优化',20,'evtexit',owner='结构',output='DVT结构件/尺寸报告',accept='结构问题关闭，材料与工艺接近量产状态')
a('fwcomplete',P,'DVT准备','固件功能完成与系统稳定性加固',20,'evtexit ota',owner='固件',output='Feature Complete固件',accept='规格内功能实现，异常恢复及接口兼容满足测试入口')
a('appcomplete',P,'DVT准备','App/云Beta与兼容性加固',20,'evtexit appint','APP','App',output='App/云Beta版本',accept='核心用户路径可验证，重大联调问题关闭')
a('secimpl',P,'DVT准备','安全与隐私控制实现及自检',15,'evtexit secplan boot',owner='安全隐私',output='控制实现/扫描结果/SBOM',accept='鉴权、加密、日志脱敏、权限与数据生命周期有实现证据')
a('jigs',P,'产测与工艺','产测夹具、ATE、气密及校准设备开发',30,'tr4 npi',owner='NPI',output='产测/校准治具与软件',accept='RF、显示、传感、电流、气密和追溯有工站方案')
a('sop0',P,'产测与工艺','工艺流程、PFMEA与控制计划初版',15,'evtbuild npi',owner='NPI',output='流程图/PFMEA/控制计划',accept='关键工序、防错、返修及密封质量控制明确')
a('packdev',P,'包装与配件','充电配件、包装结构及运输方案开发',20,'kick idfreeze regplan',owner='结构',output='配件/包装设计',accept='充电防呆、标识、运输保护及配件合规范围确认')
a('dvtbuild',P,'DVT准备','DVT整机试制、样机分配及配置审计',8,'dvtpcb dvtmd fwcomplete secimpl',owner='NPI',output='DVT样机/版本及分配表',accept='测试、认证、Beta样机数量和配置满足批准计划')
a('sit',P,'系统集成','系统集成测试与端到端功能覆盖',15,'dvtbuild appcomplete ota evtoptions',owner='测试',output='SIT报告/覆盖矩阵',accept='产品包关键路径覆盖，阻塞缺陷闭环可审计')
a('tr5',P,'技术评审','TR5：集成版本质量与验证入口评审',0,'sit evtexit dataset packdev',owner='系统架构',approver='技术评审组',output='TR5纪要/验证基线',accept='产品包具备正式验证条件，风险、配置及DVP入口核准',kind='评审',gate='TR5')

P='4 验证'
a('dvtfunc',P,'设计验证','DVT功能、性能、压力及长稳验证',20,'tr5',owner='测试',output='功能/性能/长稳报告',accept='覆盖SRS和边界条件，缺陷分级及复测证据完整')
a('dvtrel',P,'设计验证','可靠性：温湿度、冷热冲击、跌落与振动',25,'tr5',owner='可靠性',output='可靠性报告',accept='按批准任务剖面、样本量和失效准则执行')
a('dvtwater',P,'设计验证','防水、动态佩戴、声学膜及老化后复测',20,'tr5',owner='可靠性',output='防水/声学/老化报告',accept='按承诺使用场景和方法验收，覆盖老化及装配变差')
a('dvtsurface',P,'设计验证','汗液、盐雾、磨耗、按键与表带耐久',20,'tr5',owner='可靠性',output='材料/外观/耐久报告',accept='接触材料、涂层和连接机构达到批准规格')
a('dvtbattery',P,'设计验证','电池、充电安全、寿命与整机温升',25,'tr5',owner='硬件',output='电池/充电/温升报告',accept='正常、异常、保护及老化工况达到批准安全目标')
a('dvtendurance',P,'设计验证','典型/重度场景续航及功耗回归',15,'tr5',owner='测试',output='续航模型与实测',accept='亮度、采样、连接、定位等条件锁定，可重复达到已批目标')
a('dvtrf',P,'设计验证','RF、EMC、ESD及人体佩戴共存验证',20,'tr5',owner='RF',output='RF/EMC/ESD报告',accept='覆盖整机、配件、佩戴及启用无线组合')
a('dvtalg',P,'运动健康验证','心率/血氧/睡眠/运动准确度与泛化验证',25,'tr5 dataset',owner='算法',approver='QA',output='算法独立验证报告',accept='按批准参考方法、人群分层、样本和统计判据验收')
a('dvtgnss',P,'运动健康验证','GNSS静态、动态轨迹与复杂环境验证',20,'tr5 gnssdev','GNSS','测试',output='GNSS验证报告',accept='按批准的定位、轨迹和功耗目标验收')
a('dvtnfc',P,'功能选配验证','NFC用途功能、安全与合作方验收',20,'tr5 nfcdev','NFC','测试',output='NFC验证/合作方结论',accept='按已选择生态完成真实场景、互操作和安全验证')
a('dvtlte',P,'功能选配验证','蜂窝弱场、移动性、eSIM与功耗验证',25,'tr5 ltedev','LTE','RF',output='蜂窝/eSIM验证报告',accept='覆盖目标运营商、频段、漫游/切网及异常恢复')
a('dvtwifi',P,'功能选配验证','Wi-Fi吞吐、共存、网络异常与安全验证',15,'tr5 wifidev','WIFI','测试',output='Wi-Fi验证报告',accept='通过批准频段与路由器矩阵，异常场景可恢复')
a('dvtecg',P,'功能选配验证','ECG信号质量、精度与使用场景验证',25,'tr5 ecgdev','ECG','算法',output='ECG验证报告',accept='按用途、参考方法、人群和统计判据验收；不替代医疗注册')
a('dvtapp',P,'App与云验证','手机兼容、权限、升级与国际化验证',20,'tr5 appcomplete','APP','测试',output='手机OS/机型兼容报告',accept='确认支持范围，覆盖后台、断连、升级、时区和语言')
a('dvtcloud',P,'App与云验证','云性能、容灾、数据一致性与监控演练',20,'tr5 clouddev','CLOUD','云端',output='压测/恢复/数据一致性报告',accept='容量、恢复目标、告警和跨区数据策略达到已批要求')
a('dvtsec',P,'安全与隐私验证','渗透、模糊测试、依赖漏洞及隐私验证',20,'tr5 secimpl',owner='安全隐私',output='安全测试/SBOM/整改报告',accept='高风险漏洞与隐私缺口已闭环，残余风险获授权')
a('dvtota',P,'安全与隐私验证','OTA断电、回滚、跨版本及批次兼容验证',15,'tr5',owner='测试',output='OTA兼容/恢复报告',accept='覆盖升级异常、签名拒绝、恢复及数据迁移')
a('beta',P,'用户验证','Beta试戴、用户体验及真实场景验证',25,'tr5 dvtfunc',owner='产品经理',approver='QA',output='Beta报告/体验问题清单',accept='招募授权、问题闭环、体验和健康宣称证据可追溯')
a('regsample',P,'法规认证','认证样机、软件、BOM与标签配置冻结',3,'tr5 dvtrf',owner='法规认证',output='认证样机配置清单',accept='报告配置与拟量产配置一致；变更有再评估机制')
a('btsig',P,'法规认证','Bluetooth SIG资格、型号与品牌合规完成',15,'regsample',owner='法规认证',output='Qualified Product记录',accept='以适当主体完成流程，上市型号与记录一致',note='供应商设计资格不自动替代自有品牌产品资格；流程以SIG当前要求为准')
a('un383',P,'法规认证','锂电运输UN38.3报告、摘要及包装资料核验',15,'regsample dvtbattery',owner='法规认证',output='适用报告/试验摘要/运输资料',accept='型号、电芯/电池包、制造商和运输配置匹配')
a('cnradio',P,'中国市场','中国无线电型号核准适用性与办理',25,'regsample','CN','法规认证',output='型号核准或书面不适用依据',accept='根据频段、功率与目录确认，不将蓝牙一概认作豁免')
a('cnccc',P,'中国市场','中国整机/电池/适配器CCC范围判定及取证',25,'regsample','CN','法规认证',output='CCC适用结论/有效证书',accept='按目录和产品界定确认，核对电池与随附电源配置')
a('cnprivacy',P,'中国市场','中国隐私、App与数据合规验收',20,'dvtsec dvtapp','CN','安全隐私',output='适用清单/整改与验收',accept='权限、健康/位置数据、账号注销及跨境场景经责任人确认')
a('cnnetwork',P,'中国市场','蜂窝产品中国进网/运营商要求核验与办理',35,'regsample dvtlte','LTE_CN','法规认证',output='适用准入证据',accept='依现行目录及目标运营商确认，取得适用准入文件')
a('eured',P,'欧盟市场','欧盟RED、RF暴露、EMC与安全符合性',30,'regsample','EU','法规认证',output='测试/技术文件/DoC资料',accept='频段、使用配置及符合性评定路径由负责人确认')
a('eucyber',P,'欧盟市场','欧盟网络安全、CRA时间适用性与数据要求',25,'regsample dvtsec','EU','安全隐私',output='RED/CRA/数据要求适用结论',accept='按实际投放日期复核适用义务、报告与支持期；登记法源版本',note='RED网络安全相关要求自2025-08-01适用；2026/339规定相关授权法规自2027-12-11起废止，按投放日期复核CRA衔接')
a('eumat',P,'欧盟市场','欧盟材料、电池、废弃物与包装义务核验',25,'regsample','EU','法规认证',output='材料/电池/注册等合规档案',accept='适用RoHS/REACH、电池、WEEE及包装义务逐项确认')
a('usfcc',P,'美国市场','美国FCC授权、RF暴露与标签要求完成',30,'regsample','US','法规认证',output='适用授权/测试/标签文件',accept='整机配置、模块集成条件及实验室资格有效且一致')
a('usprivacy',P,'美国市场','美国目标州隐私及健康宣称适用性核验',20,'dvtsec dvtapp','US','安全隐私',output='市场适用结论/验收',accept='依据目标用户、州及用途确认数据和宣称边界')
a('operator',P,'蜂窝准入','目标运营商/GCF/PTCRB等适用准入完成',40,'regsample dvtlte','LTE','法规认证',output='适用准入/合作方验收记录',accept='按市场及运营商确定项目，全部适用准入已完成')
a('medapproval',P,'医疗专项','医疗注册/许可及临床证据放行核验',60,'medsub dvtecg','MED','法规认证',output='适用许可/证据/标签批准',accept='取得实际适用许可和证据方可放行；无许可不能用排期替代',note='60工作日只为演示占位，必须替换成经批准的专项计划及获批条件')
a('regbase',P,'认证汇总','基础与中国市场认证资料汇总',3,'btsig un383 cnradio cnccc',owner='法规认证',output='基础/中国认证证据包',accept='所有启用项目有完成或经批准不适用的证据')
a('regextra',P,'认证汇总','欧盟、美国及蜂窝认证资料汇总',3,'eured eucyber usfcc operator',owner='法规认证',output='海外/蜂窝认证证据包',accept='全部启用市场与无线配置准入证据完整')
a('regclose',P,'认证汇总','法规资料完整性及医疗路径核验',3,'regbase regextra medapproval cnnetwork',owner='法规认证',output='认证放行清单',accept='检查认证矩阵全部项目；缺失项不得以排期完成替代')
a('reglast',P,'认证汇总','材料、数据、隐私与市场文件最终核验',2,'eumat cnprivacy usprivacy regclose',owner='法规认证',output='完整市场合规包',accept='适用性矩阵所有启用行都具备放行结论')
a('fix1',P,'缺陷与回归','DVT主要功能/可靠性问题整改与复测',15,'dvtrel dvtwater dvtbattery dvtalg',owner='系统架构',output='DVT问题关闭证据',accept='根因、纠正措施及影响范围回归齐全')
a('fix2',P,'缺陷与回归','选配功能与端云问题整改与复测',12,'dvtgnss dvtnfc dvtlte dvtecg',owner='系统架构',output='选配问题关闭证据',accept='启用功能的高风险问题关闭')
a('fix3',P,'缺陷与回归','材料、续航、无线及升级问题闭环',10,'dvtsurface dvtendurance dvtrf dvtota',owner='系统架构',output='跨域问题关闭证据',accept='设计和生产影响评估完成，回归通过')
a('fix4',P,'缺陷与回归','App/云/Wi-Fi及安全问题闭环',10,'dvtapp dvtcloud dvtwifi dvtsec',owner='系统架构',output='端云与安全回归证据',accept='适用版本缺陷闭环且接口和数据兼容')
a('dvtexit',P,'设计验证','DVT退出与设计冻结',0,'fix1 fix2 fix3 fix4',owner='QA',approver='技术评审组',output='DVT退出/冻结基线',accept='需求验证覆盖、设计风险和残余问题可接受，允许PVT',kind='评审',gate='DVT退出')
a('pvtprep',P,'生产验证','PVT物料齐套、线体与人员准备',12,'dvtexit jigs sop0',owner='NPI',output='PVT准备清单/齐套表',accept='量产候选物料、设备、工艺、人员和追溯就绪')
a('pvt',P,'生产验证','PVT小批试产及制造过程确认',10,'pvtprep',owner='NPI',output='PVT Build报告',accept='记录工位、产能、良率、返修和异常，样本按计划')
a('msa',P,'生产验证','量测系统、产测覆盖与校准相关性验证',8,'pvt',owner='NPI',approver='QA',output='MSA/GR&R或适用量测评价',accept='产线与实验室相关性、误判漏判和校准溯源满足已批标准')
a('yield',P,'生产验证','良率、节拍、产能及关键过程能力验收',10,'pvt',owner='NPI',approver='QA',output='良率/产能/过程能力报告',accept='达到项目批准目标；示例目标须由制造与质量签批')
a('pvtort',P,'生产验证','PVT批次抽检、ORT与包装运输验证',15,'pvt packdev',owner='可靠性',output='PVT/ORT/运输报告',accept='生产工艺对可靠性无不利影响，运输后功能外观合格')
a('supplyready',P,'生产验证','量产供应能力、备料与替代料放行',10,'dvtexit supplier',owner='采购',output='供应保障/物料放行清单',accept='交期、产能、单一来源、PCN和替代料验证闭环')
a('service',P,'服务与上市','维修流程、备件、诊断工具和客服培训',20,'dvtexit',owner='服务',output='服务方案/备件/培训',accept='保修、退换、数据保护及返修防水复验可执行')
a('docs',P,'服务与上市','说明书、标签、健康宣称及营销资料定稿',15,'dvtexit claim',owner='产品经理',output='用户资料/标签/宣称证据',accept='与认证型号、实际功能、用途限制和市场语言一致')
a('launchplan',P,'服务与上市','渠道、定价、首销及上市供货计划',15,'dvtexit finance',owner='市场',output='上市计划/需求预测',accept='需求、渠道库存、SKU、区域和售后准备一致')
a('store',P,'服务与上市','App商店审核及正式分发准备',15,'dvtapp docs','APP','App',output='商店审核/分发就绪证据',accept='目标区域、账号、权限、政策和配套版本可供用户获取')
a('releasecandidate',P,'版本与放行','量产候选版本回归与配置审计',10,'dvtexit beta reglast',owner='测试',approver='QA',output='RC回归/配置审计',accept='BOM、固件、算法、App、云与认证/产测配置一致')
a('pvtexit',P,'生产验证','PVT退出与生产准备验收',0,'msa yield pvtort supplyready',owner='NPI',approver='QA',output='PVT退出/生产准备结论',accept='量产工艺与测试可重复，良率产能及残余风险获批',kind='评审',gate='PVT退出')
a('tr6',P,'技术评审','TR6：产品包与制造验证总评审',0,'pvtexit releasecandidate service reglast',owner='QA',approver='技术评审组',output='TR6报告/技术放行建议',accept='验证、用户试用、认证、制造及服务证据完整',kind='评审',gate='TR6')
a('adcp',P,'投资决策','ADCP：可获得性与商业发布决策',0,'tr6 launchplan docs store',owner='PM',approver='IPMT',output='ADCP决议/发布授权',accept='商业、供应、质量、法规及服务准备获授权确认',kind='评审',gate='ADCP')

P='5 发布'
a('mpbom',P,'量产准备','量产BOM、图纸、SOP与软硬件版本发布',3,'adcp',owner='NPI',output='受控量产资料包',accept='PLM/MES/ERP版本、替代料与烧录文件一致')
a('mporder',P,'量产准备','首批生产订单、物料与排产落实',5,'adcp supplyready',owner='采购',output='首批订单/排产/齐套',accept='首销区域、SKU、产能、运输和库存风险已确认')
a('mp',P,'量产爬坡','MP首批量产与过程质量巡检',10,'mpbom mporder',owner='NPI',output='首批量产报告',accept='关键工序、追溯、良率和异常处理稳定')
a('oqc',P,'量产爬坡','首批OQC、抽检与质量放行',3,'mp',owner='QA',output='OQC/批次放行记录',accept='符合已批抽样计划，重大缺陷及不合格品已处置')
a('logistics',P,'上市交付','运输文件、仓储、区域合规与交付准备',5,'oqc un383',owner='采购',output='出货/运输/仓储资料',accept='电池运输、标签、目的市场和库存追溯满足适用要求')
a('cloudprod',P,'上市交付','云生产容量、安全运维与值守就绪',5,'adcp dvtcloud','CLOUD','云端',output='生产变更/监控/值守记录',accept='备份恢复、告警、回滚及隐私事件响应已演练')
a('channel',P,'上市交付','渠道物料、培训与售后入口核验',5,'adcp docs service',owner='市场',output='渠道/客服准备记录',accept='商品信息、支持机型、功能限制及用户入口一致')
a('gaready',P,'上市交付','GA发布前产品包与证据复核',2,'logistics cloudprod channel store',output='GA检查清单',accept='所有销售市场准入有效，版本可获取，质量放行证据可追溯')
a('ga',P,'商业发布','GA：商业可获得/正式上市',0,'gaready',owner='产品经理',approver='IPMT',output='GA公告/正式SKU与版本',accept='经授权对客户正式交付并具备供货、服务和版本支持',kind='里程碑',gate='GA')
a('handover',P,'量产交接','PDT到生命周期团队移交与项目复盘',5,'ga',output='交接/项目复盘/未决项责任',accept='LMT、服务、质量及供应链接受指标、资料和遗留事项')

P='6 生命周期'
a('field',P,'在市监控','首销质量、激活、退货与投诉监测窗口',30,'ga',owner='QA',output='首销质量看板/周报',accept='按批准阈值监测批次、区域及版本异常',note='30工作日为首轮观察窗口；监测应持续到支持期结束')
a('capa',P,'在市监控','现场问题FRACAS、8D与纠正预防',15,'field',owner='QA',output='FRACAS/8D/闭环验证',accept='影响范围、根因、措施及有效性可追溯')
a('maintenance',P,'版本与支持','维护版本、漏洞与OTA灰度发布窗口',30,'ga',owner='固件',output='维护/漏洞响应与灰度记录',accept='评估回归、兼容、用户告知与回滚效果',note='30工作日为首轮维护窗口；不代表软件支持期')
a('costdown',P,'成本与供应','成本优化、PCN和第二来源验证',25,'handover',owner='采购',output='降本/PCN/替代料评审',accept='变化经ECR/ECO并评估认证、算法、质量和可靠性影响')
a('lcreview',P,'经营评审','上市后经营、质量和用户价值复盘',5,'capa maintenance costdown',owner='产品经理',approver='IPMT',output='上市后评审/迭代建议',accept='销量、毛利、退货、用户反馈和质量与商业计划比较')
a('eolplan',P,'退出与退市','EOL/EOS计划、最后采购与客户通知',20,'lcreview','RETIRE','产品经理','IPMT',output='EOL/EOS及库存/备件计划',accept='业务触发后确定停产、支持期、合同及用户告知',note='默认关闭；应按实际生命周期和支持承诺设置最早开始约束')
a('eoldata',P,'退出与退市','退市数据保留/删除、云服务与安全支持处置',15,'eolplan','RETIRE','安全隐私',output='退出数据与安全支持方案',accept='符合承诺和适用要求，迁移、删除和漏洞责任明确')
a('eoldcp',P,'退出与退市','生命周期退出决策与归档',0,'eoldata','RETIRE','产品经理','IPMT',output='退出决议/最终归档',accept='存量用户、服务、数据、库存和法律义务妥善处理',kind='评审',gate='EOL DCP')

P='7 跨阶段管理'
a('pmconcept',P,'项目与变更','概念阶段例会、风险、成本与配置管理',20,'charter',output='周报/风险与决策记录',accept='风险、假设、问题与行动项有责任人与关闭证据',note='示例管理窗口，不作为阶段退出前置；按实际周期续建')
a('pmplan',P,'项目与变更','计划阶段例会、需求与基线变更管理',30,'cdcp',output='计划变更/决策/基线记录',accept='变更影响范围、成本、资源、进度和评审均有记录')
a('pmdev',P,'项目与变更','开发阶段跨域例会、缺陷与配置管理',90,'pdcp',output='周报/缺陷/Build与ECO记录',accept='设计、采购、制造、软件及认证变更相互同步')
a('pmverify',P,'项目与变更','验证阶段风险、缺陷与认证变更管理',70,'tr5',output='验证问题/配置与决议',accept='测试版本、修复范围及重测和重新认证影响可追溯')
a('pmlaunch',P,'项目与变更','发布阶段日例会与上市异常响应',20,'adcp',output='爬坡与发布行动项',accept='质量、供应、服务和销售异常及时升级及闭环')

SOURCES = [
 ('S01','IBM Research','Concepts in the definition of an enterprise development process','2011-07-26','https://research.ibm.com/publications/concepts-in-the-definition-of-an-enterprise-development-process','IPD覆盖软硬件与服务；强调商业目标、治理和角色。','支撑方法论定位；不提供本模板任务与工期。'),
 ('S02','Huawei','华为产品安全基线白皮书','官网公开PDF第5页；文内页码05','https://www-file.huawei.com/admin/asset/v1/pro/view/44e2e06553364e42b97aca0c9ff333b6.pdf','公开图示包含IPD阶段、Charter、CDCP/PDCP/ADCP、TR与GA，并将安全活动嵌入流程。','本模板TR与智能手表Build对应关系为裁剪建议，非华为内部流程复刻。'),
 ('S03','PMI / IBM实践作者','Where the rubber meets the product development road','1996-03','https://www.pmi.org/learning/library/2019/04/07/15/15/institutionalizing-project-management-development-community-4802','IBM实践说明：跨职能团队、IPMT/PDT、投资检查点及项目管理。','历史实践来源，帮助解释投资决策与执行团队关系。'),
 ('S04','Bluetooth SIG','Qualify your product','动态页面；核验2026-11-08','https://www.bluetooth.com/develop-with-bluetooth/qualify/','蓝牙产品资格流程、品牌主体和上市前完成要求。','不用旧版Declaration/Launch Studio术语替代当前流程。'),
 ('S05','MIIT','无线电发射设备管理规定','2023发布；以现行版本为准','https://www.miit.gov.cn/zcfg/wxdl/art/2023/art_4ef6b3a619f0444697197ae33a901ce3.html','中国无线电型号核准及微功率短距离设备条件。','先按产品频段、功率和目录判断，不把蓝牙全部豁免。'),
 ('S06','MIIT','2400MHz、5100MHz和5800MHz频段无线电管理通知','2021','https://www.miit.gov.cn/jgsj/wgj/wjfb/art/2021/art_58b24430cb93476fb18a51fe7a350b61.html','蓝牙/Wi-Fi等频段、天线设计与核准规则线索。','产品具体测试限值由法规负责人核定。'),
 ('S07','CNCA','移动电源、锂离子电池和电池组CCC实施规则公告','2025年第15号','https://www.cnca.gov.cn/zwxx/gg/2025/art/2025/art_915c12eceb7a4ad1a848e9598844e911.html','电池与电池组认证实施规则。','不据此直接推定所有手表整机和所有电池都在CCC范围。'),
 ('S08','European Commission','Radio Equipment Directive (RED)','动态页面；核验2026-11-08','https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en','无线电设备欧盟符合性、网络安全与CRA衔接。','按实际投放市场日期复核适用义务和标准清单。'),
 ('S09','EUR-Lex','Commission Delegated Regulation (EU) 2026/339','2026-02-16','https://eur-lex.europa.eu/eli/reg_del/2026/339/oj/eng/pdf','规定2022/30自2027-12-11废止；此前已投放设备义务仍需判断。','避免误解为2026年已取消RED网络安全要求。'),
 ('S10','FCC / US Government','47 CFR §2.803 — marketing RF devices','2024 CFR公开版本；实际使用须复核现行条文','https://www.govinfo.gov/content/pkg/CFR-2024-title47-vol1/pdf/CFR-2024-title47-vol1-sec2-801.pdf','美国射频设备销售前授权原则。','型号、授权路径、RF暴露和实验室资格逐项确认。'),
 ('S11','UNECE','UN Recommendations on Transport of Dangerous Goods, Rev.24, Vol.I','Rev.24 / 2025','https://unece.org/sites/default/files/2025-09/ST_SG_AC10_1_Rev24e_Vol%20I_1.pdf','锂电类型试验及UN38.3试验摘要资料要求线索。','运输配置、报告和当前运输规则需匹配，不称为通用UN38.3认证证书。'),
 ('S12','FDA','General Wellness: Policy for Low Risk Devices','2026-01','https://www.fda.gov/regulatory-information/search-fda-guidance-documents/general-wellness-policy-low-risk-devices','一般健康与医疗用途的边界。','是否医疗器械取决于用途/宣称等，不由有无ECG单独决定。'),
]

GATE_INFO = [
 ('charter','立项授权','IPMT','机会、路标、概念预算、PDT任命','机会明确；有概念阶段投入上限、负责人及退出条件'),
 ('tr1','技术评审','技术评审组','产品概念、初版需求、技术与质量风险','关键技术路径可行，后续验证和残余风险有责任人'),
 ('cdcp','投资决策','IPMT','初版商业计划、TR1、产品概念、下一阶段预算','机会价值成立，批准计划阶段投入/改向/中止'),
 ('tr2','技术评审','技术评审组','PRD/SRS、需求追踪、DVP&R、认证与安全需求','规格完整、可验证，需求分配与验收责任明确'),
 ('tr3','技术评审','技术评审组','系统架构、堆叠与接口、DFMEA、DFX和风险计划','跨域设计具备可实施性，重大风险有验证方案'),
 ('pdcp','投资决策','IPMT','商业计划、WBS、预算、资源承诺、TR2/TR3','范围/进度/成本/质量/资源基线签批，允许开发投资'),
 ('tr4','技术评审','技术评审组','详细设计、DFX、生产测试方案、设计风险','详细设计可追溯，样机Build及技术验证准备就绪'),
 ('evtexit','Build退出','技术评审组','EVT报告、架构风险、根因整改与配置清单','核心可行性完成验证，允许DVT的条件获批'),
 ('tr5','技术评审','技术评审组','集成版本、SIT、EVT闭环、正式验证计划','产品包版本明确，具备正式DVT/用户验证条件'),
 ('dvtexit','Build退出','技术评审组','DVT覆盖/报告、缺陷、可靠性、安全及选配验证','满足批准的设计验证目标，设计冻结和残余风险获批'),
 ('pvtexit','Build退出','QA','PVT、MSA、良率/产能、ORT及供应能力报告','量产过程可重复，测试校准有效，生产准备获批'),
 ('tr6','技术评审','技术评审组','验证、Beta、认证、PVT、服务与RC证据包','产品包及制造验证完成，提出有证据的技术放行意见'),
 ('adcp','投资决策','IPMT','TR6、财务、供应、市场、服务和认证放行','决定商业发布；未完事项的范围、时限和风险接受明确'),
 ('ga','商业可获得','IPMT','首批放行、区域认证、正式版本、渠道及客服就绪','客户可购买、激活、使用并获得承诺的支持'),
 ('eoldcp','退出决策','IPMT','停产、库存、备件、用户通知、数据和支持处置','存量用户及法定义务已妥善处理，允许退出归档'),
]
