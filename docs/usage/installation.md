# Installation

`pytracking` requires Python 3.

On Debian or Ubuntu systems, run:

```text
sudo apt-get install python3-pip
```

Python 3 installers for Windows and macOS can be found at <https://www.python.org/downloads/>

## Install pytracking

You can install pytracking using pip:

```sh
pip install pytracking
```

You can install specific features with extras:

```sh
pip install pytracking[django,crypto]
```

You can also install all features:

```sh
pip install pytracking[all]
```

Or, install the latest development release directly from GitHub:

```sh
pip install git+https://github.com/powergo/pytracking.git
```

You can install specific features with extras directly from GitHub:

```sh
pip3 install -U "git+https://github.com/powergo/pytracking.git@master#egg=pytracking[django,crypto]"
```