from setuptools import setup, find_packages

setup(
    name="rpi_lcd_i2c_animations",
    version="1.0.0",
    description="Animations add-on for rpi_lcd_i2c LCD library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sammy",
    url="https://github.com/Sam67-coder/rpi_lcd_i2c_animations",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "rpi_lcd_i2c>=1.0.0"
    ],
    python_requires=">=3.9",
)
