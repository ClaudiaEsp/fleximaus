# fleximaus
A Python module to analyze electrical signals and behavior in amice behaving in a cognitive flexibility task. For personal use only.
Requirements


## Requirements
The module has been  tested on Python >= 3.7. We recommend to have a package manager like Anaconda with:

1. Standard scientific modules for data handling ([IPython and Jupyter](https://ipython.org/) , [pandas](https://pandas.pydata.org/)), 
2. Modules for scientific analysis ([Scipy](https://scipy.org/), [NumPy](https://numpy.org/) and machine learning ([Scikit-learn](https://scikit-learn.org/))
3. The scientific library for data visualization ([matplotlib](https://matplotlib.org/)). 

Assuming that you do not have an environment already, you can create it and download [fleximaus.yml](https://github.com/ClaudiaEsp/fleximaus/blob/master/fleximaus.yml) and type:

```bash
conda env create -f fleximaus.yml
```

## How to install it
To download and install the fleximaus package:

```bash
git clone https://github.com/ClaudiaEsp/fleximaus.git
cd fleximaus
pip install -r requirements.txt
pip install -e .
```

## License [![GitHub license](https://img.shields.io/github/license/ClaudiaEsp/fleximaus)](https://github.com/ClaudiaEsp/fleximaus/blob/master/LICENSE)

Fleximaus is free software. You can redistribute it and modify it under the terms of the GNU General Public License (GPL), either version 2 of the License, or any later version as published by the Free Software Foundation.

Fleximaus is distributed WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
