"""Pytest fixtures for Nexus CLI tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_vault(temp_dir):
    """Create a sample Obsidian vault structure."""
    vault_path = temp_dir / "vault"
    vault_path.mkdir()

    # Create .obsidian folder (marks it as a vault)
    (vault_path / ".obsidian").mkdir()

    # Create PARA structure
    for folder in ["00-INBOX", "10-PROJECTS", "20-AREAS", "30-RESOURCES", "40-ARCHIVE"]:
        (vault_path / folder).mkdir()

    # Create some sample notes
    (vault_path / "10-PROJECTS" / "test-project.md").write_text("""---
type: project
status: active
tags: [research, mediation]
---

# Test Project

This is a test project about mediation analysis.
""")

    (vault_path / "20-AREAS" / "causal-inference.md").write_text("""---
type: area
tags: [causal-inference, methods]
---

# Causal Inference

Notes about causal inference methods.

See also: [[test-project]]
""")

    return vault_path


@pytest.fixture
def sample_manuscript(temp_dir):
    """Create a sample manuscript structure."""
    ms_path = temp_dir / "manuscripts" / "test-paper"
    ms_path.mkdir(parents=True)

    # Create .STATUS file
    (ms_path / ".STATUS").write_text("""status: draft
priority: 2
progress: 45
next: Complete methods section
type: research
target: JASA
""")

    # Create _quarto.yml
    (ms_path / "_quarto.yml").write_text("""project:
  type: manuscript

manuscript:
  article: index.qmd

title: "Test Paper Title"
author:
  - name: Test Author
    affiliation: Test University
""")

    # Create main file
    (ms_path / "index.qmd").write_text("""---
title: "Test Paper"
---

# Introduction

This is a test paper about @MacKinnon2008 mediation analysis.

We also cite @VanderWeele2015 for sensitivity.

# Methods

The methods section discusses [@Baron1986; @Sobel1982].
""")

    # Create .bib file
    (ms_path / "references.bib").write_text("""@book{MacKinnon2008,
  author = {MacKinnon, David P.},
  title = {Introduction to Statistical Mediation Analysis},
  publisher = {Lawrence Erlbaum Associates},
  year = {2008},
  doi = {10.4324/9780203809556}
}

@article{VanderWeele2015,
  author = {VanderWeele, Tyler J.},
  title = {Explanation in Causal Inference},
  journal = {Epidemiology},
  year = {2015},
  volume = {26},
  pages = {805-810}
}

@article{Baron1986,
  author = {Baron, Reuben M. and Kenny, David A.},
  title = {The Moderator-Mediator Variable Distinction},
  journal = {Journal of Personality and Social Psychology},
  year = {1986},
  volume = {51},
  pages = {1173-1182}
}

@article{UnusedEntry,
  author = {Nobody, No One},
  title = {This entry is not cited},
  journal = {Fake Journal},
  year = {2020}
}
""")

    return ms_path


@pytest.fixture
def sample_course(temp_dir):
    """Create a sample course structure."""
    course_path = temp_dir / "courses" / "stat-440"
    course_path.mkdir(parents=True)

    # Create .STATUS file
    (course_path / ".STATUS").write_text("""status: active
priority: 1
progress: 60
next: Prepare Week 8 lecture
type: course
week: 7
""")

    # Create _quarto.yml
    (course_path / "_quarto.yml").write_text("""project:
  type: website
  output-dir: _output

website:
  title: "STAT 440: Regression Analysis"

format:
  html:
    theme: cosmo
""")

    # Create syllabus
    (course_path / "syllabus.qmd").write_text("""---
title: "STAT 440 Syllabus"
---

# Course Overview

This course covers regression analysis.
""")

    # Create lectures folder
    lectures = course_path / "lectures"
    lectures.mkdir()
    for i in range(1, 4):
        lec_folder = lectures / f"{i:02d}-topic{i}"
        lec_folder.mkdir()
        (lec_folder / "slides.qmd").write_text(f"""---
title: "Lecture {i}"
format: revealjs
---

# Topic {i}

Content for lecture {i}.
""")

    return course_path


@pytest.fixture
def sample_bib_content():
    """Return sample BibTeX content."""
    return """@article{Test2024,
  author = {Test, Author One and Test, Author Two},
  title = {A Test Article About Testing},
  journal = {Journal of Testing},
  year = {2024},
  volume = {1},
  pages = {1-10},
  doi = {10.1234/test.2024}
}

@book{Book2023,
  author = {Writer, Famous},
  title = {The Complete Guide to Everything},
  publisher = {Big Publisher},
  year = {2023}
}

@inproceedings{Conf2022,
  author = {Speaker, Great},
  title = {Conference Talk Title},
  booktitle = {Proceedings of Important Conference},
  year = {2022},
  pages = {100-110}
}
"""
