# NUA知网小助手

NUA知网小助手是一个面向 Codex 的 CNKI（中国知网）研究插件。它可以在用户合法授权的机构访问环境中完成知网检索、结果筛选、论文详情读取、可访问全文阅读、PDF/CAJ 下载、结构化总结和参考文献生成。

插件默认适配南京艺术学院知网代理入口，因此尤其适合南艺师生。它不会绕过登录、验证码、付费墙或机构权限；是否能够阅读或下载全文，取决于当前账号及机构的真实授权。

## 主要功能

- 直接操作知网：支持普通检索、高级检索、专业检索、年份与来源筛选。
- 阅读可访问全文：通过论文详情页进入“CNKI AI阅读”，逐页检查正文是否实际加载。
- 更可靠的权限判断：延迟等待、逐页验证并二次重试，避免把暂未加载误判为“无权限”。
- 批量研究整理：提取题名、作者、来源、年份、摘要、关键词、DOI、被引量和详情链接。
- 论文下载：在用户明确要求且具备合法权限时下载 PDF；也支持明确指定的 CAJ。
- 研究总结：区分作者主张与插件的批判性评价，输出背景、方法、结论、贡献、局限和后续方向。
- 引用生成：支持 APA、BibTeX 和 GB/T 7714。
- 公共元数据补充：可使用 OpenAlex 或 Crossref 检索 DOI、开放获取状态和出版信息，并明确标注数据来源。
- 后台可见 Chrome：macOS 上使用独立 Chrome 配置文件，允许多标签页，但启动新页面时不会强行把 Chrome 窗口切到最前面。
- 自动恢复登录后任务：遇到机构登录或人工验证时会等待并监听页面状态，完成后自动继续，无需用户再输入“继续”。

## 系统要求

推荐环境：

- macOS；“后台启动但仍可见”的 Chrome 行为目前针对 macOS 实现并验证。
- 已安装 Google Chrome，位置为系统默认路径 `/Applications/Google Chrome.app`。
- 已安装 Node.js 和 `npx`。Playwright MCP 会在首次使用时通过 `npx` 获取。
- Codex Desktop 或带有 `codex plugin` 命令的 Codex CLI。
- 如需使用机构全文权限，需有南京艺术学院代理访问资格并自行完成登录。
- 公共元数据辅助脚本需要 Python 3.9 或更高版本。

Windows 和 Linux 会回退到 Playwright MCP 的扩展模式，可以使用主要研究能力，但不保证与 macOS 完全相同的窗口后台行为。

## 最简单的安装方式

仓库发布到 GitHub 后，其他用户不需要手动复制 Skill 文件，也不需要把仓库克隆到固定目录。最简单的方式是执行两条命令：

```bash
export GITHUB_OWNER="你的 GitHub 用户名"
codex plugin marketplace add "${GITHUB_OWNER}/nua-cnki-assistant"
codex plugin add cnki-research@nua-cnki-assistant
```

安装完成后重启 Codex，或新建一个对话，使插件的 Skill 和 MCP 服务被重新加载。

也可以使用完整 Git 地址：

```bash
codex plugin marketplace add https://github.com/你的用户名/nua-cnki-assistant.git
codex plugin add cnki-research@nua-cnki-assistant
```

### 从本地目录安装

适合开发、测试或尚未发布到 GitHub 的情况：

```bash
git clone https://github.com/你的用户名/nua-cnki-assistant.git
codex plugin marketplace add /绝对路径/nua-cnki-assistant
codex plugin add cnki-research@nua-cnki-assistant
```

## 首次使用与登录

1. 安装插件并重新打开 Codex。
2. 在新对话中输入一个知网任务，例如“使用知网搜索用户体验理论更新的最新 20 篇论文”。
3. 插件会启动一个独立、可见但不抢占前台的 Chrome 实例。它使用单独的本地配置文件，不会读取普通 Chrome 配置文件。
4. 首次进入南京艺术学院代理时，如果出现统一身份认证、机构登录或浏览器连接批准，请用户在 Chrome 中手动完成。
5. 插件会持续检查页面状态。登录完成后，它应自动继续原任务，无需再次输入“已登录”或“继续”。
6. 登录状态保存在本机 `~/.codex/browser-profiles/cnki-research`，不会写入本仓库。

插件不会填写密码、破解验证码或规避安全验证。

## 如何唤醒插件

可以直接描述任务，不必记住固定命令。以下说法都应触发插件：

- `使用知网搜索……`
- `用知网查一下……`
- `查一下知网的文章……`
- `帮我上知网找论文……`
- `搜知网文献……`
- `读一下这篇知网论文的全文……`
- `下载这篇知网论文的 PDF……`
- `用 cnki-research 检索……`

## 常用示例

### 检索并整理

```text
使用知网搜索 UX 设计理论更新层面的最新 20 篇论文，限定 2022—2026 年，按相关性和理论贡献排序，并给出题名、作者、来源、年份、摘要和链接。
```

```text
在知网专业检索中查找“用户体验”和“AIGC”相关论文，只看 CSSCI 和北大核心，去重后列出前 30 篇。
```

### 阅读全文并总结

```text
阅读这 5 篇论文的可访问全文。每篇分别总结研究背景、理论框架、方法、核心结论、贡献、局限和后续研究方向，最后做横向比较。
```

插件会验证实际正文页是否加载，并至少覆盖引言、正文、结论和参考文献。只有两次独立检查均确认无法读取时，才会报告“已验证不可访问”；加载异常会单独标为“阅读器错误/不完整”。

### 下载论文

```text
下载《人工智能赋能下新媒体健康传播视频的创意设计、用户体验与效果评估体系构建探索》的 PDF 到 Downloads 文件夹。
```

```text
把这篇论文下载为 CAJ 文件。
```

下载仅在用户明确提出、且当前会话具备合法访问权时执行。文件格式以详情页实际提供的选项为准。

### 生成引用

```text
核对这几篇论文的 DOI 和出版信息，并分别生成 GB/T 7714 与 BibTeX 引用。
```

### 只查公共元数据

```text
使用 OpenAlex 查找 2023 年以来关于 AI-assisted UX design 的高被引论文，列出 DOI 和开放获取链接。
```

此类结果会标注为 OpenAlex 或 Crossref 数据，不会冒充知网直接检索结果。

## Chrome 后台运行机制

插件在 macOS 上启动独立 Chrome 实例，并只监听本机地址 `127.0.0.1` 的调试端口。默认端口为 `9337`，默认配置目录为：

```text
~/.codex/browser-profiles/cnki-research
```

启动时使用 macOS 的后台打开参数，因此 Chrome 仍然可见、用户可以随时切换过去完成登录，但打开新标签页时不会主动抢占当前应用焦点。插件允许使用多个标签页：保留结果页，按需打开详情页和阅读器页，处理完后关闭工作标签页。

如端口冲突，可以在启动 Codex 前设置：

```bash
export CNKI_CHROME_DEBUG_PORT=9347
```

如需自定义独立 Chrome 配置目录：

```bash
export CNKI_CHROME_PROFILE="$HOME/.codex/browser-profiles/my-cnki-profile"
```

不要把该配置目录上传到 GitHub，其中可能包含登录状态和站点数据。

## 更新与卸载

更新 GitHub marketplace 快照并重新安装插件：

```bash
codex plugin marketplace upgrade nua-cnki-assistant
codex plugin add cnki-research@nua-cnki-assistant
```

卸载插件：

```bash
codex plugin remove cnki-research@nua-cnki-assistant
```

如不再需要该 marketplace：

```bash
codex plugin marketplace remove nua-cnki-assistant
```

删除插件不会自动删除独立 Chrome 配置目录。如确认不再需要其中的登录状态，可自行删除：

```bash
rm -rf "$HOME/.codex/browser-profiles/cnki-research"
```

执行删除前请确认路径无误。

## 常见问题

### 安装后没有触发插件

- 重新启动 Codex，或新建一个对话。
- 运行 `codex plugin list --json`，确认 `cnki-research@nua-cnki-assistant` 的 `installed` 和 `enabled` 为 `true`。
- 使用明确表达，例如“使用知网搜索……”或“查一下知网的文章……”。

### Chrome 没有启动

- 确认 Google Chrome 安装在默认路径。
- 确认终端中可以运行 `node --version` 与 `npx --version`。
- 检查默认端口是否冲突；必要时修改 `CNKI_CHROME_DEBUG_PORT`。
- 首次运行 `npx` 可能需要联网下载 Playwright MCP。

### Chrome 仍然跳到前台

macOS 启动脚本使用 `open -g`，并且插件不会调用 `bringToFront`。如果系统、Chrome 扩展或窗口管理工具仍主动切换焦点，请先停用相关自动聚焦设置。用户手动点击 Chrome 时，窗口当然会正常置前。

### 登录后没有自动继续

- 确认浏览器已进入知网页面，并显示机构身份“南京艺术学院”。
- 不要关闭独立 Chrome 实例或正在使用的标签页。
- 若浏览器连接已断开，可在当前对话中要求“重新连接知网并继续原任务”。

### 被报告为没有全文权限

插件会等待异步加载、逐页检查，并从详情页重新进入阅读器再验证一次。若仍有疑问，可以让插件“重新检查该论文的 CNKI AI阅读权限”，或在独立 Chrome 中手动确认详情页。插件不会把暂时加载失败直接当作无权限。

### 能否给其他学校使用

当前版本默认指向南京艺术学院代理入口。其他学校的用户仍可使用 OpenAlex/Crossref 元数据功能，也可以在普通知网页面使用自己的合法访问方式，但机构代理登录流程可能需要二次适配。欢迎提交 Issue 或 Pull Request 增加可配置的机构入口。

## 隐私、安全与合规

- 仓库不包含账号、密码、Cookie、Token、私钥或已登录浏览器数据。
- 浏览器调试端口绑定到 `127.0.0.1`，不会主动暴露到局域网。
- 公共元数据检索会把检索词或 DOI 发送给 OpenAlex 或 Crossref；插件不会发送无关的私人上下文。
- 知网访问通过用户当前选择的合法网络与机构授权进行。
- 插件不会绕过 CAPTCHA、登录、机构访问控制、付费墙、限速或下载限制。
- 用户应遵守知网、所在机构以及论文出版方的使用条款和版权要求。

## 项目结构

```text
.
├── .agents/plugins/marketplace.json     # Codex marketplace 入口
├── .github/workflows/validate.yml        # GitHub Actions 完整性检查
├── plugins/cnki-research/
│   ├── .codex-plugin/plugin.json         # 插件清单与展示信息
│   ├── .mcp.json                          # Playwright MCP 配置
│   ├── .codex/config.toml                 # Codex MCP 配置镜像
│   ├── scripts/                           # 后台 Chrome 启动脚本
│   └── skills/cnki-research/              # Skill、参考资料和元数据脚本
├── scripts/validate.py                    # 可移植仓库检查
├── LICENSE
└── README.md
```

## 开发与验证

克隆仓库后运行：

```bash
python3 scripts/validate.py
python3 plugins/cnki-research/skills/cnki-research/scripts/scholar_metadata.py --help
```

在安装了 Codex 内置 `plugin-creator` 与 `skill-creator` 的开发环境中，还可以运行更严格的验证：

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/cnki-research
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/cnki-research/skills/cnki-research
```

修改插件后应更新 `plugins/cnki-research/.codex-plugin/plugin.json` 中的语义化版本号，并重新运行验证。

## 发布到你自己的 GitHub

1. 在 GitHub 创建公开仓库，建议命名为 `nua-cnki-assistant`。
2. 把本目录内容放在仓库根目录，保留 `.agents/plugins/marketplace.json` 的路径。
3. 提交并推送：

```bash
git init
git add .
git commit -m "Initial release of NUA CNKI Assistant"
git branch -M main
git remote add origin git@github.com:你的用户名/nua-cnki-assistant.git
git push -u origin main
```

如果已安装 GitHub CLI，也可以在本目录直接运行：

```bash
gh repo create nua-cnki-assistant --public --source=. --remote=origin --push
```

发布后，把本文安装示例中的“你的 GitHub 用户名”替换为真实用户名。建议在 GitHub Releases 中按插件版本创建发行版，方便用户追踪更新。

## 贡献

欢迎通过 Issue 报告知网页面变化、选择器失效、机构入口适配和全文阅读异常。提交 Pull Request 前请运行 `python3 scripts/validate.py`，并避免提交任何浏览器配置目录、登录态、Cookie 或论文全文。

## 许可证

代码与插件配置采用 [MIT License](LICENSE)。论文、知网页面内容及下载文件仍归各自权利人所有，不因本项目许可证而改变。
