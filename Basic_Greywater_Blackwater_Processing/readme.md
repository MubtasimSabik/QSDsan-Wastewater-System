These scripts simulate a Greywater processing system. 

components.py - We are modelling the greywater stream's components with the defined configurations in SAmpSONS2 tool. QSDsan by default has stream class that does not fully emulate or quantify the components we are interested in.

GreywaterBuild.py - Creating the greywater stream based on the custom list of components.

COD_MBR.py - A custom COD based MBR system. 

mainSystem.py - Main function. The process is Influent (Greywater + Blackwater) 

Greywater -> MBR -> MBR Effluent + MBR Sludge ,
Blackwater -> Anaerobic Digester -> Digestate + Biogas
