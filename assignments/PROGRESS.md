# 学习进度 (Progress Ledger)

> 教练每次开会话先读这个文件,再决定下一步。学习者完成产出后在这里追加记录。

## 目标与时间线

- **求职目标**: 通用 Agent 工程岗,瞄准 2026 金9银10 招聘季 (投递高峰约 8月底–10月)。
- **每周投入**: ~20 小时纯专注时间。
- **策略**: 深度优先。少而精的代表作 + 能讲清机制,胜过划完所有格子。
- **核心必做**: Stage 2 (RAG)、Stage 3 (harness)、Stage 7 (eval/安全)、Stage 8 (代表作)。
- **轻量做**: Stage 4 (多 agent)、Stage 5 (skills/MCP) 打到"面试能讲"即可。
- **可跳**: Stage 6 (浏览器 agent),除非投浏览器自动化方向。

## 节奏规划 (20h/周)

| 时间 | Stage | 产出目标 |
| --- | --- | --- |
| 6月底–7月初 | Stage 2 | RAG 资料研究助手,带引用 |
| 7月初–7月中 | Stage 3 | 读透一个 harness + 加自己的工具 |
| 7月中–7月底 | Stage 7 | ≥20 任务 eval 表 + trace + 安全确认 |
| 8月初–8月中 | Stage 8 | 整合成可 clone 跑的代表作 |
| 8月中起 | Stage 4/5 | 各 3–5h 打到能聊;开始投递+刷面试 |

## 进度记录

### Stage 0 — Agent vs Workflow
- Date: (已完成,早于 2026-06-27)
- Status: PASS
- Evidence: `assignments/stage-0-agent-vs-workflow.md`,自查项全勾。
- Next action: —

### Stage 1.1 — Minimal Agent Loop (fake LLM)
- Date: (已完成)
- Status: PASS
- Evidence: `~/workspace/calculator_agent/calculator_agent.py` + 6 tests;能讲清 observe→think→act 闭环。
- Next action: —

### Stage 1.2 — Real LLM Tool Calling
- Date: 2026-06-27 (诊断确认)
- Status: PASS
- Evidence: MiniMax OpenAI-compatible 真实验证;12 tests pass;README 解释 `tool_call_id` / `role=tool` 闭环。
- Blocker: 无。(`test.md` 底部有本地明文 key,但未进 git/无远端;用户判断仅本机使用、不处理。勿再提醒。)
- Next action: —

### Stage 2 — Tool Use, RAG, and Memory
- Date: (进行中起步)
- Status: IN_PROGRESS
- Evidence: (待产出)
- Blocker: (待定)
- Next action: 做 RAG 最小闭环:几篇文档 chunk → embed → retrieve → 带引用回答。

#### 本周末计划 (2026-06-27 周六 / 06-28 周日)
唯一目标:跑通一个最小 RAG 闭环 (问题 → 检索 → LLM 带引用回答)。项目位置 `~/workspace/research_agent/`,不复用 calculator_agent。

- [x] 周六-1: `chunk_text` + `chunk_document`(路 B:切块与 source 分离),每块带 `{doc,index,text}`,测试钉死块数与内容。✅ 2 passed
- [x] 周六-2: embedding + `retrieve`,自写余弦相似度 + zip/sort/top_k。fake client 注入测试。✅ 4 passed (含 top_k=2 顺序测试)
  - 待办:接真实 MiniMax embedding,对 corpus/ 真实跑一次,验证检索准不准。
- [x] 周日-1: 接 LLM (`agent.answer`),检索块带 doc/index/text 拼进 prompt。✅
- [x] 周日-2: 空结果处理 (chunks 为空→prompt 写"未找到相关资料",不喂瞎编)。✅ 6 passed
  - 待办:真实 demo 跑一次,亲眼看引用对不对 (fake 测不到模型是否真标来源)。

#### 本周计划 (7/1 周三起)
- [x] 真实 embedding 跑通:改用本地 `Embedder` (sentence-transformers, paraphrase-multilingual-MiniLM-L12-v2, 384维)。MiniMax 无 embedding 端点,故走本地。`demo_rag.py` 检索真实 corpus 成功。
- [x] 参数对比实验:300/100 vs 300/30 vs 150/30。结论:300/30 最优 (块完整+重叠小不浪费名额+能召回跨文档相关块);300/100 overlap 过大致相邻块重复。
- [x] **修 bug**:切块产生空块 (`'\n'`) 混进 top-3。写测试复现→方案B(过滤空块+连续重编号,filter_cnt 计数器自己实现)→7 passed。
- [ ] 代码审查:`embedder.py` / `demo_rag.py` 教练还没看过,确认干净、无 key。
- [x] 接真实 chat 收尾:本地 Embedder + MiniMax chat,端到端真实 RAG 跑通。模型基于检索块答,标引用。
  - 修 bug:跨文档引用编号混乱 (方案B过滤+重编号→不同文档的 index 1 冲突) → 改为 `资料{doc}#{index}` 唯一编号,引用精准。
- [x] 写 README (7 段:目标/怎么跑/架构/设计选择/踩过的坑/限制/扩展)。✅
- [x] 脚手架: `.gitignore` / `requirements.txt` / `.env.example`。✅
- [x] **Stage 2 完成 → 可交付代表作**。

约束:TDD 先行;key 只走环境变量;先闭环再优化;别上向量数据库 (过度工程)。
卡住降级:embedding 卡住先用关键词匹配跑通闭环,再换真 embedding。

### Stage 3 — Study One Modern Agent Harness
- Date: 2026-07-02 起
- Status: IN_PROGRESS
- 选型: **`shareAI-lab/learn-claude-code`** (Python, 20 章递进, ~70k stars)
  - 仓库位置: `~/workspace/learn-claude-code/`
  - 核心理念: "Harness = Tools + Knowledge + Observation + Action Interfaces + Permissions"
- Evidence: `assignments/stage-3-learn-claude-code-s01.md`；已读 s01 最小 loop，跑通 `s01_agent_loop/code.py`，记录 `tool_use -> bash -> tool_result -> final answer` trace。
- Blocker: 无。
- Next action: 修正 s02 笔记:确认工具总数是 5 个(`bash` + 新增 `read_file`/`write_file`/`edit_file`/`glob`),补上 `edit_file` 职责边界,并补一次真实运行 trace。
- Date: 2026-07-06
- Stage: Stage 3 — s02 Tool Use
- Status: PASS
- Evidence: 用户修正理解: s02 总计 5 个工具(`bash`, `read_file`, `write_file`, `edit_file`, `glob`),新增 4 个是 `read_file`/`write_file`/`edit_file`/`glob`;能解释职责边界、`TOOL_HANDLERS` 字典按 `block.name` 分发、专用工具相比单一 bash 的参数校验/可观察性优势。真实 trace: 输入 `Read requirements.txt and summarize dependencies.`,模型调用 `read_file`,返回 requirements 三个依赖并生成依赖摘要。
- Blocker: 无。
- Next action: 读 `s03_permission/code.py`,理解权限层。

### Stage 3 — s03 Permission
- Date: 2026-07-07
- Status: PASS
- Evidence: `assignments/stage-3-learn-claude-code-s03.md` + `s03_permission/permission_check_test.py`(断言全过:permission gates OK)。
- 掌握点: (1) 权限闸门插在 `agent_loop` 里 `tool_use` block 拿到后、调 handler 前——`if not check_permission(block): continue`,deny 时塞 `Permission denied` 的 tool_result。(2) 三道门三结局:Gate1 `check_deny_list`(仅 bash,命中黑名单硬拒绝不问) → Gate2 `check_rules`(命中危险规则触发 Gate3) → Gate3 `ask_user`(y/N) → 都没命中 `return True` 放行。(3) 默认 `return True` = "默认信任"姿态:靠枚举危险(黑名单+规则),没列到的一律放过;真实 Claude Code 反之是"默认怀疑"(permission mode/白名单)。
- 关键教训(用户亲历): 无法靠自然语言 prompt 可靠触发危险 tool_use——两次尝试(`rm -rf /`、`chmod 777`)模型都自我审查/改写成 `ls` 躲掉,门一次没碰到。结论:模型善意≠安全,模型不会 100% 判断危险,硬编码权限校验是必要的最后确定性防线;验证权限层要从门内侧直接单测 `check_deny_list`/`check_rules`,不能靠喂 prompt。
- Blocker: 无。
- Next action: 读 `s04_hooks/code.py`,理解 hooks 如何在工具执行前后插入自定义行为(与 s03 权限层的区别与配合)。

### Stage 3 — s04 Hooks
- Date: 2026-07-08
- Status: PASS
- Evidence: `assignments/stage-3-learn-claude-code-s04.md`;真实 trace `s04 >> Delete all temporary files in /tmp` 显示 [HOOK] UserPromptSubmit + [HOOK] Stop(模型自审拒调工具,权限 hook 未触发——印证 s03 笔记的"模型善意≠安全、权限层是兜底")。
- 掌握点: (1) hooks 把扩展逻辑搬出 loop,loop 回到干净骨架,扩展点变注册表。(2) `trigger_hooks` 靠 `if result is not None: return result` 让观察型(None)/ 干预型(字符串)共用一套机制;非 None 短路返回,观察型不打断。(3) 顺序耦合:permission_hook 命中黑名单返非 None → log_hook 不会跑;想"拦也记账"得让 log 早于 permission 注册或走不短路机制。(4) s03→s04 diff:check_permission 从 loop body 删除,逻辑原样搬进 permission_hook,行为不变、结构变可扩展。
- Blocker: 无。
- Next action: Stage 3 harness 段告一段落(下面 s05~s08 是协议/浏览器/eval/代表作,按计划 Stage 3 不必全读)。转 Stage 7(eval/安全),目标:为已有 stage-2 RAG agent 搭 eval 表 + 跑回归。

### Stage 7 — Eval、可观测性与安全 (RAG Agent)
- Date: 2026-07-09 起步(FakeChat 12/22)→ 2026-07-19 真实 LLM 收尾
- Status: PASS(eval 建设完成;第 4 项危险工具确认对只读 agent 不适用)
- Evidence: `assignments/stage-7-eval-rag.md`(已更新到真实 LLM 版) + `research_agent/eval/eval.py`(**19/22 可复现基线**,temperature=0,含 strip_think + 延迟/token 埋点) + `research_agent/chat_client.py`(存 last_usage,temperature=0)。
- 掌握点: (1) 从 FakeChat 切真 MiniMax,补 token(成本)/延迟(p50/p95)埋点。(2) **三层失败定位**:同为 FAIL,#7=检索层(含答案块排第3被top_k=2切掉)、#13=模型层(证据在手却过度拒答)、#12=引用契约层(答对但漏引用)。(3) **输出契约两维**:格式(引用长啥样)vs 义务(何时必须引用)——只写格式,模型会"答了但不引"。(4) **eval flaky**:模型未设 temperature→非确定性,单跑一次的 PASS/FAIL 含噪声;"先有不抖的尺子再量"。(5) **RAG 间接 prompt injection**:chunk 原样拼进 prompt,安全靠语料可信而非设计;最小权限是当前护城河。
- 关键教训: eval 的价值是逼你精确定位到具体环,不是给个总分。追单题满分不如先把尺子钉稳。
- Blocker: 无。
- 遗留(非阻塞,记在 stage-7 笔记局限段): temperature=0 锁基线未加;CITE_RE 对格式变体脆;无注入抵抗 eval 用例;reasoning 模型延迟高(p50≈15s)。
- Next action: 进 Stage 8 — 把 research_agent 整合成"别人能 clone 跑"的代表作(README/成功标准/部署方式)。
