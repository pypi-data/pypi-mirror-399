"""Custom tool example demonstrating tool creation.

Run with:
    python -m miu_examples.tool_usage

Requires:
    ANTHROPIC_API_KEY environment variable
"""

import ast
import asyncio
import operator
from typing import Any

from pydantic import BaseModel, Field

from miu_core.agents import AgentConfig, ReActAgent
from miu_core.providers import create_provider
from miu_core.tools import Tool, ToolContext, ToolRegistry, ToolResult


# Define input schema for the weather tool
class WeatherInput(BaseModel):
    """Input schema for weather tool."""

    city: str = Field(description="City name to get weather for")


# Define the custom tool
class WeatherTool(Tool):
    """Mock weather tool for demonstration."""

    name = "get_weather"
    description = "Get current weather for a city. Returns temperature and conditions."

    def get_input_schema(self) -> type[BaseModel]:
        """Return input schema."""
        return WeatherInput

    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Execute weather lookup (mock implementation)."""
        city = kwargs.get("city", "Unknown")

        # Mock weather data
        weather_data = {
            "tokyo": ("22°C", "Sunny"),
            "london": ("15°C", "Cloudy"),
            "new york": ("18°C", "Partly cloudy"),
            "paris": ("20°C", "Clear"),
        }

        city_lower = city.lower()
        if city_lower in weather_data:
            temp, conditions = weather_data[city_lower]
            return ToolResult(output=f"Weather in {city}: {temp}, {conditions}")

        return ToolResult(output=f"Weather in {city}: 20°C, Clear (default)")


# Define another tool - calculator
class CalculatorInput(BaseModel):
    """Input schema for calculator tool."""

    expression: str = Field(description="Math expression to evaluate (e.g., '2 + 2')")


class CalculatorTool(Tool):
    """Simple calculator tool."""

    name = "calculate"
    description = "Evaluate a mathematical expression. Supports +, -, *, /, and parentheses."

    def get_input_schema(self) -> type[BaseModel]:
        """Return input schema."""
        return CalculatorInput

    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Execute calculation using safe AST evaluation."""
        expression = kwargs.get("expression", "")

        try:
            result = self._safe_eval(expression)
            return ToolResult(output=f"{expression} = {result}")
        except (ValueError, SyntaxError, TypeError) as e:
            return ToolResult(output=f"Error: {e}", success=False)

    def _safe_eval(self, expression: str) -> float | int:
        """Safely evaluate math expression using AST.

        Only supports: numbers, +, -, *, /, parentheses.
        """
        # Supported binary operators
        bin_ops: dict[type[ast.operator], Any] = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        # Supported unary operators
        unary_ops: dict[type[ast.unaryop], Any] = {
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def _eval(node: ast.AST) -> float | int:
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError(f"Unsupported constant: {node.value!r}")
            elif isinstance(node, ast.BinOp):
                op_type = type(node.op)
                if op_type not in bin_ops:
                    raise ValueError(f"Unsupported operator: {op_type.__name__}")
                left = _eval(node.left)
                right = _eval(node.right)
                op_func = bin_ops[op_type]
                result: float | int = op_func(left, right)
                return result
            elif isinstance(node, ast.UnaryOp):
                unary_op_type = type(node.op)
                if unary_op_type not in unary_ops:
                    raise ValueError(f"Unsupported operator: {unary_op_type.__name__}")
                operand = _eval(node.operand)
                unary_op_func = unary_ops[unary_op_type]
                unary_result: float | int = unary_op_func(operand)
                return unary_result
            else:
                raise ValueError(f"Unsupported expression: {type(node).__name__}")

        tree = ast.parse(expression, mode="eval")
        return _eval(tree)


async def main() -> None:
    """Run agent with custom tools."""
    # Create provider
    provider = create_provider("anthropic:claude-sonnet-4-20250514")

    # Create tool registry and register tools
    registry = ToolRegistry()
    registry.register(WeatherTool())
    registry.register(CalculatorTool())

    # Create agent with tools
    agent = ReActAgent(
        provider=provider,
        tools=registry,
        config=AgentConfig(
            name="tool-agent",
            system_prompt="You are a helpful assistant with access to tools.",
        ),
    )

    # Test weather tool
    print("Query: What's the weather in Tokyo?")
    response = await agent.run("What's the weather in Tokyo?")
    print(f"Response: {response.get_text()}\n")

    # Test calculator tool
    print("Query: What is 25 * 4 + 100?")
    response = await agent.run("What is 25 * 4 + 100?")
    print(f"Response: {response.get_text()}")


if __name__ == "__main__":
    asyncio.run(main())
