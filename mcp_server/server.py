import sys
from pathlib import Path

# Make project root importable
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP

from app import app
from tools.college_compare import compare_colleges
from tools.college_recommend import recommend_colleges
from tools.document_search import search_documents
from tools.college_search import search_colleges

mcp = FastMCP("College Predictor")

app.app_context().push()


@mcp.tool(name="search_colleges")
def search_colleges_mcp(
    exam: str,
    category: str,
    quota: str,
    rank: int,
):
    return search_colleges(
        exam,
        category,
        quota,
        rank,
    )

@mcp.tool(name="compare_colleges")
def compare_colleges_mcp(
    college_1: str,
    branch_1: str,
    college_2: str,
    branch_2: str,
):
    return compare_colleges(
        college_1,
        branch_1,
        college_2,
        branch_2,
    )

@mcp.tool(name="recommend_colleges")
def recommend_colleges_mcp(
    exam: str,
    category: str,
    quota: str,
    rank: int,
    preferred_branch: str = None,
    budget: int = None,
):
    return recommend_colleges(
        exam,
        category,
        quota,
        rank,
        preferred_branch,
        budget,
    )

@mcp.tool(name="search_documents")
def search_documents_mcp(
    query: str,
):
    return search_documents(query)


if __name__ == "__main__":
    mcp.run()