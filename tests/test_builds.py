"""
Modules test that builds with different setting succeed.

Note that pytest offers a `tmp_path`. 
You can reproduce locally with

```python
%load_ext autoreload
%autoreload 2
import os
import tempfile
import shutil
from pathlib import Path
tmp_path = Path(tempfile.gettempdir()) / 'pytest-table-builder'
if os.path.exists(tmp_path):
    shutil.rmtree(tmp_path)
os.mkdir(tmp_path)
```
"""

import re
import os
import shutil
import logging
from click.testing import CliRunner
from mkdocs.__main__ import build_command


def setup_clean_mkdocs_folder(mkdocs_yml_path, output_path):
    """
    Sets up a clean mkdocs directory
    
    outputpath/testproject
    ├── docs/
    └── mkdocs.yml
    
    Args:
        mkdocs_yml_path (Path): Path of mkdocs.yml file to use
        output_path (Path): Path of folder in which to create mkdocs project
        
    Returns:
        testproject_path (Path): Path to test project
    """

    testproject_path = output_path / "testproject"

    # Create empty 'testproject' folder
    if os.path.exists(str(testproject_path)):
        logging.warning(
            """This command does not work on windows. 
        Refactor your test to use setup_clean_mkdocs_folder() only once"""
        )
        shutil.rmtree(str(testproject_path))

    # Copy correct mkdocs.yml file and our test 'docs/'
    yml_dir = os.path.dirname(mkdocs_yml_path)
    shutil.copytree(yml_dir, str(testproject_path))
    shutil.copyfile(mkdocs_yml_path, str(testproject_path / "mkdocs.yml"))

    return testproject_path


def build_docs_setup(testproject_path):
    """
    Runs the `mkdocs build` command
    
    Args:
        testproject_path (Path): Path to test project
    
    Returns:
        command: Object with results of command
    """

    cwd = os.getcwd()
    os.chdir(str(testproject_path))

    try:
        run = CliRunner().invoke(build_command)
        os.chdir(cwd)
        return run
    except:
        os.chdir(cwd)
        raise


def test_basic_build(tmp_path):

    # Basic docs/ folder has bad page 'zero_h1.md'
    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/simple/mkdocs.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert (
        result.exit_code == 1
    ), "'mkdocs build' command succeeded but should have failed"

    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/simple/mkdocs_notstrict.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    index_file = tmp_proj / "site/index.html"
    assert index_file.exists(), "%s does not exist" % index_file

    # index.html is always first page, so should have chapter 1
    contents = index_file.read_text(encoding="utf-8")
    assert re.search(r"1.</span> Homepage", contents)
    assert re.search(r"1.2.1</span> sub heading three deep", contents)

    # 'a_third_page.md` is first alphabetical, but second due to index.md
    third_page = tmp_proj / "site/a_third_page.html"
    contents = third_page.read_text(encoding="utf-8")
    assert re.search(r"2.</span> Normal", contents)

    # 'zero_h1.md' is follows a page with 2 headings
    second_page = tmp_proj / "site/zero_h1.html"
    contents = second_page.read_text(encoding="utf-8")
    assert re.search(r"4.0.0.1</span> Zero h1", contents)


def test_build_with_nav(tmp_path):

    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/simple/mkdocs_with_nav.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    index_file = tmp_proj / "site/index.html"
    assert index_file.exists(), "%s does not exist" % index_file

    # index.html is always first page, so should have chapter 1
    contents = index_file.read_text(encoding="utf-8")
    assert re.search(r"1.</span> Homepage", contents)
    assert re.search(r"1.2.1</span> sub heading three deep", contents)

    # 'second_page' is 2+1 = third.
    second_page = tmp_proj / "site/two_h1.html"
    contents = second_page.read_text(encoding="utf-8")
    assert re.search(r"2.</span> Two h1", contents)
    assert re.search(r"3.</span> Second level 1 heading", contents)

    # 'a_third_page.md`
    third_page = tmp_proj / "site/a_third_page.html"
    contents = third_page.read_text(encoding="utf-8")
    assert re.search(r"4.</span> Normal", contents)


def test_compatibility_monorepo_plugin1(tmp_path):
    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/monorepo_ok/mkdocs.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    page = tmp_proj / "site/test/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"2.</span> Hello world!", contents)


def test_compatibility_monorepo_plugin2(tmp_path):
    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/monorepo_ok/mkdocs_enum_first.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    page = tmp_proj / "site/test/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"2.</span> Hello world!", contents)


def test_compatibility_monorepo_plugin3(tmp_path):
    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/monorepo_sample_docs/mkdocs.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    page = tmp_proj / "site/versions/v2/changelog/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"7.</span> Changelog", contents)


def test_compatibility_monorepo_plugin4(tmp_path):
    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/monorepo_sample_docs/mkdocs_enum_first.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    page = tmp_proj / "site/versions/v2/changelog/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"7.</span> Changelog", contents)


def test_compatibility_awesomepages_plugin1(tmp_path):
    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/awesome_pages/mkdocs.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    page = tmp_proj / "site/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"5.</span> Homepage", contents)

    page = tmp_proj / "site/section2/page4/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"1.</span> Page 4", contents)


def test_compatibility_awesomepages_plugin2(tmp_path):
    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/awesome_pages/mkdocs_enum_first.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    page = tmp_proj / "site/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"5.</span> Homepage", contents)

    page = tmp_proj / "site/section2/page4/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"1.</span> Page 4", contents)


def test_compatibility_pymarkx_snippets1(tmp_path):

    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/pymarkx_snippet/mkdocs.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    page = tmp_proj / "site/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"1.</span> Homepage", contents)

    page = tmp_proj / "site/snippet.html"
    contents = page.read_text(encoding="utf-8")
    # First check if content was inserted
    assert re.search(r"Extra page</h1>", contents)
    # Then check if enumeration was done
    assert re.search(r"3.</span> Extra page", contents)


def test_compatibility_pymarkx_snippets2(tmp_path):

    tmp_proj = setup_clean_mkdocs_folder(
        "tests/fixtures/projects/pymarkx_snippet/mkdocs_with_nav.yml", tmp_path
    )
    result = build_docs_setup(tmp_proj)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    page = tmp_proj / "site/index.html"
    contents = page.read_text(encoding="utf-8")
    assert re.search(r"1.</span> Homepage", contents)

    page = tmp_proj / "site/snippet.html"
    contents = page.read_text(encoding="utf-8")
    # First check if content was inserted
    assert re.search(r"Extra page</h1>", contents)
    # Then check if enumeration was done
    assert re.search(r"2.</span> Extra page", contents)
