"""基础组件类."""

from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from ..logging import LogPublisher, setup_component_logger
from .data import Data
from .io import Input, Output


class Component(ABC):
    """基础组件类.

    所有自定义组件都应继承此类并实现 run() 方法
    """

    # 组件元信息
    name: str = "Component"
    display_name: str = "Component"
    description: str = "Base component"
    documentation: str = ""
    icon: str = "box"

    # 输入输出定义
    inputs: list[Input] = []
    outputs: list[Output] = []

    def __init__(self, **kwargs):
        """初始化组件.

        Args:
            **kwargs: 输入参数，会根据 inputs 定义自动设置

        """
        # 初始化输入值
        for input_def in self.inputs:
            # 优先使用传入的参数，否则使用默认值
            value = kwargs.get(input_def.name, input_def.value)
            setattr(self, input_def.name, value)

        # 状态信息
        self.status: Any = None

        # 从项目配置系统加载日志配置
        from ..logging import get_workflow_context, load_logging_config

        logging_config = load_logging_config()
        workflow_context = get_workflow_context()

        # 初始化 artifact 管理器
        self._artifact_manager = None
        self._workflow_id = workflow_context.get("workflow_id")
        self._node_id = kwargs.get("_node_id")  # 从内部参数获取节点ID

        # 初始化日志发布器（仅在配置启用时）
        if logging_config.get("enabled"):
            self._log_publisher: LogPublisher | None = setup_component_logger(
                rabbitmq_host=logging_config.get("rabbitmq_host"),
                rabbitmq_port=logging_config.get("rabbitmq_port", 5672),
                rabbitmq_user=logging_config.get("rabbitmq_user", "guest"),
                rabbitmq_password=logging_config.get("rabbitmq_password", "guest"),
                user_id=workflow_context.get("user_id"),
                workflow_id=workflow_context.get("workflow_id"),
                enable_local_log=logging_config.get("enable_local_log", True),
            )
        else:
            self._log_publisher = None

    @abstractmethod
    def run(self) -> Data:
        """执行组件核心逻辑.

        这是抽象方法，子类必须实现此方法。

        Returns:
            Data: 组件执行结果

        Raises:
            NotImplementedError: 子类未实现此方法时抛出

        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement run() method")

    def execute(self, **kwargs) -> Data:
        """执行组件（框架方法）.

        这是框架提供的完整执行流程：
        1. 前置：更新输入值、验证输入
        2. 中间：调用 run() 执行业务逻辑
        3. 后置：验证输出、设置状态

        Args:
            **kwargs: 输入参数

        Returns:
            Data: 执行结果

        Raises:
            ValueError: 输入验证失败
            NotImplementedError: 未定义输出或未实现 run() 方法

        """
        try:
            self.log("INFO", f"组件 {self.name} 开始执行")

            # 1. 前置处理：更新输入值
            for key, value in kwargs.items():
                # 跳过以 _ 开头的内部参数
                if not key.startswith("_"):
                    self.set_input_value(key, value)

            # 2. 验证输入
            self._validate_inputs()
            self.log("DEBUG", "输入验证通过")

            # 3. 检查输出定义
            if not self.outputs:
                raise NotImplementedError("Component must define at least one output")

            # 4. 执行核心业务逻辑
            self.log("INFO", "开始执行组件业务逻辑")
            result = self.run()

            # 5. 后置处理：验证输出
            self._validate_output(result)
            self.log("DEBUG", "输出验证通过")

            # 6. 设置状态
            self.status = result

            self.log("INFO", f"组件 {self.name} 执行成功")
            return result

        except Exception as e:
            self.log("ERROR", f"组件 {self.name} 执行失败: {e}", error=str(e), error_type=type(e).__name__)
            raise

    def _validate_inputs(self) -> None:
        """验证输入参数.

        Raises:
            ValueError: 必填参数缺失或类型错误

        """
        for input_def in self.inputs:
            if input_def.required:
                value = getattr(self, input_def.name, None)
                if value is None:
                    raise ValueError(f"Required input '{input_def.name}' is missing")

    def _validate_output(self, result: Data) -> None:
        """验证输出结果.

        Args:
            result: 输出结果

        Raises:
            ValueError: 输出验证失败

        """
        if not isinstance(result, Data):
            raise ValueError(f"run() must return a Data object, got {type(result)}")

    def get_input_value(self, name: str) -> Any:
        """获取输入值.

        Args:
            name: 输入名称

        Returns:
            输入值

        """
        return getattr(self, name, None)

    def set_input_value(self, name: str, value: Any) -> None:
        """设置输入值.

        Args:
            name: 输入名称
            value: 输入值

        """
        setattr(self, name, value)

    def get_inputs_dict(self) -> dict[str, Any]:
        """获取所有输入值的字典.

        Returns:
            输入值字典

        """
        return {input_def.name: getattr(self, input_def.name) for input_def in self.inputs}

    def to_dict(self) -> dict[str, Any]:
        """转换为字典.

        Returns:
            组件信息字典

        """
        return {
            "display_name": self.display_name,
            "description": self.description,
            "documentation": self.documentation,
            "icon": self.icon,
            "name": self.name,
            "inputs": [input_def.model_dump() for input_def in self.inputs],
            "outputs": [output_def.model_dump() for output_def in self.outputs],
        }

    def to_lfx_format(self) -> dict[str, Any]:
        """转换为 LFX 格式.

        用于导出到 langflow 平台

        Returns:
            LFX 格式的组件定义

        """
        from .types import LFX_INPUT_MAPPING, LFX_OUTPUT_MAPPING

        return {
            "display_name": self.display_name,
            "description": self.description,
            "documentation": self.documentation,
            "icon": self.icon,
            "name": self.name,
            "inputs": [
                {
                    "name": input_def.name,
                    "display_name": input_def.display_name,
                    "type": LFX_INPUT_MAPPING.get(input_def.type, input_def.type),
                    "value": input_def.value,
                    "info": input_def.description,
                    "required": input_def.required,
                    "tool_mode": input_def.tool_mode,
                    "options": input_def.options,
                }
                for input_def in self.inputs
            ],
            "outputs": [
                {
                    "name": output_def.name,
                    "display_name": output_def.display_name,
                    "type": LFX_OUTPUT_MAPPING.get(output_def.type, output_def.type),
                    "description": output_def.description,
                }
                for output_def in self.outputs
            ],
        }

    def get_artifact_manager(self):
        """获取 artifact 管理器.

        Returns:
            ArtifactManager 实例
        """
        if self._artifact_manager is None:
            from ..artifact import ArtifactManager, FileSystemStorage
            from ..config_cache import get_output_path
            from pathlib import Path

            # 从缓存获取 artifact 存储路径
            storage_path = get_output_path()

            # 如果没有从平台获取到路径,使用默认路径
            if not storage_path:
                storage_path = Path("./artifacts") / (self._workflow_id or "default")
                self.log("WARNING", "未从平台获取到 output_path 配置,使用默认路径")
            else:
                storage_path = Path(storage_path) / (self._workflow_id or "default")

            storage = FileSystemStorage(storage_path)

            self._artifact_manager = ArtifactManager(
                storage=storage,
                workflow_id=self._workflow_id,
                node_id=self._node_id,
            )

        return self._artifact_manager

    def save_artifact_dataframe(self, df: Any, name: str, format: str = "parquet", **kwargs):
        """保存 DataFrame 成果物.

        Args:
            df: DataFrame 对象
            name: 成果物名称
            format: 保存格式 (parquet, csv, arrow)
            **kwargs: 额外参数

        Returns:
            ArtifactInfo 对象
        """
        manager = self.get_artifact_manager()
        return manager.save_dataframe(df, name, format, **kwargs)

    def save_artifact_file(self, file_path: str, name: str | None = None):
        """保存文件成果物.

        Args:
            file_path: 文件路径
            name: 成果物名称

        Returns:
            ArtifactInfo 对象
        """
        manager = self.get_artifact_manager()
        return manager.save_file(file_path, name)

    def save_artifact_json(self, data: Any, name: str):
        """保存 JSON 成果物.

        Args:
            data: 要保存的数据
            name: 成果物名称

        Returns:
            ArtifactInfo 对象
        """
        manager = self.get_artifact_manager()
        return manager.save_json(data, name)

    def export_artifact_manifest(self, output_path: str | None = None) -> dict[str, Any]:
        """导出成果物清单.

        Args:
            output_path: 输出路径

        Returns:
            清单字典
        """
        manager = self.get_artifact_manager()
        return manager.export_manifest(output_path)

    def output_artifact_result(self, result_json_path: str = "./result.json") -> dict[str, Any]:
        """输出成果物结果到 stdout.

        生成简化的结果格式(只包含 4 个核心字段),并输出到 stdout。
        详细的成果物信息保存在 result.json 文件中。

        Args:
            result_json_path: result.json 文件路径

        Returns:
            简化的结果字典
        """
        from pathlib import Path
        import json

        # 导出完整清单到 result.json
        manifest_dict = self.export_artifact_manifest(result_json_path)

        # 获取 result.json 的 URI
        result_path = Path(result_json_path).resolve()
        result_uri = result_path.as_uri()

        # 生成简化结果
        manager = self.get_artifact_manager()
        simple_result = manager.manifest.to_simple_result(result_uri)

        # 输出到 stdout
        print(json.dumps(simple_result, ensure_ascii=False))

        self.log("INFO", f"成果物结果已输出: {len(manifest_dict.get('outputs', []))} 个输出")
        return simple_result

    def submit_artifacts_to_platform(self) -> dict[str, Any]:
        """
        这个暂时不用，我们通过std_out的方式把json返回
        提交成果物清单到平台.


        Returns:
            提交结果
        """
        from ..platform_client import PlatformClient
        from ..project_settings import get_platform_settings
        import os

        # 获取平台配置
        platform_settings = get_platform_settings()
        platform_url = platform_settings.get("url") or os.getenv("SDWK_PLATFORM_URL")
        platform_token = os.getenv("SDWK_PLATFORM_TOKEN")

        if not platform_url:
            raise ValueError("Platform URL not configured")

        # 导出清单
        manifest = self.export_artifact_manifest()

        # 提交到平台
        with PlatformClient(platform_url, platform_token) as client:
            result = client.submit_artifact_manifest(manifest)
            self.log("INFO", f"成果物清单已提交到平台: {len(manifest.get('outputs', []))} 个输出")
            return result

    def log(self, level: str, message: str, **extra: Any) -> None:
        """记录日志.

        日志会同时输出到本地（loguru）和 RabbitMQ（如果已配置）

        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: 日志消息
            **extra: 额外的日志字段

        """
        # 输出到本地日志
        logger.log(level.upper(), message)

        # 发送到 RabbitMQ
        if self._log_publisher:
            self._log_publisher.publish(level, message, component=self.name, **extra)

    def close(self) -> None:
        """关闭组件资源.

        关闭 RabbitMQ 日志发布器连接。
        """
        if self._log_publisher:
            self._log_publisher.close()
            self._log_publisher = None

    def __del__(self):
        """析构函数，确保资源被释放."""
        try:
            self.close()
        except Exception:
            pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
