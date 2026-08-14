# 校验规则

`scripts/check.py` 不再是一串顺序执行的检查，而是这些规则文件的**解释器**。
每条规则是一个对象，`kind` 决定用哪个检查器，其余字段是这条规则的参数。

    加一条同类规则  → 只改这里的 JSON
    加一种新检查器  → 才需要动 check.py

这么分是因为有两类东西会**持续累积**：废弃译名、豁免白名单。它们一旦硬编码进
脚本，脚本就会慢慢变成垃圾桶——`check.py` 里曾经直接写着一个废弃译名元组，
那就是第一处渗水（现在它在 `terms.json` 里）。

## 字段

所有规则都有：

| 字段 | 说明 |
|---|---|
| `id` | 唯一标识，报错时打印，方便定位是哪条规则 |
| `kind` | 检查器名字。未知的 `kind` 直接让校验失败，防止改错字段名后规则静默失效 |
| `why` | **必填**。为什么有这条规则。多数是真事故，写清楚，否则后人不敢删也不敢改 |

`scope` 缺省是 `tree`（查出货树）；`repo` 表示查整个仓库。

## 检查器一览

| kind | 干什么 |
|---|---|
| `json_parses` | glob 命中的文件必须是合法 JSON |
| `json_assert` | 某个 JSON 文件里某个路径的值必须等于给定值 |
| `file_absent` | 这个文件不许存在（废弃产物禁止复活） |
| `filename_prefix` | glob 命中的文件名必须带前缀 |
| `forbidden_text` | 一批词不许出现在文件里，可按路径尾巴豁免 |
| `vp_shape` | VaultPatcher 模块的 JSON 结构 |
| `vp_pair_key_in` | 某批原文串不许被替换（可限定只查「有风险」的块） |
| `vp_pair_regex` | 原文匹配某正则、且译文含中文 → 报错 |
| `vp_server_global` | 服务端模块清单里不许有全局替换块 |
| `vp_keybind_names` | 替换的原文不许撞上按键注册名及其字符串原子 |
| `gui_choice_ascii` | `.gui` 里 `choice(...)` 的参数必须保持英文 |
| `format_safety` | 译文的占位符 / 颜色码不得比英文原文更危险 |
| `snbt_no_dup_keys` | 任务书 delta 之间不许有重复键 |
| `pb_single_source` | 蜂名脚本表必须与资源包 zh_cn 一致 |
| `vp_value_conflict` | 同类同原文同匹配模式下不许有两句译文 |
| `term_binding` | 英文词与中文词双向绑定，出现其一必须出现其二 |
| `tiered_family` | 同一族 N 档的词干必须相同、档位后缀写法必须统一 |
