This is the new **Conquest DICOM Server** source code repository, it is the first ever release of the full source code of Conquest Dicom server with full source code, including the windows GUI.

Its USP is simplicity for starters, speed for serious users, and endless configurability for nerds and anybody wanting to automate DICOM workflows.

[Web page] http://www.natura-ingenium.nl/dicom.html

[Forum] (https://forum.image-systems.biz/forum/index.php?board/33-conquest-users/)

[Download current stable release 1.5.0e] (http://natura-ingenium.nl/dicomserver/dicomserver150e.zip)

The commit corresponding to 1.5.0e is here: https://github.com/marcelvanherk/Conquest-DICOM-Server/commit/f7c072e70c8f73482bd35a2fc8ffb23ec2ab39d8

**Conquest DICOM Server** is a group effort and I would like to thank Mark Oskin for the initial library; Lambert Zijp for years of development while at NKI, especially fixing bugs in the transport layers, and adding initial jpeg codecs; Lennert Ploeger for optimising the array implementation and the Delphi exe launcher; Bruce Barton for greatly extending compression and decompression, many many bug fixes and startup code; and Luiz Oliveira for enthousiastically helping developing WEBDicom, providing a sample webDICOM/Cornerstone based viewer, and endless bug finding.

Open source code used includes the Independent JPEG Group's software; charls by Jan de Vaan; François PIETTE's Delphi socket components, Lua5.1 by Roberto Ierusalimschy, Luasocket by Diego Nehab, OpenJpeg (for jepg2000) by Herve Drolon, FreeImage Team, and CS Systemes d'Information, France, SQlite by D Richard Hipp, Delphi UService from an unknown source, MiTeC DBF Table by Michal Mutl, Lunatic Python by Gustavo Niemeyer and PhP Router by Bramus Van Damme. 

In addition, the following minimised sample web viewers are included: papaya (https://github.com/rii-mango/Papaya, build 1446) and ohif (https://github.com/OHIF/Viewers, 1.03). 

The app/newweb code also contains unmaintained interfaces for dwv (https://github.com/ivmartel/dwv), and weasis (https://nroduit.github.io/en/).
