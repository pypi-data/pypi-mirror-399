"""Course management for Nexus CLI."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class CourseStatus:
    """Parsed .STATUS file for a course."""

    status: str = "unknown"
    priority: str = "--"
    progress: int = 0
    next: str = ""
    course_type: str = "teaching"
    week: int | None = None
    target: str = ""

    @classmethod
    def from_file(cls, path: Path) -> "CourseStatus":
        """Parse a .STATUS file."""
        if not path.exists():
            return cls()

        content = path.read_text()
        result = cls()

        # Parse YAML-like frontmatter
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("status:"):
                result.status = line.split(":", 1)[1].strip()
            elif line.startswith("priority:"):
                result.priority = line.split(":", 1)[1].strip()
            elif line.startswith("progress:"):
                try:
                    result.progress = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("next:"):
                result.next = line.split(":", 1)[1].strip()
            elif line.startswith("type:"):
                result.course_type = line.split(":", 1)[1].strip()
            elif line.startswith("week:"):
                try:
                    result.week = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("target:"):
                result.target = line.split(":", 1)[1].strip()

        return result


@dataclass
class QuartoConfig:
    """Parsed _quarto.yml configuration."""

    title: str = ""
    subtitle: str = ""
    author: str = ""
    formats: list[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> "QuartoConfig":
        """Parse a _quarto.yml file."""
        if not path.exists():
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            return cls()

        result = cls()

        # Get project metadata
        project = data.get("project", {})
        book = data.get("book", {})
        website = data.get("website", {})

        result.title = book.get("title") or website.get("title") or project.get("title") or data.get("title", "")
        result.subtitle = book.get("subtitle") or data.get("subtitle", "")
        result.author = book.get("author") or data.get("author", "")

        # Get format types
        if "format" in data:
            fmt = data["format"]
            if isinstance(fmt, dict):
                result.formats = list(fmt.keys())
            elif isinstance(fmt, str):
                result.formats = [fmt]

        return result


@dataclass
class Course:
    """A teaching course."""

    name: str
    path: str
    title: str = ""
    status: str = "unknown"
    progress: int = 0
    week: int | None = None
    next_action: str = ""
    formats: list[str] = field(default_factory=list)
    lecture_count: int = 0
    assignment_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "title": self.title or self.name,
            "status": self.status,
            "progress": self.progress,
            "week": self.week,
            "next_action": self.next_action,
            "formats": self.formats,
            "lecture_count": self.lecture_count,
            "assignment_count": self.assignment_count,
        }


@dataclass
class Lecture:
    """A course lecture."""

    name: str
    path: str
    course: str
    week: int | None = None
    title: str = ""
    format: str = "qmd"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "course": self.course,
            "week": self.week,
            "title": self.title or self.name,
            "format": self.format,
        }


class CourseManager:
    """Manage teaching courses."""

    def __init__(self, courses_dir: Path, materials_dir: Path | None = None):
        """Initialize course manager.

        Args:
            courses_dir: Path to courses directory (e.g., ~/projects/teaching)
            materials_dir: Path to teaching materials (e.g., ~/Documents/Teaching)
        """
        self.courses_dir = Path(courses_dir).expanduser()
        self.materials_dir = Path(materials_dir).expanduser() if materials_dir else None

    def exists(self) -> bool:
        """Check if courses directory exists."""
        return self.courses_dir.exists()

    def list_courses(self) -> list[Course]:
        """List all courses in the courses directory."""
        if not self.exists():
            return []

        courses = []
        for course_path in sorted(self.courses_dir.iterdir()):
            if not course_path.is_dir():
                continue
            if course_path.name.startswith("."):
                continue

            course = self._load_course(course_path)
            if course:
                courses.append(course)

        return courses

    def get_course(self, name: str) -> Course | None:
        """Get a specific course by name."""
        course_path = self.courses_dir / name
        if not course_path.exists():
            # Try case-insensitive match
            for p in self.courses_dir.iterdir():
                if p.name.lower() == name.lower():
                    course_path = p
                    break
            else:
                return None

        return self._load_course(course_path)

    def _load_course(self, course_path: Path) -> Course | None:
        """Load course data from a directory."""
        if not course_path.is_dir():
            return None

        # Parse .STATUS file
        status_file = course_path / ".STATUS"
        status = CourseStatus.from_file(status_file)

        # Parse _quarto.yml
        quarto_file = course_path / "_quarto.yml"
        quarto = QuartoConfig.from_file(quarto_file)

        # Count lectures
        lecture_count = self._count_lectures(course_path)

        # Count assignments
        assignment_count = self._count_assignments(course_path)

        return Course(
            name=course_path.name,
            path=str(course_path),
            title=quarto.title or course_path.name,
            status=status.status,
            progress=status.progress,
            week=status.week,
            next_action=status.next,
            formats=quarto.formats,
            lecture_count=lecture_count,
            assignment_count=assignment_count,
        )

    def _count_lectures(self, course_path: Path) -> int:
        """Count lecture files in a course."""
        count = 0
        for pattern in ["lectures/*.qmd", "slides/*.qmd", "weeks/*.qmd"]:
            count += len(list(course_path.glob(pattern)))
        # Also count week-* files in root
        count += len(list(course_path.glob("week-*.qmd")))
        return count

    def _count_assignments(self, course_path: Path) -> int:
        """Count assignment files in a course."""
        count = 0
        for pattern in ["assignments/*.qmd", "homework/*.qmd", "labs/*.qmd"]:
            count += len(list(course_path.glob(pattern)))
        return count

    def list_lectures(self, course_name: str) -> list[Lecture]:
        """List all lectures for a course."""
        course = self.get_course(course_name)
        if not course:
            return []

        course_path = Path(course.path)
        lectures = []

        # Find lecture files in various locations
        lecture_patterns = [
            ("lectures", "lectures/*.qmd"),
            ("slides", "slides/*.qmd"),
            ("weeks", "weeks/*.qmd"),
            ("root", "week-*.qmd"),
            ("root", "_week-*.qmd"),
        ]

        for location, pattern in lecture_patterns:
            for qmd_file in sorted(course_path.glob(pattern)):
                lecture = self._parse_lecture(qmd_file, course_name)
                if lecture:
                    lectures.append(lecture)

        return lectures

    def _parse_lecture(self, qmd_path: Path, course_name: str) -> Lecture | None:
        """Parse a lecture file."""
        name = qmd_path.stem

        # Try to extract week number from filename
        week = None
        week_match = re.search(r"week[-_]?(\d+)", name, re.IGNORECASE)
        if week_match:
            week = int(week_match.group(1))

        # Try to extract title from file
        title = ""
        try:
            content = qmd_path.read_text()
            # Check YAML frontmatter
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    frontmatter = content[3:end]
                    for line in frontmatter.split("\n"):
                        if line.strip().startswith("title:"):
                            title = line.split(":", 1)[1].strip().strip("\"'")
                            break
        except Exception:
            pass

        return Lecture(
            name=name,
            path=str(qmd_path),
            course=course_name,
            week=week,
            title=title or name.replace("-", " ").replace("_", " ").title(),
            format="qmd",
        )

    def get_current_week_lectures(self, course_name: str) -> list[Lecture]:
        """Get lectures for the current week."""
        course = self.get_course(course_name)
        if not course or not course.week:
            return []

        lectures = self.list_lectures(course_name)
        return [l for l in lectures if l.week == course.week]

    def search_lectures(self, query: str) -> list[Lecture]:
        """Search for lectures across all courses."""
        results = []
        pattern = re.compile(query, re.IGNORECASE)

        for course in self.list_courses():
            for lecture in self.list_lectures(course.name):
                if pattern.search(lecture.name) or pattern.search(lecture.title):
                    results.append(lecture)

        return results

    def get_syllabus(self, course_name: str) -> str | None:
        """Get the syllabus content for a course."""
        course = self.get_course(course_name)
        if not course:
            return None

        course_path = Path(course.path)

        # Try common syllabus locations
        syllabus_files = [
            "syllabus.qmd",
            "syllabus.md",
            "_syllabus.qmd",
            "00-syllabus.qmd",
            "docs/syllabus.qmd",
        ]

        for filename in syllabus_files:
            syllabus_path = course_path / filename
            if syllabus_path.exists():
                return syllabus_path.read_text()

        return None

    def get_materials(self, course_name: str) -> list[dict]:
        """List teaching materials for a course."""
        course = self.get_course(course_name)
        if not course:
            return []

        materials = []
        course_path = Path(course.path)

        # Collect different types of materials
        material_types = {
            "lectures": ["lectures/*.qmd", "slides/*.qmd"],
            "assignments": ["assignments/*.qmd", "homework/*.qmd"],
            "labs": ["labs/*.qmd"],
            "exams": ["exams/*.qmd", "midterm*.qmd", "final*.qmd"],
            "resources": ["resources/*", "handouts/*"],
        }

        for mat_type, patterns in material_types.items():
            for pattern in patterns:
                for file_path in course_path.glob(pattern):
                    materials.append(
                        {
                            "type": mat_type,
                            "name": file_path.stem,
                            "path": str(file_path),
                            "format": file_path.suffix[1:] if file_path.suffix else "unknown",
                        }
                    )

        return materials
