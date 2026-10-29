# 对象 Entities

按对象组织的记录。每个对象一份文件，文件头写稳定 `id`、`type` 和 `aliases`（别名）。别处用编号引用对象，不复制整份资料。记录变长时，把 `P01.md` 拆成 `P01/README.md` 加子文件，原有链接改指向文件夹。

## 参与者 Participants

| id | 别名 | 观察日期 | 主页 |
|---|---|---|---|
| P01 | Sarah · Sara · UserA | 2026-10-27 | [P01](participants/P01.md) |
| P02 | Caicai · UserB | 2026-10-27 | [P02](participants/P02.md) |
| P03 | Peter · UserC · Participant C | 2026-10-27 | [P03](participants/P03.md) |
| P04 | Tom · UserD ·（研究员口述）用户 C | 2026-10-28 | [P04](participants/P04.md) |
| P05 | Chenggong · 程功 · UserE | 2026-10-28 | [P05](participants/P05.md) |

注意编号混用：研究员口述里的"用户 C"是 Tom（P04），组员文档里的 "Participant C" 是 Peter（P03）。本仓库一律以 P01–P05 为准。

时间线见 [timeline](../timeline/README.md)，正在进行的工作见 [workstreams](../workstreams/README.md)。
