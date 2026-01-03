from __future__ import annotations

from enum import Enum, auto

from typing import TYPE_CHECKING, Literal
import logging

if TYPE_CHECKING:
    from kele.syntax import FACT_TYPE, Question
    from kele.equality import Equivalence
    from collections.abc import Sequence, Mapping
    from kele.syntax import Variable, Rule, CompoundTerm, Constant, _QuestionRule
    from kele.syntax import SankuManagementSystem

logger = logging.getLogger(__name__)


class InferenceStatus(Enum):
    """推理过程的终止状态类型"""

    SUCCESS = auto()  # 成功推理出答案
    MAX_STEPS_REACHED = auto()  # 达到最大执行轮次限制
    MAX_ITERATIONS_REACHED = auto()  # 达到最大迭代次数限制（从main循环）
    FIXPOINT_REACHED = auto()  # 达到不动点
    CONFLICT_DETECTED = auto()  # 推理中发现矛盾
    EXTERNALLY_INTERRUPTED = auto()  # 被外部中断（如人为终止）
    NO_MORE_RULES = auto()  # 没有更多实例化规则可以推理
    CONTINUE = auto()  # 当前轮未结束，继续执行

    def log_message(self) -> str:
        """每个状态对应的日志输出信息"""
        return {
            InferenceStatus.SUCCESS: "Successfully inferred the answer.",
            InferenceStatus.MAX_STEPS_REACHED: "Max execution steps reached, terminating.",
            InferenceStatus.MAX_ITERATIONS_REACHED: "Max inference iterations reached, terminating.",
            InferenceStatus.FIXPOINT_REACHED: "Fixpoint reached, terminating.",
            InferenceStatus.CONFLICT_DETECTED: "Conflict detected during execution.",
            InferenceStatus.EXTERNALLY_INTERRUPTED: "Execution was externally interrupted.",
            InferenceStatus.NO_MORE_RULES: "No more grounded rules available for execution.",
            InferenceStatus.CONTINUE: "Execution continues to next round."
        }[self]

    def is_terminal_for_executor(self) -> bool:
        """判断执行器是否应该终止"""
        return self != InferenceStatus.CONTINUE

    def is_terminal_for_main_loop(self) -> bool:
        """判断主循环是否应该终止"""
        return self in {
            InferenceStatus.SUCCESS,
            InferenceStatus.MAX_STEPS_REACHED,
            InferenceStatus.MAX_ITERATIONS_REACHED,
            InferenceStatus.FIXPOINT_REACHED,
            InferenceStatus.EXTERNALLY_INTERRUPTED
        }


class QuerySolutionManager:
    """查询解管理器：负责打印、收集和管理查询解"""

    def __init__(self, interactive_query_mode: Literal["interactive", "first", "all"] = "first",
                 *, store_solutions: bool = False) -> None:
        self.collected_solutions: list[Mapping[Variable, Constant | CompoundTerm]] = []
        self.interactive_query_mode = interactive_query_mode
        self.store_solutions = store_solutions
        self._solution_count: int = 0

    def reset(self) -> None:
        """清空已收集的解和计数"""
        self.collected_solutions.clear()
        self._solution_count = 0

    def print_and_collect(
        self,
        question: Question,
        solutions: list[Mapping[Variable, Constant | CompoundTerm]],
        question_rule: _QuestionRule
    ) -> bool:
        """
        打印并收集解
        :return: 是否应该终止推理
        """
        question_str = ", ".join(str(q) for q in question.question)

        for combination in solutions:
            self._solution_count += 1

            if combination:
                binding_str = self._display_binding(combination)
                logger.info("Query solution: %s variable bindings: %s", question_str, binding_str)
                if self.store_solutions:
                    self.collected_solutions.append(combination)
            else:
                logger.info("Query solution: %s", question_str)
                if self.store_solutions:
                    self.collected_solutions.append(combination)
                if not question_rule.free_variables:
                    return True

            # 根据模式决定是否终止
            if self._should_terminate(self.interactive_query_mode):
                return True

        return False  # 继续推理

    @staticmethod
    def _display_binding(combination: Mapping[Variable, Constant | CompoundTerm]) -> str:
        """ 将内部变量名还原为查询中的原始变量名"""
        entries: list[str] = []
        for var, term in combination.items():
            entries.append(f"{var.display_name}={term}")
        return ", ".join(entries)

    @staticmethod
    def _should_terminate(mode: Literal["interactive", "first", "all"]) -> bool:
        """根据交互模式决定是否应该终止推理"""
        if mode == "first":
            logger.info("Configured to output only the first query solution; stopping inference.")
            return True

        if mode == "all":
            return False

        user_input = input("发现解，输入 ';' 并回车继续本次推理；输入其他任意键并回车将终止本次推理: ").strip()  # TODO: input不太适合后续扩展
        if user_input != ';':
            logger.info("用户选择终止推理。")
            return True
        return False

    def get_all_solutions(self) -> list[Mapping[Variable, Constant | CompoundTerm]]:
        """返回所有已收集的解映射（如果 store_solutions=False，返回空列表）"""
        return self.collected_solutions

    def get_solution_count(self) -> int:
        """返回找到的解数量"""
        return self._solution_count


class StatusChecker:
    """通用状态检查逻辑"""

    def __init__(self, equivalence: Equivalence, sk_system_handler: SankuManagementSystem):
        self.equivalence = equivalence
        self.sk_system_handler = sk_system_handler

    def check_conflict(self, new_facts: list[FACT_TYPE]) -> bool:
        """检查是否发生了矛盾。!!! 注意这里传入的是new_facts"""
        return self._has_conflict_occurred(new_facts)

    @staticmethod
    def _has_conflict_occurred(new_facts: list[FACT_TYPE]) -> bool:
        """检查是否发生了矛盾"""
        # TODO: 实现矛盾检测逻辑
        return False


class MainLoopManager:
    """主循环管理器"""

    def __init__(self, status_checker: StatusChecker, max_iterations: int = 300):
        self.status_checker = status_checker
        self.max_iterations = max_iterations
        self._current_iteration = 0

        self.normal_rule_activated: dict[Rule, bool] = {}  # 如果某条rule上一轮有新事实生成，则True；反之False
        self._true_count = -1

    def check_status(self,
                     current_facts: list[FACT_TYPE],
                     question: Question) -> InferenceStatus:
        """检查主循环状态"""
        # 先检查迭代次数
        if self._current_iteration >= self.max_iterations:
            return InferenceStatus.MAX_ITERATIONS_REACHED

        if self._true_count == 0:
            return InferenceStatus.FIXPOINT_REACHED

        if self._current_iteration == 0 and question.question and all(q in current_facts for q in question.question):
            # FIXME: 这里的判断可能需要分的更细致
            return InferenceStatus.SUCCESS

        return InferenceStatus.CONTINUE

    def next_iteration(self) -> None:
        """进入下一轮迭代"""
        self._current_iteration += 1

    def reset(self) -> None:
        """重置计数"""
        self._current_iteration = 0

    def initial_manager(self, normal_rules: Sequence[Rule] | None = None, *, resume: bool = False) -> None:
        """
        修改current rules, 为当前一个question的推理做准备
        :raise ValueError: 如果待推理问题不变，仅中止引擎并重新推理时，认为不需要修改rules（其他各处也应调整）
        """  # noqa: DOC501
        if normal_rules is None:
            if resume:
                self.normal_rule_activated = dict.fromkeys(self.normal_rule_activated, True)  # 继续推理当前时，使用之前存储好的rule
                # 但是清空之前的_activated记录（因为可能有新事实变化）
            else:
                raise ValueError("normal_rules is None")
        else:
            self.normal_rule_activated = dict.fromkeys(normal_rules, True)  # 如果某条rule上一轮有新事实生成，则True；反之False
        self._true_count = len(self.normal_rule_activated)

    @property
    def iteration(self) -> int:
        """获取当前迭代次数"""
        return self._current_iteration

    def update_normal_rule_activation(self, new_facts: list[FACT_TYPE], used_rule: Rule) -> None:
        """每条规则完成推理后，使用本函数更新main_manager，用于判断是否所有的规则同时达到了不动点"""
        activated = bool(new_facts)

        old_value = self.normal_rule_activated.get(used_rule)
        self.normal_rule_activated[used_rule] = activated

        if old_value and not activated:
            self._true_count -= 1
        elif not old_value and activated:
            self._true_count += 1

    def is_at_fixpoint(self) -> bool:
        """是否所有 normal rule 都已不再产生新事实（不动点，仅看 normal rules）"""
        return self._true_count == 0


class ExecutorManager:
    """执行器管理器"""

    def __init__(self, status_checker: StatusChecker, solution_manager: QuerySolutionManager,
                  max_steps: int = 1000):
        self.status_checker = status_checker
        self.max_steps = max_steps
        self._current_step = 1
        self.solution_manager = solution_manager

    def check_status(self, new_facts: list[FACT_TYPE], question: Question,
                     solutions: list[Mapping[Variable, Constant | CompoundTerm]],
                     question_rule: _QuestionRule | None) -> InferenceStatus:
        """检查执行器状态"""
        if self.max_steps != -1 and self._current_step >= self.max_steps:
            return InferenceStatus.MAX_STEPS_REACHED  # 有解是success，且需要解

        # 检查是否有矛盾
        if self.status_checker.check_conflict(new_facts):  # TODO: 冲突时同步清理 solutions
            return InferenceStatus.CONFLICT_DETECTED

        if question_rule is not None and solutions:
            terminate_sign = self.solution_manager.print_and_collect(question, solutions, question_rule)
            if terminate_sign:
                return InferenceStatus.SUCCESS

        return InferenceStatus.CONTINUE

    def next_step(self) -> None:
        """执行下一步"""
        self._current_step += 1

    def reset_for_new_inference(self) -> None:
        """为新的推理过程重置步数计数（仅在开始全新推理时调用）"""
        self._current_step = 1

    @property
    def step_num(self) -> int:
        """获取当前步数"""
        return self._current_step


def create_main_loop_manager(equivalence: Equivalence,
                             sk_system_handler: SankuManagementSystem,
                             max_iterations: int = 300) -> MainLoopManager:
    """创建主循环管理器"""
    status_checker = StatusChecker(equivalence, sk_system_handler)
    return MainLoopManager(status_checker, max_iterations)


def create_executor_manager(equivalence: Equivalence,
                            sk_system_handler: SankuManagementSystem,
                            solution_manager: QuerySolutionManager,
                            max_steps: int = 1000) -> ExecutorManager:
    """创建执行器管理器"""
    status_checker = StatusChecker(equivalence, sk_system_handler)
    return ExecutorManager(status_checker, solution_manager, max_steps)
