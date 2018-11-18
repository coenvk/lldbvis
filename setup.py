from setuptools import setup, find_packages

packages = find_packages()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name="lldbvis",
      version="0.0.2",
      description="A GUI application to visualize debug data.",
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
          'Environment :: GUI',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
          'Topic :: Debugging',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: User Interfaces'
      ]
      )
