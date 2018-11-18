from setuptools import setup, find_packages

packages = find_packages()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r') as f:
    long_description = f.read()

setup(name="lldbvis",
      version="0.0.2",
      description="A GUI application to visualize debug data.",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/campoe/lldbvis",
      author="Coen van Kampen",
      author_email="c.m.vankampen14@gmail.com",
      license="MIT",
      packages=packages,
      package_data={'': ['*.ico', '*.svg']},
      include_package_data=True,
      entry_points={
          'console_script': ['lldbvis=lldbvis:main'],
      },
      install_requires=requirements,
      keywords=['lldbvis', 'lldb', 'python', 'debugger', 'visualization', 'qt4', 'GUI'],
      classifiers=[
          'Environment :: X11 Applications :: Qt',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 2 :: Only',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: User Interfaces'
      ]
      )
