# mypy: ignore-errors
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """用于修改pip包tag的hook"""
    def initialize(self, version, build_data) -> None:  # noqa: ANN001, PLR6301
        """修改pip包tag"""
        # 让 Hatch 用“最具体”的 wheel tag（cp313-cp313-win32 / manylinux / macosx...）
        # 注意：只有在你没有手动设置 build_data["tag"] 时才会生效
        build_data["infer_tag"] = True

        # 明确声明不是纯 Python 包（影响 wheel 元数据 / 纯包判断）
        build_data["pure_python"] = False
