<h1 align="center">TomoXRD</h1>

TomoXRD is a package that makes use of Qt5 to create an GUI application that can run trajectory scans using 
the Aerotech driver, and the Pilatus 1M 3S detector. Collections are set for .tiff, .cbf and .esperanto files.

## Installation

---

TomoXRD requires the use of Python 3.10 or higher. In some cases lower versions are also accepted,
but version 3.10 is recommended for best compatibility. See the full [requirements list](#urequirementsu)
for the TomoXRD package. Temporary there is support only for Windows OS. 

<br />

#### <u>Source files</u>
To install you can download the project from the package 
[releases](https://github.com/GSECARS/TomoXRD/releases) 
or use: 
````
git clone https://github.com/GSECARS/TomoXRD.git
````
Move into the project directory: 
````
cd TomoXRD
````
Install using pip: 
````
pip install .
````

<br />

#### <u>Requirements</u>
1. Python >= 3.10
2. PyQt5 >= 5.15.7
3. qtpy >= 2.3.0
4. numpy >= 1.23.5
5. pyepics >= 3.5.1
6. pywin32 >= 305
7. cryio >= 2018.5.30
<br />

<br />

## License

---

TomoXRD is distributed under the GNU General Public License version 3. You should have 
received a copy of the GNU General Public License along with this program.  If not, see 
<https://www.gnu.org/licenses/>.

<br />

[Christofanis Skordas](mailto:skordasc@uchicago.edu) - Last updated: 1-Dec-2022