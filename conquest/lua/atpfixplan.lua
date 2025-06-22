-- Process RTPLAN for ATP course
-- relink to original case
-- mvh 20231126 creation for ATP Lisbon 2023

if Data.Modality~='RTPLAN' then
  return
end

-- use drag and drop filename to get to folder names e.g. breast\elekta\1.dcm
local cas, man, nr = string.match(Filename, '.+\\(.-)\\(.-)\\(.-)%.dcm')
print(Filename)
print(cas, man, nr)

-- use original plan to read UIDs to link to correct item
local target = [[C:\Data\ESTRO_ATP_2022\casedata\Meningioma\2.16.840.1.113669.2.931128.94439860.20120719155307.454283_0001_000000_15635445090251.dcm]]
if string.find(Filename, 'lung') then
  target = [[C:\Data\ESTRO_ATP_2022\casedata\Lung\2.16.840.1.113669.2.931128.94439860.20120719155334.479424_0001_000000_156354453202e0.dcm]]
elseif string.find(Filename, 'breast') then
  target = [[C:\Data\ESTRO_ATP_2022\casedata\Breast\RS.1.2.246.352.221.4836170325121371215.18437098840638767749.dcm]]
elseif string.find(Filename, 'oropharynx') then
  target = [[C:\Data\ESTRO_ATP_2022\casedata\Oropharnyx\2.16.840.1.113669.2.931128.94439860.20120719155239.706621_0000_000000_156354449801fe.dcm]]
end

local tgt= DicomObject:new()
tgt:Read(target)

-- only for layout of RTDOSE object contents not used
local sample =
{
 MediaStorageSOPClassUID="1.2.840.10008.5.1.4.1.1.481.2",
 MediaStorageSOPInstanceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816249.140.12",
 TransferSyntaxUID="1.2.840.10008.1.2",
 ImplementationClassUID="1.2.826.0.1.3680043.2.135.1066.101",
 ImplementationVersionName="1.5.0/WIN32\000",

 SpecificCharacterSet="ISO_IR 100",
 InstanceCreationDate="20220926",
 InstanceCreationTime="181558.000000",
 SOPClassUID="1.2.840.10008.5.1.4.1.1.481.2",
 SOPInstanceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816249.140.12",
 StudyDate="20170407",
 SeriesDate="20220926",
 ContentDate="20220926",
 StudyTime="112341.000000",
 SeriesTime="181558.000000",
 ContentTime="181558.000000",
 AccessionNumber="",
 Modality="RTDOSE",
 Manufacturer="RaySearch Laboratories",
 InstitutionName="",ReferringPhysicianName="",
 SeriesDescription="Menigeoom_4",
 OperatorsName="",
 ManufacturerModelName="RayStation",

 PatientName="MENINGIOMA",
 PatientID="MENINGIOMA",
 PatientBirthDate="",
 PatientSex="",

 StudyInstanceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816223.406.7",
 SeriesInstanceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816249.156.14",
 StudyID="",
 SeriesNumber="1 ",
 InstanceNumber="1 ",
 ImagePositionPatient="-169.3403\\-90.49844\\-24 ",
 ImageOrientationPatient="1\\0\\0\\0\\1\\0 ",
 FrameOfReferenceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816223.421.9",
 PositionReferenceIndicator="",

 RTPlanLabel =           "51" ,
 RTPlanName =            "BHprim4005" ,
 RTPlanDescription =     "",
 RTPlanDate =            "20180424"  ,
 RTPlanTime =            "154237.000000 " ,
 RTPlanGeometry =        "PATIENT " ,
 PrescriptionDescript =  "BHprim4005:19220180424.141858.001 " ,

--DoseReferenceSequence   Sequence Item
--ToleranceTableSequence   Sequence Item
--FractionGroupSequence   Sequence Item
--PatientSetupSequence   Sequence Item
--BeamSequence           Sequence Item
--ReferencedStructureSetSequence   Sequence Item
}
 
-- create minimal RTPLAN object ignoring unneeded stuff
local t = Data:Copy()
Data:Reset()
for k, v in pairs(sample) do
  Data[k] = t[k]
end
 
-- keep reference to the plan (which mim does not have)
-- keep the pixeldata and offset vectors (may be too long for = syntax)
local g, e = dictionary('DoseReferenceSequence')
Data:SetVR(g, e, t:GetVR(g, e))
local g, e = dictionary('ToleranceTableSequence')
Data:SetVR(g, e, t:GetVR(g, e))
local g, e = dictionary('FractionGroupSequence')
Data:SetVR(g, e, t:GetVR(g, e))
local g, e = dictionary('PatientSetupSequence')
Data:SetVR(g, e, t:GetVR(g, e))
local g, e = dictionary('BeamSequence')
Data:SetVR(g, e, t:GetVR(g, e))
local g, e = dictionary('IonBeamSequence')
Data:SetVR(g, e, t:GetVR(g, e))
local g, e = dictionary('ReferencedStructureSetSequence')
Data:SetVR(g, e, t:GetVR(g, e))

-- link the RTPLAN to the target RTPLAN (clinical plan from institute)
Data.StudyInstanceUID = tgt.StudyInstanceUID
Data.SeriesInstanceUID= changeuid(tgt.SeriesInstanceUID, '', '#'..man)
Data.SeriesDescription = man

Data.PatientID = tgt.PatientID
Data.PatientName = tgt.PatientName
Data.RTPlanName = man..nr
Data.InstanceNumber = nr

Data.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID = tgt.SOPInstanceUID

-- just to make sure it is unique (use updated dgate64.exe!)
Data.SOPInstanceUID = changeuid(Data.SOPInstanceUID, '', '#'..tgt.PatientID)

local fixed = [[C:\Data\ESTRO_ATP_2023\fixedplans\]]..cas..[[\]]..man..[[\\]]
mkdir(fixed)
Data:Write(fixed..nr..[[.dcm]])

--call destroy if you do not want to load data into the server
--destroy()
