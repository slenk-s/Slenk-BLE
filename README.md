# Slenk BLE Monitor — 蓝牙上位机

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.6+-41CD52?logo=qt&logoColor=white)
![Bleak](https://img.shields.io/badge/Bleak-0.21+-0082FC?logo=bluetooth&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**跨平台 BLE（低功耗蓝牙）数据采集上位机软件**  
支持多设备连接、实时数据可视化、自定义协议解析与 OTA 固件升级

</div>

---

## 📋 功能总览

| 功能 | 描述 |
|------|------|
| 🔍 **BLE 扫描** | 扫描周围 BLE 设备，显示名称 / 信号强度 / MAC 地址 |
| 🔗 **多设备连接** | 最多同时连接 5 台设备，独立管理每个连接 |
| 📊 **实时数据** | 表格实时显示 4 列（时间 / 设备 / HEX / 解析值） |
| 📈 **实时图表** | 每设备多通道实时折线图，500 点滚动窗口 |
| 🔧 **协议解析** | 支持 **Raw HEX / JSON / Modbus RTU** 三种协议，可扩展自定义解析器 |
| 📁 **数据导出** | CSV / Excel / SQLite 三种格式，支持按设备筛选 |
| 🔄 **OTA 升级** | 分包发送 + 序号 + CRC + SHA-256 校验，支持断点续传与重试 |
| 📝 **日志系统** | 控制台 + 文件双输出，每日轮转，保留历史日志 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Windows 10+ / Linux / macOS
- 蓝牙 4.0+ 适配器

### 安装

```bash
git clone https://github.com/slenk-s/Slenk-BLE.git
cd Slenk-BLE
pip install -r requirements.txt
```

### 运行

```bash
# 方式一（推荐）
python -m src.main

# 方式二
python src/main.py
```

---

## 🏗️ 软件架构

```
src/
├── ble/                  # BLE 服务层（Bleak 封装）
│   ├── scanner.py        # BLE 扫描器（非阻塞，自动超时停止）
│   ├── connector.py      # 连接池管理（最多 5 设备）
│   ├── gatt_service.py   # GATT 读写/通知/服务发现
│   ├── manager.py        # BLE 管理器（组合 Scanner + Connector + GattService）
│   └── signals.py        # Qt 信号桥接（9 个信号）
├── app_layer/            # 应用层
│   ├── connection_manager.py   # 连接状态机（4 状态 + 重试策略）
│   ├── data_cache.py           # 环形缓冲区数据缓存（O(1) 读写）
│   ├── protocol_engine.py      # 协议解析引擎（策略模式）
│   ├── protocols/              # 协议解析器
│   │   ├── base.py             # ProtocolParser ABC
│   │   ├── raw.py              # Raw HEX
│   │   ├── json_proto.py       # JSON
│   │   └── modbus.py           # Modbus RTU (CRC16)
│   ├── export_service.py       # CSV / Excel / SQLite 导出
│   └── ota_service.py          # OTA 固件升级（分包 + 校验 + 重试）
├── ui/                   # GUI 层（PySide6）
│   ├── main_window.py    # 主窗口（左侧设备面板 + 右侧标签页）
│   ├── device_panel.py   # 设备列表面板（扫描/连接/断开）
│   ├── tabs/             # 5 个功能标签页
│   │   ├── data_tab.py   # 数据表格
│   │   ├── chart_tab.py  # 实时图表
│   │   ├── log_tab.py    # 日志查看
│   │   ├── protocol_tab.py    # 协议配置
│   │   └── ota_tab.py         # OTA 升级
│   └── widgets/          # 自定义组件
│       └── realtime_chart.py   # 实时图表组件
├── utils/
│   └── logger.py         # 日志工具（控制台 + 文件轮转）
├── app.py                # BLEApplication 入口
└── main.py               # 主函数入口
```

### 数据流

```
BLE 设备 → BleakScanner/Client → BLE Manager → Qt 信号 → UI 更新
                                                     ↕
                                          Application Layer（缓存 / 协议解析 / 导出）
```

---

## 🧪 测试

```bash
# 运行全部测试
pytest

# 指定模块测试
pytest tests/test_scanner.py
pytest tests/app_layer/test_data_cache.py

# 带覆盖率报告
pytest --cov=src --cov-report=html
```

共 **142 个测试**，核心模块覆盖率 >95%。

---

## 📦 打包为单文件 Exe

```bash
pip install pyinstaller
python build.py
```

生成的可执行文件位于 `dist/BLE-Monitor.exe`，无需 Python 环境即可运行。

---

## 🔧 支持的协议解析

| 协议 | 说明 |
|------|------|
| **Raw HEX** | 默认协议，原始十六进制显示 + ASCII 可读字符 |
| **JSON** | 自动解析 JSON 格式数据，字段友好显示 |
| **Modbus RTU** | CRC16 校验验证，帧结构分析 |

可通过实现 `ProtocolParser` 抽象基类扩展自定义协议：

```python
from src.app_layer.protocols.base import ProtocolParser, ParsedData

class MyProtocol(ProtocolParser):
    @property
    def name(self) -> str:
        return "自定义协议"

    def parse(self, data: bytes) -> ParsedData:
        # 实现自定义解析逻辑
        ...
```

---

## 📄 数据导出格式

| 格式 | 文件后缀 | 特点 |
|------|---------|------|
| CSV | `.csv` | 通用，Excel 可直接打开（UTF-8 BOM） |
| Excel | `.xlsx` | 多 Sheet，格式化表格 |
| SQLite | `.db` | 结构化存储，支持 SQL 查询 |

---

## 🧑‍💻 开发者

- **项目**: [Slenk-BLE](https://github.com/slenk-s/Slenk-BLE)
- **技术栈**: Python 3.11 / PySide6 6.6 / Bleak 0.21 / qasync / pyqtgraph

---

## 📜 许可证

MIT License