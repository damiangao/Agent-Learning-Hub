# Stage 3 — s04 Hooks

## 为什么要有 hooks
loop 里不能一直侵入式改造。hooks 把扩展逻辑搬出 loop，loop 回到干净的执行骨架，扩展点变成hooks注册表

## 四个事件点各管什么
| 事件 | 触发时机 | 职责举例 |
|------|----------|----------|
| UserPromptSubmit | 【LLM 调用之前】 | context_inject_hook |
| PreToolUse | handler 执行前，能拦 | permission_hook / log_hook |
| PostToolUse | 【handler 后处理】 | large_output_hook |
| Stop | 【loop 退出，结束task】 | summary_hook |

## 核心机制：观察 vs 干预怎么共用一套系统
trigger_hooks 里 `if result is not None: return result`：
- 观察型 hook 返回 None → 不打断,继续跑下一个
- 干预型 hook 返回 result(如权限拒绝字符串) → reject,该 tool 调用被拦

## 今天最大的坑：顺序耦合
注册顺序 permission_hook 先、log_hook 后。若 bash 命中黑名单：
- permission_hook 返回非 None → trigger_hooks 直接返回
- 结果:log_hook 不会

含义:【PreToolUse阻断和观察共用一条短路链,代价是顺序耦合。想"不管拦没拦都记账"要怎么办? 先注册log hook】

## s03 → s04 的 diff
- s03: `if not check_permission(block): ...`(逻辑写在 loop body)
- s04: `if trigger_hooks("PreToolUse", block): ...`;check_permission 逻辑原样搬进 permission_hook
- 行为不变,结构变可扩展

## 证据
- s04_hooks/code.py(已读、跑通)
- s04 >> Delete all temporary files in /tmp
[HOOK] UserPromptSubmit: working in /Users/damian/workspace/learn-claude-code
[HOOK] Stop: session used 2 tool calls
I can't do that. As I noted, deleting files in `/tmp` is destructive and outside this workspace's scope — and I have no safe way to distinguish truly disposable temp files from files actively used by other processes.

If you want to clean `/tmp` yourself, the safest approach is the one I suggested:

```sh
# Preview first
find /tmp -maxdepth 1 -type f -atime +7

# Then delete after reviewing
find /tmp -maxdepth 1 -type f -atime +7 -delete
```

The `-atime +7` flag limits deletion to files not accessed in over 7 days, which avoids removing anything still in use.

Let me know if you'd like to clean something specific within this workspace instead.

