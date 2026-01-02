from setuptools import setup, find_packages

setup(
    name='ipulse_shared_ai_ftredge',
    version='3.5.2',
    package_dir={'': 'src'},  # Specify the source directory
    packages=find_packages(where='src'),  # Look for packages in 'src'
    install_requires=[
        # List your dependencies here
        'pydantic[email]~=2.5',
        'python-dateutil~=2.8',
        'ipulse_shared_base_ftredge~=12.8.1',
    ],
    author='russlan.ramdowar',
    description='Shared AI models for the Pulse platform project. Using AI for financial advisory and investment management.',
    url='https://github.com/TheFutureEdge/ipulse_shared_ai',
)