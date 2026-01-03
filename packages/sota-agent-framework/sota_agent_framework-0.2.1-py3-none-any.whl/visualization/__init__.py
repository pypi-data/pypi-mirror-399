"""
Visualization & Debugging Module

Production-grade visualization and debugging tools for agent workflows:
- Execution graph visualizer
- Trace timeline
- Tool call replay
- Prompt version comparison
- Agent decision inspection
- Explainability ("why did the agent do this?")
- Gradio UI for interactive exploration

Install:
    pip install sota-agent-framework[ui]

Usage:
    from visualization import ExecutionVisualizer, TraceTimeline, launch_ui
    
    # Visualize execution
    viz = ExecutionVisualizer()
    graph = viz.create_graph(execution_trace)
    
    # Launch UI
    launch_ui(port=7860)
"""

from .graph import (
    ExecutionVisualizer,
    ExecutionGraph,
    GraphNode,
    GraphEdge
)

from .timeline import (
    TraceTimeline,
    TimelineEvent,
    TimelineRenderer
)

from .replay import (
    ToolCallReplayer,
    ReplaySession,
    ReplayResult
)

from .comparison import (
    PromptComparator,
    VersionDiff,
    PromptVersion
)

from .inspector import (
    DecisionInspector,
    Decision,
    DecisionPath,
    DecisionExplainer
)

from .explainer import (
    AgentExplainer,
    Explanation,
    ExplanationType
)

from .ui import (
    launch_ui,
    create_dashboard,
    ExecutionDashboard
)

__all__ = [
    # Graph
    "ExecutionVisualizer",
    "ExecutionGraph",
    "GraphNode",
    "GraphEdge",
    
    # Timeline
    "TraceTimeline",
    "TimelineEvent",
    "TimelineRenderer",
    
    # Replay
    "ToolCallReplayer",
    "ReplaySession",
    "ReplayResult",
    
    # Comparison
    "PromptComparator",
    "VersionDiff",
    "PromptVersion",
    
    # Inspector
    "DecisionInspector",
    "Decision",
    "DecisionPath",
    "DecisionExplainer",
    
    # Explainer
    "AgentExplainer",
    "Explanation",
    "ExplanationType",
    
    # UI
    "launch_ui",
    "create_dashboard",
    "ExecutionDashboard",
]

