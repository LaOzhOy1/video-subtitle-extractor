import os
import config
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None

def run_extractor(video_path: str, subtitle_area: tuple | None, extractor_cls):
    se = extractor_cls(video_path, subtitle_area, True)
    se.run()
    return os.path.splitext(video_path)[0] + ".srt"

def start_mcp(name: str, host: str, port: int, extractor_cls):
    if FastMCP is None:
        return
    mcp = FastMCP(name=name, host=host, port=port)

    @mcp.prompt(name="extract_subtitles_prompt", description="Extract SRT from a video. video_path is required; sub_area is optional [ymin,ymax,xmin,xmax].")
    def describe_extract_subtitles(video_path: str, sub_area: list | tuple | None = None) -> str:
        return (
            "Tool: extract_subtitles\n"
            "Purpose: Extract hard subtitles from a video file into an SRT.\n"
            "Required: video_path (absolute path to the video).\n"
            "Optional: sub_area as [ymin,ymax,xmin,xmax] to constrain detection.\n"
            "If sub_area is omitted, the default detection area is used."
        )

    @mcp.tool(name="extract_subtitles")
    def extract_subtitles_tool(video_path: str, sub_area: list | tuple | None = None) -> dict:
        subtitle_area = None
        if sub_area is not None and isinstance(sub_area, (list, tuple)) and len(sub_area) == 4:
            y_min, y_max, x_min, x_max = sub_area
            subtitle_area = (int(y_min), int(y_max), int(x_min), int(x_max))
        srt_path = run_extractor(video_path, subtitle_area, extractor_cls)
        return {"srt_path": srt_path}

    mcp.run(transport="sse")

def start_mcp_from_config(extractor_cls):
    if FastMCP is None:
        return False
    enable_mcp = getattr(config, 'MCP_ENABLED', False)
    host = getattr(config, 'MCP_HOST', '127.0.0.1')
    port = getattr(config, 'MCP_PORT', 30002)
    if not enable_mcp:
        return False
    start_mcp("video-subtitle-extractor", host, port, extractor_cls)
    return True
