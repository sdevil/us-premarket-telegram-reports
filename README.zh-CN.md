# 美股盘前报告自动化

这个仓库保存的是一套**可工作的**自动化方案，用于把美股盘前做多观察名单定时发送到 Telegram。

## 功能说明

它会向 Telegram 定时发送三类报告：

1. **主报告**
   - 时间：**新西兰时间（NZT）每周一到周五 22:30**
   - 作用：在睡前生成**下一个美股交易日**的做多观察名单

2. **隔夜更新**
   - 时间：**纽约时间每周一到周五 09:30**
   - 作用：在美股正常开市附近，结合隔夜市场、盘前异动和突发新闻更新观察名单

3. **收盘后复盘**
   - 时间：**纽约时间每周一到周五 17:00**
   - 作用：在美股收盘后复盘当天实际走势，对照盘前建议提炼经验并持续优化策略

## 报告范围

生成的报告遵循这些原则：

- **只做多（LONG only）**
- 只扫描 **S&P 500** 和 **Nasdaq 100** 股票
- 优先筛选**机构级质量**的交易机会
- 重点关注：
  - 强催化剂
  - 强相对成交量
  - 高流动性
  - 机构参与
  - 强板块共振
  - 良好的风险回报比
- 研究资料使用**英文金融来源**
- 最终报告输出为**简体中文**

## 为什么要做这个版本

在这台机器上，OpenClaw 内建 cron 在测试中表现不稳定：

- `isolated cron` 会创建 run/session 索引，但实际缺少对应的 session transcript 文件
- `main-session system-event cron` 虽然显示执行完成，但不能稳定投递 Telegram 消息

所以这个仓库采用了一个更稳的绕过方案。

## 实际可工作的架构

- 使用 **systemd user timers** 做调度
- 使用 **OpenClaw CLI** 生成报告并投递到 Telegram
- 核心发送方式：

```bash
openclaw agent --channel telegram --to <TELEGRAM_TARGET> --deliver --message "..."
```

## 仓库内容

- `scripts/premarket_primary_report.sh`
  - 发送 22:30 NZT 的主报告
  - 同时把生成内容归档到 `reports/`
- `scripts/premarket_overnight_update.sh`
  - 发送纽约开市时段的更新报告
  - 同时把生成内容归档到 `reports/`
- `scripts/postmarket_review.sh`
  - 在美股收盘后复盘同一交易日
  - 从 `reports/` 读取当日盘前报告
  - 把复盘结果写入 `reviews/`

## 使用的调度

### 定时器 1
- 名称：`premarket-primary-report.timer`
- 时间：`Mon..Fri 22:30`
- 时区：`Pacific/Auckland`

### 定时器 2
- 名称：`premarket-overnight-update.timer`
- 时间：`Mon..Fri 09:30`
- 时区：`America/New_York`

### 定时器 3
- 名称：`postmarket-review.timer`
- 时间：`Mon..Fri 17:00`
- 时区：`America/New_York`

## systemd 单元示例

### `premarket-primary-report.service`
```ini
[Unit]
Description=OpenClaw US premarket primary report

[Service]
Type=oneshot
WorkingDirectory=<WORKSPACE_PATH>
ExecStart=<WORKSPACE_PATH>/scripts/premarket_primary_report.sh
```

### `premarket-primary-report.timer`
```ini
[Unit]
Description=22:30 NZT weekdays premarket primary report

[Timer]
OnCalendar=Mon..Fri 22:30 Pacific/Auckland
Persistent=true
Unit=premarket-primary-report.service

[Install]
WantedBy=timers.target
```

### `premarket-overnight-update.timer`
```ini
[Unit]
Description=09:30 New York time weekdays premarket overnight update

[Timer]
OnCalendar=Mon..Fri 09:30 America/New_York
Persistent=true
Unit=premarket-overnight-update.service

[Install]
WantedBy=timers.target
```

## 部署说明

1. 给脚本增加执行权限：

```bash
chmod +x scripts/premarket_primary_report.sh scripts/premarket_overnight_update.sh
```

2. 把 systemd user service/timer 文件放到：

```bash
~/.config/systemd/user/
```

3. 重新加载并启用：

```bash
systemctl --user daemon-reload
systemctl --user enable --now premarket-primary-report.timer
systemctl --user enable --now premarket-overnight-update.timer
```

## Prompt 设计原则

报告 prompt 明确要求：

- **严格返回 3 个输出位**
- 不编造行情数据
- 如果盘前价位不可用，则退回使用前一交易日关键位
- 输出简洁，能在两分钟内看完
- 同时提供适合 Telegram 的交易卡片摘要
- 排名按**次日可交易性**而不是公司名气
- 优先选择**单股明确催化**，而不是仅靠板块跟涨
- 如果真正高质量机会只有两只，第 3 个位置应降级为 **条件观察名单 / 候补**，而不是假装三个都同等级

### 当前 prompt 行为

主报告和隔夜更新现在已经统一成更严格的筛选逻辑：

- 前两名优先保留真正高确信度 setup
- 第三个位置在质量明显下降时，会明确标记为 **Watchlist / 条件观察名单**
- 报告会直接承认“前两名之后质量明显下滑”
- 不会因为某只大市值 AI 龙头很有名、流动性很强，就自动把它塞进前三

## 经验总结

### 1. 投递链路比调度形式更重要
理论上更优雅的内建调度，如果不能稳定创建会话或发送消息，实际价值就不高。

### 2. 研究生成与消息投递要解耦
直接使用 `openclaw agent --deliver`，让投递链路更可观测、更容易验证。

### 3. 数据缺失时宁可明确说明，也不要乱编
如果拿不到可靠的盘前高低点，就直接说明 unavailable，而不是伪造精确价格。

### 4. 限制股票池能显著提高质量
把范围限制在 S&P 500 和 Nasdaq 100，可以显著提升流动性质量，减少垃圾 setup。

## 当前状态

这个仓库保存的是**最终可工作的版本**：

- 用 OpenClaw CLI 生成和发送
- 用 systemd timers 定时运行
- 避开当前机器上有问题的 OpenClaw 内建 cron 路径

## English documentation

See: `README.md`
