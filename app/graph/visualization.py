"""Graph visualization support."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def export_graph_visualization(compiled_graph, output_dir: str = "travel_plans") -> str | None:
    """Export LangGraph workflow as Mermaid PNG if dependencies available."""
    try:
        mermaid_png = compiled_graph.get_graph().draw_mermaid_png()
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_dir) / "workflow_graph.png"
        output_path.write_bytes(mermaid_png)
        return str(output_path)
    except Exception as exc:
        logger.info("Graph visualization unavailable: %s", exc)
        try:
            mermaid = compiled_graph.get_graph().draw_mermaid()
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            output_path = Path(output_dir) / "workflow_graph.mmd"
            output_path.write_text(mermaid, encoding="utf-8")
            return str(output_path)
        except Exception as inner_exc:
            logger.warning("Mermaid export failed: %s", inner_exc)
            return None
