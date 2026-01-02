from setuptools import setup
import sys

# Define platform-specific dependencies
install_requires = []
if sys.platform.startswith('win'):
    install_requires.append('playsound3')

setup(
    name='ez_background_music',
    version='1.0.0',
    description='A lightweight, cross-platform Python library for playing background music in CLI tools without blocking.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/ez_background_music',
    py_modules=['ez_background_music'],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='background music cli audio non-blocking terminal',
)
