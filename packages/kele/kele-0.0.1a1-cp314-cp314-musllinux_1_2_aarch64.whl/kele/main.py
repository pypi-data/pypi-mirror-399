import logging
from collections.abc import Sequence
from typing import Literal, Any, ClassVar
from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict

from kele.syntax import Assertion, _QuestionRule
from kele.config import init_config_logger, Config
from kele.control.grounding_selector import GroundingFlatTermWithWildCardSelector
from kele.control.status import InferenceStatus, QuerySolutionManager
from kele.executer import Executor
from kele.grounder import Grounder, GroundedRule, GroundedRuleDS
from kele.knowledge_bases import FactBase, RuleBase, load_ontologies
from kele.control.metrics import PhaseTimer, observe_counts, init_metrics, \
    measure, end_run, start_run, inc_iter
from kele.syntax import FACT_TYPE, Rule, SankuManagementSystem, Question, Constant, CompoundTerm, Variable
from kele.equality import Equivalence
from kele.control import create_main_loop_manager, GroundingRuleSelector, InferencePath
from kele.control.infer_path import FactStep

logger = logging.getLogger(__name__)


class QueryStructure(BaseModel):
    """Query structure used as input when calling the inference engine."""
    premises: Sequence[Assertion]
    question: Sequence[FACT_TYPE]

    model_config: ClassVar = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class EngineRunResult(BaseModel):
    """Return structure from the inference engine."""
    model_config: ClassVar = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    status: InferenceStatus
    final_facts: list[FACT_TYPE]
    fact_num: int
    include_final_facts: bool
    question: Question
    iterations: int
    execute_steps: int
    terminated_by: Literal["initial_check", "executor", "main_loop", "unknown"]
    solution_count: int  # Number of solutions found

    # Detailed solution bindings (empty list if save_solutions=False in config)
    solutions: list[Mapping[Variable, Constant | CompoundTerm]]

    @property
    def has_solution(self) -> bool:
        """Return whether any solution exists."""
        return self.solution_count > 0

    @property
    def is_success(self) -> bool | None:  # None means unknown/undetermined
        """
        - SUCCESS  -> 成功
        - FIXPOINT_REACHED 且有解 -> 成功
        - MAX_* / EXTERNALLY_INTERRUPTED 且有解 -> 只能算部分成功
        """
        if self.status == InferenceStatus.SUCCESS:
            return True

        if self.status == InferenceStatus.FIXPOINT_REACHED:
            return self.has_solution

        return False

    @property
    def is_partial_success(self) -> bool | None:  # None means unknown/undetermined
        """
        Has solutions, but stopped early due to resource limits or external interruption.
        There may be more solutions; no solutions does not imply failure.
        """
        return self.has_solution and self.status in {
                InferenceStatus.MAX_STEPS_REACHED,
                InferenceStatus.MAX_ITERATIONS_REACHED,
                InferenceStatus.EXTERNALLY_INTERRUPTED,
            }

    def log_message(self) -> str:
        """Build a log-friendly message."""
        msg = (f"Inference finished.\n"
               f"status={self.status}, success={self.is_success}, partial_success=={self.is_partial_success}, "
               f"terminated_by={self.terminated_by}, iterations={self.iterations}, facts_num={self.fact_num}, "
               f"has_solution={self.has_solution}, solution_count={self.solution_count}")

        # Show detailed solutions if stored
        if self.solutions:
            for i, sol in enumerate(self.solutions):
                msg += f"\n  Solution {i + 1}: " + ", ".join(f"{var.display_name}={val}" for var, val in sol.items())

        return msg

    def to_dict(self, *, include_final_facts: bool | None = None) -> dict[str, Any]:
        """Serialize the result (solutions may be empty if save_solutions=False)."""
        if include_final_facts is None:
            include_final_facts = self.include_final_facts
        if include_final_facts:
            return self.model_dump()
        return self.model_dump(exclude={"final_facts"})


class InferenceEngine:
    """Inference engine main program that wraps grounding + executing."""

    def __init__(self,  # noqa: PLR0913
                 facts: Sequence[FACT_TYPE] | str | None,
                 rules: Sequence[Rule] | str | None,
                 *,
                 concept_dir_or_path: str = 'knowledge_bases/builtin_base/builtin_concepts.py',
                 operator_dir_or_path: str = 'knowledge_bases/builtin_base/builtin_operators.py',
                 user_config: Config | None = None,
                 config_file_path: str | None = None,  # TODO: Consider moving custom log file into Config.
                 ) -> None:
        """
        Initialize the inference engine with initial facts and rules.
        If facts and rules are None, use the default initial facts and rules.
        """
        self.args = init_config_logger(user_config, config_file_path)

        def _get_source_info(obj: Sequence[FACT_TYPE] | Sequence[Rule] | str | None, name: str) -> str:
            if isinstance(obj, str):  # Note that str is also a Sequence.
                return f"{name} from file: {obj}"
            if isinstance(obj, Sequence):
                return f"{name} from list, length={len(obj)}"
            if obj is None:
                return f"{name} is None"

            raise TypeError(f"Unsupported type for obj: {type(obj).__name__}")

        logger.info("Initializing inference engine: Load %s; Load %s",
                    _get_source_info(facts, "facts"),
                    _get_source_info(rules, "rules"))

        self.equivalence = Equivalence(args=self.args)
        sk_system_handler = SankuManagementSystem()
        # TODO: Knowledge base declarations may require db_url from args; not implemented yet.

        facts = self.args.path.fact_dir if facts is None else facts
        rules = self.args.path.rule_dir if rules is None else rules

        try:
            load_ontologies(concept_dir_or_path=concept_dir_or_path,
                            operator_dir_or_path=operator_dir_or_path)

            # selector
            self.rule_selector = GroundingRuleSelector(strategy=self.args.strategy.grounding_rule_strategy,
                                                       question_rule_interval=self.args.strategy.question_rule_interval)

            self.term_selector = GroundingFlatTermWithWildCardSelector(equivalence=self.equivalence,
                                                                       args=self.args)

            # knowledge base
            self.fact_base = FactBase(initial_facts_or_dir_or_path=facts,
                                      equivalence_handler=self.equivalence,
                                      term_selector=self.term_selector,
                                      sk_system_handler=sk_system_handler,
                                      args=self.args.engineering)
            # only one global fact_base is maintained.

            self.rule_base = RuleBase(rules, args=self.args.engineering)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Fact base created with %s facts", len(self.fact_base.facts))

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Rule base created with %s rules", len(self.rule_base.rules))
            logger.info("Inference engine created successfully.")

        except Exception:
            logger.exception("Initialization failed: ontologies_path=(concept=%s, operator=%s)\n(facts=%s, rules=%s)",
                             concept_dir_or_path,
                             operator_dir_or_path,
                             facts[:2] if facts else None,
                             rules[:2] if rules else None)
            raise

        # Create the solution manager.
        self.solution_manager = QuerySolutionManager(
            interactive_query_mode=self.args.run.interactive_query_mode,
            store_solutions=self.args.run.save_solutions
        )

        # Create the main loop manager.
        self.main_loop_manager = create_main_loop_manager(
            self.equivalence,
            sk_system_handler,
            max_iterations=self.args.run.iteration_limit
        )

        # Create inference path dealer
        self.inference_path = InferencePath(self.args.run, self.equivalence)

        # Create the Grounder.
        grounded_structure = GroundedRuleDS(equivalence=self.equivalence, sk_system_handler=sk_system_handler,
                                            args=self.args, inference_path=self.inference_path)
        # FIXME: Extract DS into a standalone component.
        self.grounder = Grounder(fact_base=self.fact_base,
                                 rule_base=self.rule_base,
                                 rule_selector=self.rule_selector,
                                 term_selector=self.term_selector,
                                 grounded_structure=grounded_structure,
                                 rules_num_every_step=self.args.grounder.grounding_rules_num_every_step,  # TODO: Can
                                 # wrap these into args as a grounder config type; keep separate to avoid conflicts.
                                 facts_num_for_each_rule=self.args.grounder.grounding_facts_num_for_each_rule)

        self.executor = Executor(equivalence=self.equivalence,
                                 sk_system_handler=sk_system_handler,
                                 fact_base=self.fact_base,
                                 main_loop_manager=self.main_loop_manager,
                                 solution_manager=self.solution_manager,
                                 inference_path=self.inference_path,
                                 select_num=self.args.executor.executing_rule_num,
                                 max_steps=self.args.executor.executing_max_steps)

        # Track whether the engine has completed at least one inference run.
        self._has_previous_run: bool = False

        # Initialize metrics monitoring.
        init_metrics(job="al_inference", grouping={"env": "dev"})

    def _infer(self, question: Question) -> EngineRunResult:
        """Run a full forward-chaining inference cycle."""
        mod = __name__
        # Initial snapshot.
        observe_counts(facts_count=len(self.fact_base.get_facts()))

        logger.info("InferenceEngine: Starting full inference...")

        # Check whether the question can be answered before the loop starts.
        initial_status, result = self._check_initial_status(question)
        if initial_status is not None and result is not None:
            return result

        final_status: InferenceStatus | None = None
        terminated_by: Literal['initial_check', 'executor', 'main_loop', 'unknown']

        while True:
            logger.info("Inference iteration %s...", self.main_loop_manager.iteration)

            # Grounding process produce instantiated rules (based on current facts)
            with PhaseTimer("grounding", module=mod):
                grounded_rules: Sequence[GroundedRule] = self.grounder.grounding_process(question=question)
            observe_counts(grounded_rules=len(grounded_rules), facts_count=len(grounded_rules))

            selection_only_question_rules = self.grounder.selected_only_question_rules()
            if not grounded_rules:
                if not selection_only_question_rules:
                    inc_iter(mod)
                logger.info("Inference iteration %s: No new groundings found.", self.main_loop_manager.iteration)
                continue
            if not selection_only_question_rules:
                inc_iter(mod)

            with PhaseTimer("execute", module=mod):
                exec_status = self.executor.execute(grounded_rules=grounded_rules, question=question)

            if exec_status.is_terminal_for_main_loop():
                logger.result("Inference terminated due to executor: %s", exec_status.log_message())  # type: ignore[attr-defined]
                terminated_by = "executor"
                final_status = exec_status

                logger.info("Executing: %i rules", len(grounded_rules))  # Placeholder: may be grounding/executing.
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Executing rules: %s", [str(r.rule) for r in grounded_rules])

                break

            with PhaseTimer("main_check", module=mod):  # Unified check for all termination conditions.
                main_status = self.main_loop_manager.check_status([], question)
            # main checks facts before the loop, executor checks new facts, so pass an empty fact list here.

            if main_status.is_terminal_for_main_loop():
                logger.result("Main loop terminating: %s", main_status.log_message())  # type: ignore[attr-defined]
                terminated_by = "main_loop"
                final_status = main_status
                self._handle_fixpoint(final_status=final_status, question=question)
                break

            # Move to the next iteration.
            if not selection_only_question_rules:
                self.main_loop_manager.next_iteration()

        facts = self.fact_base.get_facts()
        observe_counts(facts_count=len(facts))
        logger.result("Total facts when terminal: %s", len(facts))  # type: ignore[attr-defined]

        solution_count = self.solution_manager.get_solution_count()
        all_solutions = self.solution_manager.get_all_solutions()

        include_final_facts = self.args.run.include_final_facts
        final_facts = facts if include_final_facts else []
        return EngineRunResult(
            status=final_status,
            solution_count=solution_count,
            solutions=all_solutions,
            final_facts=final_facts,
            fact_num=len(facts),
            include_final_facts=include_final_facts,
            question=question,
            iterations=self.main_loop_manager.iteration,
            execute_steps=self.executor.executor_manager.step_num,
            terminated_by=terminated_by,
        )

    @measure("infer_query", module="inference")
    def infer_query(self, query: QueryStructure, *, resume: bool = False) -> EngineRunResult:  # TODO: Between runs,
        # EngineRunResult is still returned per call; last result can be treated as authoritative.
        """
        Public interface for the inference engine: accept QueryStructure and return results.
        :param resume: Set True to continue a previous run after injecting new facts externally.
            HACK: logs are split into two files, so timing stats will be inaccurate.
        :raise: ValueError: The first call must have resume=False.
            If resume=True is used before any inference run, ValueError is raised.
        """  # noqa: DOC501
        start_run(log_dir="metrics_logs")  # Start a new metrics record per outer call.

        try:
            if not resume:
                self._reset()
            elif not self._has_previous_run:
                # Attempting resume without any prior run is invalid.
                raise ValueError(
                    "Invalid use of `resume=True` when"
                    "no previous inference run is available to continue from. "
                    "Please set resume=False when calling infer_query(...) first."
                )

            self._has_previous_run = True  # At least one inference run completed.

            premises = query.premises
            question = Question(premises=premises, question=query.question)  # TODO: Consider internal-only Question
            # and avoid storing premises to reduce duplication with QueryStructure.

            if not resume:  # Redundant check, but keeps the flow clearer.
                self._initial_engine(question=question, premises=premises)
            else:
                self.fact_base.add_facts(premises, check_free_variables=True)
                self.main_loop_manager.initial_manager(normal_rules=None, resume=resume)  # If continue_infer is added
                # everywhere, this branch could be omitted.

            engine_result = self._infer(question=question)
            logger.result(engine_result.log_message())  # type: ignore[attr-defined]

            return engine_result

        finally:
            end_run(extra_meta={
                "facts_final": len(self.fact_base.get_facts()),
                "rules_total": len(self.rule_base.rules),
            })

    def get_facts(self) -> list[FACT_TYPE]:
        """Return facts used (selected by initial_fact_base) and all derived facts."""
        return self.fact_base.get_facts()

    def get_infer_path(self, terminal_fact: FACT_TYPE) -> tuple[list[FactStep], FACT_TYPE | None]:
        """
        get the infer path message, the message will be returned in a tuple,
        the first element is the infer path message(a list of FactStep), the second element is the terminal fact.

        :param terminal_fact: the terminal fact
        :type terminal_fact: FACT_TYPE
        :return: the infer path message(a list of FactStep), the terminal fact.
        :rtype: tuple[list[FactStep], FACT_TYPE | None]
        """
        return self.inference_path.get_infer_graph(terminal_fact)

    def generate_infer_path_graph(self, infer_path: list[FactStep]) -> None:
        """
        generate graph through infer path message
        important: you should use "get_infer_path" method to get the infer path message first

        :param infer_path: the infer path message(a list of FactStep)
        :type infer_path: list[FactStep]
        """
        self.inference_path.gennerate_infer_path_graph(infer_path)

    def _reset(self) -> None:
        self.fact_base.reset_fact_base()
        self.rule_base.reset_rule_base()

        self.equivalence.clear()
        self.grounder.reset()
        self.executor.reset()

        self.main_loop_manager.reset()
        self.solution_manager.reset()
        self.inference_path.reset()

        # Reset resume flag.
        self._has_previous_run = False

    def _initial_engine(self, question: Question, premises: Sequence[Assertion]) -> None:
        self.fact_base.initial_fact_base(question=question, topn=self.args.strategy.select_facts_num)
        self.fact_base.add_facts(facts=premises, force_add=True, check_free_variables=True)

        self.rule_base.initial_rule_base(question=question, topn=self.args.strategy.select_rules_num)

        self._initialize_term_selector()

        question_rules = self.rule_base.get_question_rules()
        normal_rules = [r for r in self.rule_base.get_rules() if not isinstance(r, _QuestionRule)]

        self.rule_selector.set_rules(normal_rules=normal_rules,
                         question_rules=question_rules)  # HACK: Not linked to fact base.

        self.main_loop_manager.initial_manager(normal_rules=normal_rules)

        if self.args.run.trace:
            for f in self.fact_base.get_facts():
                self.inference_path.add_infer_edge(consequent=f)  # FIXME: Keep change small for this PR; later use list
                # types and revert to Assertion, or at least include a CNF split.

    def _check_initial_status(self, question: Question) -> tuple[InferenceStatus | None, EngineRunResult | None]:
        """Check whether the question can be answered before the loop starts."""
        current_facts = self.fact_base.get_facts()
        initial_status = self.main_loop_manager.check_status(current_facts, question)
        if initial_status.is_terminal_for_main_loop():
            logger.info("Initial check result: %s", initial_status.log_message())
            include_final_facts = self.args.run.include_final_facts
            final_facts = current_facts if include_final_facts else []
            result = EngineRunResult(
                status=initial_status,
                solution_count=1,
                solutions=[{}],  # The question already exists in facts; treat {} as a "true" solution for display.
                final_facts=final_facts,
                fact_num=len(current_facts),
                include_final_facts=include_final_facts,
                question=question,
                iterations=self.main_loop_manager.iteration,
                execute_steps=self.executor.executor_manager.step_num,
                terminated_by="initial_check",
            )
            return initial_status, result
        return None, None

    def _handle_fixpoint(self, final_status: InferenceStatus, question: Question) -> None:
        """Handle actions when a FIXPOINT_REACHED status is detected."""
        if final_status == InferenceStatus.FIXPOINT_REACHED:
            self.rule_selector.set_at_fixpoint(at_fixpoint=True)
            grounded_rules = self.grounder.grounding_process(question=question)
            if grounded_rules:
                self.executor.execute(grounded_rules=grounded_rules, question=question)

    def _initialize_term_selector(self) -> None:
        """Initialize term candidates from facts and rule/question ground terms."""
        self.term_selector.update_terms(facts=self.fact_base.get_facts())

        rules = self.rule_base.get_rules()
        question_rules = self.rule_base.get_question_rules()
        self.term_selector.update_terms_from_rules([*rules, *question_rules])


if __name__ == '__main__':
    logger.info("Inference Engine Started")
