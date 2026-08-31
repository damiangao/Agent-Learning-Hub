# Stage 1.2 作业：Real LLM Tool Calling Calculator Agent

> 学习目标：把 Stage 1.1 的 fake LLM 替换成真实 LLM tool/function calling。重点不是扩展工具，而是理解真实模型如何请求工具、程序如何执行工具、再如何把工具结果回传给模型。

---

## 0. 当前基础

你已经完成：

```text
Stage 1.1 - Fake LLM Calculator Agent: PASS
```

项目位置：`/Users/damian/workspace/calculator_agent`

已有能力：

- `calculator(expression)`：安全计算器工具；
- `run_agent(user_input, llm, max_steps)`：fake LLM agent loop；
- 6 个 pytest 测试；
- README 说明了 agent loop。

---

## 1. 本阶段目标

实现一个真实 LLM tool calling 版本，使流程变成：

```text
用户输入
-> OpenAI 模型返回 calculator tool call
-> 本地程序执行 calculator
-> 程序把 tool result 回传给 OpenAI
-> OpenAI 返回最终自然语言答案
```

示例目标：

```text
输入：请计算 324*97.2-879.33
输出：计算结果是 30613.47
```

---

## 2. 为什么不是直接重写整个 agent？

Stage 1.1 已经证明你理解了抽象 loop。Stage 1.2 只替换其中的 `think` 部分：

```text
Stage 1.1: fake LLM 决定下一步动作
Stage 1.2: real OpenAI LLM 决定下一步动作
```

所以不要扩展到 web search、RAG、多 agent、browser agent。

---

## 3. OpenAI tool calling 最小知识

从当前 OpenAI Python SDK 文档可知，Chat Completions 支持：

```python
client.chat.completions.create(
    model="...",
    messages=[...],
    tools=[...],
    tool_choice="auto",
)
```

模型如果要调用工具，会在 assistant message 中返回：

```text
message.tool_calls
```

程序执行工具后，需要追加一条 tool message。tool message 的关键字段是：

```python
{
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": "工具执行结果"
}
```

关键点：

- `role` 必须是 `tool`；
- 必须带 `tool_call_id`；
- `content` 是本地工具执行结果；
- 回传工具结果后，要再次调用模型，让模型生成最终答案。

---

## 4. 推荐实现边界

建议新建或新增这些内容：

```text
openai_agent.py
test_openai_agent.py
```

或者在现有 `calculator_agent.py` 中增加函数，但建议小文件更清楚。

推荐函数边界：

```python
CALCULATOR_TOOL = {...}

def run_openai_agent(user_input: str, client, model: str, max_steps: int = 3) -> str:
    ...
```

说明：

- `client` 从外部传入，方便测试时用 fake client；
- 单元测试不要真的调用 OpenAI API；
- 真 API 调用放在手动 demo 或 integration 记录里。

---

## 5. TDD 测试设计

先不要写实现。先写测试表。

最低测试用例：

| 测试函数名 | 验证行为 | 输入 / 模拟条件 | 期望结果 |
| --- | --- | --- | --- |
| test_calculator_tool_schema_defines_expression | calculator tool schema 正确定义 expression 参数 | 检查 `CALCULATOR_TOOL` | tool 名称是 `calculator`，参数包含必填 `expression` |
| test_run_openai_agent_returns_final_answer_without_tool_call | 模型直接返回最终答案时 agent 停止 | fake client 返回无 tool_calls 的 assistant message | 返回 message content |
| test_run_openai_agent_executes_calculator_tool_call | 模型请求 calculator 时 agent 执行本地工具并回传结果 | fake client 第一次返回 calculator tool_call，第二次返回 final answer | 返回最终答案，且 fake client 收到 tool result message |
| test_run_openai_agent_rejects_unknown_tool_call | 模型请求未知工具时 agent 返回错误 | fake client 返回 tool_call name=`unknown_tool` | 返回“未知工具”错误 |
| test_run_openai_agent_reports_tool_failure | calculator 执行失败时 agent 返回错误 | fake client 请求计算 `1/0` | 返回“工具调用失败”或“计算失败” |
| test_run_openai_agent_stops_after_max_steps | 模型持续请求工具时 agent 达到 max_steps 后停止 | fake client 每次都返回 calculator tool_call | 返回“达到最大执行轮数” |

---

## 6. RED 要求

在实现前，先写 `test_openai_agent.py`，然后运行：

```bash
pytest -q test_openai_agent.py
```

预期失败，例如：

```text
ModuleNotFoundError: No module named 'openai_agent'
```

或者：

```text
AttributeError: module 'openai_agent' has no attribute 'run_openai_agent'
```

这才是 RED。

---

## 7. GREEN 要求

只写最小实现让测试通过：

- 定义 calculator tool schema；
- 调用 fake client 的 `chat.completions.create`；
- 解析 `message.tool_calls`；
- 只支持 calculator；
- 执行已有 `calculator(expression)`；
- 追加 `role="tool"` 且带 `tool_call_id` 的 message；
- 再次调用模型获取 final answer；
- max_steps 生效；
- 错误信息明确。

---

## 8. 手动真实 API 验证

单元测试通过后，再做一次真实 API 手动验证。

需要：

```bash
export OPENAI_API_KEY="你的 key"
```

然后运行 demo。

README 记录：

```text
1. 使用的模型
2. 输入
3. 模型是否发起 tool call
4. 工具结果
5. 最终答案
6. 遇到的问题
```

不要把 API key 写进代码或 README。

---

## 9. 完成标准

提交给教练时附上：

```text
1. test_openai_agent.py
2. openai_agent.py 或新增函数路径
3. pytest 输出
4. 一次真实 API 手动验证记录，或说明为什么暂时没跑真实 API
5. 解释真实 tool calling 中 observe / think / act / observe 分别对应哪里
```

---

## 10. 通过标准

- **pass**：测试先行，fake client 单元测试通过，真实 API 调用流程理解清楚，能解释 tool_call_id 和 role=tool 的作用。
- **revise**：测试或 README 不完整，真实 API 只是能跑但解释不清，或错误处理不够明确。
- **fail**：没写测试先实现，直接复制 SDK 示例但不能解释，或把 API key 写进代码。
