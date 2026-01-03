"""Core digital employee orchestrator.

This module provides the base DigitalEmployee class that manages agents,
tools, and MCPs. It implements the ConfigBuilder interface to
provide configuration building capabilities.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)
    Vio Albert Ferdinand (vio.a.ferdinand@gdplabs.id)

References:
    NONE
"""

from typing import Any, Callable

from glaip_sdk import MCP, Agent, Tool
from gllm_core.utils import LoggerManager
from omegaconf import OmegaConf

from digital_employee_core.config_templates.loader import DEFAULTS_TEMPLATE, ConfigTemplateLoader
from digital_employee_core.configuration.agent_configuration import AgentConfigKeys, StepLimitConfig
from digital_employee_core.configuration.configuration import DigitalEmployeeConfiguration
from digital_employee_core.constants import DEFAULT_MODEL_NAME
from digital_employee_core.digital_employee.dependencies import (
    DependencyBundle,
    MCPConfigBuilder,
    ToolConfigBuilder,
)
from digital_employee_core.escalation import EscalationConfig
from digital_employee_core.escalation.base_escalation_channel import EscalationChannel
from digital_employee_core.escalation.constant import (
    ESCALATION_NO_CHANNELS_DEPENDENCIES_WARNING,
    ESCALATION_NO_CHANNELS_PROMPT_WARNING,
    ESCALATION_PROMPT,
)
from digital_employee_core.identity.identity import DigitalEmployeeIdentity

logger = LoggerManager().get_logger(__name__)


class DigitalEmployee:
    """Core digital employee orchestrator.

    This class manages the lifecycle of a digital employee, including
    initialization, deployment, and execution of agents with tools and MCPs.
    Provides methods for building tool and MCP configurations from YAML templates.

    Attributes:
        identity (DigitalEmployeeIdentity): The digital employee's identity.
        tools (list[Tool]): List of tools the digital employee can use.
        sub_agents (list[Agent]): List of sub-agents (for future use).
        mcps (list[MCP]): List of MCPs the digital employee can use.
        configurations (list[DigitalEmployeeConfiguration]): List of configuration objects for tools and MCPs.
        model (str): Model identifier to use for the agent.
        agent_config (dict[str, Any] | Agent._UNSET): Agent execution configuration (e.g., execution_timeout).
        agent_coordinator_name (str | None): Name for the agent coordinator. If provided, this name
            will be used when initializing the Agent class instead of self.identity.name.
        agent (Agent | None): The main agent instance.
        config_loaders (list[ConfigTemplateLoader]): List of configuration template loader instances.
        escalation_config (EscalationConfig): Escalation configuration.
    """

    def __init__(  # noqa: PLR0913
        self,
        identity: DigitalEmployeeIdentity,
        tools: list[Tool] | None = None,
        sub_agents: list[Agent] | None = None,
        mcps: list[MCP] | None = None,
        configurations: list[DigitalEmployeeConfiguration] | None = None,
        model: str = DEFAULT_MODEL_NAME,
        agent_config: dict[str, Any] | None = None,
        agent_coordinator_name: str | None = None,
        escalation_config: EscalationConfig | None = None,
    ):
        """Initialize the digital employee.

        Args:
            identity (DigitalEmployeeIdentity): The digital employee's identity.
            tools (list[Tool] | None, optional): List of tools the digital employee can use. Defaults to None.
            sub_agents (list[Agent] | None, optional): List of sub-agents (for future use). Defaults to None.
            mcps (list[MCP] | None, optional): List of MCPs the digital employee can use. Defaults to None.
            configurations (list[DigitalEmployeeConfiguration] | None, optional): List of configuration objects
                for tools and MCPs. Defaults to None.
            model (str, optional): Model identifier to use for the agent. Defaults to DEFAULT_MODEL_NAME.
            agent_config (dict[str, Any] | None, optional): Agent execution configuration (e.g., execution_timeout).
                Defaults to None. If None, will be converted to Agent._UNSET internally.
            agent_coordinator_name (str | None, optional): Name for the agent coordinator. If provided, this name
                will be used when initializing the Agent class instead of self.identity.name. Defaults to None.
            escalation_config (EscalationConfig | None, optional): Escalation configuration. Defaults to None.
        """
        self.identity = identity
        self.tools = tools or []
        self.sub_agents = sub_agents or []
        self.mcps = mcps or []
        self.configurations = configurations or []
        self.model = model
        # TODO: make agent config strong typing
        self.agent_config = self._ensure_valid_agent_config(agent_config) if agent_config is not None else Agent._UNSET
        if agent_coordinator_name is not None:
            agent_coordinator_name = agent_coordinator_name.strip() or None
        self.agent_coordinator_name = agent_coordinator_name
        self.escalation_config = escalation_config or EscalationConfig(enabled=False, channels=[])
        self.agent: Agent | None = None
        # Initialize with base config loader - subclasses can add more loaders
        self.config_loaders: list[ConfigTemplateLoader] = [ConfigTemplateLoader()]

    @property
    def _is_escalation_active(self) -> bool:
        """Check if escalation is currently active.

        Returns:
            bool: True if escalation is enabled, a supervisor is set, and channels are configured.
        """
        return bool(self.escalation_config.enabled and self.identity.supervisor and self.escalation_config.channels)

    def add_tools(self, tools: list[Tool]) -> None:
        """Add tools to the digital employee.

        Args:
            tools (list[Tool]): List of tools to add.
        """
        self.tools.extend(tools)

    def remove_tools(self, tools: list[Tool]) -> None:
        """Remove tools from the digital employee.

        Args:
            tools (list[Tool]): List of tools to remove.
        """
        tools_to_remove = set(tools)
        self.tools = [tool for tool in self.tools if tool not in tools_to_remove]

    def add_mcps(self, mcps: list[MCP]) -> None:
        """Add MCPs to the digital employee.

        Args:
            mcps (list[MCP]): List of MCPs to add.
        """
        self.mcps.extend(mcps)

    def remove_mcps(self, mcps: list[MCP]) -> None:
        """Remove MCPs from the digital employee.

        Args:
            mcps (list[MCP]): List of MCPs to remove.
        """
        mcps_to_remove = set(mcps)
        self.mcps = [mcp for mcp in self.mcps if mcp not in mcps_to_remove]

    def add_config_loader(self, config_loader: ConfigTemplateLoader) -> None:
        """Add a config loader to the list of loaders.

        Args:
            config_loader (ConfigTemplateLoader): Config loader to add.
        """
        self.config_loaders.append(config_loader)

    def add_sub_agents(self, sub_agents: list[Agent]) -> None:
        """Add sub-agents to the digital employee.

        Args:
            sub_agents (list[Agent]): List of sub-agents to add.
        """
        self.sub_agents.extend(sub_agents)

    def remove_sub_agents(self, sub_agents: list[Agent]) -> None:
        """Remove sub-agents from the digital employee by name.

        Args:
            sub_agents (list[Agent]): List of sub-agents to remove.
        """
        agent_names_to_remove = {agent.name for agent in sub_agents if agent.name}
        self.sub_agents = [agent for agent in self.sub_agents if agent.name not in agent_names_to_remove]

    def enable_escalation(self) -> None:
        """Enable escalation for the digital employee."""
        self.escalation_config.enabled = True

    def disable_escalation(self) -> None:
        """Disable escalation for the digital employee."""
        self.escalation_config.enabled = False

    def add_escalation_channel(self, channel: EscalationChannel) -> None:
        """Add an escalation channel to the digital employee.

        Args:
            channel (EscalationChannel): The escalation channel to add.
        """
        if channel not in self.escalation_config.channels:
            self.escalation_config.channels.append(channel)

    def remove_escalation_channel(self, channel: EscalationChannel) -> None:
        """Remove an escalation channel from the digital employee.

        Args:
            channel (EscalationChannel): The escalation channel to remove.
        """
        if channel in self.escalation_config.channels:
            self.escalation_config.channels.remove(channel)

    def build_prompt(self) -> str:
        """Build the prompt for the agent.

        This method can be overridden by subclasses to provide custom
        prompts based on the digital employee's identity and job.
        Always includes the digital employee's name, email, and language preferences
        in the prompt to ensure identity awareness. Supports placeholders in job instruction.

        Returns:
            str: The prompt string for the agent.

        Raises:
            ConfigurationValidationError: If required placeholders in instruction cannot be resolved.
        """
        language_names = [lang.value for lang in self.identity.languages]

        if len(language_names) > 1:
            language_list = ", ".join(language_names[:-1]) + f" and {language_names[-1]}"
            language_instruction = (
                f"You must respond only in the following languages: {language_list}. "
                f"Choose the most appropriate language based on the user's input or context."
            )
        else:
            language_instruction = f"You must respond only in {language_names[0]} language."

        identity_prefix = (
            f"You are {self.identity.name} ({self.identity.email}), {self.identity.job.title}. {language_instruction}"
        )

        # Resolve placeholders in job instruction using all config loaders
        # Use the first loader as the base, and merge additional loaders' defaults
        base_loader = self.config_loaders[0] if self.config_loaders else ConfigTemplateLoader()
        additional_loaders = self.config_loaders[1:] if len(self.config_loaders) > 1 else None

        resolved_instruction = base_loader.resolve_placeholders(
            self.identity.job.instruction,
            self.configurations,
            additional_loaders=additional_loaders,
        )

        prompt = f"{identity_prefix}\n\n{resolved_instruction}"

        if not (self.escalation_config.enabled and self.identity.supervisor):
            return prompt

        if not self.escalation_config.channels:
            logger.warning(ESCALATION_NO_CHANNELS_PROMPT_WARNING)
            return prompt

        if self._is_escalation_active:
            return self._inject_escalation_prompt(prompt)

        return prompt

    def deploy(self) -> None:
        """Deploy the digital employee.

        This method initializes the agent with tools and MCPs,
        builds configurations, and deploys it to the AI platform.
        """
        tools, mcps, tool_configs, mcp_configs = self._prepare_tools_mcps_and_configs()

        self.agent = Agent(
            name=self.agent_coordinator_name or self.identity.name,
            description=self.identity.job.description,
            instruction=self.build_prompt(),
            tools=tools,
            agents=self.sub_agents,
            mcps=mcps,
            tool_configs=tool_configs,
            mcp_configs=mcp_configs,
            model=self.model,
            agent_config=self.agent_config,
        )

        self.agent.deploy()

    def run(
        self,
        message: str,
        configurations: list[DigitalEmployeeConfiguration] | None = None,
        override_agent_config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """Run the digital employee with a message.

        Args:
            message (str): The message/prompt to send to the digital employee.
            configurations (list[DigitalEmployeeConfiguration] | None, optional): List of configuration objects.
                Defaults to None.
            override_agent_config (dict[str, Any] | None, optional): Dictionary of agent config to be overridden.
                Defaults to None.
            **kwargs (Any): Additional keyword arguments to pass to agent.run.

        Returns:
            str: The agent's response as a string.

        Raises:
            RuntimeError: If the agent has not been deployed.
        """
        if self.agent is None:
            raise RuntimeError("Agent has not been deployed. Call deploy() before run().")

        runtime_config = {}

        if configurations:
            runtime_config.update(self._build_runtime_configs(configurations))

        if override_agent_config:
            validated_agent_config = self._ensure_valid_agent_config(override_agent_config)
            if validated_agent_config:
                runtime_config.update({"agent_config": validated_agent_config})

        return self.agent.run(message=message, runtime_config=runtime_config or None, **kwargs)

    def build_tool_config(self, configurations: list[DigitalEmployeeConfiguration]) -> dict[str, dict[str, Any]]:
        """Build tool configuration based on identity and configurations.

        This method loads tool configuration templates from YAML and replaces
        placeholders with values from DigitalEmployeeConfiguration objects.
        Merges configs from all config loaders in order (later loaders override earlier ones).

        Example for subclasses:
            def build_tool_config(self, configurations):
                # Get base configs from parent
                base_configs = super().build_tool_config(configurations)

                # Load additional configs for this subclass
                additional = self.hr_config_loader.load_tool_configs(configurations)

                # Merge them
                return ConfigTemplateLoader.merge_configs(base_configs, additional)

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of configuration objects.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping tool names to their configuration dictionaries.
        """
        return self._build_merged_configs(
            configurations, lambda loader, configs, items: loader.load_tool_configs(configs, items), self.tools
        )

    def build_mcp_config(self, configurations: list[DigitalEmployeeConfiguration]) -> dict[str, dict[str, Any]]:
        """Build MCP configuration based on identity and configurations.

        This method loads MCP configuration templates from YAML and replaces
        placeholders with values from DigitalEmployeeConfiguration objects.
        Merges configs from all config loaders in order (later loaders override earlier ones).

        Example for subclasses:
            def build_mcp_config(self, configurations):
                # Get base configs from parent
                base_configs = super().build_mcp_config(configurations)

                # Load additional configs for this subclass
                additional = self.hr_config_loader.load_mcp_configs(configurations)

                # Merge them
                return ConfigTemplateLoader.merge_configs(base_configs, additional)

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of configuration objects.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping MCP names to their configuration dictionaries.
        """
        return self._build_merged_configs(
            configurations, lambda loader, configs, items: loader.load_mcp_configs(configs, items), self.mcps
        )

    def _build_merged_configs(
        self,
        configurations: list[DigitalEmployeeConfiguration],
        load_fn: Callable[
            [ConfigTemplateLoader, list[DigitalEmployeeConfiguration], list[Any] | None], dict[str, dict[str, Any]]
        ],
        filter_items: list[Any] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Build merged configurations from all config loaders.

        This is a helper method that reduces code duplication between
        build_tool_config() and build_mcp_config().

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of configuration objects.
            load_fn (Callable): Function that takes (loader, configurations, filter_items) and returns configs.
            filter_items (list[Any] | None, optional): Items to filter (tools or MCPs). Defaults to None.

        Returns:
            dict[str, dict[str, Any]]: Dictionary mapping names to their configuration dictionaries.
        """
        if not self.config_loaders:
            return {}

        # First, merge all defaults from all loaders
        merged_defaults = OmegaConf.create({})
        for loader in self.config_loaders:
            defaults_path = loader.template_dir / DEFAULTS_TEMPLATE
            if defaults_path.exists():
                loader_defaults = OmegaConf.load(defaults_path)
                merged_defaults = OmegaConf.merge(merged_defaults, loader_defaults)

        # Convert merged defaults to DigitalEmployeeConfiguration list
        defaults_dict = OmegaConf.to_container(merged_defaults, resolve=False)
        defaults_config_list = [DigitalEmployeeConfiguration(key=str(k), value=v) for k, v in defaults_dict.items()]

        # Merge: defaults + user configurations (user takes precedence)
        all_configs = defaults_config_list + configurations

        # Start with configs from the first loader (base) - using merged configs
        result = load_fn(self.config_loaders[0], all_configs, filter_items)

        # Merge configs from additional loaders (if any) - using merged configs
        for loader in self.config_loaders[1:]:
            additional_configs = load_fn(loader, all_configs, filter_items)
            result = ConfigTemplateLoader.merge_configs(result, additional_configs)

        return result

    def _build_tools_and_mcps_configs(
        self,
        tools: list[Tool],
        mcps: list[MCP],
        build_tool_configs: ToolConfigBuilder,
        build_mcp_configs: MCPConfigBuilder,
    ) -> tuple[dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
        """Build tool and MCP configuration maps for the given dependencies.

        This helper builds configuration dictionaries only when instance
        configurations are present (`self.configurations`). When no configurations
        are provided, both configuration maps are returned as `None`.

        Args:
            tools (list[Tool]): Tools to build configurations for.
            mcps (list[MCP]): MCPs to build configurations for.
            build_tool_configs (ToolConfigBuilder): Callable that builds tool configs.
            build_mcp_configs (McpConfigBuilder): Callable that builds MCP configs.

        Returns:
            tuple[dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
                Tool config map and MCP config map.
        """
        tool_configs = None
        mcp_configs = None
        if self.configurations:
            tool_configs = build_tool_configs(self.configurations, tools)
            mcp_configs = build_mcp_configs(self.configurations, mcps)

        return tool_configs, mcp_configs

    def _build_base_tools_mcps_and_configs(
        self,
    ) -> tuple[list[Tool], list[MCP], dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
        """Build base Tools/MCPs and their configurations.

        Returns:
            tuple[list[Tool], list[MCP], dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
                Base tools, base MCPs, tool config map, and MCP config map.
        """
        tool_configs, mcp_configs = self._build_tools_and_mcps_configs(
            tools=self.tools,
            mcps=self.mcps,
            build_tool_configs=lambda configurations, _tools: self.build_tool_config(configurations),
            build_mcp_configs=lambda configurations, _mcps: self.build_mcp_config(configurations),
        )
        return self.tools, self.mcps, tool_configs, mcp_configs

    def _build_escalation_tools_mcps_and_configs(
        self,
    ) -> tuple[list[Tool], list[MCP], dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
        """Build escalation Tools/MCPs and their configurations.

        Returns:
            tuple[list[Tool], list[MCP], dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
                Escalation tools, escalation MCPs, tool config map, and MCP config map.
        """
        tools, mcps = self._build_escalation_dependencies()
        loader = self.config_loaders[0] if self.config_loaders else ConfigTemplateLoader()
        tool_configs, mcp_configs = self._build_tools_and_mcps_configs(
            tools=tools,
            mcps=mcps,
            build_tool_configs=(lambda configurations, tools: loader.load_tool_configs(configurations, tools)),
            build_mcp_configs=lambda configurations, mcps: loader.load_mcp_configs(configurations, mcps),
        )
        return tools, mcps, tool_configs, mcp_configs

    def _build_base_dependency_bundle(self) -> DependencyBundle:
        """Build the base dependency bundle containing tools, MCPs, and their configurations.

        Returns:
            DependencyBundle: Bundle containing base tools, MCPs, and their config maps.
        """
        tools, mcps, tool_configs, mcp_configs = self._build_base_tools_mcps_and_configs()
        return DependencyBundle(tools=tools, mcps=mcps, tool_configs=tool_configs, mcp_configs=mcp_configs)

    def _build_escalation_dependency_bundle(self) -> DependencyBundle:
        """Build the escalation dependency bundle containing tools, MCPs, and their configurations.

        Returns:
            DependencyBundle: Bundle containing escalation tools, MCPs, and their config maps.
        """
        tools, mcps, tool_configs, mcp_configs = self._build_escalation_tools_mcps_and_configs()
        return DependencyBundle(tools=tools, mcps=mcps, tool_configs=tool_configs, mcp_configs=mcp_configs)

    def _prepare_tools_mcps_and_configs(
        self,
    ) -> tuple[list[Tool], list[MCP], dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
        """Prepare the final Tools/MCPs lists and their configurations.

        This combines base dependencies with additional dependencies and merges their corresponding configuration maps.

        Returns:
            tuple[list[Tool], list[MCP], dict[str, dict[str, Any]] | None, dict[str, dict[str, Any]] | None]:
                Tools, MCPs, tool config map, and MCP config map to be used for agent deployment.
        """
        base = self._build_base_dependency_bundle()
        escalation = self._build_escalation_dependency_bundle()
        merged = base.merged_with(
            escalation,
            merge_configs=bool(self.configurations),
        )
        return merged.tools, merged.mcps, merged.tool_configs, merged.mcp_configs

    def _build_escalation_prompt(self) -> str:
        """Build the escalation protocol section of the prompt.

        Returns:
            str: The escalation protocol instructions.
        """
        if not self.identity.supervisor:
            return ""

        escalation_prompt_lines = [ESCALATION_PROMPT]

        for channel in self.escalation_config.channels:
            escalation_prompt_lines.append(channel.get_prompt_instruction(self.identity.supervisor))

        return "\n".join(escalation_prompt_lines).strip()

    def _inject_escalation_prompt(self, prompt: str) -> str:
        """Inject the escalation protocol section into the prompt.

        Args:
            prompt (str): The original prompt.

        Returns:
            str: The prompt with the escalation protocol section injected.
        """
        new_prompt = f"{prompt}\n\n{self._build_escalation_prompt()}"
        return new_prompt

    def _build_escalation_dependencies(self) -> tuple[list[Tool], list[MCP]]:
        """Build tools and MCPs required by escalation channels.

        Returns:
            tuple[list[Tool], list[MCP]]: Tuple containing the required tools and MCPs.
        """
        if not (self.escalation_config.enabled and self.identity.supervisor):
            return [], []

        if not self.escalation_config.channels:
            logger.warning(ESCALATION_NO_CHANNELS_DEPENDENCIES_WARNING)
            return [], []

        required_mcps = DependencyBundle.dedupe_preserve_order(
            [mcp for channel in self.escalation_config.channels for mcp in channel.get_required_mcps()]
        )
        required_tools = DependencyBundle.dedupe_preserve_order(
            [tool for channel in self.escalation_config.channels for tool in channel.get_required_tools()]
        )

        return required_tools, required_mcps

    def _ensure_valid_agent_config(self, agent_config: dict[str, Any]) -> dict[str, Any]:
        """Ensure agent config is valid.

        Args:
            agent_config (dict[str, Any]): Agent config to validate.

        Returns:
            dict[str, Any]: Validated agent config.
        """
        agent_config = agent_config.copy()
        if AgentConfigKeys.STEP_LIMIT_CONFIG in agent_config:
            step_limit_config = agent_config[AgentConfigKeys.STEP_LIMIT_CONFIG]
            if isinstance(step_limit_config, dict):
                step_limit_object = StepLimitConfig.model_validate(step_limit_config)
            elif isinstance(step_limit_config, StepLimitConfig):
                step_limit_object = step_limit_config
            else:
                raise TypeError(
                    f"step_limit_config must be a StepLimitConfig instance or dict, "
                    f"got {type(step_limit_config).__name__}"
                )
            step_limit_dict = step_limit_object.to_dict()
            if step_limit_dict:
                agent_config[AgentConfigKeys.STEP_LIMIT_CONFIG] = step_limit_dict
            else:
                agent_config.pop(AgentConfigKeys.STEP_LIMIT_CONFIG, None)

        return agent_config

    def _build_runtime_configs(
        self,
        configurations: list[DigitalEmployeeConfiguration],
    ) -> dict[str, dict[str, Any]]:
        """Build runtime configurations for tools and MCPs.

        This method builds all configurations and filters them to only include
        tools and MCPs that are actually used by the agent. Runtime configurations
        are merged with instance configurations (self.configurations), with runtime
        configurations taking precedence.

        Args:
            configurations (list[DigitalEmployeeConfiguration]): List of runtime configuration objects.

        Returns:
            dict[str, dict[str, Any]]: Runtime configuration dictionary.
        """
        # Merge instance configurations with runtime configurations
        # Runtime configurations override instance configurations
        merged_configs = self.configurations + configurations

        # Use the first loader (or create a default one if none exist)
        loader = self.config_loaders[0] if self.config_loaders else ConfigTemplateLoader()
        tool_configs = loader.load_tool_configs(merged_configs, self.agent.tools)
        mcp_configs = loader.load_mcp_configs(merged_configs, self.agent.mcps)

        return {
            "tool_configs": tool_configs,
            "mcp_configs": mcp_configs,
        }
