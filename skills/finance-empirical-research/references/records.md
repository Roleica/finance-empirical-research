# 可替换记录接口

用 JSON/JSONL/CSV/Parquet/SQLite，不依赖服务。以下为最小信息，不强迫同列名；自有格式附字段映射与查询。只建需要的文件，不预建空治理体系。

建议 `catalog/` 字典/README，`data/` 加工表，`code/` 项目代码，`runs/<id>/` 规格/结果/日志，`studies/` 候选/方法/审核，`literature/` 书目/证据。原始只读引用或授权复制；输出根相对路径配独立原始路径映射，便于迁移。

- 数据：id、来源/哈希/表区域、字段/单位/主键/时间/层级、检查覆盖、处理代码、版本、unknown/问题。
- 方法：id、问题/目标量、数据 id、规格 id、公式、全部选项/控制/固定效应/聚类、变换/缺失/样本、理由与限制、代码/依赖/命令、执行状态。
- 规格：`id`、`space_version`、输入/代码/选项指纹、完整模型/样本/变量/参数；ID 对完整语义唯一。仅对顺序无意义的集合规范排序。
- 结果：`id`（规格 id）、`status`、尝试/运行标识、全部估计或完整表路径、实际样本、诊断/错误、来源。未执行不造数值。当前一规格一条，历史尝试另表。
- 候选：id、问题、数据/方法/规格/结果引用、筛选依据、使用史、解释强度、审核、问题/版本。
- 文献：id、书目/永久标识/版本、检索/核验、原文位置、论断关系、审核。
- 报告：id、层级/问题/主题、阶段/状态/版本、正文与附件路径、来源 id 和证据映射；结构与逐项数字溯源见 [reporting.md](reporting.md)。目录保留查询入口，不在启动时加载报告全文。

JSON 不写 NaN/Infinity，用 null 并记原因。金额、日期、标识符不因导出丢精度或含义。方法记“做了什么/为何/如何/结果”，不规定未来只能这样做。

## 可选工具

```
python3 <skill>/scripts/ledger.py query <records.jsonl> --query 中介 --fields id,status,method --limit 20
python3 <skill>/scripts/ledger.py coverage <specs.jsonl> <results.jsonl>
python3 <skill>/scripts/ledger.py hash <input-file>
```

query 是字面子串匹配，不是语义搜索。将主题/变量/方法写入可查询字段；大规模可换索引。coverage 非零表示缺/额外/重复 id、非法状态或未成功/未合理排除项。它不核验生成规则、证据路径、数值或不适用理由真假，需要项目自己的单元格、样本、连接与统计校验。
