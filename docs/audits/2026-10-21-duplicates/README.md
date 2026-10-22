# 重复记录审计（2026-10-21）

本目录将上传的 `book-index-duplicate-audit-2026-10-21.zip` 整理为可审阅的审计档案，保留原始结论与证据。此次变更仅添加报告及验证工具，不合并、删除或改写任何元数据。

## 基线与适用范围

原审计基于 **open-guji/book-index@4d6e3219417ac0f2217548b7c241e098c4d39815**，不是当前仓库的扫描结果。原文中的「确认」表示附件作者在该快照上的结论；本次只验证交付物完整性、证据引用及统计一致性，没有重新访问外部文献或重新完成原快照的全量身份判定。

当前接收仓库为 `sheldonli-babelstacks/book-index`。在提交前基线 `dde7426d22fa5772fd52135500d3835e7884b222` 上，报告引用的路径中仅 32/39 条人物、24/910 条 Work、14/2,796 条 Book 存在且 ID 相符、未标为合并或退役。其余记录无法直接在本 checkout 复核。**不得把本报告直接用作当前库的自动合并清单。** 原快照 commit 当前不在本地对象库中。

## 阅读顺序

1. 本页了解范围与限制；[summary.json](summary.json) 查看去重后的总数。
2. [confirmed-records.csv](confirmed-records.csv) 按记录筛选；[confirmed-clusters.json](confirmed-clusters.json) 按连通组查看归并后的证据。
3. [all-evidence.json](all-evidence.json) 查看 confirmed、probable、unresolved、retain 等原始裁定，不同置信度不能混计。
4. 阅读下表六份专题报告，核对误报、待核事项和合并前提。[report.html](report.html) 是附件原有的浏览版。

| 专题 | 报告 |
|---|---|
| 人物强标识 | [报告](lanes/people_identifiers/报告.md) |
| 人物姓名与异名 | [报告](lanes/people_names/报告.md) |
| 经史作品 | [报告](lanes/works_classics_history/报告.md) |
| 后期及其他作品 | [报告](lanes/works_later_other/报告.md) |
| Book 强标识 | [报告](lanes/books_identifiers/报告.md) |
| Book 版本 | [报告](lanes/books_editions/报告.md) |

## 原附件的汇总结果

| 类型 | 重复组 | 涉及记录 | 冗余记录 |
|---|---:|---:|---:|
| 人物 | 19 | 39 | 20 |
| Work | 452 | 910 | 458 |
| Book | 1,398 | 2,796 | 1,398 |
| 合计 | 1,869 | 3,745 | 1,876 |

组数按证据关系的连通分量去重，不是各专题命中数相加。独立机器核验只是子集：Work 439 组，Book 1,391 组；与上表含人工裁定的最终总数口径不同。7 对父 Collection 的重复关系是部分 Book 判断的依赖，不额外计入这三类汇总。

合并前仍须逐组核定保留 ID、异名、来源、墓碑及反向引用。人物同人不推导作品同书；Book 同源不推导其 Work 可以合并；共用馆藏号、合集资源或外部标识也不自动构成重复。

## 文件组织与溯源

- `lanes/`：六专题的原始报告与裁定文件。
- `verification/`：原快照清点、独立核验统计及机器证据；不是本次运行生成的结果。
- 顶层 CSV、JSON、HTML：附件中的原始汇总交付物，字节保持不变。
- [provenance.json](provenance.json)：原 ZIP 的 SHA-256、所有导入文件的大小和哈希，以及未导入文件的完整清单与哈希。
- [verify.py](verify.py)：本次新增的离线一致性检查。

为便于代码审阅，未导入约百 MB 级的原始候选列表和临时脚本。完整扫描材料仍在原 ZIP 中；这些材料不是已确认重复清单。原脚本依赖原工作目录与源快照，不能在当前 checkout 直接复跑，因此不将其包装为可运行工具。专题原文提到的部分候选文件未随本 PR 导入，见 provenance 的 `omitted_files`。

原证据引用保留附件的相对命名：`people_names/findings.json#9` 应解析为本目录的 `lanes/people_names/findings.json` 第 9 项（从 0 开始）；`verified-work-machine.json#0` 应解析为 `verification/verified-work-machine.json` 第 0 项。`verify.py` 实现这一映射。原 HTML 的快照链接仍指向原仓库，不改写成当前库链接。

## 验证

在仓库根执行：

```sh
python3 docs/audits/2026-10-21-duplicates/verify.py
/workspace/.venvs/book-index/bin/python -m pytest -q -p no:cacheprovider tests
python3 .claude/qa/verify.py
```

离线检查会验证全部导入文件的 SHA-256、证据引用、confirmed 连通组、记录 ID 与路径、CSV 内容和汇总数字。它不执行任何原附件脚本，也不写入元数据。仓库测试与常规校验验证当前开发基线；它们不证明历史快照的重复判断正确。
