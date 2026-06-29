# 蓝牙上位机软件 — 技术设计文档

> 创建日期：2026-06-30
> 技术栈：Python + PySide6 + Bleak
> 目标平台：Windows 桌面

## 1. 项目概述

一款产品级蓝牙上位机软件，用于与 BLE 设备进行通信、数据采集、实时监控、协议解析及固件升级。支持通用 BLE 设备及自定义协议。

## 2. 整体架构

采用**分层 + 事件驱动**架构，共 4 层：

```
┌─────────────────────────────────────────┐
│           Presentation Layer             │
│  (PySide6 Widgets — 主窗口、设备面板、    │
│   数据表格、实时图表、日志、OTA)           │
├─────────────────────────────────────────┤
│           Application Layer              │
│  (连接管理、数据缓存、协议引擎、导出、OTA)  │
├─────────────────────────────────────────┤
│           BLE Service Layer              │
│  (Bleak 封装 — 扫描、连接、GATT、通知)   │
├─────────────────────────────────────────┤
│           BLE Hardware Layer             │
│  (Windows 蓝牙栈 / Bleak 抽象)           │
└─────────────────────────────────────────┘
```

**数据流向：**

- 下行：UI 事件 → Application 层命令 → BLE Service 层写入特征值
- 上行：BLE 通知 → Service 层 → Application 层解析/缓存 → UI 更新

**设计原则：**

- BLE Service 层运行在 asyncio 事件循环，通过 Qt 信号桥接安全更新 UI
- Application 层持有统一数据总线，UI 组件订阅各自所需数据流
- 协议解析采用策略模式，可热插拔

## 3. BLE Service 层

### 组件

| 组件           | 职责                                               |
| -------------- | -------------------------------------------------- |
| `Scanner`      | 设备扫描，支持过滤条件和 RSSI 排序                 |
| `Connector`    | 多设备连接池管理，断连检测与自动重连               |
| `GATT Service` | 服务发现、特征值读写、Notification/Indication 订阅 |

### 核心接口

```python
class BleSignals(QObject):
    device_found = Signal(object)
    device_connected = Signal(object)
    device_disconnected = Signal(object)
    data_received = Signal(object, bytes)  # (device_address, data)
    scan_finished = Signal()
    error_occurred = Signal(str)
```

### 多设备支持

维护 `dict[address, BleakClient]` 连接池，每个 Client 独立运行在 asyncio Task 中。支持最多 N 个并发连接（N 可配置，默认 5）。

## 4. Application 层

### 组件

| 组件                | 职责                                                           |
| ------------------- | -------------------------------------------------------------- |
| `ConnectionManager` | 连接状态机（已断开/连接中/已连接/断开中），重连策略，连接池    |
| `DataCache`         | 环形缓冲区缓存，每个设备一个数据通道，按时间戳索引，容量可配置 |
| `ProtocolEngine`    | 协议引擎，策略模式，支持内置协议和自定义脚本                   |
| `DataExportService` | 导出到 CSV / Excel / SQLite                                    |
| `OTAService`        | 固件升级（分包-应答-校验），进度回调                           |

### 协议引擎设计

```python
class ProtocolParser(ABC):
    @abstractmethod
    def parse(self, raw_data: bytes) -> ParsedData: ...
    @abstractmethod
    def serialize(self, data: ParsedData) -> bytes: ...

# 内置实现
class RawProtocol(ProtocolParser): ...
class JSONProtocol(ProtocolParser): ...
class ModbusProtocol(ProtocolParser): ...
class CustomScriptProtocol(ProtocolParser): ...  # 加载用户脚本
```

### OTA 流程

1. 读取固件文件 (.bin/.hex)
2. 按 MTU 分包（默认 240 bytes/包）
3. 逐包发送，等待 ACK
4. 超时重传（最多 3 次）
5. 发送完毕校验 CRC/哈希
6. 触发设备重启

## 5. Presentation 层（UI）

### 主窗口布局

PySide6 QMainWindow：

- 菜单栏（文件、视图、工具、帮助）
- 设备面板（左侧，固定宽度）
- 多标签页（右侧，内容区）
- 状态栏（底部）

### 设备面板

- 扫描控制：开始/停止按钮
- 设备列表：设备名称、MAC 地址、RSSI、连接状态
- 操作按钮：连接、断开、查看服务

### 标签页

| 标签页   | 功能                                                       |
| -------- | ---------------------------------------------------------- |
| 数据视图 | 实时数据表格（时间、设备、HEX、ASCII、解析值），筛选和搜索 |
| 图表     | PyQtGraph 实时曲线，多通道叠加，缩放，历史回溯             |
| 日志     | 系统级日志（连接、错误、操作、调试信息）                   |
| 协议配置 | 选择/配置/上传自定义协议解析脚本                           |
| OTA      | 固件选择、升级启动、进度条、日志输出                       |

## 6. 项目结构

```
ble-upper-monitor/
├── src/
│   ├── main.py                    # 应用入口
│   ├── app.py                     # QApplication + 主窗口
│   ├── ble/
│   │   ├── manager.py             # BLE Manager
│   │   ├── scanner.py             # 扫描器
│   │   ├── connector.py           # 连接管理器
│   │   ├── gatt_service.py        # GATT 操作
│   │   └── signals.py             # Qt 信号桥接
│   ├── app_layer/
│   │   ├── connection_manager.py  # 连接状态机
│   │   ├── data_cache.py          # 环形缓冲区
│   │   ├── protocol_engine.py     # 协议引擎
│   │   ├── protocols/
│   │   │   ├── base.py            # 抽象基类
│   │   │   ├── raw.py             # 原始 HEX
│   │   │   ├── json_proto.py      # JSON
│   │   │   └── modbus.py          # Modbus RTU
│   │   ├── export_service.py      # 导出服务
│   │   └── ota_service.py         # OTA 升级
│   ├── ui/
│   │   ├── main_window.py         # 主窗口
│   │   ├── device_panel.py        # 设备面板
│   │   ├── tabs/
│   │   │   ├── data_tab.py
│   │   │   ├── chart_tab.py
│   │   │   ├── log_tab.py
│   │   │   ├── protocol_tab.py
│   │   │   └── ota_tab.py
│   │   └── widgets/
│   │       ├── device_list.py
│   │       ├── hex_view.py
│   │       └── realtime_chart.py
│   └── utils/
│       ├── logger.py              # 日志系统
│       └── helpers.py
├── docs/specs/
├── tests/
├── resources/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 7. 测试策略

| 层级     | 工具                | 覆盖范围                                          |
| -------- | ------------------- | ------------------------------------------------- |
| 单元测试 | pytest              | BLE 抽象层 (mock)、协议解析器、导出逻辑、数据缓存 |
| 集成测试 | pytest + bleak 模拟 | 扫描/连接/读写流程                                |
| UI 测试  | pytest-qt           | 组件渲染、交互逻辑                                |
| 硬件测试 | 真实 BLE 设备       | 端到端验证                                        |

## 8. 打包部署

- 打包工具：PyInstaller（优先）或 Nuitka（备选）
- 安装包制作：Inno Setup
- 依赖管理：pyproject.toml + requirements.txt
- 分发：单文件安装包

## 9. 依赖清单

```
PySide6>=6.6
bleak>=0.21
pyqtgraph>=0.13
pandas>=2.0
openpyxl>=3.1
numpy>=1.24
pyserial>=3.5       # 串口备用通信
```

## 10. 可选扩展（后续迭代）

- **串口通信支持** — 兼容传统蓝牙串口模块（HC-08/HM-10）
- **插件系统** — 第三方开发者可编写独立解析插件
- **远程监控** — WebSocket 推送到云端或 Web 端
- **脚本自动化** — 支持 Python 脚本自动化测试流程
