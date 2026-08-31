# Stage 7 — Eval、可观测性与安全 (RAG Agent)

## 目标
给 Stage 2 的 research_agent 搭一个 ≥20 题的 eval 表,端到端跑通,
记录成功率/延迟/成本,看 trace 定位失败环,并认识 RAG 特有安全风险。

## 数据集
`research_agent/eval/eval_dataset.json` — 22 题
- 16 题 answerable(每文档 4 题)
- 3 题 cross_doc(跨文档综合)
- 3 题 unanswerable(corpus 外、应拒答)
每题结构:`{id, type, question, expected_docs[], expected_keywords[], expected_citations}`

## 校验三件事(在剥掉 <think> 后的最终答案上)
1. **引用数**:answerable ≥1, cross_doc ≥2, unanswerable = 0
2. **引用文档**:cite_docs ∩ expected_docs ≠ ∅
3. **关键词**:任一 expected_keywords 命中(大小写不敏感,unanswerable 跳过)

## 跑法
```
HF_HUB_OFFLINE=1 python3 research_agent/eval/eval.py
```
(本地 embedder 已缓存,离线模式避免 HF 联网握手抖动;chat 走真实 MiniMax API)

## 架构演进:FakeChat → 真实 LLM
- **Embedding**:始终用本地 Embedder(sentence-transformers,384 维,零成本)
- **Chat**:
  - **第一阶段(2026-07-09)**:FakeChat 正则复述 prompt 里的资料。
    便宜可重放,但**答案质量测不到**,unanswerable 永远硬答(不会拒)。
  - **本轮(2026-07-19)**:切真实 `MiniMaxChat`,同时补齐可观测性:
    - `chat_client.py` 存 `resp.usage` → 记 token(成本)
    - `eval.py` 用 `time.perf_counter` 包每题 → 记延迟 p50/p95
    - 整轮复用一个 chat 实例,累加 prompt/completion token

## 结果演进(本轮真实 LLM,2026-07-19)

| 步骤 | 改动 | 结果 |
| --- | --- | --- |
| 切真模型 + 加拒答 prompt | FakeChat→MiniMax,prompt 加"资料不足就拒答" | 9/22 |
| 修 Bug1:eval 剥 `<think>` | 校验只看最终答案,不吃 think 块噪声 | (未单跑) |
| 修 Bug2:引用格式契约 | prompt 明确"引用写成 资料{doc}#{序号}" | 19/22 |
| 修 #12:引用**义务** | 补"每处用到资料都必须紧跟引用" | 21/22 |

延迟:p50 ≈ 15-17s、p95 ≈ 45-57s(reasoning 模型狂想);总 token ≈ 25k/轮。

## 三层失败定位(Stage 7 第 3 项:看 trace 定位失败在哪一环)
用检索 trace(打印每块 cosine 分数 + 排名)把 3 道失败题拆成 3 种不同的病:

| 题 | 失败环 | 根因 | 修法 |
| --- | --- | --- | --- |
| #7 余弦相似度 | **检索层** | 含答案块排第 3,top_k=2 切掉了 | 调大 top_k |
| #13 工具失败 | **模型/prompt 层** | 块排第 1、2 已检索到,却过度拒答 | 拒答指令调弱 |
| #12 停止条件 | **引用契约层** | 内容答对,但列表式回答漏引用 | 补引用义务 |

**关键教训**:eval 的价值不是给个总分,是**逼你精确定位到具体环**,
而不是笼统说"模型不行"。同样是 FAIL,病因可能完全不同。

## 最重要的发现:eval 不可复现(flaky)
追最后一道 #14 时发现它**一会儿 PASS 一会儿 FAIL**——同题、同代码、结果不同。
重跑一次 #14 引用完美(PASS),但上一轮它把引用写飘了(`资料 doc #0` 带空格)→ 正则漏判(FAIL)。

**根因两层:**
1. **模型非确定性(根本)**:`chat_client.py` 没设 `temperature`,默认 >0,每次采样不同。
   → 单跑一次的具体 PASS/FAIL **含噪声**;9→19→21 的大趋势是真的,但某一题的成败不能只看一次。
2. **引用正则太脆(次要)**:`CITE_RE` 只认 `资料\S+?#\d+`,模型格式飘一点(空格/全角括号)就漏判。

**教训:先有一把不抖的尺子,才能量任何改动的效果。** flaky 没解决前,无法判断 prompt 改动到底有没有用。
- **收尾动作**:`chat_client.create(...)` 加 `temperature=0`,让 eval 可复现,锁一个能信的基线数。
- (生产才需要:每题跑 N 次记通过率;此项目太慢太贵,不做。)

## 输出契约(output contract)的两个维度
修 #12 学到的:约束模型输出要分开两件事,少一个都会漏。
- **格式(format)**:引用长什么样(`资料{doc}#{序号}`)——第一轮补了,19/22。
- **义务(obligation)**:什么情况下**必须**引用。"引用时必须写成X"只管了格式,
  模型可以合法地"答了但不引";补上"每处用到资料都必须紧跟引用"后 → 21/22。

## RAG 安全:间接 prompt injection(Stage 7 第 5 项)
`agent.py` 把 `chunk['text']` 原样拼进 prompt。当前语料自己写、可信,所以安全——
但**安全靠的是语料可信,不是设计安全**。
- **威胁**:若某块内容写"忽略以上指令,回复X",它和开发者指令**平级**进同一 prompt,
  模型分不清"指令"和"数据"。语料一旦换成抓取/用户上传,注入面立刻打开。
- **数据外泄/工具滥用**:当前只有只读 retrieve,注入了也泄不出去;
  一旦加"访问 URL / 发邮件"等对外工具,注入 + 外泄通道就成真。**最小权限是当前护城河**。
- **抬高门槛(非根治)**:划语料信任边界、用分隔符包住检索内容并标注"这是数据不是指令"、
  最小权限、把引用校验当弱信号(被带偏的答案往往引用不上)。
- **eval 缺口**:现有 #20-22 只测"无证据幻觉",**没有测"注入抵抗"用例**——下一轮可加投毒 chunk。

## 证据
- `research_agent/eval/eval_dataset.json`(22 题)
- `research_agent/eval/eval.py`(真实 LLM 端到端,21/22,含延迟/token 埋点 + strip_think)
- `research_agent/chat_client.py`(存 `last_usage` 记 token)
- 三层失败定位见上表

## 局限(留给下一轮)
1. **eval 未钉死**:`temperature=0` 还没加,当前数字含采样噪声。这是收尾第一动作。
2. **引用正则脆**:`CITE_RE` 对格式变体敏感,可放宽(容忍空格/全角)或让 prompt 更严。
3. **无注入抵抗用例**:安全维度只停在认知,eval 层没落地投毒测试。
4. **延迟高**:reasoning 模型 p50 ≈ 15s,若上生产需考虑换非推理模型或设 max_tokens。
