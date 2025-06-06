import pytest

from dynamiq import Workflow
from dynamiq.connections import OpenAI as OpenAIConnection
from dynamiq.flows import Flow
from dynamiq.nodes.agents.react import InferenceMode, ReActAgent
from dynamiq.nodes.llms import OpenAI
from dynamiq.runnables import RunnableConfig, RunnableStatus
from dynamiq.utils.logger import logger


@pytest.mark.unit
def test_react_agent_without_tools_or_memory():
    connection = OpenAIConnection()
    llm = OpenAI(
        connection=connection,
        model="gpt-4o-mini",
        max_tokens=300,
        temperature=0,
    )

    agent = ReActAgent(
        name="TestReactAgent",
        id="test_react_agent",
        llm=llm,
        role="You are a helpful assistant.",
        inference_mode=InferenceMode.DEFAULT,
        tools=[],
        memory=None,
        verbose=False,
        max_loops=3,
    )

    input_data = {
        "input": "What is 2 + 2?",
        "user_id": None,
        "session_id": None,
    }

    config = RunnableConfig(request_timeout=30)
    result = agent.run(input_data=input_data, config=config)

    assert result.status == RunnableStatus.SUCCESS

    content = result.output["content"]
    assert isinstance(content, str)
    assert "4" in content, f"Expected '4' in the output, got: {content!r}"


@pytest.fixture(scope="module")
def openai_connection():
    """Provides a reusable OpenAI connection."""
    return OpenAIConnection()


@pytest.fixture(scope="module")
def test_llm(openai_connection):
    """Provides a lightweight LLM instance for testing."""
    return OpenAI(
        connection=openai_connection,
        model="gpt-4o-mini",
        max_tokens=300,
        temperature=0,
    )


@pytest.fixture
def test_react_agent(test_llm):
    """Provides a configured ReActAgent instance."""
    return ReActAgent(
        name="TestReactAgentInWorkflow",
        id="test_react_agent_workflow_node",
        llm=test_llm,
        role="You are a helpful assistant.",
        inference_mode=InferenceMode.DEFAULT,
        tools=[],
        memory=None,
        max_loops=3,
    )


@pytest.fixture
def test_workflow(test_react_agent):
    """Provides a Workflow containing the test ReActAgent."""
    return Workflow(flow=Flow(nodes=[test_react_agent]))


@pytest.fixture
def agent_input_data():
    """Provides standard input data for the agent."""
    return {
        "input": "What is 2 + 2?",
        "user_id": None,
        "session_id": None,
    }


@pytest.fixture
def run_config():
    """Provides a standard RunnableConfig."""
    return RunnableConfig(request_timeout=30)


@pytest.mark.unit
def test_react_agent_in_workflow(
    test_workflow: Workflow,
    test_react_agent: ReActAgent,
    agent_input_data: dict,
    run_config: RunnableConfig,
):
    """
    Tests running a basic ReActAgent (no tools/memory) within a Workflow.
    Verifies that the workflow executes successfully and the agent produces the expected output.
    """
    logger.info("--- Running test_react_agent_in_workflow ---")
    logger.info(f"Workflow ID: {test_workflow.id}")
    logger.info(f"Agent Node ID: {test_react_agent.id}")
    logger.info(f"Input Data: {agent_input_data}")

    result = test_workflow.run(input_data=agent_input_data, config=run_config)

    logger.info(f"Workflow Run Status: {result.status}")
    logger.info(f"Workflow Output: {result.output}")

    assert result.status == RunnableStatus.SUCCESS, f"Workflow failed with status: {result.status}"
    assert isinstance(result.output, dict), "Workflow output should be a dictionary"

    agent_node_id = test_react_agent.id
    assert (
        agent_node_id in result.output
    ), f"Agent node ID '{agent_node_id}' not found in workflow output keys: {list(result.output.keys())}"

    agent_result = result.output[agent_node_id]
    assert isinstance(agent_result, dict), f"Agent result for node '{agent_node_id}' should be a dictionary"
    assert (
        agent_result.get("status") == RunnableStatus.SUCCESS
    ), f"Agent node '{agent_node_id}' failed within the workflow"

    agent_output = agent_result.get("output")
    assert isinstance(agent_output, dict), f"Agent node '{agent_node_id}' output should be a dictionary"

    content = agent_output.get("content")
    assert content is not None, f"Agent node '{agent_node_id}' output dictionary is missing 'content' key"
    assert isinstance(content, str), f"Agent node '{agent_node_id}' content should be a string, got: {type(content)}"

    expected_answer = "4"
    assert expected_answer in content, f"Expected '{expected_answer}' in the agent output, got: {content!r}"

    logger.info("--- Test test_react_agent_in_workflow PASSED ---")
