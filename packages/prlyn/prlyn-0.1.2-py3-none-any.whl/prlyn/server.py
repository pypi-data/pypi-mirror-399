"""
MCP Server implementation for prlyn.
"""
from fastmcp import FastMCP
from prlyn.analyzer import Analyzer
from prlyn import history
from prlyn.template_generator import generate_improvement_template
from typing import Optional

# Initialize the MCP server
mcp = FastMCP("prlyn")

# Global instance to cache Spacy loading
_analyzer = None


def get_analyzer() -> Analyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = Analyzer()
    return _analyzer


@mcp.tool()
def analyze_prompt(
    prompt: str, output_format: str = "json", model_name: Optional[str] = None
) -> str:
    """
    Analyze a prompt for quality issues using Plint.

    Args:
        prompt: The raw prompt text to analyze.
        output_format: "json", "markdown", or "table". Defaults to "json".
        model_name: Optional target LLM name (e.g., "gpt-4", "claude-3-5-sonnet") for biased scoring.

    Returns:
        Analysis report in requested format.
    """
    analyzer = get_analyzer()
    result = analyzer.analyze(prompt, model_name=model_name)

    # Save for history
    history.save_analysis(result)

    if output_format.lower() == "markdown":
        return analyzer.report_generator.generate_markdown_report(result)
    elif output_format.lower() == "table":
        return analyzer.report_generator.generate_table_report(result)
    else:
        return result.model_dump_json(indent=2)


@mcp.tool()
def get_improvement_template(prompt: str, model_name: Optional[str] = None) -> str:
    """
    Analyze a prompt and generate actionable improvement instructions.

    This tool returns a structured template with SPECIFIC fixes that you (the AI assistant)
    can use to rewrite the prompt. The template includes:
    - Buried instructions to move
    - Vague terms to replace
    - Weak verbs to strengthen
    - Missing delimiters to add
    - Flow issues to resolve

    Args:
        prompt: The raw prompt text to analyze and improve.
        model_name: Optional target LLM name for model-aware analysis.

    Returns:
        A populated meta-prompt with specific, actionable improvement instructions.
    """
    analyzer = get_analyzer()
    result = analyzer.analyze(prompt, model_name=model_name)
    return generate_improvement_template(result)


def run() -> None:
    """Entry point for the application script."""
    import argparse

    parser = argparse.ArgumentParser(description="Plint: Prompt Analyzer")
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt text to analyze (skips server mode if provided)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "table"],
        default="table",
        help="Output format",
    )
    parser.add_argument("--model", help="Target model name for biased analysis")
    parser.add_argument("--diff", action="store_true", help="Compare against last scan")

    args = parser.parse_args()

    if args.prompt:
        analyzer = get_analyzer()
        result = analyzer.analyze(args.prompt, model_name=args.model)

        if args.diff:
            prev = history.find_latest_history()
            if prev:
                print("## Revision Comparison")
                # Simple score diff comparison
                p_read = prev.get("readability_score", {}).get("flesch_reading_ease", 0)
                c_read = (
                    result.readability_score.flesch_reading_ease
                    if result.readability_score
                    else 0
                )
                print(
                    f"Readability: {p_read} -> {c_read} ({'+' if c_read > p_read else ''}{c_read - p_read:.2f})"
                )

                # Save as current
                history.save_analysis(result)
            else:
                print("No historical data found for comparison.")
        else:
            history.save_analysis(result)
            if args.format == "markdown":
                print(analyzer.report_generator.generate_markdown_report(result))
            elif args.format == "table":
                print(analyzer.report_generator.generate_table_report(result))
            else:
                print(result.model_dump_json(indent=2))
    else:
        mcp.run()


if __name__ == "__main__":
    run()
