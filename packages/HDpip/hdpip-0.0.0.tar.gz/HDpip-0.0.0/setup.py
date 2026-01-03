import setuptools
 
with open("HDpip\\README.md", 'r', encoding="utf8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name = "HDpip",
    version = "0.0.0",
    author = "寒冬利刃(handongliren(hdlr))",
    author_email = "1079489986@qq.com",
    description = "寒冬pip(HDpip)",
    long_description = long_description,
    long_description_content_type = "text/Markdown",
    license = "MIT",
    url = "https://gitee.com/handongliren",
    packages = setuptools.find_packages(),
    package_data={
        "HDpip": ["*"],
    },
    python_requires = ">=3.10",
    install_requires = [
        # "wheel>=0.40.0", 
        "maliang[opt]>=3.0.0", 
    ],
    entry_points={
        "console_scripts": [
            "HDpip=HDpip.main:main",
            "hdpip=HDpip.main:main"
        ],
    },
)