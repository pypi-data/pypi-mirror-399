from crewai import Agent, Crew, Task, Process
from crewai.tools import BaseTool
from fabriq.config_parser import ConfigParser
from crewai.llm import LLM
from typing import Dict, Any
from tenacity import stop_after_attempt, retry, wait_exponential
import os

class AgentBuilder:
    """
    AgentBuilder aligns with the agent_builder config in config.yaml.
    It supports multiple agents and tasks as defined in the config.
    """

    def __init__(self, config: ConfigParser, **kwargs):
        self.config = config
        self.llm = self._create_llm()
        self.agent_cfg = (
            self.config.get("agent_builder", {}).get("params", {}).get("agents", [])
        )
        self.task_cfg = (
            self.config.get("agent_builder", {})
            .get("params", {})
            .get("tasks", {})
            .get("params", [])
        )
        self.process_type = self.config.get("agent_builder", {}).get(
            "process", "sequential"
        )
        self.tracing_enabled = self.config.get("tracing", {}).get("params", {}).get("enabled", False)
        self.tracing_uri = self.config.get("tracing", {}).get("params", {}).get("uri", None)

        if self.tracing_enabled:
            import mlflow
            if self.tracing_uri:
                mlflow.set_tracking_uri(self.tracing_uri)
            mlflow.set_experiment("Fabriq Agents Traces")
            mlflow.crewai.autolog()
        
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        self.loom = self._create_loom()

    def _create_tool(self, tool_name: str, **kwargs) -> Any:

        from fabriq.fabriq_tools import get_tool_by_name

        tool_class = get_tool_by_name(tool_name)
        if tool_class:
            langchain_tool = tool_class(**kwargs)
            class ToolWrapper(BaseTool):
                name: str = tool_name
                description: str = langchain_tool.description

                def _run(self, query: str) -> str:
                    return langchain_tool.run(query)

            return ToolWrapper()
        else:
            raise ValueError(f"Tool '{tool_name}' not found.")

    def _create_llm(self, **kwargs) -> LLM:
        llm_config = self.config.get("llm", {})
        params = llm_config.get("params", {})
        model_type = llm_config.get("type", "")
        model_kwargs = llm_config.get("kwargs", {})

        # if model_type.lower() in {"openai", "azure_openai"}:
        #     model_type = "openai"

        if "model_name" in params:
            model = params.pop("model_name")
        elif "model" in params:
            model = params.pop("model")
        elif "deployment_name" in params:
            model = params.pop("deployment_name")
        if "/" not in model:
            model = model_type + "/" + model

        api_base = params.pop("endpoint", "")
        params["model"] = model
        params["api_base"] = api_base
        params['base_url'] = api_base
        
        llm = LLM(**params, **model_kwargs, **kwargs)
        return llm

    def _create_agents(self) -> Dict[str, Agent]:
        agents = {}
        for agent in self.agent_cfg:
            name = agent["name"]
            tool_names = agent.get("tools", [])
            agent_tools = []
            for tool_name in tool_names:
                tool_instance = self._create_tool(tool_name)
                agent_tools.append(tool_instance)
            
            agent_instance = Agent(
                role=agent["role"],
                goal=agent.get("goal", ""),
                backstory=agent.get(
                    "backstory",
                    "You are a highly skilled AI agent performing your assigned task.",
                ),
                tools=agent_tools,
                memory=agent.get("memory", True),
                verbose=agent.get("verbose", False),
                llm=self.llm,
                allow_delegation=agent.get("allow_delegation", False),
            )
            agents[name] = agent_instance
        return agents

    def _create_tasks(self) -> Dict[str, Task]:
        tasks = {}
        for task in self.task_cfg:
            agent_name = task["agent"]
            task_name = task["name"]
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not defined in agents config.")
            task_instance = Task(
                description=task["description"],
                expected_output=task["expected_output"],
                agent=self.agents[agent_name],
                human_input=task.get("human_input", False),
            )
            tasks[task_name] = task_instance
        return tasks

    def _create_loom(self) -> Crew:
        process = (
            Process.sequential
            if self.process_type == "sequential"
            else Process.hierarchical
        )

        manager = self.config.get("agent_builder", {}).get("params", {}).get("manager", None)
        manager_agent = None
        manager_llm = None

        if manager in self.agents :
            manager_agent = self.agents.get(manager, None)
        
        elif manager and manager.lower() == "llm":
            manager_llm = self.llm


        self.loom = Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            process=process,
            manager_agent=manager_agent,
            manager_llm=manager_llm
        )
        return self.loom
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=3))
    def run_loom_with_retry(self, loom, inputs):
        return loom.kickoff(inputs)

    def run(self, inputs: Dict[str, Any], response_format: Dict[str, Any] = None) -> dict:
        
        if response_format:
            for task in self.loom.tasks:
                if task in response_format:
                    self.loom.tasks[task].output_json = response_format[task]

        # result = self.loom.kickoff(inputs=inputs)
        result = self.run_loom_with_retry(self.loom, inputs)

        return {
            "output": result.raw,
            "json_output": result.json_dict,
            "structured_output": result.pydantic,
            "tasks_output": getattr(result, "tasks_output", None),
            "token_usage": getattr(result, "token_usage", None),
        }
