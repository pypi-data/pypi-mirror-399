"""Tests for dependency vulnerability scanning functionality."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime
import json


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        from bpsai_pair.security.dependencies import Severity

        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"

    def test_severity_from_string(self):
        """Test converting string to severity."""
        from bpsai_pair.security.dependencies import Severity

        assert Severity.from_string("low") == Severity.LOW
        assert Severity.from_string("HIGH") == Severity.HIGH
        assert Severity.from_string("Critical") == Severity.CRITICAL
        assert Severity.from_string("unknown_value") == Severity.UNKNOWN

    def test_severity_comparison(self):
        """Test severity comparison operators."""
        from bpsai_pair.security.dependencies import Severity

        assert Severity.LOW < Severity.MEDIUM
        assert Severity.MEDIUM < Severity.HIGH
        assert Severity.HIGH < Severity.CRITICAL
        assert Severity.CRITICAL <= Severity.CRITICAL
        assert not Severity.HIGH < Severity.LOW


class TestVulnerability:
    """Tests for Vulnerability dataclass."""

    def test_vulnerability_creation(self):
        """Test creating a vulnerability."""
        from bpsai_pair.security.dependencies import Vulnerability, Severity

        vuln = Vulnerability(
            package="requests",
            version="2.25.0",
            cve_id="CVE-2021-12345",
            severity=Severity.HIGH,
            description="Test vulnerability",
            fixed_version="2.26.0",
            source="pip-audit",
        )

        assert vuln.package == "requests"
        assert vuln.version == "2.25.0"
        assert vuln.cve_id == "CVE-2021-12345"
        assert vuln.severity == Severity.HIGH
        assert vuln.fixed_version == "2.26.0"

    def test_vulnerability_format(self):
        """Test vulnerability formatting."""
        from bpsai_pair.security.dependencies import Vulnerability, Severity

        vuln = Vulnerability(
            package="flask",
            version="1.0.0",
            cve_id="CVE-2020-99999",
            severity=Severity.CRITICAL,
            description="Critical issue",
            fixed_version="2.0.0",
        )

        formatted = vuln.format()
        assert "CRITICAL" in formatted
        assert "flask@1.0.0" in formatted
        assert "CVE-2020-99999" in formatted
        assert "2.0.0" in formatted

    def test_vulnerability_to_dict(self):
        """Test converting vulnerability to dict."""
        from bpsai_pair.security.dependencies import Vulnerability, Severity

        vuln = Vulnerability(
            package="django",
            version="3.0.0",
            cve_id="CVE-2021-11111",
            severity=Severity.MEDIUM,
            description="Medium severity issue",
        )

        d = vuln.to_dict()
        assert d["package"] == "django"
        assert d["severity"] == "medium"
        assert d["cve_id"] == "CVE-2021-11111"


class TestScanReport:
    """Tests for ScanReport dataclass."""

    def test_empty_report(self):
        """Test empty scan report."""
        from bpsai_pair.security.dependencies import ScanReport

        report = ScanReport()
        assert len(report.vulnerabilities) == 0
        assert not report.has_critical()
        assert not report.has_high_or_above()

    def test_report_with_vulnerabilities(self):
        """Test report with vulnerabilities."""
        from bpsai_pair.security.dependencies import ScanReport, Vulnerability, Severity

        vulns = [
            Vulnerability(
                package="pkg1", version="1.0", cve_id="CVE-1",
                severity=Severity.HIGH, description="High"
            ),
            Vulnerability(
                package="pkg2", version="2.0", cve_id="CVE-2",
                severity=Severity.CRITICAL, description="Critical"
            ),
        ]

        report = ScanReport(vulnerabilities=vulns, packages_scanned=10)

        assert len(report.vulnerabilities) == 2
        assert report.has_critical()
        assert report.has_high_or_above()
        assert report.packages_scanned == 10

    def test_has_severity(self):
        """Test has_severity method."""
        from bpsai_pair.security.dependencies import ScanReport, Vulnerability, Severity

        vulns = [
            Vulnerability(
                package="pkg1", version="1.0", cve_id="CVE-1",
                severity=Severity.MEDIUM, description="Medium"
            ),
        ]

        report = ScanReport(vulnerabilities=vulns)

        assert report.has_severity(Severity.LOW)
        assert report.has_severity(Severity.MEDIUM)
        assert not report.has_severity(Severity.HIGH)
        assert not report.has_severity(Severity.CRITICAL)

    def test_count_by_severity(self):
        """Test counting vulnerabilities by severity."""
        from bpsai_pair.security.dependencies import ScanReport, Vulnerability, Severity

        vulns = [
            Vulnerability(package="a", version="1", cve_id="1", severity=Severity.HIGH, description=""),
            Vulnerability(package="b", version="1", cve_id="2", severity=Severity.HIGH, description=""),
            Vulnerability(package="c", version="1", cve_id="3", severity=Severity.CRITICAL, description=""),
        ]

        report = ScanReport(vulnerabilities=vulns)
        counts = report.count_by_severity()

        assert counts["high"] == 2
        assert counts["critical"] == 1

    def test_report_to_dict(self):
        """Test converting report to dict."""
        from bpsai_pair.security.dependencies import ScanReport, Vulnerability, Severity

        vulns = [
            Vulnerability(package="pkg", version="1.0", cve_id="CVE-1",
                         severity=Severity.HIGH, description="Desc"),
        ]

        report = ScanReport(
            vulnerabilities=vulns,
            packages_scanned=5,
            scan_duration=1.5,
        )

        d = report.to_dict()
        assert len(d["vulnerabilities"]) == 1
        assert d["packages_scanned"] == 5
        assert d["scan_duration"] == 1.5
        assert d["summary"]["total"] == 1
        assert d["summary"]["has_high"]

    def test_report_format_no_vulnerabilities(self):
        """Test formatting report with no vulnerabilities."""
        from bpsai_pair.security.dependencies import ScanReport

        report = ScanReport(packages_scanned=10, scan_duration=0.5)
        formatted = report.format()

        assert "No vulnerabilities found" in formatted
        assert "10 packages" in formatted

    def test_report_format_with_vulnerabilities(self):
        """Test formatting report with vulnerabilities."""
        from bpsai_pair.security.dependencies import ScanReport, Vulnerability, Severity

        vulns = [
            Vulnerability(package="pkg1", version="1.0", cve_id="CVE-1",
                         severity=Severity.CRITICAL, description="Critical issue"),
            Vulnerability(package="pkg2", version="2.0", cve_id="CVE-2",
                         severity=Severity.HIGH, description="High issue"),
        ]

        report = ScanReport(vulnerabilities=vulns, packages_scanned=5)
        formatted = report.format()

        assert "2 vulnerabilities" in formatted
        assert "CRITICAL" in formatted
        assert "HIGH" in formatted


class TestDependencyScanner:
    """Tests for DependencyScanner class."""

    def test_scanner_creation(self):
        """Test creating a scanner."""
        from bpsai_pair.security.dependencies import DependencyScanner

        scanner = DependencyScanner()
        assert scanner is not None
        assert scanner.cache_ttl == 3600

    def test_scanner_custom_cache(self, tmp_path):
        """Test scanner with custom cache directory."""
        from bpsai_pair.security.dependencies import DependencyScanner

        scanner = DependencyScanner(cache_dir=tmp_path, cache_ttl=1800)
        assert scanner.cache_dir == tmp_path
        assert scanner.cache_ttl == 1800


class TestPythonScanning:
    """Tests for Python dependency scanning."""

    @patch('subprocess.run')
    def test_scan_python_no_pip_audit(self, mock_run):
        """Test scanning when pip-audit is not installed."""
        from bpsai_pair.security.dependencies import DependencyScanner

        mock_run.side_effect = FileNotFoundError()

        scanner = DependencyScanner()
        vulns, errors = scanner.scan_python(Path("requirements.txt"), use_cache=False)

        assert len(vulns) == 0
        assert len(errors) == 1
        assert "pip-audit not installed" in errors[0]

    @patch('subprocess.run')
    def test_scan_python_with_vulnerabilities(self, mock_run, tmp_path):
        """Test scanning Python deps with vulnerabilities found."""
        from bpsai_pair.security.dependencies import DependencyScanner, Severity

        # Mock pip-audit output
        pip_audit_output = {
            "dependencies": [
                {
                    "name": "requests",
                    "version": "2.25.0",
                    "vulns": [
                        {
                            "id": "CVE-2021-12345",
                            "description": "Test vulnerability",
                            "fix_versions": ["2.26.0"],
                            "severity": "high",
                        }
                    ]
                }
            ]
        }

        # First call checks pip-audit version, second does the scan
        mock_run.side_effect = [
            MagicMock(returncode=0),  # version check
            MagicMock(returncode=1, stdout=json.dumps(pip_audit_output), stderr=""),  # scan
        ]

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests==2.25.0\n")

        scanner = DependencyScanner()
        vulns, errors = scanner.scan_python(req_file, use_cache=False)

        assert len(vulns) == 1
        assert vulns[0].package == "requests"
        assert vulns[0].cve_id == "CVE-2021-12345"
        assert vulns[0].severity == Severity.HIGH
        assert vulns[0].fixed_version == "2.26.0"

    @patch('subprocess.run')
    def test_scan_python_no_vulnerabilities(self, mock_run, tmp_path):
        """Test scanning Python deps with no vulnerabilities."""
        from bpsai_pair.security.dependencies import DependencyScanner

        pip_audit_output = {"dependencies": []}

        mock_run.side_effect = [
            MagicMock(returncode=0),  # version check
            MagicMock(returncode=0, stdout=json.dumps(pip_audit_output), stderr=""),  # scan
        ]

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests==2.28.0\n")

        scanner = DependencyScanner()
        vulns, errors = scanner.scan_python(req_file, use_cache=False)

        assert len(vulns) == 0
        assert len(errors) == 0

    @patch('subprocess.run')
    def test_scan_python_timeout(self, mock_run, tmp_path):
        """Test scanning Python deps with timeout."""
        from bpsai_pair.security.dependencies import DependencyScanner
        import subprocess

        mock_run.side_effect = [
            MagicMock(returncode=0),  # version check
            subprocess.TimeoutExpired(cmd="pip-audit", timeout=300),  # scan timeout
        ]

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests==2.25.0\n")

        scanner = DependencyScanner()
        vulns, errors = scanner.scan_python(req_file, use_cache=False)

        assert len(vulns) == 0
        assert any("timed out" in e for e in errors)


class TestNpmScanning:
    """Tests for npm dependency scanning."""

    @patch('subprocess.run')
    def test_scan_npm_no_npm(self, mock_run):
        """Test scanning when npm is not installed."""
        from bpsai_pair.security.dependencies import DependencyScanner

        mock_run.side_effect = FileNotFoundError()

        scanner = DependencyScanner()
        vulns, errors = scanner.scan_npm(Path("package.json"), use_cache=False)

        assert len(vulns) == 0
        assert len(errors) == 1
        assert "npm not installed" in errors[0]

    @patch('subprocess.run')
    def test_scan_npm_no_node_modules(self, mock_run, tmp_path):
        """Test scanning when node_modules doesn't exist."""
        from bpsai_pair.security.dependencies import DependencyScanner

        mock_run.return_value = MagicMock(returncode=0)  # npm version check

        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"dependencies": {}}')

        scanner = DependencyScanner()
        vulns, errors = scanner.scan_npm(pkg_file, use_cache=False)

        assert len(vulns) == 0
        assert any("node_modules not found" in e for e in errors)

    @patch('subprocess.run')
    def test_scan_npm_with_vulnerabilities(self, mock_run, tmp_path):
        """Test scanning npm deps with vulnerabilities found."""
        from bpsai_pair.security.dependencies import DependencyScanner, Severity

        npm_audit_output = {
            "vulnerabilities": {
                "lodash": {
                    "severity": "high",
                    "range": "4.17.0",
                    "via": [
                        {
                            "title": "Prototype Pollution",
                            "url": "https://github.com/advisories/GHSA-xxxx",
                            "source": 12345,
                        }
                    ],
                    "fixAvailable": {"version": "4.17.21"},
                }
            }
        }

        mock_run.side_effect = [
            MagicMock(returncode=0),  # npm version check
            MagicMock(returncode=1, stdout=json.dumps(npm_audit_output), stderr=""),  # audit
        ]

        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"dependencies": {"lodash": "^4.17.0"}}')

        # Create node_modules directory
        (tmp_path / "node_modules").mkdir()

        scanner = DependencyScanner()
        vulns, errors = scanner.scan_npm(pkg_file, use_cache=False)

        assert len(vulns) == 1
        assert vulns[0].package == "lodash"
        assert vulns[0].severity == Severity.HIGH


class TestScanAll:
    """Tests for scan_all method."""

    @patch('subprocess.run')
    def test_scan_all_no_deps(self, mock_run, tmp_path):
        """Test scanning directory with no dependency files."""
        from bpsai_pair.security.dependencies import DependencyScanner

        scanner = DependencyScanner()
        report = scanner.scan_all(tmp_path)

        assert len(report.vulnerabilities) == 0
        assert report.packages_scanned == 0

    @patch('subprocess.run')
    def test_scan_all_with_requirements(self, mock_run, tmp_path):
        """Test scanning directory with requirements.txt."""
        from bpsai_pair.security.dependencies import DependencyScanner

        pip_audit_output = {"dependencies": []}

        mock_run.side_effect = [
            MagicMock(returncode=0),  # pip-audit version
            MagicMock(returncode=0, stdout=json.dumps(pip_audit_output), stderr=""),
        ]

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\nrequests==2.28.0\n")

        scanner = DependencyScanner()
        report = scanner.scan_all(tmp_path, use_cache=False)

        assert len(report.vulnerabilities) == 0
        assert report.packages_scanned >= 2


class TestCaching:
    """Tests for scan result caching."""

    @patch('subprocess.run')
    def test_cache_saves_results(self, mock_run, tmp_path):
        """Test that scan results are cached."""
        from bpsai_pair.security.dependencies import DependencyScanner

        pip_audit_output = {"dependencies": []}

        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0, stdout=json.dumps(pip_audit_output), stderr=""),
        ]

        cache_dir = tmp_path / "cache"
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\n")

        scanner = DependencyScanner(cache_dir=cache_dir)
        scanner.scan_python(req_file, use_cache=True)

        # Cache directory should have been created
        assert cache_dir.exists()
        # Should have at least one cache file
        cache_files = list(cache_dir.glob("*.json"))
        assert len(cache_files) >= 1

    @patch('subprocess.run')
    def test_cache_returns_cached_results(self, mock_run, tmp_path):
        """Test that cached results are returned."""
        from bpsai_pair.security.dependencies import DependencyScanner, Vulnerability, Severity
        import json

        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\n")

        # Pre-populate cache
        scanner = DependencyScanner(cache_dir=cache_dir)
        cache_key = scanner._get_cache_key(req_file)
        cache_file = cache_dir / f"{cache_key}.json"

        cached_vulns = [
            {
                "package": "flask",
                "version": "2.0.0",
                "cve_id": "CVE-CACHED",
                "severity": "high",
                "description": "Cached vulnerability",
                "source": "cache",
            }
        ]
        cache_file.write_text(json.dumps(cached_vulns))

        # Scan should return cached results without calling subprocess
        vulns, errors = scanner.scan_python(req_file, use_cache=True)

        assert len(vulns) == 1
        assert vulns[0].cve_id == "CVE-CACHED"
        # subprocess.run should not have been called
        mock_run.assert_not_called()


class TestParsePipAudit:
    """Tests for pip-audit output parsing."""

    def test_parse_newer_format(self):
        """Test parsing newer pip-audit format with dependencies key."""
        from bpsai_pair.security.dependencies import DependencyScanner

        data = {
            "dependencies": [
                {
                    "name": "django",
                    "version": "3.1.0",
                    "vulns": [
                        {
                            "id": "PYSEC-2021-123",
                            "aliases": ["CVE-2021-44444"],
                            "description": "SQL Injection",
                            "fix_versions": ["3.1.14"],
                        }
                    ]
                }
            ]
        }

        scanner = DependencyScanner()
        vulns = scanner._parse_pip_audit(data)

        assert len(vulns) == 1
        assert vulns[0].package == "django"
        assert vulns[0].cve_id == "CVE-2021-44444"
        assert vulns[0].fixed_version == "3.1.14"

    def test_parse_older_format(self):
        """Test parsing older pip-audit format (direct list)."""
        from bpsai_pair.security.dependencies import DependencyScanner

        data = [
            {
                "name": "flask",
                "version": "1.0.0",
                "vulns": [
                    {
                        "id": "CVE-2019-12345",
                        "description": "XSS vulnerability",
                    }
                ]
            }
        ]

        scanner = DependencyScanner()
        vulns = scanner._parse_pip_audit(data)

        assert len(vulns) == 1
        assert vulns[0].package == "flask"
        assert vulns[0].cve_id == "CVE-2019-12345"


class TestParseNpmAudit:
    """Tests for npm audit output parsing."""

    def test_parse_npm_audit_v7(self):
        """Test parsing npm audit v7+ format."""
        from bpsai_pair.security.dependencies import DependencyScanner, Severity

        data = {
            "vulnerabilities": {
                "minimist": {
                    "severity": "critical",
                    "range": "<1.2.6",
                    "via": [
                        {
                            "title": "Prototype Pollution",
                            "url": "https://github.com/advisories/GHSA-xxx",
                            "source": 1179,
                        }
                    ],
                    "fixAvailable": True,
                }
            }
        }

        scanner = DependencyScanner()
        vulns = scanner._parse_npm_audit(data)

        assert len(vulns) == 1
        assert vulns[0].package == "minimist"
        assert vulns[0].severity == Severity.CRITICAL

    def test_parse_npm_audit_no_vulns(self):
        """Test parsing npm audit with no vulnerabilities."""
        from bpsai_pair.security.dependencies import DependencyScanner

        data = {"vulnerabilities": {}}

        scanner = DependencyScanner()
        vulns = scanner._parse_npm_audit(data)

        assert len(vulns) == 0


class TestFormatScanReport:
    """Tests for format_scan_report function."""

    def test_format_empty_report(self):
        """Test formatting empty report."""
        from bpsai_pair.security.dependencies import ScanReport, format_scan_report

        report = ScanReport(packages_scanned=10, scan_duration=0.5)
        formatted = format_scan_report(report)

        assert "No vulnerabilities found" in formatted

    def test_format_report_verbose(self):
        """Test verbose formatting."""
        from bpsai_pair.security.dependencies import ScanReport, Vulnerability, Severity, format_scan_report

        vulns = [
            Vulnerability(
                package="pkg",
                version="1.0",
                cve_id="CVE-2021-12345",
                severity=Severity.HIGH,
                description="A very long description that should be truncated in verbose mode for readability",
                fixed_version="2.0",
            ),
        ]

        report = ScanReport(vulnerabilities=vulns, packages_scanned=5)
        formatted = format_scan_report(report, verbose=True)

        assert "CVE-2021-12345" in formatted
        assert "pkg@1.0" in formatted
        assert "upgrade to 2.0" in formatted


class TestFindDependencyFiles:
    """Tests for finding dependency files."""

    def test_find_python_requirements(self, tmp_path):
        """Test finding Python requirements files."""
        from bpsai_pair.security.dependencies import DependencyScanner

        # Create test files
        (tmp_path / "requirements.txt").write_text("flask\n")
        (tmp_path / "requirements-dev.txt").write_text("pytest\n")

        scanner = DependencyScanner()
        files = scanner._find_python_deps(tmp_path)

        assert len(files) >= 2

    def test_find_pyproject_toml(self, tmp_path):
        """Test finding pyproject.toml."""
        from bpsai_pair.security.dependencies import DependencyScanner

        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        scanner = DependencyScanner()
        files = scanner._find_python_deps(tmp_path)

        assert len(files) == 1
        assert files[0].name == "pyproject.toml"

    def test_find_npm_package_json(self, tmp_path):
        """Test finding package.json files."""
        from bpsai_pair.security.dependencies import DependencyScanner

        (tmp_path / "package.json").write_text('{"name": "test"}')

        # Should ignore node_modules
        nm = tmp_path / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "package.json").write_text('{"name": "dep"}')

        scanner = DependencyScanner()
        files = scanner._find_npm_deps(tmp_path)

        assert len(files) == 1
        assert "node_modules" not in str(files[0])


class TestCountPackages:
    """Tests for counting packages in dependency files."""

    def test_count_python_requirements(self, tmp_path):
        """Test counting packages in requirements.txt."""
        from bpsai_pair.security.dependencies import DependencyScanner

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\nrequests\n# comment\npytest\n")

        scanner = DependencyScanner()
        count = scanner._count_python_packages(req_file)

        assert count == 3

    def test_count_npm_packages(self, tmp_path):
        """Test counting packages in package.json."""
        from bpsai_pair.security.dependencies import DependencyScanner

        pkg_file = tmp_path / "package.json"
        pkg_file.write_text(json.dumps({
            "dependencies": {"express": "^4.0.0", "lodash": "^4.17.0"},
            "devDependencies": {"jest": "^27.0.0"},
        }))

        scanner = DependencyScanner()
        count = scanner._count_npm_packages(pkg_file)

        assert count == 3
