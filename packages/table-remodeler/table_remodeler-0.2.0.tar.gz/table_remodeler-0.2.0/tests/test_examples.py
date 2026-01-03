"""Tests for example Jupyter notebooks to ensure they execute without errors."""

import unittest
import subprocess
import tempfile
from pathlib import Path


class TestExampleNotebooks(unittest.TestCase):
    """Test that example notebooks execute successfully."""

    @classmethod
    def setUpClass(cls):
        """Set up paths for notebook testing."""
        cls.repo_root = Path(__file__).parent.parent
        cls.examples_dir = cls.repo_root / "examples"

        # Check if examples directory exists
        if not cls.examples_dir.exists():
            cls.skip_tests = True
            return

        # Find all notebook files
        cls.notebooks = list(cls.examples_dir.glob("*.ipynb"))
        cls.skip_tests = len(cls.notebooks) == 0

    def setUp(self):
        """Skip tests if no notebooks are present."""
        if self.skip_tests:
            self.skipTest("No example notebooks found in examples/ directory")

    def _execute_notebook(self, notebook_path):
        """
        Execute a Jupyter notebook and check for errors.

        Parameters:
            notebook_path (Path): Path to the notebook file.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Create a temporary directory for output
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = Path(tmpdir) / notebook_path.name

                # Execute notebook using nbconvert
                result = subprocess.run(
                    [
                        "jupyter",
                        "nbconvert",
                        "--to",
                        "notebook",
                        "--execute",
                        "--output",
                        str(output_path),
                        str(notebook_path),
                        "--ExecutePreprocessor.timeout=300",  # 5 minute timeout
                    ],
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )

                if result.returncode != 0:
                    # Check if it's a missing kernel error
                    if "No such kernel" in result.stderr:
                        return False, "SKIP_KERNEL_MISSING"
                    return False, f"Execution failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

                return True, None

        except FileNotFoundError:
            return False, "jupyter nbconvert not found. Install with: pip install jupyter nbconvert"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def test_all_notebooks_execute(self):
        """Test that all example notebooks execute without errors."""
        if not self.notebooks:
            self.skipTest("No notebooks to test")

        failures = []
        kernel_missing = False

        for notebook in self.notebooks:
            with self.subTest(notebook=notebook.name):
                success, error = self._execute_notebook(notebook)
                if not success:
                    if error == "SKIP_KERNEL_MISSING":
                        kernel_missing = True
                    else:
                        failures.append((notebook.name, error))

        # Skip test if kernel is missing (common in CI without ipykernel installed)
        if kernel_missing and not failures:
            self.skipTest(
                "Python kernel not available. Install with: pip install ipykernel && python -m ipykernel install --user"
            )

        # Report all failures at once
        if failures:
            failure_report = "\n\n".join([f"Notebook: {name}\n{error}" for name, error in failures])
            self.fail(f"The following notebooks failed to execute:\n\n{failure_report}")

    def test_notebooks_exist(self):
        """Verify that example notebooks are present."""
        self.assertGreater(len(self.notebooks), 0, "No example notebooks found in examples/ directory")


if __name__ == "__main__":
    unittest.main()
