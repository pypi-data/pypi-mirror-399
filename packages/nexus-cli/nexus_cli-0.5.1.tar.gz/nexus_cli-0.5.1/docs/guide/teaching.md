# Teaching Domain

The Teaching domain helps manage courses and Quarto-based teaching materials.

## Course Management

### Listing Courses

```bash
# List all courses
nexus teach course list

# Active courses only
nexus teach course list --active

# JSON output
nexus teach course list --json
```

### Course Details

```bash
nexus teach course show stat-440
```

## Quarto Integration

### Building Documents

```bash
# Build with default format
nexus teach quarto build slides.qmd

# Specific format
nexus teach quarto build slides.qmd --format revealjs
nexus teach quarto build notes.qmd --format pdf
```

### Preview Server

```bash
# Start preview (default port 4200)
nexus teach quarto preview course-site/

# Custom port
nexus teach quarto preview . --port 8080
```

### Check Dependencies

```bash
nexus teach quarto check course-dir/
```

### Clean Build Artifacts

```bash
nexus teach quarto clean course-dir/
```

## Configuration

```yaml
teaching:
  courses_dir: ~/projects/teaching
  active_semester: Fall 2025
```

## Course Directory Structure

```
stat-440/
├── .STATUS           # Course status file
├── _quarto.yml       # Quarto config
├── lectures/
│   ├── week-01.qmd
│   └── week-02.qmd
├── labs/
└── exams/
```

## Requirements

- **Quarto**: `brew install quarto`
- **TinyTeX** (for PDF): `quarto install tinytex`
