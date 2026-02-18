## 本地库存管理系统（PySide6 + SQLite + SQLAlchemy）

本项目是一个面向中小企业的本地 Windows 桌面库存管理系统原型，技术栈为 **Python 3 + PySide6 + SQLite + SQLAlchemy**，结构分层清晰，便于后续扩展为联网版或打包为安装程序。

### 目录结构（当前阶段）

- `main.py`：应用入口，初始化数据库并启动主窗口。
- `config/`：应用配置与路径管理（数据库、导出目录等）。
- `models/`：SQLAlchemy ORM 模型与数据库基础设施。
- `services/`：业务服务层（商品、库存、入库、出库等）。
- `ui/`：PySide6 界面层（主窗口及各功能页面）。
- `data/`、`exports/`：开发阶段默认在项目根目录下，用于存放 SQLite 数据库和报表导出文件。

### 开发环境

- Python 3.10+（推荐）
- 依赖安装：

```bash
pip install -r requirements.txt
```

### 运行方式

```bash
python main.py
```

### 打包为 Windows 可执行文件（预览）

1. 在虚拟环境中安装 PyInstaller：

```bash
pip install pyinstaller
```

2. 在项目根目录执行打包脚本：

```bash
build_exe.bat
```

3. 打包成功后，可在 `dist/` 目录下找到 `InOutInventory.exe`，双击即可运行。数据库和报表导出目录由 `config/settings.py` 管理，开发阶段默认在项目根下的 `data/` 与 `exports/` 中。

