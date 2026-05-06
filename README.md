# Thesis Workflow Agent Skill

`thesis-workflow-agent` 是一套面向论文编写、修改、优化、降 AIGC、参考文献补证、论文插图与 Word 正式落地的 Codex Skill。它以总控 Skill 的方式编排论文全流程，并内嵌两个核心子 Skill：

- `skills/minimax-docx`：负责 `.docx` 创建、编辑、套模板、排版、OpenXML 校验。
- `skills/thesis-optimizer`：负责论文章节诊断、扩写、删减、润色、转义、降重、降低 AIGC 风险。

## 适用场景

- 从零编写论文，先生成目录结构树，再逐章写作。
- 基于学校模板创建论文文档。
- 在已有论文基础上修改、扩写、删减、润色、转义或格式整理。
- 根据 Paperyy 等检测报告做 AIGC/查重定向优化。
- 补充研究现状、参考文献候选与章节证据。
- 规划论文插图，并可选使用内嵌 Suxi `gpt-image-2-vip` MCP 生成位图插图。
- 使用 `minimax-docx` 将稳定内容写入正式 Word 文档。

## 目录结构

```text
thesis-workflow-agent/
  SKILL.md
  README.md
  agents/
    openai.yaml
  references/
    metaso-setup.md
    report-handling.md
    suxi-image-mcp.md
    workflow-details.md
  scripts/
    check_thesis_environment.ps1
    find_aigc_reports.ps1
  mcp/
    suxi-image/
      suxi_image_mcp.py
      mcp-config.example.json
  skills/
    minimax-docx/
    thesis-optimizer/
  template/
    simple.docx
```

## 快速开始

将本目录放入 Codex 可发现的 Skill 目录，例如：

```text
C:/Users/Administrator/.agents/skills/thesis-workflow-agent
```

在论文工作区中请求：

```text
请使用 thesis-workflow-agent 扫描当前论文工作区，建立论文工作台并给出下一步执行方案。
```

Skill 会先检查依赖、扫描材料、识别模板/初稿/参考资料/检测报告，再根据任务进入创建、编辑、优化、降 AIGC、补文献、配图或 DOCX 落地流程。

## 标准论文工作区

Skill 会建议使用以下产物目录：

```text
chapters/    章节草稿和确认稿
images/      图片、截图、图表导出
templates/   学校模板和格式参考
references/  文献、项目资料、论文资料
reports/     AIGC/查重报告
outputs/     输出的 DOCX/PDF/TXT
logs/        审计记录和变更说明
```

## 默认模板

默认模板路径为：

```text
template/simple.docx
```

如果用户没有提供学校模板且该文件存在，Skill 会通过 `minimax-docx` 使用它创建默认论文文档。

## DOC 文件转换

如果检测到论文模板或参考文件为旧版 Word `.doc`，Skill 会提示用户先到以下页面转换为 `.docx`：

```text
https://www.freeconvert.com/zh/docx-converter
```

该转换用于保留文档内容并便于后续 `.docx` 处理；如果最终仍需要 `.doc`，后续可以再转换回去。

## AIGC 降低流程

当用户需要降低 AIGC 率时，Skill 会提示用户：

1. 前往 `https://www.paperyy.com/` 做免费 AIGC 检测。
2. 下载检测报告。
3. 由 Agent 自动在 Downloads、`reports/` 和工作区中定位报告。
4. 解析命中段落后，调用 `thesis-optimizer` 做定向优化。
5. 再调用 `minimax-docx` 输出新版本 Word。

优化范围默认只覆盖高风险/中风险命中段及相邻承接句，不做无依据整篇重写。

## 可选 Suxi 生图 MCP

如果用户需要论文位图插图，可配置内嵌 MCP：

```text
mcp/suxi-image/suxi_image_mcp.py
```

用户需要先：

1. 注册 Suxi 账号。
2. 前往 `https://new.suxi.ai/console/topup` 充值。
3. 前往 `https://new.suxi.ai/console/token` 创建 API key。
4. 将 API key 发给 Agent，由 Agent 注入当前本地 MCP 配置。

费用说明按当前工作流约定：`1 元 = 1 美元额度`，每次生图消耗 `0.12` 美元额度，约 `0.12 元`。

如果用户不需要生图，跳过此步骤，不索要 API key。

## 安全规则

- 不要把 Metaso、Suxi 或其他 API key 写入 `SKILL.md`、README、示例配置或 Git 仓库。
- 不要提交用户论文、查重报告、生成图片、日志、输出文档或本地临时文件。
- `.gitignore` 已排除常见密钥、缓存、构建产物和运行时产物。
- 子 Skill 的 `.NET bin/obj` 构建产物不应上传。

## 验证

Skill 结构校验：

```powershell
$env:PYTHONUTF8='1'
python "C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py" "C:/Users/Administrator/.agents/skills/thesis-workflow-agent"
```

Suxi MCP 本地自检：

```powershell
python "C:/Users/Administrator/.agents/skills/thesis-workflow-agent/mcp/suxi-image/suxi_image_mcp.py" --self-test
```

环境扫描：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:/Users/Administrator/.agents/skills/thesis-workflow-agent/scripts/check_thesis_environment.ps1" -Workspace "<论文工作区>"
```

## 许可证

请在发布前根据你的分发需求补充许可证文件。当前仓库仅包含 Skill 编排文件、内嵌子 Skill 与辅助脚本。
