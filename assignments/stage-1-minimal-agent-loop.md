# Stage 1 作业：Build A Minimal Agent Loop

> 学习目标：用最小代码理解 agent loop 的核心结构：用户输入、模型决策、工具调用、工具结果回传、最终回答、最大步数和错误处理。

---

## 0. 基本信息

- 姓名 / 昵称：Damian Gao
- 当前阶段：Stage 1 - Build A Minimal Agent Loop
- 推荐实现语言：Python
- 推荐项目：Calculator Agent

---

## 1. 为什么 Stage 1 先做 Calculator Agent？

不要一开始就做完整资料研究助手。资料研究助手需要搜索、网页读取、来源质量判断、引用检查和多轮策略调整，变量太多。

Stage 1 的目标是先吃透最小 agent loop，因此选择 Calculator Agent：

- 工具结果确定，容易判断对错；
- 不依赖搜索 API 和网页质量；
- 便于观察模型什么时候调用工具、什么时候直接回答；
- 失败时更容易定位是 schema、prompt、tool execution、loop control 还是错误处理的问题。

---

## 2. 最小功能要求

实现一个 50-150 行左右的最小 agent，支持：

1. 接收用户输入；
2. 调用一次 LLM；
3. 让 LLM 决定是否使用工具；
4. 至少支持一个工具：`calculator(expression)`；
5. 执行工具；
6. 把工具结果喂回 LLM；
7. 输出最终答案；
8. 有最大步数限制；
9. 有基本错误处理。

---

## 3. 推荐目录结构

```text
stage1-calculator-agent/
  README.md
  agent.py
  test_agent.py
```

说明：

- `agent.py`：最小 agent loop 和 calculator 工具。
- `test_agent.py`：测试 calculator、工具执行和最大步数逻辑。
- `README.md`：运行方式、示例输入输出、调试记录。

---

## 4. TDD 要求

本阶段必须遵守 TDD：

```text
先写测试 -> 运行并看到失败 -> 写最小实现 -> 运行通过 -> 再重构
```

禁止先写完整 agent 再补测试。

### 4.1 RED：先写失败测试

至少先写这些测试：

```text
1. calculator 能正确计算简单表达式。
2. calculator 遇到非法表达式时返回明确错误。
3. agent loop 在超过最大步数时停止。
```

### 4.2 GREEN：写最小实现

只写能让测试通过的最小代码，不要提前加入：

- web search；
- 文件读写；
- 多工具注册表；
- 多 agent；
- 长期记忆；
- UI；
- 复杂日志系统。

### 4.3 REFACTOR：通过后再整理

测试通过后再做小范围清理：

- 函数命名清楚；
- 错误信息明确；
- agent loop 不要深层嵌套；
- 最大步数和工具名使用常量。

---

## 5. 推荐测试用例

### 5.1 calculator 正常计算

```text
输入："23 * 17 + 5"
期望：396
```

### 5.2 calculator 拒绝危险表达式

```text
输入："__import__('os').system('rm -rf /')"
期望：返回错误，不执行危险代码
```

### 5.3 最大步数限制

```text
当模型一直要求继续调用工具时，agent loop 应该在 max_steps 后停止，并返回明确错误。
```

---

## 6. 安全要求

Calculator 工具不能直接使用不受限制的 `eval`。

允许：

- 只支持数字、括号和基本运算符；
- 使用 Python `ast` 白名单解析表达式；
- 拒绝函数调用、属性访问、import、变量名等危险输入。

最低要求：

```text
非法表达式必须失败，不能静默返回错误结果。
```

---

## 7. README 最低要求

`stage1-calculator-agent/README.md` 至少包含：

```text
1. 项目目标
2. 如何运行测试
3. 如何运行 demo
4. 示例输入输出
5. 一次失败或调试记录
6. 我学到了什么
```

---

## 8. 完成标准

提交前自查：

- [ ] 我先写了测试，并看到测试失败。
- [ ] 我只写了最小实现让测试通过。
- [ ] calculator 有正常输入测试。
- [ ] calculator 有非法输入测试。
- [ ] agent loop 有最大步数测试。
- [ ] 工具错误有明确返回或异常处理。
- [ ] 没有使用不安全的 unrestricted `eval`。
- [ ] README 说明了运行方式和调试记录。
- [ ] 我能解释 observe -> think -> act -> observe 在代码中分别对应哪里。

---

## 9. 提交给教练时请附上

完成后发给教练：

```text
1. 代码路径
2. 测试运行输出
3. README 内容或链接
4. 一段解释：我的 agent loop 中 observe / think / act / observe 分别在哪里
5. 遇到的一个问题，以及怎么解决的
```

---

## 10. 通过标准

我会按以下标准批改：

- **pass**：测试先行，最小 agent loop 可运行，工具调用闭环清楚，安全边界基本合理。
- **revise**：主体正确，但测试不足、错误处理不清楚、README 不完整或 loop 解释不清。
- **fail**：没有 TDD、没有真实工具调用闭环、calculator 不安全，或无法运行。
