from setuptools import setup, find_packages

setup(    
    name="keycase-agent-sdk",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.31.0",
        "websocket-client>=1.7.0",
    ],
    author="Apo",
    description="Python SDK for Keycase Agent execution and keyword integration",
    entry_points={
        "console_scripts": [
            "keycase-agent=keycase_agent.__init__:start_agent"
        ]
    },
    python_requires=">=3.8",
)
