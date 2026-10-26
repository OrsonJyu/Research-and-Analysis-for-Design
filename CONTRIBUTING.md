# 维护流程 Maintaining the research archive

1. 读取当前状态和最新用户资料，确认属于 SD5008。
2. 将新原件放入清晰的版本／日期目录，记录来源、收到日期及证据状态；保留旧版。
3. 更新可阅读入口、当前状态与决策。涉及研究分类时，同时更新知识网与文献条目的作用／边界。
4. 修订 proposal 时同步检查中英含义；原历史文件仍保留。
5. 按[版本政策](docs/VERSIONING.md)更新 VERSION、CHANGELOG 和 project.json。
6. 运行 `python3 scripts/build_catalog.py`，再运行 `python3 scripts/check_repository.py`。
7. 用清晰的 Git commit 同步；重要里程碑实际创建 tag／Release 后再记入发布记录。

所有新来源都要能追溯到仓库文件或外部链接。结论需要区分来源主张、研究计划、参与者证据和研究者解释。新材料改变旧假设时，修改当前综合文档并记录理由，不覆盖历史原件。

本项目已授权日后继续管理此仓库；这项约定不表示后台定时同步已启动。每次新增讨论或文件后，应在相应任务内实际完成整理、版本记录与同步。
