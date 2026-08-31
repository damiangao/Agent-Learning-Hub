# Stage 3 学习笔记：learn-claude-code s02 Tool Use

> 学习目标：在 s01 最小 agent loop 的基础上，理解如何把单一 `bash` 工具扩展成多个专用工具，并通过工具名分发到不同本地函数。

## 1. 学习对象

- 项目：`shareAI-lab/learn-claude-code`
- 本地路径：`/Users/damian/workspace/learn-claude-code/`
- 章节：`s02_tool_use/code.py`
- 主题：Tool Use / 多工具分发

s02 保留了 s01 的 agent loop 主结构，但把工具层从单一 `bash` 扩展成多个工具。核心变化是：模型不再只能生成 shell 命令，而是可以选择更具体的文件读写、编辑和搜索工具。

## 2. s02 的工具清单

s02 总计暴露 5 个工具：

1. `bash`
2. `read_file`
3. `write_file`
4. `edit_file`
5. `glob`

其中 `bash` 来自 s01，s02 新增的 4 个工具是：

- `read_file`
- `write_file`
- `edit_file`
- `glob`

对应的工具定义都放在 `TOOLS` 里。每个工具都有：

- `name`：模型请求工具时使用的名字；
- `description`：告诉模型这个工具能做什么；
- `input_schema`：规定模型必须传入哪些参数。

## 3. 每个工具的职责边界

### `bash`

职责：执行 shell 命令。

它能力最强，也最危险。s02 仍然保留了 s01 的简单危险命令拦截和 120 秒超时。

适合：没有专用工具覆盖的通用命令。

不适合：优先做文件读取、写入、编辑、搜索等已有专用工具能完成的任务。

### `read_file`

职责：读取文件内容。

输入参数：

- `path`：文件路径；
- `limit`：可选，限制读取行数。

对应本地函数是 `run_read(path, limit=None)`。

它只负责读文件，不负责修改文件。相比让模型用 `cat` 或 `head` 拼 shell 命令，`read_file` 的意图更明确，也更容易做路径安全校验和 tracing。

### `write_file`

职责：把内容写入文件。

输入参数：

- `path`：目标文件路径；
- `content`：写入内容。

对应本地函数是 `run_write(path, content)`。

它会先通过 `safe_path` 检查路径是否仍在工作区内，然后创建父目录并写入文件。

它不负责“局部替换”，如果只是替换已有文件中的一段文本，应使用 `edit_file`。

### `edit_file`

职责：在文件中精确替换一段文本一次。

输入参数：

- `path`：目标文件路径；
- `old_text`：要查找的旧文本；
- `new_text`：替换后的新文本。

对应本地函数是 `run_edit(path, old_text, new_text)`。

它的边界比 `write_file` 更窄：不是整体覆盖文件，而是读取原文件后只替换第一次出现的 `old_text`。如果旧文本不存在，它会返回错误：

```text
Error: text not found in {path}
```

这让模型能在下一轮根据工具错误调整操作。

### `glob`

职责：按 glob pattern 搜索文件。

输入参数：

- `pattern`：搜索模式。

对应本地函数是 `run_glob(pattern)`。

它用于发现文件，而不是读取文件内容。搜索结果仍然经过路径检查，避免返回工作区外的路径。

## 4. 路径安全：`safe_path`

s02 新增了 `safe_path(p)`：

```python
def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path
```

我的理解：

- 所有文件类工具都先把用户/模型传入的相对路径解析到 `WORKDIR` 下；
- 再检查解析后的路径是否仍然属于 `WORKDIR`；
- 如果路径逃逸工作区，就抛出错误。

这比 s01 单纯拦截几个危险 shell 字符串更明确，但仍然不是完整权限系统。

## 5. Tool definition

s02 的 `TOOLS` 不再只有 `bash`，而是包含 5 个工具定义：

```python
TOOLS = [
    {"name": "bash", ...},
    {"name": "read_file", ...},
    {"name": "write_file", ...},
    {"name": "edit_file", ...},
    {"name": "glob", ...},
]
```

关键点：

- 模型根据 `name` 决定请求哪个工具；
- `description` 影响模型什么时候选择这个工具；
- `input_schema` 限制工具输入结构；
- 但 schema 只约束形状，不等于完整安全策略。

## 6. 工具分发机制

s01 只有一个工具，所以执行逻辑可以直接写死：

```python
output = run_bash(block.input["command"])
```

s02 改成了工具名到本地函数的映射：

```python
TOOL_HANDLERS = {
    "bash": run_bash,
    "read_file": run_read,
    "write_file": run_write,
    "edit_file": run_edit,
    "glob": run_glob,
}
```

agent loop 中根据 `block.name` 查找 handler：

```python
handler = TOOL_HANDLERS.get(block.name)
output = handler(**block.input) if handler else f"Unknown: {block.name}"
```

我的理解：

- Claude 返回的 `tool_use` block 里有工具名和参数；
- harness 不信任模型直接执行能力，而是通过 `TOOL_HANDLERS` 查表；
- 找到对应函数后，用 `block.input` 作为参数调用；
- 如果工具名不存在，返回 `Unknown: {block.name}`。

这就是 s02 的核心变化：从“单工具硬编码调用”变成“多工具注册与分发”。

## 7. agent loop 与 s01 的关系

s02 的主循环结构和 s01 基本一样：

```text
user query
-> messages + system + tools 发给 Claude
-> Claude 返回 assistant content blocks
-> 如果 stop_reason == tool_use，执行 tool_use block
-> 把执行结果作为 tool_result 回填
-> 再次调用 Claude
-> 直到 Claude 不再请求工具
```

变化只在工具执行部分：

```text
s01: 固定调用 run_bash
s02: 根据 block.name 查 TOOL_HANDLERS，再调用对应函数
```

所以 s02 不是重写 agent loop，而是在 s01 的 loop 里替换了 action interface 层。

## 8. 相比 s01 的改进

### 更安全

s01 主要依赖 `bash`。模型需要自己把任务翻译成 shell 命令，这容易出错，也容易越界。

s02 把常见操作拆成专用工具，例如读文件用 `read_file`，写文件用 `write_file`，搜索文件用 `glob`。这些工具的参数更明确，执行逻辑也更窄。

`s02` 还通过 `safe_path` 对文件路径做工作区限制，避免文件工具访问工作区外路径。

### 更可控

专用工具把模型的行动空间变小了：

- 读文件就是 `path` + 可选 `limit`；
- 写文件就是 `path` + `content`；
- 编辑文件就是 `path` + `old_text` + `new_text`；
- 搜索文件就是 `pattern`。

模型不需要自己拼复杂 shell，harness 也更容易检查参数是否合法。

### 更可观察

s02 在执行工具时会打印工具名：

```python
print(f"\033[33m> {block.name}\033[0m")
```

相比单一 `bash`，看到 `read_file`、`write_file`、`glob` 这样的工具名，更容易理解模型正在做什么。

如果后续要做 tracing，也可以按工具名统计：模型读了哪些文件、写了哪些文件、搜索了哪些 pattern、哪些工具失败了。

## 9. 仍未解决的风险

s02 只是教学级 harness，仍然不是生产级安全实现：

- `bash` 仍然很宽，只做了少量危险字符串拦截；
- `write_file` 会直接覆盖目标文件，没有用户确认；
- `edit_file` 只替换第一次出现的文本，但没有检查 old_text 是否唯一；
- 没有 allowlist / denylist 权限策略；
- 没有用户确认流程；
- 没有沙箱隔离；
- 没有完整审计日志；
- 工具结果只截断打印前 200 字，观察性还比较粗。

我的理解：s02 的重点不是生产安全，而是展示“工具可以被拆分、注册、分发，并通过更窄的接口提升可控性”。

## 10. 运行证据

运行命令：

```bash
/usr/local/bin/python3 /Users/damian/workspace/learn-claude-code/s02_tool_use/code.py
```

输入：

```text
Read requirements.txt and summarize dependencies.
```

观察到工具调用：

```text
> read_file
```

工具结果：

```text
anthropic>=0.25.0
python-dotenv>=1.0.0
pyyaml>=6.0
```

模型最终回答：

```text
## Dependencies in requirements.txt

| Package | Version | Role |
|---|---|---|
| `anthropic` | `>=0.25.0` | Claude API client — the LLM SDK used by the agent loop |
| `python-dotenv` | `>=1.0.0` | Loads `ANTHROPIC_API_KEY` and other secrets from a `.env` file |
| `pyyaml` | `>=6.0` | YAML parsing for skill manifests and config files (notably used by the skill loading lesson, s07) |

Minimal footprint — three packages total. The tutorial leans on the Python standard library for everything else (threading, asyncio, file I/O, JSON, etc.).
```

这次 trace 说明：

1. 模型选择了 `read_file`，而不是自己拼 `cat requirements.txt`；
2. harness 执行本地读取函数并返回文件内容；
3. Claude 基于 `tool_result` 总结依赖，而不是凭空猜测。

## 11. 我的阶段性理解

s02 展示的是 agent harness 的工具层升级：

- s01 是一个粗粒度 `bash` action interface；
- s02 把常见能力拆成多个更窄的工具；
- `TOOLS` 负责告诉模型有哪些工具；
- `TOOL_HANDLERS` 负责把模型请求分发到本地函数；
- `safe_path` 展示了 harness 可以在工具执行前做安全边界检查；
- 工具名和参数 schema 让行为更可控，也更适合 tracing。

我认为 s02 的关键不是“多了几个函数”，而是把 agent 的行动接口从自由命令行拆成了更结构化、更可控的 API。

## 12. 下一步

继续学习 s03，重点观察：

1. `tool_result` 在 `messages` 里具体长什么样；
2. 工具结果如何影响 Claude 下一轮输出；
3. 如果工具返回错误，模型是否会根据错误信息修正下一步行动。
