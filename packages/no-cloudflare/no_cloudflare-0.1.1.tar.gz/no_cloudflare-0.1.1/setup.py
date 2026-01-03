from setuptools import setup, find_packages

setup(
    name="no_cloudflare",  # Aapke package ka naam
    version="0.1.1",   # Version number
    packages=find_packages(),  # Yeh aapke package ko find karega
    install_requires=[  # Dependencies jo aapke package ko chahiye
        "DrissionPage",  # Agar aapne kisi external library ka use kiya hai toh yeh yahan aayega
    ],
)


# setup(
#     name="no_cloudflare",  # Aapke package ka naam
#     version="0.1.0",   # Version number
#     packages=find_packages(),  # Yeh aapke package ko find karega
#     install_requires=[  # Dependencies jo aapke package ko chahiye
#         "DrissionPage",  # Agar aapne kisi external library ka use kiya hai toh yeh yahan aayega
#     ],
#     # entry_points={  # Agar aapka package command line se run hota ho toh entry point define karein
#     #     'console_scripts': [
#     #         'myscript=mypackage.myscript:main_'  # Yeh line entry point specify karti hai
#     #     ]
#     # },
#     # description="A simple script to interact with Inmuebles24",  # Package ka short description
#     # author="Your Name",  # Aapka naam
#     # author_email="your.email@example.com",  # Aapka email
# )