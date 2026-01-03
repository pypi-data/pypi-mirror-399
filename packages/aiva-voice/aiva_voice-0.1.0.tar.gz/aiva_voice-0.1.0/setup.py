from setuptools import setup, find_packages

setup(
    name="aiva-voice",
    version="0.1.0",
    packages=["aiva"],
    description="AIVA Voice: Go-to voice solution for AI agents - telephony, TTS, STT",
    long_description="# AIVA Voice\n\nThe go-to voice platform for AI agents. Add phone, TTS, and STT capabilities to any project.\n\n```python\nfrom aiva import AIVA\n\naiva = AIVA(api_key='aiva_sk_xxx')\nnumber = aiva.phone.buy('+61720001234')\naiva.voice.speak('Hello from AIVA!')\n```\n\nLearn more at https://aiva.help",
    long_description_content_type="text/markdown",
    author="Midnight Now",
    author_email="studio@macagent.pro",
    url="https://aiva.help",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
