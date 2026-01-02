# WeData Pre-Code Library

WeData平台的预执行代码库，为机器学习实验提供与MLflow的深度集成和WeData平台的功能增强。

## 项目概述

本项目提供了两个版本的WeData客户端，用于在WeData平台上运行机器学习实验时提供以下功能：

- **MLflow集成增强**：自动注入WeData平台特定的标签和过滤条件
- **权限控制**：基于项目/工作空间的权限验证机制
- **URL生成**：自动生成实验和运行的查看链接
- **环境配置**：自动设置运行环境变量

## 版本说明

### Wedata2PreCodeClient (WeData 2.0版本)

适用于WeData 2.0平台的客户端，主要特性：

- 基于项目ID进行权限控制
- 支持国内站和国际站URL模板
- 自动注入项目标签和机器学习类型标签
- 提供完整的MLflow客户端装饰器

### Wedata3PreCodeClient (WeData 3.0版本)

适用于WeData 3.0平台的客户端，主要特性：

- 基于工作空间ID进行权限控制
- 支持更灵活的配置选项
- 增强的标签注入和验证机制
- 支持机器学习和深度学习两种实验类型

## 安装和使用

### 安装依赖

```bash
pip install mlflow
```

### 使用Wedata2PreCodeClient

```python
from wedata_pre_code.wedata2.client import Wedata2PreCodeClient

# 初始化客户端
client = Wedata2PreCodeClient(
    wedata_project_id="{{WEDATA_PROJECT_ID}}",
    wedata_notebook_engine="{{WEDATA_NOTEBOOK_ENGINE}}",
    qcloud_uin="{{QCLOUD_UIN}}",
    qcloud_subuin="{{QCLOUD_SUBUIN}}",
    wedata_default_feature_store_database="{{WEDATA_DEFAULT_FEATURE_STORE_DATABASE}}",
    wedata_feature_store_databases="{{WEDATA_FEATURE_STORE_DATABASES}}",
    qcloud_region="{{QCLOUD_REGION}}",
    mlflow_tracking_uri="{{KERNEL_MLFLOW_TRACKING_URI}}",
    feast_remote_address="{{KERNEL_FEAST_REMOTE_ADDRESS}}",
    kernel_submit_form_workflow="{{KERNEL_SUBMIT_FORM_WORKFLOW}}",
    kernel_task_name="{{KERNEL_TASK_NAME}}",
    kernel_task_id="{{KERNEL_TASK_ID}}",
    kernel_region="ap-chongqing",
    kernel_is_international=bool("{{KERNEL_IS_INTERNATIONAL}}")
)

# 现在可以使用MLflow客户端，会自动应用WeData的增强功能
import mlflow
mlflow.start_run()
# ... 你的实验代码
```

### 使用Wedata3PreCodeClient

```python
from wedata_pre_code.wedata3.client import Wedata3PreCodeClient

# 初始化客户端
client = Wedata3PreCodeClient(
    workspace_id="{{WorkspaceID}}",
    mlflow_tracking_uri="{{MlflowTrackingUri}}",
    base_url="{{BaseUrl}}",
    region="{{Region}}",
    ap_region_id=int("{{RegionId}}"),
    run_context_data="{{RunContextData}}"
)

# 需要主意run_context_data为 json.dumps格式：
# 类似效果
# '{"mlflow.source.name": "test_task", "mlflow.user": "test_user", "wedata.datascience.type": "MACHINE_LEARNING"}'

# ... 你的实验代码
```

## 功能特性

### 自动标签注入

- 自动为实验、运行和模型注入WeData平台标签
- 包括项目ID、工作空间ID、机器学习类型等信息
- 确保数据在平台上的可追溯性

### 权限验证

- 在执行敏感操作前验证权限
- 防止跨项目/工作空间的未授权操作
- 保护内置标签不被修改

### URL生成

- 自动生成实验和运行的查看URL
- 在运行终止时显示访问链接
- 方便用户快速访问实验结果

### 环境配置

- 自动设置MLflow跟踪URI
- 配置运行上下文环境变量
- 支持国际站和国内站的不同配置

## 项目结构

```
pre-execute/
├── src/
│   └── wedata_pre_code/
│       ├── __init__.py
│       ├── client.py              # 主客户端入口
│       ├── common/
│       │   ├── __init__.py
│       │   └── base_client.py     # 基础客户端类
│       ├── wedata2/
│       │   ├── __init__.py
│       │   └── client.py          # WeData 2.0客户端
│       └── wedata3/
│           ├── __init__.py
│           └── client.py          # WeData 3.0客户端
├── docs/                          # 文档目录
├── pyproject.toml                 # 项目配置
├── requirement.txt                # 依赖文件
└── README.md                     # 项目说明
```

## 开发指南

### 添加新的装饰器

要添加新的MLflow客户端方法装饰器，可以参考现有的实现模式：

1. 在相应的客户端类中定义装饰器函数
2. 使用`@wraps`保留原函数属性
3. 在装饰器内部实现特定的逻辑
4. 将装饰器应用到目标MLflow方法

### 测试

确保在修改代码后测试以下场景：

- 正常创建实验和运行
- 权限验证功能
- 标签注入的正确性
- URL生成的准确性

## 注意事项

- 确保MLflow服务器配置正确
- 验证环境变量设置完整
- 注意不同版本客户端的参数差异
- 在生产环境使用前进行充分测试

## 支持与反馈

如有问题或建议，请联系WeData平台技术支持团队。