"""Tests for miu-examples package structure."""

import importlib


def test_package_importable() -> None:
    """Test miu_examples package can be imported."""
    import miu_examples

    assert miu_examples.__version__ == "0.1.0"


def test_simple_agent_importable() -> None:
    """Test simple_agent module can be imported."""
    from miu_examples import simple_agent

    assert hasattr(simple_agent, "main")


def test_multi_provider_importable() -> None:
    """Test multi_provider module can be imported."""
    from miu_examples import multi_provider

    assert hasattr(multi_provider, "main")


def test_tool_usage_importable() -> None:
    """Test tool_usage module can be imported."""
    from miu_examples import tool_usage

    assert hasattr(tool_usage, "WeatherTool")
    assert hasattr(tool_usage, "CalculatorTool")


def test_mcp_client_importable() -> None:
    """Test mcp_client module can be imported."""
    from miu_examples import mcp_client

    assert hasattr(mcp_client, "main")


def test_rag_agent_importable() -> None:
    """Test rag_agent module can be imported."""
    from miu_examples import rag_agent

    assert hasattr(rag_agent, "DocumentSearchTool")
    assert hasattr(rag_agent, "DOCUMENTS")


def test_multi_agent_importable() -> None:
    """Test multi_agent module can be imported."""
    from miu_examples import multi_agent

    assert hasattr(multi_agent, "orchestrate")
    assert hasattr(multi_agent, "create_researcher")
    assert hasattr(multi_agent, "create_writer")


def test_all_examples_have_main() -> None:
    """Test all example modules have a main function."""
    examples = [
        "miu_examples.simple_agent",
        "miu_examples.multi_provider",
        "miu_examples.tool_usage",
        "miu_examples.mcp_client",
        "miu_examples.rag_agent",
        "miu_examples.multi_agent",
    ]

    for module_name in examples:
        module = importlib.import_module(module_name)
        assert hasattr(module, "main"), f"{module_name} missing main function"
