from setuptools import setup, find_packages

setup(
    name="userrecon",
    version="1.0.3",
    author="CyberWithPriyanshu",
    author_email="Cyberwithpriyanshu@gmail.com",
    description="CLI-based OSINT tool for username reconnaissance",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=["userrecon"],
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "userrecon=userrecon.recon:main"
        ]
    },
    python_requires=">=3.7",
)
