from setuptools import find_packages, setup

from rhytmiq.config import APP_DESCRIPTION, APP_NAME, APP_VERSION, AUTHOR, AUTHOR_EMAIL

setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url="https://github.com/LxrdShadow/Rhytmiq",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["rhytmiq=rhytmiq.main:main"]},
)
