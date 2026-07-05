# NUA知网小助手

NUA知网小助手是一个面向 Codex 与 Claude Code 的跨平台 CNKI 研究插件。它可以在用户合法授权的机构访问环境中完成知网检索、结果筛选、论文详情读取、可访问全文阅读、PDF/CAJ 下载、结构化总结和参考文献生成。

插件默认适配南京艺术学院知网代理入口，因此尤其适合南艺师生。它不会绕过登录、验证码、付费墙或机构权限；是否能够阅读或下载全文，取决于当前账号及机构的真实授权。

## 兼容性

| 平台 | 支持程度 | Chrome 行为 | Skill 与 MCP |
|---|---|---|---|
| Codex + macOS | 完整支持 | 可见、后台启动，不主动抢焦点 | 完整 |
| Codex + Windows | 完整支持 | 自动最小化启动，可从任务栏打开 | 完整 |
| Claude Code + macOS | 完整支持 | 可见、后台启动，不主动抢焦点 | 完整 |
| Claude Code + Windows 原生 | 完整支持 | 自动最小化启动 | 完整 |
| Claude Code + WSL | 支持 | 调用 Windows Chrome 并最小化启动 | 完整 |
| Claude Code Desktop 的 Code 标签页 | 完整支持 | 与 Claude Code 相同 | 完整 |
| Claude Desktop 普通聊天 | MCP 兼容 | 与所在系统相同 | 仅浏览器工具；不自动加载 Claude Code Skill |
| Linux | 实验性支持 | 尝试最小化启动 | 完整 |

## 主要功能

- 普通检索、高级检索、专业检索及年份、来源、学科、文献类型筛选。
- 按题名、关键词、摘要和直接主题重合度重新排序，不把高被引简单等同于高相关。
- 通过论文详情页进入 `CNKI AI阅读`，逐页检查正文是否实际加载。
- 延迟等待、逐页验证并二次重试，减少把暂未加载误判为“无权限”的情况。
- 提取题名、作者、来源、年份、摘要、关键词、DOI、被引量和详情链接。
- 在用户明确要求且具备合法权限时下载 PDF；也支持明确指定的 CAJ。
- 输出研究背景、理论框架、方法、结论、贡献、局限和后续研究方向。
- 生成 APA、BibTeX 和 GB/T 7714 引用。
- 使用 OpenAlex 或 Crossref 补充 DOI、开放获取状态和出版信息，并明确标注来源。
- 登录完成后自动恢复原任务，无需再次输入“继续”。

## 系统要求

- Google Chrome。
- Node.js 18 或更高版本，并能运行 `node` 与 `npx`。
- Codex 或 Claude Code 的较新版本，需支持插件与 MCP。
- 如需机构全文权限，需有南京艺术学院代理访问资格并自行完成登录。
- 公共元数据脚本需要 Python 3.9 或更高版本；Windows 可使用 `py -3`。

Windows 原生 Claude Code 还需要 Git for Windows；WSL 用户需确保 Windows 侧已经安装 Chrome。

## 安装到 Codex

```bash
codex plugin marketplace add xinghaoshi-ux/nua-cnki-assistant
codex plugin add cnki-research@nua-cnki-assistant
```

安装完成后重启 Codex，或新建一个对话，使 Skill 和 MCP 服务重新加载。

## 安装到 Claude Code

在终端运行：

```bash
claude plugin marketplace add xinghaoshi-ux/nua-cnki-assistant
claude plugin install cnki-research@nua-cnki-assistant
```

已经打开 Claude Code 时，运行：

```text
/reload-plugins
```

插件 Skill 的显式调用方式为：

```text
/cnki-research:cnki-research
```

也可以直接使用“用知网查一下……”“使用 NUA论文小助手……”等自然语言，Claude 会根据 Skill 描述自动选择插件。

Claude Code Desktop 的 Code 标签页与 Claude Code 使用相同的插件体系，安装后在 Code 会话中执行 `/reload-plugins` 即可。

## 安装到 Claude Desktop 普通聊天

普通聊天应用使用独立的 `claude_desktop_config.json`，不会自动加载 Claude Code marketplace 中的 Skill。本仓库提供一个安全合并配置的脚本：它会保留已有 MCP 服务，并在修改前创建备份。

```bash
git clone https://github.com/xinghaoshi-ux/nua-cnki-assistant.git
cd nua-cnki-assistant
node scripts/configure-claude-desktop.mjs
```

Windows PowerShell：

```powershell
git clone https://github.com/xinghaoshi-ux/nua-cnki-assistant.git
Set-Location nua-cnki-assistant
node .\scripts\configure-claude-desktop.mjs
```

完成后重启 Claude Desktop。此方式只提供 Playwright MCP 浏览器工具；如需完整的自动检索、全文验证和引用工作流，推荐使用 Claude Code 或 Claude Code Desktop 的 Code 标签页。

从 Claude Desktop 普通聊天配置中移除：

```bash
node scripts/configure-claude-desktop.mjs --remove
```

## 首次使用与登录

1. 安装插件并重新加载客户端。
2. 输入“使用知网搜索用户体验理论更新的最新 20 篇论文”等任务。
3. 插件启动独立 Chrome 配置，不读取普通 Chrome 配置文件。
4. macOS 上 Chrome 在后台可见；Windows 上 Chrome 默认最小化，需要登录时从任务栏打开。
5. 如出现统一身份认证、机构登录或安全验证，请手动完成。
6. 插件会继续监听页面状态，登录成功后自动恢复任务。

已有旧版 Codex 配置时，插件会继续使用：

```text
~/.codex/browser-profiles/cnki-research
```

新安装默认使用：

```text
macOS/Linux: ~/.nua-cnki-assistant/chrome-profile
Windows:     %USERPROFILE%\.nua-cnki-assistant\chrome-profile
WSL:         %LOCALAPPDATA%\NUA-CNKI-Assistant\chrome-profile
```

这些目录可能包含登录状态，绝对不要上传到 GitHub。

## 唤醒示例

- `使用 NUA知网小助手搜索……`
- `使用 NUA论文小助手查找……`
- `用知网查一下……`
- `查一下知网的文章……`
- `帮我上知网找论文……`
- `读一下这篇知网论文的全文……`
- `下载这篇知网论文的 PDF……`
- `用 cnki-research 检索……`

Claude Code 中也可以显式输入：

```text
/cnki-research:cnki-research 搜索AI介入UI设计的论文，按需求相关度取前20篇
```

## 使用示例

### 检索并整理

```text
使用知网搜索 UX 设计理论更新层面的最新 20 篇论文，限定 2022—2026 年，按相关性和理论贡献排序，并给出题名、作者、来源、年份、摘要和链接。
```

### 阅读全文并总结

```text
阅读这 5 篇论文的可访问全文。每篇总结研究背景、理论框架、方法、核心结论、贡献、局限和后续研究方向，最后进行横向比较。
```

### 下载论文

```text
下载《论文标题》的 PDF 到 Downloads 文件夹。
```

### 生成引用

```text
核对这些论文的 DOI 和出版信息，并分别生成 GB/T 7714 与 BibTeX 引用。
```

## 跨平台 Chrome 启动机制

插件的 `.mcp.json` 使用嵌入式 Node 启动器，因此不依赖 `/bin/zsh`、固定安装目录或 Claude 专属路径变量。

- macOS：使用 `open -g` 启动独立 Chrome，不主动激活窗口。
- Windows 原生：自动查找用户目录、Program Files 和 Program Files (x86) 中的 Chrome，通过 `--start-minimized` 启动，并在内部使用 `cmd.exe /c npx`。
- WSL：识别 Windows Chrome，使用 `wslpath` 转换配置目录，并连接本机 CDP 端口。
- Linux：查找常见的 Chrome/Chromium 路径，并尝试最小化启动。
- 所有平台：调试端口仅绑定 `127.0.0.1`，默认端口为 `9337`。

可选环境变量：

```text
CNKI_CHROME_EXECUTABLE   自定义 Chrome 可执行文件
CNKI_CHROME_PROFILE      自定义独立浏览器配置目录
CNKI_CHROME_DEBUG_PORT   自定义本地调试端口，默认 9337
```

PowerShell 示例：

```powershell
$env:CNKI_CHROME_EXECUTABLE = "D:\Apps\Chrome\Application\chrome.exe"
$env:CNKI_CHROME_DEBUG_PORT = "9347"
```

## 更新与卸载

### Codex

```bash
codex plugin marketplace upgrade nua-cnki-assistant
codex plugin add cnki-research@nua-cnki-assistant
```

```bash
codex plugin remove cnki-research@nua-cnki-assistant
codex plugin marketplace remove nua-cnki-assistant
```

### Claude Code

```bash
claude plugin marketplace update nua-cnki-assistant
claude plugin install cnki-research@nua-cnki-assistant
```

```bash
claude plugin uninstall cnki-research@nua-cnki-assistant
claude plugin marketplace remove nua-cnki-assistant
```

更新或安装后，在现有 Claude Code 会话中执行 `/reload-plugins`。

## 常见问题

### 安装后没有触发插件

- 新建会话或重新加载插件。
- Codex：运行 `codex plugin list --json`。
- Claude Code：运行 `claude plugin list` 和 `claude mcp list`。
- 使用明确说法，例如“使用知网搜索……”或 Claude Code 的 `/cnki-research:cnki-research`。

### Windows 提示 Connection closed

新版启动器已经在 Windows 内部使用 `cmd.exe /c npx`。请确认安装的是 0.2.0 或更高版本，并确认 `node --version`、`npx --version` 可正常运行。

### 找不到 Chrome

- 确认 Chrome 已安装。
- 非标准安装位置请设置 `CNKI_CHROME_EXECUTABLE`。
- WSL 中建议把 Chrome 安装在 Windows 的标准 Program Files 目录。

### Chrome 没有出现在前台

这是预期行为。macOS 不主动激活 Chrome；Windows/WSL 默认最小化。需要登录时请手动切换到 Chrome 或从任务栏恢复窗口。

### 登录后没有自动继续

- 确认页面已经进入知网并显示“南京艺术学院”。
- 不要关闭独立 Chrome 或当前知网页签。
- 可要求“重新连接知网并继续原任务”。

### 被报告为没有全文权限

插件会等待异步加载、逐页检查，并从详情页重新进入阅读器再验证一次。可以要求“重新检查该论文的 CNKI AI阅读权限”。

### 其他学校能否使用

当前默认指向南京艺术学院代理入口。其他学校可以使用 OpenAlex/Crossref 功能和普通知网访问，但机构代理登录流程需要进一步适配。

## 隐私、安全与合规

- 仓库不包含账号、密码、Cookie、Token、私钥或浏览器登录数据。
- 浏览器调试端口绑定到 `127.0.0.1`。
- OpenAlex/Crossref 检索会发送检索词或 DOI，但不发送无关私人上下文。
- 插件不会绕过 CAPTCHA、机构访问控制、付费墙、限速或下载限制。
- 用户应遵守知网、所在机构和论文出版方的使用条款与版权要求。

## 项目结构

```text
.
├── .agents/plugins/marketplace.json       # Codex marketplace
├── .claude-plugin/marketplace.json        # Claude Code marketplace
├── .github/workflows/validate.yml          # 多平台 CI
├── plugins/cnki-research/
│   ├── .codex-plugin/plugin.json           # Codex 插件清单
│   ├── .claude-plugin/plugin.json          # Claude Code 插件清单
│   ├── .mcp.json                            # 两端共用的 MCP 配置
│   ├── scripts/
│   │   ├── launch-cnki-playwright-mcp.cjs  # 跨平台启动器
│   │   └── sync-mcp-config.py              # 同步嵌入式启动器
│   └── skills/cnki-research/                # 共用 Agent Skill
├── scripts/
│   ├── configure-claude-desktop.mjs        # 普通聊天应用配置工具
│   └── validate.py                          # 跨平台完整性检查
├── LICENSE
└── README.md
```

## 开发与验证

```bash
python3 plugins/cnki-research/scripts/sync-mcp-config.py
python3 scripts/validate.py
python3 plugins/cnki-research/skills/cnki-research/scripts/scholar_metadata.py --help
```

Codex 验证：

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/cnki-research
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/cnki-research/skills/cnki-research
```

Claude Code 验证：

```bash
claude plugin validate .
claude plugin validate ./plugins/cnki-research
```

发布新版本时，需要同时更新：

- `.claude-plugin/plugin.json` 的版本号。
- `.codex-plugin/plugin.json` 的基础版本号。
- 运行 Codex cachebuster 更新与重新安装流程。

## 贡献

欢迎通过 Issue 报告知网页面变化、Windows/WSL 启动问题、机构入口适配和全文阅读异常。提交 Pull Request 前请运行 `python3 scripts/validate.py`，并避免提交浏览器配置目录、登录态、Cookie 或论文全文。

## 许可证

代码与插件配置采用 [MIT License](LICENSE)。论文、知网页面内容及下载文件仍归各自权利人所有。
