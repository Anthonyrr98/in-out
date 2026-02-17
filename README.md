## 本地库存管理系统（PySide6 + SQLite + SQLAlchemy）

本项目是一个面向中小企业的本地 Windows 桌面库存管理系统原型，技术栈为 **Python 3 + PySide6 + SQLite + SQLAlchemy**，结构分层清晰，便于后续扩展为联网版或打包为安装程序。

### 目录结构（当前阶段）

- `main.py`：应用入口，初始化数据库并启动主窗口。
- `models/`：SQLAlchemy ORM 模型与数据库基础设施。
- `services/`：业务服务层（商品、库存、入库、出库等）。
- `ui/`：PySide6 界面层（主窗口及各功能页面）。
- `data/`：本地 SQLite 数据库存放目录。

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

