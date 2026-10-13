# turn-anything-into-3b1b

给它一篇 paper、一个链接、一个 repo，或者只有一个 topic。它把内容整份读完、核实，然后交回一份 3Blue1Brown 风格的动画讲解：讲清楚这个东西到底怎么运作，带着真实的名字和数字，而不是一份 summary。

这是一套给 **Claude Code** 和 **Codex** 用的 skill，一共四个。[English](README.md)

## 安装

**一行命令，同时装到 Claude Code 和 Codex**（macOS 或 Linux）：

```bash
curl -fsSL https://raw.githubusercontent.com/youxiangdev/turn-anything-into-3b1b/main/install.sh | bash
```

它把这套 skill 下载到 `~/.turn-anything-into-3b1b`，再把四个 skill 链接到 `~/.claude/skills`；如果装了 Codex，也会链接到 Codex 的 skills 目录。别的东西它不碰，你已有的同名 skill 也不会被覆盖。以后要更新，再运行一次同一行命令。

**或者作为 Claude Code plugin 安装**（需要 Claude Code 2.1.275 或更新）：

```
/plugin install turn-anything-into-3b1b --marketplace youxiangdev/turn-anything-into-3b1b
```

两种装法选一种。两种都装，每个 skill 会出现两次。

## 怎么用

开一个新的 session，输入：

```
/deep-dive <paper 的路径、链接、repo，或者一个 topic>
```

| 在哪里 | 怎么调用 |
|---|---|
| Claude Code，用一行命令装的 | `/deep-dive ...` |
| Claude Code，作为 plugin 装的 | `/turn-anything-into-3b1b:deep-dive ...` |
| Codex | `$deep-dive ...`，或者在 `/skills` 里选 |

也可以直接说："帮我 deep dive 这篇 paper"、"帮我把 X 怎么运作讲清楚"。

## 它做什么

三段依次运行。它只在第 2 段停下来问你一次。

| 段 | Skill | 做什么 | 留下什么 |
|---|---|---|---|
| 1 | `research` | 把来源整份读完，把关键说法拿到一手资料（官方文档、源码、原始论文）核实，每个部分写到"它怎么运作"的深度 | `dossier/`：每一条说法，都标明来源和可信程度 |
| 2 | `scope` | 给你一页：会讲什么、发现哪些内容已经过时、这次要做多大。最多问四个问题，只问一次 | `scope.md`：你确认过的范围 |
| 3 | `visual-explainer` | 用同一个故事做出两个网页：一个自己从头播到尾的 video 版，一个可以滚动、可以自己动手试的 slides 版 | `output/`，以及 `coverage.md`：每一条内容出现在哪里 |

每一段也可以单独用：`/research <来源>` 只要研究档案，`/scope <run folder>` 给已有的档案确认范围，`/visual-explainer` 讲解你描述的东西。

中途断掉（用量到上限、session 关了）不会丢东西。对同一个 folder 再运行 `/deep-dive`，它从停下的地方继续。

## 靠什么保证不乱讲

有两个脚本检查成果，所以"全部都讲到了"不只是 agent 自己说的。

- **每条说法都有标签**：来自来源、已经用第二个来源核实、已更正、我们自己的推理，或者没有任何来源能回答的问题。没有答案的问题不会被猜一个填上。
- **档案检查**：来源有哪几页没读，它就不通过；它还会报告有多少条说法用第二个来源核实过，包括整个讲解赖以成立的那几条。
- **覆盖检查**：范围内的内容没出现在成品里、真实的名字或数字被换成了含糊的说法、更正或推理在画面上没有标明、清单里写的画面根本不存在，这些情况它都不通过。
- **证明不了的，它会说出来**。一条说法里如果没有名字也没有数字，就没法用搜索来核对。检查会把这些单独数出来，并要求 agent 抽一部分打开看。

## 擅长什么，不擅长什么

**擅长**：任何有"运作机制"的东西。paper 里的一个方法、一个系统、一个算法、一个协议、一个产品、一个流程。来源可以是 PDF、网页、repo、贴进来的文字，或者只给 topic 让它自己找来源。

**目前验证过的**：一整篇 paper，从头跑到尾。其他几种来源在说明里是支持的，实际用得还少。

**还不行的**：

- 没有运作机制的主题：纯数学概念、一段历史、一篇议论文。档案格式要求有步骤、失败路径和一个走一遍的例子。
- 图表和公式。绘图工具有五种呈现形式（带旁白的动画、一步一步的模拟器、时序图、可缩放的总图、等距小世界），还没有内置的函数图和公式排版。
- 以视频、音频、slide deck 作为来源。

对一篇长 paper 跑完整流程是个大工程：这套 skill 背后的那次示例运行，产出了大约 400 条内容和一个 370 个画面的讲解。第 2 段会在你确认之前告诉你规模，你也可以要求先看一章。

## 需要什么

| | 用来做什么 |
|---|---|
| Python 3 | 全部脚本。只用标准库 |
| 读 PDF 的办法 | macOS 自带。其他系统装任意一个：poppler（`pdftotext`、`pdftoppm`）、`pypdf`、`PyMuPDF`、`pdfminer.six` |
| Node | 列出讲解的逐画面文稿，以及 build 之前的语法检查 |
| Chrome 或 Chromium | 可选：给做好的网页截图、检查排版 |
| `git` 和 `gh` | 可选：核实时读源码 |

## 一次运行会留下什么

```
deep-dive-<名字>/
├── sources/        来源材料的全文，和一份来源清单
├── dossier/        研究档案：总览、总图、每个部分一个文件、情景、结论、名词表
├── scope.md        你确认过的范围
├── coverage.md     范围里的每一条，出现在成品的哪里
└── output/         讲解成品
```

这个 folder 建在你当前工作的目录下。研究档案和成品是分开的，所以同一份档案以后可以交给另一个 output skill，不用重新研究。

## 换一种输出

第 3 段是一个插槽，现在装着 `visual-explainer`。任何"根据给它的内容来制作"的 skill 都可以替换它或者和它并列，比如做 slide deck 或者写报告的 skill：见 [skills/deep-dive/references/output-skills.md](skills/deep-dive/references/output-skills.md)。在 clone 下来的 folder 里，`./install.sh --adopt <folder>` 会把这样的 skill 复制进来并链接好。

## 更新和移除

| | 一行命令装的 | Plugin |
|---|---|---|
| 更新 | 再运行一次安装命令 | `/plugin update turn-anything-into-3b1b` |
| 移除 | `bash ~/.turn-anything-into-3b1b/install.sh --remove`，然后删掉 `~/.turn-anything-into-3b1b` | `/plugin uninstall turn-anything-into-3b1b` |

`install.sh` 还有几个选项（`--no-codex`、`--codex`、`--list`），见文件开头。

## 修改这套 skill

```bash
git clone https://github.com/youxiangdev/turn-anything-into-3b1b
cd turn-anything-into-3b1b
./install.sh              # 链接这份 clone，改了文件立即生效
python3 tests/run_tests.py
```

测试用 `tests/fixture/` 里一个虚构的小例子跑每个脚本。这个例子是编出来的，不描述任何真实系统。

```
skills/
├── deep-dive/           入口：依次跑三段；带覆盖检查脚本
├── research/            第 1 段：全文提取、页面渲染、档案检查
├── scope/               第 2 段
└── visual-explainer/    第 3 段：绘图工具、build 脚本、排版检查
tests/                   脚本测试、虚构的小例子、手动试用的提示
```

## 许可和名字

MIT，见 [LICENSE](LICENSE)。

本项目与 3Blue1Brown 没有关联，也没有得到其认可。这个名字说的是它追求的讲解方式：让想法动起来给你看，而不是用文字描述它。
