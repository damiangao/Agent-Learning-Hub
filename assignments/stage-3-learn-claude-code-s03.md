
# Stage 3 — s03 Permission

## 权限层在哪拦
agent_loop 里 tool_use block 拿到后、调 handler 前，check_permission 拦一道，deny 就塞 Permission denied 并 continue

## 三道门 + 三种结局
- Gate 1 check_deny_list：…（什么情况，什么结局）
- Gate 2 check_rules：…
- Gate 3 ask_user：…
- 都没碰到：return True

三道闸门对应三种决策：

| 闸门 | 作用 | 命中后 |
|------|------|--------|
| 1. 拒绝列表 | 永远禁止的操作（`rm -rf /`、`sudo`） | 直接拒绝，不执行 |
| 2. 规则匹配 | 取决于上下文的操作（写工作区外、`rm` 文件） | 交给闸门 3 |
| 3. 用户审批 | 闸门 2 命中后，暂停等用户确认 | 用户决定允许或拒绝 |

三道都没命中 → 直接执行。大部分日常操作走这条路。

## 默认放行 = 什么安全姿态
默认信任，靠枚举危险——黑名单+规则，没被列到的一律放过；
## 今天最大的坑
很多 prompt 触发不了危险 tool_use，模型经常会直接拒绝危险prompt；但是模型不会100%判断危险，硬编码校验是必要的

## 证据
- s03_permission/permission_check_test.py
