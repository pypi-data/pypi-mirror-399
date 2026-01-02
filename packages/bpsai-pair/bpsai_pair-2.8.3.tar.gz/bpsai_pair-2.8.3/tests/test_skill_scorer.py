"""Tests for skill quality scorer."""

import pytest
from pathlib import Path

from bpsai_pair.skills.scorer import (
    DimensionScore,
    SkillScore,
    SkillScorer,
    score_skills,
    format_skill_score,
    format_score_table,
)


class TestDimensionScore:
    """Tests for DimensionScore dataclass."""

    def test_create_dimension_score(self):
        """Test creating a dimension score."""
        score = DimensionScore(
            name="token_efficiency",
            weight=0.25,
            score=0.8,
            reason="Good efficiency",
        )
        assert score.name == "token_efficiency"
        assert score.weight == 0.25
        assert score.score == 0.8
        assert score.reason == "Good efficiency"

    def test_weighted_score_property(self):
        """Test weighted score calculation."""
        score = DimensionScore(
            name="test",
            weight=0.25,
            score=0.8,
            reason="Test",
        )
        assert score.weighted_score == 0.2  # 0.25 * 0.8

    def test_to_dict(self):
        """Test converting to dictionary."""
        score = DimensionScore(
            name="completeness",
            weight=0.20,
            score=0.9,
            reason="Very complete",
            recommendations=["Add more examples"],
        )
        d = score.to_dict()
        assert d["name"] == "completeness"
        assert d["weight"] == 0.20
        assert d["score"] == 0.9
        assert abs(d["weighted_score"] - 0.18) < 0.001
        assert "Add more examples" in d["recommendations"]


class TestSkillScore:
    """Tests for SkillScore dataclass."""

    def test_create_skill_score(self, tmp_path):
        """Test creating a skill score."""
        score = SkillScore(
            skill_name="test-skill",
            skill_path=tmp_path / "test-skill" / "SKILL.md",
            overall_score=85,
            dimensions=[],
            recommendations=["Add trigger section"],
            grade="B",
        )
        assert score.skill_name == "test-skill"
        assert score.overall_score == 85
        assert score.grade == "B"

    def test_to_dict(self, tmp_path):
        """Test converting to dictionary."""
        score = SkillScore(
            skill_name="test-skill",
            skill_path=tmp_path / "test-skill" / "SKILL.md",
            overall_score=75,
            dimensions=[
                DimensionScore("test", 0.25, 0.8, "Test reason"),
            ],
            recommendations=["Improve clarity"],
            grade="C",
        )
        d = score.to_dict()
        assert d["skill_name"] == "test-skill"
        assert d["overall_score"] == 75
        assert d["grade"] == "C"
        assert len(d["dimensions"]) == 1


class TestSkillScorer:
    """Tests for SkillScorer class."""

    @pytest.fixture
    def skills_dir(self, tmp_path):
        """Create a skills directory with test skills."""
        skills = tmp_path / "skills"
        skills.mkdir()
        return skills

    @pytest.fixture
    def good_skill(self, skills_dir):
        """Create a well-structured skill."""
        skill_dir = skills_dir / "good-skill"
        skill_dir.mkdir()
        content = """---
name: good-skill
description: A well-structured skill for testing that helps with development
---

# Good Skill

## Trigger

Use when you need to test something.

## Workflow

1. First step
2. Second step
3. Third step

## Examples

```python
# Example code
print("Hello")
```

## Output

Expected output description.
"""
        (skill_dir / "SKILL.md").write_text(content)
        return skill_dir

    @pytest.fixture
    def minimal_skill(self, skills_dir):
        """Create a minimal skill."""
        skill_dir = skills_dir / "minimal-skill"
        skill_dir.mkdir()
        content = """---
name: minimal-skill
description: Minimal
---

# Minimal Skill

Just some text without structure.
"""
        (skill_dir / "SKILL.md").write_text(content)
        return skill_dir

    def test_init_default(self, skills_dir):
        """Test default initialization."""
        scorer = SkillScorer(skills_dir)
        assert scorer.skills_dir == skills_dir
        assert scorer.usage_data == {}

    def test_init_with_usage_data(self, skills_dir):
        """Test initialization with usage data."""
        usage = {"skill1": 10, "skill2": 5}
        scorer = SkillScorer(skills_dir, usage_data=usage)
        assert scorer.usage_data == usage

    def test_weights_sum_to_one(self):
        """Test that dimension weights sum to 1.0."""
        total = sum(SkillScorer.WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_score_skill_not_found(self, skills_dir):
        """Test scoring a non-existent skill returns None."""
        scorer = SkillScorer(skills_dir)
        result = scorer.score_skill("nonexistent")
        assert result is None

    def test_score_good_skill(self, skills_dir, good_skill):
        """Test scoring a well-structured skill."""
        scorer = SkillScorer(skills_dir)
        result = scorer.score_skill("good-skill")

        assert result is not None
        assert result.skill_name == "good-skill"
        assert result.overall_score >= 50  # Should score well
        assert len(result.dimensions) == 5

    def test_score_minimal_skill(self, skills_dir, minimal_skill):
        """Test scoring a minimal skill gets lower score."""
        scorer = SkillScorer(skills_dir)
        result = scorer.score_skill("minimal-skill")

        assert result is not None
        assert result.skill_name == "minimal-skill"
        assert len(result.recommendations) > 0  # Should have improvement suggestions

    def test_score_all(self, skills_dir, good_skill, minimal_skill):
        """Test scoring all skills."""
        scorer = SkillScorer(skills_dir)
        results = scorer.score_all()

        assert len(results) == 2
        # Should be sorted by score (good-skill should be first)
        assert results[0].skill_name == "good-skill"

    def test_calculate_grade(self, skills_dir):
        """Test grade calculation."""
        scorer = SkillScorer(skills_dir)
        assert scorer._calculate_grade(95) == "A"
        assert scorer._calculate_grade(85) == "B"
        assert scorer._calculate_grade(75) == "C"
        assert scorer._calculate_grade(65) == "D"
        assert scorer._calculate_grade(55) == "F"

    def test_parse_frontmatter(self, skills_dir):
        """Test frontmatter parsing."""
        scorer = SkillScorer(skills_dir)
        content = """---
name: test
description: Test skill
---

# Body content
"""
        fm, body = scorer._parse_frontmatter(content)
        assert fm["name"] == "test"
        assert fm["description"] == "Test skill"
        assert "# Body content" in body

    def test_parse_frontmatter_no_frontmatter(self, skills_dir):
        """Test parsing content without frontmatter."""
        scorer = SkillScorer(skills_dir)
        content = "# Just content"
        fm, body = scorer._parse_frontmatter(content)
        assert fm == {}
        assert body == "# Just content"


class TestScoreTokenEfficiency:
    """Tests for token efficiency scoring."""

    @pytest.fixture
    def scorer(self, tmp_path):
        """Create a scorer."""
        return SkillScorer(tmp_path)

    def test_score_dense_content(self, scorer):
        """Test scoring dense content."""
        content = """# Heading

- Point 1
- Point 2
- Point 3

```python
code
```
"""
        body = content
        result = scorer._score_token_efficiency(content, body)
        assert result.name == "token_efficiency"
        assert 0.5 <= result.score <= 1.0

    def test_score_sparse_content(self, scorer):
        """Test scoring sparse content."""
        content = """
This is just a lot of text without any structure.
More text here.
And more text.
Continuing with text.
Still more text.
Even more.
""" * 10
        body = content
        result = scorer._score_token_efficiency(content, body)
        # Sparse content should score lower
        assert result.score < 0.8

    def test_penalizes_very_long_skills(self, scorer):
        """Test that very long skills get penalized."""
        content = "# Heading\n" + "Some text.\n" * 400
        body = content
        result = scorer._score_token_efficiency(content, body)
        assert "splitting" in result.recommendations[0].lower()


class TestScoreTriggerClarity:
    """Tests for trigger clarity scoring."""

    @pytest.fixture
    def scorer(self, tmp_path):
        """Create a scorer."""
        return SkillScorer(tmp_path)

    def test_score_with_trigger_section(self, scorer):
        """Test scoring with trigger section."""
        frontmatter = {"description": "Helps with testing"}
        body = """## Trigger

Use when you need to test. Invoke when debugging."""
        result = scorer._score_trigger_clarity(frontmatter, body)
        assert result.score >= 0.5

    def test_score_without_trigger_section(self, scorer):
        """Test scoring without trigger section."""
        frontmatter = {"description": "Something"}
        body = "Just content without trigger info."
        result = scorer._score_trigger_clarity(frontmatter, body)
        assert result.score < 0.5
        assert any("trigger" in r.lower() for r in result.recommendations)


class TestScoreCompleteness:
    """Tests for completeness scoring."""

    @pytest.fixture
    def scorer(self, tmp_path):
        """Create a scorer."""
        return SkillScorer(tmp_path)

    def test_score_complete_workflow(self, scorer):
        """Test scoring a complete workflow."""
        body = """# Workflow

## Trigger
When to use.

## Steps
1. First step
2. Second step

## Examples
```
code
```

## Output
Expected output.
"""
        result = scorer._score_completeness(body)
        assert result.score >= 0.6

    def test_score_incomplete_workflow(self, scorer):
        """Test scoring an incomplete workflow."""
        body = "Just text."
        result = scorer._score_completeness(body)
        assert result.score < 0.5


class TestScoreUsageFrequency:
    """Tests for usage frequency scoring."""

    @pytest.fixture
    def scorer_with_usage(self, tmp_path):
        """Create a scorer with usage data."""
        return SkillScorer(
            tmp_path,
            usage_data={"popular": 15, "moderate": 5, "rare": 1},
        )

    def test_high_usage(self, scorer_with_usage):
        """Test scoring high usage skill."""
        result = scorer_with_usage._score_usage_frequency("popular")
        assert result.score == 1.0

    def test_moderate_usage(self, scorer_with_usage):
        """Test scoring moderate usage skill."""
        result = scorer_with_usage._score_usage_frequency("moderate")
        assert result.score == 0.8

    def test_low_usage(self, scorer_with_usage):
        """Test scoring low usage skill."""
        result = scorer_with_usage._score_usage_frequency("rare")
        assert result.score == 0.3

    def test_no_usage(self, scorer_with_usage):
        """Test scoring skill with no usage."""
        result = scorer_with_usage._score_usage_frequency("unknown")
        assert result.score == 0.1
        assert len(result.recommendations) > 0


class TestScorePortability:
    """Tests for portability scoring."""

    @pytest.fixture
    def scorer(self, tmp_path):
        """Create a scorer."""
        return SkillScorer(tmp_path)

    def test_portable_content(self, scorer):
        """Test scoring portable content."""
        content = """# Generic Skill

Works with any tool. Standard commands only.
"""
        result = scorer._score_portability(content)
        assert result.score == 1.0

    def test_platform_specific_content(self, scorer):
        """Test scoring platform-specific content."""
        content = """# PairCoder Specific

Use bpsai-pair command.
Check .paircoder directory.
Use Claude Code subagent.
"""
        result = scorer._score_portability(content)
        assert result.score < 0.5
        assert len(result.recommendations) > 0


class TestScoreSkillsFunction:
    """Tests for score_skills function."""

    def test_score_skills_empty_dir(self, tmp_path):
        """Test scoring empty directory."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        results = score_skills(skills_dir)
        assert results == []

    def test_score_skills_with_skills(self, tmp_path):
        """Test scoring directory with skills."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill = skills_dir / "test-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("---\nname: test\n---\n# Test")

        results = score_skills(skills_dir)
        assert len(results) == 1
        assert results[0].skill_name == "test-skill"


class TestFormatSkillScore:
    """Tests for format_skill_score function."""

    def test_format_basic(self, tmp_path):
        """Test basic formatting."""
        score = SkillScore(
            skill_name="test-skill",
            skill_path=tmp_path / "test" / "SKILL.md",
            overall_score=85,
            dimensions=[
                DimensionScore("token_efficiency", 0.25, 0.9, "Good density"),
            ],
            recommendations=["Add examples"],
            grade="B",
        )
        output = format_skill_score(score)
        assert "test-skill" in output
        assert "85" in output
        assert "B" in output
        assert "token_efficiency" in output
        assert "Add examples" in output

    def test_format_includes_score_bars(self, tmp_path):
        """Test that format includes visual score bars."""
        score = SkillScore(
            skill_name="test",
            skill_path=tmp_path / "test" / "SKILL.md",
            overall_score=50,
            dimensions=[
                DimensionScore("test", 0.25, 0.5, "Test"),
            ],
            recommendations=[],
            grade="F",
        )
        output = format_skill_score(score)
        assert "█" in output or "░" in output


class TestFormatScoreTable:
    """Tests for format_score_table function."""

    def test_format_empty_list(self):
        """Test formatting empty list."""
        output = format_score_table([])
        assert "Quality Report" in output
        assert "Total: 0 skills" in output

    def test_format_with_scores(self, tmp_path):
        """Test formatting with scores."""
        scores = [
            SkillScore(
                skill_name="skill-a",
                skill_path=tmp_path / "a" / "SKILL.md",
                overall_score=90,
                dimensions=[
                    DimensionScore("token_efficiency", 0.25, 0.9, "Good"),
                    DimensionScore("trigger_clarity", 0.20, 0.8, "Good"),
                    DimensionScore("completeness", 0.20, 0.85, "Good"),
                ],
                recommendations=[],
                grade="A",
            ),
            SkillScore(
                skill_name="skill-b",
                skill_path=tmp_path / "b" / "SKILL.md",
                overall_score=70,
                dimensions=[
                    DimensionScore("token_efficiency", 0.25, 0.7, "OK"),
                    DimensionScore("trigger_clarity", 0.20, 0.6, "OK"),
                    DimensionScore("completeness", 0.20, 0.7, "OK"),
                ],
                recommendations=[],
                grade="C",
            ),
        ]
        output = format_score_table(scores)
        assert "skill-a" in output
        assert "skill-b" in output
        assert "Total: 2 skills" in output
