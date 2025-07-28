# DissolvPCB 
### Fully Recyclable Electronics with Liquid Metal Conductors and 3D-Printed PVA Substrates
DissolvPCB is a fully recyclable printed circuit board assembly (PCBA) manufacturing technique 
that utilizes affordable FDM 3D printing with Polyvinyl Alcohol (PVA) as a water-soluble substrate 
and eutectic gallium-indium (EGaIn) as the conductive material. 

This Github repository contains the Python macro component used during the DissolvPCB fabrication process. 
The macro enables users to design custom PCB assemblies using standard practices, then automatically
convert the design into a 3D model ready to be printed. Also included are some PCB design examples that 
were used for the demonstration of the DissolvPCB fabrication process. 
Listed below are the prerequisites and instructions on how to utilize this tool. 
Detailed instructions on the entire DisssolvPCB fabrication process can be found under [DissolvPCB Processs Details](DissolvPCB_Process_Details.md).

![fab 5](https://github.com/user-attachments/assets/b1558e9b-292b-478c-9791-79eaf2e3ef7f)

## Installation 

### Prerequisites
  - Python 3.0.0 or above
  - FreeCAD 1.0.0 or above
    - https://www.freecad.org/downloads.php
  - KiCAD 8.0.7 or above
    - https://www.kicad.org/download/

### KiCAD Libraries Installation
  - Add Symbol Library
    - Located in /libray/PVA_board.kicad_sym
    - Add by going to: Symbol Editor -> File -> Add Library
  - Add Footprint Library
    - Located in /library/PVA_board.pretty
    - Add by going to: Footprint Editor -> File -> Add Library
  - Copy 3D moddels to KiCAD 3D Models
    - Copy the folder /library/PVA_Board_3Dmodels into directory
    - Set Global Variable "KICAD_3DMODEL_DIR" to correct directory
      - Usually Located under C:\Program Files\KiCad\8.0\share\kicad\3dmodels
      - You can locate the direcotry by going to the KiCAD project window, then Preferences -> Configure Paths
   
## DissolvPCB Design in KiCAD
### PCB Schematic Design
  If you have imported the libraries as described above, the schematic design follows standard procedues.
  During the footprint assignment at the end of your schematic design procecss, verify that 
  footprints are from the PVA_Board library.
    
### PCB Layout Design
  To ensure compatibility with the DissolvPCB fabrication process, a few settings must be changed first. 
  The DRC settings can simply be imported from /KiCAD/DRC_Import_Prj/DRC_Import/DRC_Import.kicad_pcb, using the "Import Settings from Another Board" button under File -> Board Setup. 
  By importing "Design rule constraints", "Predefined track & via dimensions", and "Violation severities" (optional), 
  the PCB design will become compatible with the DissolvPCB fabrication process. (See attached below)
	<img width="471" height="348" alt="432048682-aeb7e37b-99a9-4a01-ab0c-9ea9d6ce369a" src="https://github.com/user-attachments/assets/58cc6446-e25f-443b-9e18-76bdb193775a" />

## Macro Execution
FreeCAD has built-in support for Python macros. 
To run, open the Python script by going to File -> Open and open /Python/create.py.
Then, run the macro by going to Macro -> Run Macro. 
Note that the boolean process step at the end can take some time depending on the complexity of your design and your compute power. 
Therefore, it is recommended that you run the macro on a system with a more powerful CPU if possible.

### Macro Functions
The Python scripts contain code comments throughout to help users debug and modify. Overall, the 4 main steps of the macro includes:
- Trace & Pad Generation
- DissolvPCB Body Creation
- 3D Footprint Insertion
- Boolean Operation

Except for the Boolean Operation, these parts are independant of each other. 
Thus, it is possible to run any combination of of the first 3 as desired. 

*Note: If the boolean operation fails from an error relating to 'multiple bodies', you may have to enable a setting. 
Go to Edit -> Preferences -> Part/Part Design -> Experimental -> check "Allow multiple solids in Part Design Body by Defualt"

## Examples 

Some KiCAD Designs are provided, which are listed below.
Note that Circuit_sample_01, circuit_sample_02, and ESP_Speaker designs are directly compatible with the macro, and does not require any modifications to replicate our designs. 
  - /KiCAD/circuit_sample/circuit_sample_01
    - Hall Sensor & ATTiny85 design, used throughout the paper
      <img src="https://github.com/user-attachments/assets/d3338a86-03d3-4dde-baab-4d2cc3d44e42" width="700">
  - /KiCAD/circuit_sample/circuit_sample_02
    - Identical Hall Sensor & ATTiny85 design, but with different board outline
	- /KiCAD/circuit_sample/recycled_driver
		- Motor driver circuit design, used to demonstrate the capabilities of the recycled PVA filament
  - /KiCAD/ESP_Breakout
    - Breakout board(s) designed to house the ESP32 board used for the ESP_Speaker Design
    - The version utilized on the paper is the "2mm_2row_esp_breakout" design
  - /KiCAD/ESP_Speaker
    - ESP32-based bluetooth speaker design.
    - The exact design used on the paper demo is "rev_2_ESP_Speaker_2row_esp"
    - Alternatively, a design with components only on one side is under "rev_3_ESP_Speaker_2row_esp"
      <img src="https://github.com/user-attachments/assets/2b750f86-1c0d-4df2-8728-5473241576fc" width="700">
  - /KiCAD/fidget
    - Fidget toy example used on the paper, utilizing a 3D circuit design process.
      <img src="https://github.com/user-attachments/assets/3157769b-eb6f-4d5d-8955-e13ad4a703e3" width="700">

