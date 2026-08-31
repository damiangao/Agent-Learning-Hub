# Stage 3 学习笔记：learn-claude-code s01 Agent Loop

> 学习目标：读懂一个现代 agent harness 的最小闭环，理解 Claude 如何通过 `tool_use` 请求工具、harness 如何执行工具并把 `tool_result` 回填给模型。

## 1. 学习对象

- 项目：`shareAI-lab/learn-claude-code`
- 本地路径：`/Users/damian/workspace/learn-claude-code/`
- 章节：`s01_agent_loop/code.py`
- 主题：最小 agent loop

s01 展示的是一个极简 Claude Code-like harness：只有一个 `bash` 工具，没有复杂工具注册、权限审批、上下文压缩、记忆或多 agent。

## 2. s01 的核心流程

主循环可以概括为：

```text
user query
-> messages + system + tools 发给 Claude
-> Claude 返回 assistant content blocks
-> 如果 stop_reason == tool_use，执行 tool_use block
-> 把执行结果作为 user/tool_result 回填
-> 再次调用 Claude
-> 直到 Claude 不再请求工具，输出最终答案
```

对应代码结构：

```python
messages = [{"role": "user", "content": query}]

response = client.messages.create(
    model=MODEL,
    system=SYSTEM,
    messages=messages,
    tools=TOOLS,
    max_tokens=8000,
)

messages.append({"role": "assistant", "content": response.content})

if response.stop_reason != "tool_use":
    return

results = []
for block in response.content:
    if block.type == "tool_use":
        output = run_bash(block.input["command"])
        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": output,
        })

messages.append({"role": "user", "content": results})
```

关键点：Claude API 本身是无状态的，状态由本地 `messages` 列表保存；每一轮都要把完整历史重新发给模型。

## 3. Tool definition

s01 只暴露一个工具：`bash`。

```python
{
    "name": "bash",
    "description": "Run a shell command.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {"type": "string"}
        },
        "required": ["command"]
    }
}
```

我的理解：

- `TOOLS` 是 harness 告诉 Claude 的行动接口。
- Claude 不是直接运行 shell，而是生成一个 `tool_use` block，请求 harness 执行 `bash`。
- `input_schema` 限定模型必须传入 `command` 字符串。
- s01 没有真正的 tool registry；因为只有一个工具，执行逻辑可以直接调用 `run_bash`。

## 4. System prompt

```python
SYSTEM = f"You are a coding agent at {WORKDIR}. Use tools to solve tasks. Act, don't explain."
```

这条 system prompt 做了三件事：

1. 告诉 Claude 当前工作目录是 `WORKDIR`。
2. 告诉 Claude 它是 coding agent，可以使用工具完成任务。
3. 用 `Act, don't explain.` 压低纯解释倾向，鼓励模型直接行动。

我的理解：system prompt 不是工具本身，但它影响模型是否选择工具、如何规划工具输入。

## 5. Claude Messages API 语义

### assistant content blocks

`response.content` 不是普通字符串，而是 content block 列表。里面可能包含：

- `text`
- `tool_use`

所以 harness 必须把完整 `response.content` 追加回 `messages`：

```python
messages.append({"role": "assistant", "content": response.content})
```

如果只保存文本，会丢失 `tool_use.id`、`tool_use.name`、`tool_use.input`，下一轮无法正确关联工具结果。

### stop_reason == tool_use

当：

```python
response.stop_reason == "tool_use"
```

说明 Claude 请求 harness 执行工具。此时 assistant content 中会出现 `tool_use` block。

s01 为了教学简化，只区分两类情况：

```text
tool_use     -> 执行工具并继续循环
非 tool_use  -> 认为模型已经结束，返回最终回答
```

真实 harness 还需要处理 `max_tokens`、`refusal`、`pause_turn` 等情况。

### tool_result 的 role/content 形态

Claude 请求工具时返回：

```text
assistant: tool_use(id=..., name="bash", input={"command": "..."})
```

harness 执行本地工具后，要用 `role=user` 回填：

```python
{
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": output,
        }
    ]
}
```

关键点：

- `tool_result` 放在 `role: "user"` 的消息里。
- `tool_use_id` 必须等于前面 Claude 返回的 `tool_use.id`。
- 如果一次有多个 `tool_use`，多个 `tool_result` 应放在同一个 user message 中回传。

## 6. Safety / permission gate

s01 的 `run_bash` 只做了教学级安全限制：

```python
dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
if any(d in command for d in dangerous):
    return "Error: Dangerous command blocked"
```

并处理超时：

```python
except subprocess.TimeoutExpired:
    return "Error: Timeout (120s)"
```

已有能力：

- 阻止少量危险命令片段；
- 120 秒超时；
- 把错误作为工具结果返回给 Claude。

缺少能力：

- 用户确认；
- allowlist；
- 沙箱隔离；
- 精细权限策略；
- 命令解析；
- 文件写入保护；
- 审计日志。

我的理解：s01 的 permission gate 重点是展示“harness 位于模型和真实系统之间，可以拦截工具调用”，不是生产级安全方案。

## 7. 运行证据

运行命令：

```bash
/usr/local/bin/python3 /Users/damian/workspace/learn-claude-code/s01_agent_loop/code.py
```

输入：

```text
列出当前目录，并读取 README 的前几行，总结这个项目是什么。
```

Claude 选择调用 `bash`，生成命令：

```bash
ls -la && echo "---README---" && head -50 README.md 2>/dev/null || head -50 README* 2>/dev/null
```

工具返回当前目录列表和 README 前 50 行内容。随后 Claude 基于工具结果总结项目定位。

## 8. 链路复盘

```text
user:
列出当前目录，并读取 README 的前几行，总结这个项目是什么。

assistant tool_use:
bash(command="ls -la && echo \"---README---\" && head -50 README.md 2>/dev/null || head -50 README* 2>/dev/null")

tool_result:
目录列表 + README 前 50 行内容

assistant final:
总结 learn-claude-code 是一个 Harness Engineering 教学仓库，教人从零搭建 Claude Code-like agent harness。
```

## 9. 我的阶段性理解

s01 展示了最小 agent harness：

- `TOOLS` 定义模型可以请求哪些行动；
- `SYSTEM` 设定模型的角色和行动倾向；
- `messages` 保存本地会话状态；
- Claude 通过 `tool_use` 请求工具；
- harness 执行本地工具；
- harness 用 `tool_result` 把结果回填给 Claude；
- Claude 基于工具结果继续思考或输出最终答案。

s01 的特点是只有一个 `bash` 工具。模型需要自己把任务转成 shell 命令，因此能力强但边界粗。后续章节需要解决的问题是：如何把粗粒度 bash 拆成更安全、更可控、更可观察的专用工具和权限系统。

## 10. 下一步

继续学习 `s02_tool_use/code.py`，重点观察：

1. s02 暴露了哪 4 个工具；
2. 每个工具的职责边界是什么；
3. harness 如何根据 `tool_use.name` 分发到不同本地函数；
4. 相比 s01，专用工具是否提升了安全性、可控性和可观察性。
