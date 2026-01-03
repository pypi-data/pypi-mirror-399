from setuptools import setup, find_packages

setup(
    name="fitPlotpy",
    version="0.1.0",
    author="Muhammad Osama",
    author_email="muhammadosama0846@gmail.com",  
    description="Probability distribution plotting",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["numpy", "scipy", "pandas", "matplotlib", "seaborn"],
    license="MIT",  
)

