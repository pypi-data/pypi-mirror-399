#!/usr/bin/env python3
"""
Setup script for ProleTRact
"""
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from pathlib import Path
import subprocess
import sys
import os

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "proletract" / "backend" / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


class BuildFrontend(build_py):
    """Custom build step to compile React frontend with npm"""
    
    def run(self):
        """Build the React frontend before packaging"""
        frontend_dir = Path(__file__).parent / "proletract" / "frontend"
        
        if not frontend_dir.exists():
            print("⚠️  Frontend directory not found, skipping build")
            super().run()
            return
        
        # Check for npm
        try:
            npm_version = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"📦 Found npm version {npm_version.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npm not found. Please install Node.js and npm first.")
            print("   Frontend will need to be built manually on first run.")
            super().run()
            return
        
        # Check if node_modules exists, install if needed
        node_modules = frontend_dir / "node_modules"
        package_json = frontend_dir / "package.json"
        
        if not package_json.exists():
            print("❌ package.json not found in frontend directory")
            super().run()
            return
        
        if not node_modules.exists():
            print("📦 Installing frontend dependencies with npm...")
            try:
                result = subprocess.run(
                    ["npm", "install", "--legacy-peer-deps"],
                    cwd=frontend_dir,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                print("✅ Frontend dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                error_output = e.stdout.decode() if e.stdout else str(e)
                print(f"❌ Failed to install frontend dependencies:")
                print(error_output[:500])  # Print first 500 chars
                print("\n⚠️  The frontend will need to be built manually.")
                super().run()
                return
        
        # Build the React app with npm
        print("🔨 Building React application with npm...")
        build_dir = frontend_dir / "build"
        
        # Remove old build if it exists
        if build_dir.exists():
            import shutil
            shutil.rmtree(build_dir)
            print("🧹 Removed old build directory")
        
        try:
            # Run npm build
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            
            # Verify build output
            if build_dir.exists() and (build_dir / "index.html").exists():
                build_size = sum(f.stat().st_size for f in build_dir.rglob('*') if f.is_file())
                print(f"✅ React frontend built successfully!")
                print(f"   Build directory: {build_dir}")
                print(f"   Build size: {build_size / 1024 / 1024:.2f} MB")
            else:
                print("⚠️  Build completed but index.html not found")
                print("   The frontend will be built on first run instead")
        except subprocess.CalledProcessError as e:
            error_output = e.stdout.decode() if e.stdout else str(e)
            print(f"❌ Failed to build frontend with npm:")
            print(error_output[:1000])  # Print first 1000 chars
            print("\n⚠️  The frontend will need to be built manually on first run.")
            print("   Run: cd proletract/frontend && npm install && npm run build")
        
        # Continue with normal Python package build
        super().run()


setup(
    name="proletract",
    # Version is defined in pyproject.toml
    description="ProleTRact - Tandem Repeat Visualization Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lion Ward Al Raei",
    author_email="lionward.alraei@gmail.com",
    url="https://github.com/Lionward/ProleTRact",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
    package_data={
        "proletract": [
            "frontend/public/**/*",
            "frontend/src/**/*",
            "frontend/build/**/*",  # Include built React app
            "frontend/package.json",
            "frontend/package-lock.json",
            "frontend/tsconfig.json",
        ],
    },
    install_requires=requirements,
    python_requires=">=3.9",
    cmdclass={
        "build_py": BuildFrontend,
    },
    entry_points={
        "console_scripts": [
            "proletract=proletract.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: Other/Proprietary License",
    ],
    keywords="tandem repeat, VCF, visualization, bioinformatics, genomics",
)
