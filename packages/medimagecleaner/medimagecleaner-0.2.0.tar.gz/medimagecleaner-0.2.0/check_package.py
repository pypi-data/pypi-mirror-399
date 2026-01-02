#!/usr/bin/env python3
"""
Pre-deployment Checklist for medimagecleaner

Run this script before deploying to PyPI to verify package integrity.
"""

import sys
from pathlib import Path
import subprocess


def check_file_exists(filepath, required=True):
    """Check if a file exists."""
    exists = Path(filepath).exists()
    status = "✓" if exists else "✗"
    level = "ERROR" if (required and not exists) else "OK" if exists else "WARNING"
    print(f"  {status} {filepath} - {level}")
    return exists


def check_version_consistency():
    """Check that version is consistent across files."""
    print("\n2. Checking version consistency...")
    
    versions = {}
    
    # Check __init__.py
    init_file = Path("medimagecleaner/__init__.py")
    if init_file.exists():
        content = init_file.read_text()
        for line in content.split('\n'):
            if '__version__' in line:
                version = line.split('=')[1].strip().strip('"\'')
                versions['__init__.py'] = version
                break
    
    # Check setup.py
    setup_file = Path("setup.py")
    if setup_file.exists():
        content = setup_file.read_text()
        for line in content.split('\n'):
            if 'version=' in line and not line.strip().startswith('#'):
                version = line.split('=')[1].split(',')[0].strip().strip('"\'')
                versions['setup.py'] = version
                break
    
    # Check pyproject.toml
    pyproject_file = Path("pyproject.toml")
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        for line in content.split('\n'):
            if 'version =' in line:
                version = line.split('=')[1].strip().strip('"\'')
                versions['pyproject.toml'] = version
                break
    
    # Check consistency
    unique_versions = set(versions.values())
    
    if len(unique_versions) == 1:
        print(f"  ✓ All versions match: {list(unique_versions)[0]}")
        return True
    else:
        print(f"  ✗ Version mismatch detected:")
        for file, version in versions.items():
            print(f"    - {file}: {version}")
        return False


def check_imports():
    """Check that all modules can be imported."""
    print("\n3. Checking module imports...")
    
    try:
        import medimagecleaner
        print(f"  ✓ medimagecleaner imported successfully")
        print(f"    Version: {medimagecleaner.__version__}")
        
        # Check all modules
        modules = [
            'DicomDeidentifier',
            'TextRemover',
            'FormatConverter',
            'DeidentificationValidator',
            'AuditLogger',
            'BatchProcessor',
            'FaceRemover',
            'RiskAssessment',
            'ProgressTracker',
        ]
        
        for module in modules:
            if hasattr(medimagecleaner, module):
                print(f"  ✓ {module} available")
            else:
                print(f"  ✗ {module} NOT available")
                return False
        
        return True
    
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def check_readme():
    """Check README.md quality."""
    print("\n4. Checking README.md...")
    
    readme = Path("README.md")
    if not readme.exists():
        print("  ✗ README.md not found")
        return False
    
    content = readme.read_text()
    
    checks = {
        "Has title": content.startswith("# "),
        "Has installation section": "## Installation" in content or "## Quick Start" in content,
        "Has usage examples": "```python" in content,
        "Has license info": "License" in content or "LICENSE" in content,
        "Sufficient length": len(content) > 1000,
    }
    
    all_passed = True
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    """Run all checks."""
    print("=" * 60)
    print("medimagecleaner Pre-deployment Checklist")
    print("=" * 60)
    
    print("\n1. Checking required files...")
    
    required_files = [
        "setup.py",
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "MANIFEST.in",
        "requirements.txt",
        "medimagecleaner/__init__.py",
        "medimagecleaner/dicom_deidentifier.py",
        "medimagecleaner/text_remover.py",
        "medimagecleaner/format_converter.py",
        "medimagecleaner/validator.py",
        "medimagecleaner/audit_logger.py",
        "medimagecleaner/batch_processor.py",
        "medimagecleaner/face_remover.py",
        "medimagecleaner/risk_assessment.py",
        "medimagecleaner/progress.py",
        "medimagecleaner/cli.py",
    ]
    
    optional_files = [
        "CHANGELOG.md",
        "DEPLOYMENT.md",
        ".gitignore",
        "examples/complete_example.py",
        "examples/advanced_features_example.py",
    ]
    
    all_required_exist = all(check_file_exists(f, required=True) for f in required_files)
    
    print("\n  Optional files:")
    for f in optional_files:
        check_file_exists(f, required=False)
    
    # Run other checks
    version_ok = check_version_consistency()
    imports_ok = check_imports()
    readme_ok = check_readme()
    
    # Final summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_checks = [
        ("Required files", all_required_exist),
        ("Version consistency", version_ok),
        ("Module imports", imports_ok),
        ("README quality", readme_ok),
    ]
    
    all_passed = all(passed for _, passed in all_checks)
    
    for check, passed in all_checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {check}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✓ ALL CHECKS PASSED - Ready for deployment!")
        print("\nNext steps:")
        print("  1. Build the package: python -m build")
        print("  2. Check with twine: twine check dist/*")
        print("  3. Upload to Test PyPI: twine upload --repository testpypi dist/*")
        print("  4. Test installation from Test PyPI")
        print("  5. Upload to PyPI: twine upload dist/*")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please fix issues before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
