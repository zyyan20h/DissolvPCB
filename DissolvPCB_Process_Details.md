# DissolvPCB 
### Fully Recyclable Electronics with Liquid Metal Conductors and 3D-Printed PVA Substrates
This document the full work flow of creating a circuit board based on the DissolvPCB process in detail, along with tips, recommendations, and general cautions. 
This guide will instruct users through the steps of printing and preparation, assembling, and recycling, as highlighted in the figure below. 

![fab 5](https://github.com/user-attachments/assets/1bb0047c-1413-4340-b7ba-0c9d1987fcdd)


# DissolvPCB Printing & Preparation
## Materials 
- In addition to things like 3D printers and EGaIn, other materials and tools needed for the DissolvPCB fabrication process are:
	- PPE - Gloves, Goggles
 	- Wet wipes (Such as Clorox)
  	- Magnetic Stirrers
  	- Glass Beakers
  	- Scale
  	- Syringe
  	- Fine Tweezers
  	  
		<img src="https://github.com/user-attachments/assets/93e96a32-d90e-4850-b1aa-2b93d38e27f2" width="700">
 
## DissolvPCB Printing
### PVA Nozzle 
- Size
  	- A nozzle size of 0.2 mm is recommended for the smallest possible feature size, trace dimensions, layer detail, etc.
  	- A 0.4 mm nozzle may be used, although some dimensions may have to be increased and the finest pitch components may not be as feasible.
  		In this case, 0.85 mm traces are recommended instead of the default 0.75 mm.
- Cleanup
    - Nozzle Storage
    	- After printing with PVA, it is recommended PLA is loaded into the filament in place and any leftover PVA be extruded out.
  		- As is standard, the unloaded PVA filament should be kept in a filament dryer.
    - Nozzle Cleanout
  		- In cases where the entire nozzle needs to be cleaned, it could be submerged in water to remove any remaining PVA.

### PVA Print Storage
- Moisture Control
    - Filament Dryer should be used whenever possible for the storage of filaments, prints, and finished circuits to avoid moisture damage.
    - If at any point of the DissolvPCB assembly the circuit gets moisture damaged, it can be reversed in most cases in a dryer. Slight changes like warping may remain to some degree.
		
## EGaIn Preparation 

### EGaIn Viscosity Control 
- Oxidation Level
	- The viscosity of the liquid metal is controlled by the oxidation level of EGaIn.
	- EGaIn is very liquid at room temperature. If a thicker consistency is desired, the EGaIn can be oxidized using the magnetic stirrer.
		(Over the air exposure with periodic stirring will work, just slower)
- Viscosity Control
	- EGaIn viscosity can be fine tuned by mixing unoxidized EGaIn in appropriate ratios until the desired consistency is achieved.
		<img src="https://github.com/user-attachments/assets/2fce9176-427c-4d46-b72e-ade76bdb8b0b" width="700">

### EGaIn Storage and Collection 
- General Storage
	- EGaIn should be stored in neutral constainers, such as glass beakers.
		If EGaIn is being stored period of time longer than an hour, a lid is recommended to prevent unwanted oxidation.
	- For long term storage, plastic paint containers may be a good alternative.
		A good sealing lid is essential.
		<img src="https://github.com/user-attachments/assets/221ab0b0-e042-4a6e-814a-f14693b3120c" width="700">

- Collection
	- In most cases, EGaIn can easily be collected using a syringe or a pipette.
   		<img src="https://github.com/user-attachments/assets/e09c6688-989d-4ebf-9490-9ab704cb41a9" width="700">
	- In rare cases where the EGaIn is too thick to be sucked into a syringe, the EGaIn may have to be scooped into the syringe bit by bit.
- EGaIn Recollection ('dump')
    - Having a small beaker of Sodium Hyroxide solution readily available is highly recommended.
    - Any excess EGaIn can be easily collected into one container, while the NaOH solution deoxidizes them, ready for recollection and reuse.
 
### Safety and Cautions
- PPE
	- Gloves and Goggles are a must.
 	- Lab coats may be desireable in case of spills.
- Cautions
	- Small bits of EGaIn may remain on any surface and can spread easily if caution is not taken.
 	- Wet wipes (as pictured) can be a great tool to pick up EGaIn on any surface for cleaning.
  	- Always keep a seperate station dedicated to anything involved with EGaIn.


# DissolvPCB Assembly
## EGaIn
### EGaIn Injection
- Syringe Tip
	- Make sure the tip is clear of any obstruction before attaching to a syringe.
	- The syringe tip can be stored in the NaOH solution after use to remove any leftover EGaIn.
- What is a 'good' injection?
    - A slightly concave shape is desired, as excessive EGaIn can cause shorts and spills.
	<img src="https://github.com/user-attachments/assets/5f4d4545-0a47-4672-acd7-4e3b5c15d19d" width="700">

### Safety & Cautions
- PPE
	- Gloves and Goggles are a must.
 	- Lab coats may be desireable in case of spills.
- Cautions
	- Be weary of potential spills being directed towards the body, especially the face.
 	- Slow, fine manipulation of the EGaIn syringe is recommended, as EGaIn injection takes little to no force.
	- Excessive injections on the print or syringe can be collected into the NaOH solution beaker.
 		Here, the wet wipes can be used to 'wipe' execessive EGaIn into the beaker.
	- When placing components later, checking the EGaIn for proper contact may be necessary.

## Component Assembly
### Component Placement
- Component can be gently seated into its respective sockets once EGaIn is injected.
	A light push may be needed to ensure proper seating.
	<img src="https://github.com/user-attachments/assets/b4e195d6-d039-4eca-82b7-757dfa06f793" width="700">
 
### Component PVA Glue 
- The purpose of PVA glue is to:
  - Hold components in place
  - Prevent EGaIn spills
- Cautions
  - PVA glue, especially ones with higher water content, may deform the circuit body slightly. 
  - Again, make sure there aren't any short circuits before the glue cures.
- After everything is finished, the circuit can be dried and kept using a filament drier.
  	<img src="https://github.com/user-attachments/assets/e7e492cc-4249-4bd3-81b9-32645a3f2dff" width="700">

# DissolvPCB Recycling

## Component Recovery 

### Dissolving DissolvPCB Assemblies
- Any DissolvPCB assembly may be dissolved simply by dropping it into water.
  The dissolving process can be accelerated using warmer water temperatures and occasional stirring.
  	<img src="https://github.com/user-attachments/assets/2203e801-1fb0-4cb1-a3e8-d7e339d98891" width="700">
   
### Component Recovery
- After DissolvPCB is completely dissolved in water, components can be simply plucked out of the PVA solution.
- Components then can be cleaned and dried, then be ready for reuse.
	<img src="https://github.com/user-attachments/assets/61a6ffb1-b46d-496a-831f-566b7ee21e63" width="700">

### Safety & Cautions
- PPE
	- Gloves and Goggles are a must.
 	- Lab coats may be desireable in case of spills.
- Cautions
	- Residual PVA and/or EGaIn may remain on surfaces. Take cautions to avoid contamination
    
## EGaIn Recovery 

### EGaIn Collection & De-Oxidation
- Leftover EGaIn can be de-oxidized and re-consolidated easily using a solution of NaOH.
- Afterwards, EGaIn can be collected using a pipette and stored safely until reuse.
  	<img src="https://github.com/user-attachments/assets/c121fcb1-de04-4462-b4d6-fc394a2756b0" width="700">

### Safety & Disposal 
- After the NaOH solution is used, the basic solution must be neutralized. A safe acidic solution, such as Citric Acid, may be used.
  
## PVA Recovery 

### PVA Recovery - Filter
- The PVA solution should be filtered in case any contaminents are present.
  This also guarentees a cleaner extrusion when recyling the PVA into filament.
  
	<img src="https://github.com/user-attachments/assets/b4269e1b-559c-441a-8d22-488fc39dc5a1" width="700">
  
### PVA Recovery - Drying
- The PVA solution can be transferred into a petri dish to dry. A hot plate can be used here to accelerate the drying.
	<img src="https://github.com/user-attachments/assets/7fc9c474-944d-4756-82d1-f8fb5fb6eafb" width="700">


### PVA Recovery - PVA Glue
- After a certain moisture content of the PVA solution is reached, it can be used as PVA glue for the next iteration of DissolvPCB.
- Storage of PVA glue in a capped syringe may be appropriate.
	<img src="https://github.com/user-attachments/assets/39718fad-2894-4c61-ae3d-16adc372913d" width="700">
  
### PVA Recovery - PVA Filament
#### Raw PVA Material Collection
- Dried PVA Sheets
	- By drying the PVA solution all the way, sheets of PVA can be peeled from the container of choice.
		A slightly flexible container can be easier to peel.

	<img src="https://github.com/user-attachments/assets/778a2f83-fc05-4724-a9cc-3031a2be884d" width="700">

- Moisture Control
	- Extrusion quality can be heavily impacted by moisture in the processing material.
 		Ensure the filament material is kept dry as possible.
   
- Sheet Processing
	- The PVA sheets should be cut into appropriate sizes for filament extrusion.
  

#### PVA Recovery - Filament Extrusion
- Extrusion Temperature
	- Extrusion temperature may vary between extruder machines.
		However, extruded material should be a mouldable clay consistency than a liquid.
	- Too low of a temperature can prevent the extruded filament from being stretched to the desired diameter.
	- Too high of a temperature may cause filament deformation and sticking.

 	- It may be helpful to have airflow over the filament to help it hold its shape after being stretched out
- Extrusion of crude filament
	- Depending on the quality of the PVA base material, the extruded filament may be of low quality (such as bubbling).
   	  In this case, the extruded filament needs to be re-cut and processed again for a high-quality filament.
   - If low quality first extrusion is expected, it may help to extrude thicker filament to reduce work in filament processing.

#### Safety & Cautions
- PPE
	- A mask is highly recommended, gloves may be helpful.
	- Make sure filament extrusion is done in a well-ventilated area.
 		A fume hood, if available, is recommended.
