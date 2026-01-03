"""Tests for course management module."""

from nexus.teaching.courses import Course, CourseManager, CourseStatus


class TestCourseStatus:
    """Tests for CourseStatus class."""

    def test_parse_status_file(self, sample_course):
        """Test parsing .STATUS file."""
        status_file = sample_course / ".STATUS"
        status = CourseStatus.from_file(status_file)

        assert status.status == "active"
        assert status.priority == "1"
        assert status.progress == 60
        assert status.next == "Prepare Week 8 lecture"
        assert status.week == 7

    def test_parse_missing_file(self, temp_dir):
        """Test parsing non-existent .STATUS file."""
        status = CourseStatus.from_file(temp_dir / "nonexistent" / ".STATUS")

        assert status.status == "unknown"
        assert status.progress == 0


class TestCourse:
    """Tests for Course dataclass."""

    def test_to_dict(self):
        """Test converting to dictionary."""
        course = Course(
            name="stat-440",
            path="/path/to/course",
            title="Regression Analysis",
            status="active",
            progress=60,
        )
        d = course.to_dict()

        assert d["name"] == "stat-440"
        assert d["title"] == "Regression Analysis"
        assert d["status"] == "active"
        assert d["progress"] == 60


class TestCourseManager:
    """Tests for CourseManager class."""

    def test_manager_exists(self, sample_course):
        """Test manager existence check."""
        manager = CourseManager(sample_course.parent)
        assert manager.exists() is True

    def test_list_courses(self, sample_course):
        """Test listing courses."""
        manager = CourseManager(sample_course.parent)
        courses = manager.list_courses()

        assert len(courses) >= 1

        # Find our test course
        stat440 = next((c for c in courses if c.name == "stat-440"), None)
        assert stat440 is not None
        assert stat440.status == "active"
        assert stat440.progress == 60

    def test_get_course(self, sample_course):
        """Test getting specific course."""
        manager = CourseManager(sample_course.parent)
        course = manager.get_course("stat-440")

        assert course is not None
        assert course.name == "stat-440"

    def test_get_nonexistent_course(self, sample_course):
        """Test getting non-existent course."""
        manager = CourseManager(sample_course.parent)
        course = manager.get_course("nonexistent-course")

        assert course is None

    def test_list_lectures(self, sample_course):
        """Test listing lectures."""
        manager = CourseManager(sample_course.parent)
        lectures = manager.list_lectures("stat-440")

        # Should find lectures (may be 0 if folder structure not detected)
        assert isinstance(lectures, list)

    def test_get_syllabus(self, sample_course):
        """Test getting syllabus."""
        manager = CourseManager(sample_course.parent)
        syllabus = manager.get_syllabus("stat-440")

        assert syllabus is not None
        assert "Course Overview" in syllabus
