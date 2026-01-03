---
name: nexus-teaching
description: Course management, Quarto operations, and teaching material workflows
---

# Nexus Teaching Domain

**Course management and Quarto operations for academic teaching**

Use this skill when working on: managing courses, building lecture materials, previewing Quarto documents, tracking course progress, or organizing teaching workflows.

---

## Command Reference

### Course Operations

```bash
# List all courses
nexus teach course list
nexus teach course list --all  # Include archived

# Show course details
nexus teach course show COURSE_NAME

# List lectures
nexus teach course lectures COURSE_NAME

# Get course materials
nexus teach course materials COURSE_NAME

# View syllabus
nexus teach course syllabus COURSE_NAME
```

### Quarto Operations

```bash
# Build document/project
nexus teach quarto build /path/to/project
nexus teach quarto build /path/to/file.qmd --format pdf

# Preview with live reload
nexus teach quarto preview /path/to/project
nexus teach quarto preview /path/to/project --port 4200

# Get project info
nexus teach quarto info /path/to/project

# Clean build artifacts
nexus teach quarto clean /path/to/project

# List output formats
nexus teach quarto formats /path/to/project
```

---

## Detailed Command Reference

### `nexus teach course list`

List all courses with status and progress:

```bash
# Active courses only
nexus teach course list

# Include archived
nexus teach course list --all

# JSON output
nexus teach course list --json
```

**Output includes:**
- Course name and title
- Status (active, complete, planning)
- Progress bar
- Lecture count
- Next action

### `nexus teach course show`

Detailed view of a specific course:

```bash
nexus teach course show stat-440
nexus teach course show stat-440 --json
```

**Shows:**
- Full title and description
- Status and progress
- Lecture count
- Assignment count
- Next action

### `nexus teach course lectures`

List all lectures for a course:

```bash
nexus teach course lectures stat-440
nexus teach course lectures stat-440 --json
```

### `nexus teach course materials`

Find teaching materials:

```bash
nexus teach course materials stat-440
```

### `nexus teach course syllabus`

Display course syllabus:

```bash
nexus teach course syllabus stat-440
```

---

## Quarto Commands

### `nexus teach quarto build`

Build Quarto documents/projects:

```bash
# Build project (default format)
nexus teach quarto build /path/to/course

# Specific format
nexus teach quarto build /path/to/course --format html
nexus teach quarto build /path/to/course --format pdf

# Build specific file
nexus teach quarto build /path/to/lecture.qmd
```

### `nexus teach quarto preview`

Start live preview server:

```bash
nexus teach quarto preview /path/to/course
nexus teach quarto preview /path/to/course --port 4200
```

### `nexus teach quarto info`

Get project configuration:

```bash
nexus teach quarto info /path/to/course
nexus teach quarto info /path/to/course --json
```

### `nexus teach quarto clean`

Remove build artifacts:

```bash
nexus teach quarto clean /path/to/course
```

### `nexus teach quarto formats`

List available output formats:

```bash
nexus teach quarto formats /path/to/course
```

---

## Course Directory Structure

```
course-name/
├── .STATUS              # Course status (required)
├── _quarto.yml          # Quarto configuration
├── syllabus.qmd         # Course syllabus
├── lectures/
│   ├── 01-introduction/
│   │   └── slides.qmd
│   └── 02-regression/
│       └── slides.qmd
├── assignments/
│   └── hw01.qmd
└── _output/             # Built artifacts
```

### .STATUS File Format

```yaml
status: active
priority: 1
progress: 60
next: Prepare Week 8 lecture
type: course
week: 7
```

---

## Common Workflows

### Weekly Lecture Prep

```bash
# Check current status
nexus teach course show stat-440

# List upcoming lectures
nexus teach course lectures stat-440

# Preview lecture slides
nexus teach quarto preview ~/projects/teaching/stat-440/lectures/08/slides.qmd
```

### Build and Deploy

```bash
# Build entire course
nexus teach quarto build ~/projects/teaching/stat-440

# Check output
ls ~/projects/teaching/stat-440/_output/
```

### Course Dashboard

```bash
# All courses status
nexus teach course list --json | jq -r '.[] | "\(.name): \(.progress)%"'
```

---

## Status Emojis

| Status | Emoji |
|--------|-------|
| active | 🔥 |
| planning | 📋 |
| paused | ⏸️ |
| complete | ✅ |
| archived | 📦 |

---

## Troubleshooting

### Courses Not Found

```bash
nexus doctor
nexus config
```

### Quarto Build Errors

```bash
quarto check
nexus teach quarto info /path --json
```

---

**Version**: 1.0.0
**Commands**: `nexus teach course list|show|lectures|materials|syllabus`, `nexus teach quarto build|preview|info|clean|formats`
