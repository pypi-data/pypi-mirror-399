"""Test runs each notebook in the docs/Examples directory."""

from pathlib import Path

import pytest
from nbclient import NotebookClient
from nbformat import read

# Only run if certain packages are installed
pynhd = pytest.importorskip("pynhd")
hvplot = pytest.importorskip("hvplot")
nbformat = pytest.importorskip("nbformat")


NOTEBOOK_DIR = Path("docs/Examples")


def get_notebooks():
    """Find all Jupyter notebooks in the Examples directory."""
    return list(NOTEBOOK_DIR.rglob("*.ipynb"))


@pytest.mark.parametrize("notebook_path", get_notebooks(), ids=lambda p: p.name)
def test_notebook_execution(notebook_path) -> None:
    """Runs each notebook and reports failures with the cell that caused the error."""
    with open(notebook_path, encoding="utf-8") as f:
        nb = read(f, as_version=4)

    client = NotebookClient(nb, timeout=600, allow_errors=True)

    try:
        client.execute()
    except Exception as e:
        for i, cell in enumerate(nb.cells):
            if cell.get("outputs"):
                for output in cell["outputs"]:
                    if output.output_type == "error":
                        pytest.fail(
                            f"Notebook {notebook_path.name} failed on cell {i}: {output['ename']}: {output['evalue']}"
                        )
        pytest.fail(f"Notebook {notebook_path.name} execution failed: {e}")
