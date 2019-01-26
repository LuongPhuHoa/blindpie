import setuptools
from distutils.core import setup
from blindpie.core import __version__, DESCRIPTION


setup(name="blindpie",
      version=__version__,
      description=DESCRIPTION,
      url="https://github.com/alessiovierti/blindpie",
      author="Alessio Vierti",
      author_email="alessio.vierti@gmail.com",
      license="MIT",
      packages=["blindpie"],
      scripts=["bin/blindpie.py"],
      requires=["requests", "typing"])
