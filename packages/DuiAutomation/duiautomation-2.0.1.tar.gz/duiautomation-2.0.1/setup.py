from os.path import dirname, join
from setuptools import setup, find_packages


with open(join(dirname(__file__), 'dui_automation/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()


install_requires = [
    'frida==16.0.19',
    'frida-tools==12.1.2',
    'psutil~=5.9.5',
    'jsonpath==0.82',
    'uiautomation==2.0.29'
]


setup(
    name='DuiAutomation',
    version=version,
    url='https://gitee.com/qetest/DuiAutomation',
    description='An ui-autotest framework for windows DuiLib.',
    author='Bruce Cai',
    maintainer='Bruce Cai',
    maintainer_email='caibin@qiyou.cn',
    packages=find_packages(),
    data_files=[
        ('dui_automation', ['dui_automation/VERSION']),
        ('dui_automation', ['dui_automation/scripts/duilib.js']),
                ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Framework :: Scrapy',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.5',
    install_requires=install_requires,
)
