# Stage 2 — RAG Research Agent（指针文档）

> Stage 2 是**项目级代表作**，证据不在这里——这里是**索引**，
> 指向真正的代码项目。详细笔记请到 `~/workspace/research_agent/` 看 README + 代码 + 测试。

## 项目位置
`~/workspace/research_agent/`（与本仓库 `assignments/` 平级，不在仓库内）

## 一句话
基于本地语料的 RAG 资料研究助手：**问题 → 检索 → LLM 带引用回答**。
端到端真实跑通（本地 sentence-transformers embedding + MiniMax chat），能精准标引用（`资料{doc}#{index}`）。

## 关键产出（在该项目下）
- `README.md` — 7 段：目标 / 怎么跑 / 架构 / 设计选择 / 踩过的坑 / 限制 / 扩展
- `agent.py` — 端到端：retrieve → 拼 prompt → LLM 回答
- `chunking.py` / `retrieval.py` / `embedder.py` — 三段闭环
- `demo_rag.py` — 真实语料演示脚本
- `test_chunking.py` / `test_retrieval.py` / `test_agent.py` — 测试

## 核心设计选择（README 已展开）
- **切块**：路 B（切块与 source 分离），每块带 `{doc, index, text}`
- **embedding**：本地 sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`, 384 维)
- **参数**：300/30（chunk_size/overlap），对比过 300/100 和 150/30
- **引用编号**：跨文档唯一 `资料{doc}#{index}`，避免不同 doc 的 index 1 冲突

## 踩过的坑（面试能讲的点）
1. 空块（`'\n'`）混进 top-3 → 过滤空块 + 连续重编号
2. 跨文档引用编号冲突 → 改用 `资料{doc}#{index}`
3. LLM 无资料时空回答 → 空结果时 prompt 写"未找到相关资料"

## 跑法（不复制到这，从 README 看）
```bash
cd ~/workspace/research_agent
# 配置 .env（MiniMax chat key）
python demo_rag.py
```

## 在 PROGRESS 中的对应条目
见 `assignments/PROGRESS.md` 里 "Stage 2 — Tool Use, RAG, and Memory" 段，状态 PASS。