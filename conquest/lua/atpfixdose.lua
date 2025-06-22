-- Process RTDOSE for ATP course
-- relink to original case
-- mvh 20231126 creation for ATP Lisbon 2023

if Data.Modality~='RTDOSE' then
  return
end

-- use drag and drop filename to get to folder names e.g. breast\elekta\1.dcm
local cas, man, nr = string.match(Filename, '.+\\(.-)\\(.-)\\(.-)%.dcm')
print(Filename)
print(cas, man, nr)

-- use original dose to read UIDs to link to correct item
-- used for UIDs to link to correct item
local target = [[C:\Data\ESTRO_ATP_2022\Clinical_doses\clincal_dose_meningioma.dcm]]
if string.find(Filename, 'lung') then
  target = [[C:\Data\ESTRO_ATP_2022\Clinical_doses\clinical_dose_lung.dcm]]
elseif string.find(Filename, 'breast') then
  target = [[C:\Data\ESTRO_ATP_2022\Clinical_doses\clinical_dose_breast.dcm]]
elseif string.find(Filename, 'oropharynx') then
  target = [[C:\Data\ESTRO_ATP_2022\Clinical_doses\clinical_dose_oropharynx.dcm]]
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

 SliceThickness="3 ",
 SoftwareVersions="13.0.0.1547 (Dicom Export)",

 StudyInstanceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816223.406.7",
 SeriesInstanceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816249.156.14",
 StudyID="",
 SeriesNumber="1 ",
 InstanceNumber="1 ",
 ImagePositionPatient="-169.3403\\-90.49844\\-24 ",
 ImageOrientationPatient="1\\0\\0\\0\\1\\0 ",
 FrameOfReferenceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816223.421.9",
 PositionReferenceIndicator="",

 SamplesPerPixel=1,
 PhotometricInterpretation="MONOCHROME2",
 NumberOfFrames="117 ",
 FrameIncrementPointer="\0040\f\000",
 Rows=101,
 Columns=114,
 PixelSpacing="3\\3 ",
 BitsAllocated=16,
 BitsStored=16,
 HighBit=15,
 PixelRepresentation=0,

 DoseUnits="GY",
 DoseType="EFFECTIVE",
 DoseComment="",
 DoseSummationType="PLAN",
 GridFrameOffsetVector="0\\3\\6\\9\\12\\15\\18\\21\\24\\27\\30\\33\\36\\39\\42\\45\\48\\51\\54\\57\\60\\63\\66\\69\\72\\75\\78\\81\\84\\87\\90\\93\\96\\99\\102\\105\\108\\111\\114\\117\\120\\123\\126\\129\\132\\135\\138\\141\\144\\147\\150\\153\\156\\159\\162\\165\\168\\171\\174\\177\\180\\183\\186\\189\\192\\195\\198\\201\\204\\207\\210\\213\\216\\219\\222\\225\\228\\231\\234\\237\\240\\243\\246\\249\\252\\255\\258\\261\\264\\267\\270\\273\\276\\279\\282\\285\\288\\291\\294\\297\\300\\303\\306\\309\\312\\315\\318\\321\\324\\327\\330\\333\\336\\339\\342\\345\\348 ",
 DoseGridScaling="0.001242712 ",
 TissueHeterogeneityCorrection="IMAGE",
 
 --ReferencedRTPlanSequence=
 --{{ReferencedSOPClassUID="1.2.840.10008.5.1.4.1.1.481.8",
 --  ReferencedSOPInstanceUID="1.2.826.0.1.3680043.2.135.738767.74838703.7.1700816249.156.15"
 --}},
 --PixelData=nil --[[OW not serialized]]
 }
 
-- create minimal RTDOSE object ignoring unneeded stuff
local t = Data:Copy()
Data:Reset()
for k, v in pairs(sample) do
  Data[k] = t[k]
end
 
-- keep reference to the plan (which mim does not have)
-- keep the pixeldata and offset vectors (may be too long for = syntax)
local g, e = dictionary('ReferencedRTPlanSequence')
Data:SetVR(g, e, t:GetVR(g, e))
local g, e = dictionary('PixelData')
Data:SetVR(g, e, t:GetVR(g, e, true))
local g, e = dictionary('GridFrameOffsetVector')
Data:SetVR(g, e, t:GetVR(g, e))


-- link the RTDOSE to the target RTDOSE (clinical plan from institute)
Data.StudyInstanceUID = tgt.StudyInstanceUID
Data.SeriesInstanceUID= changeuid(tgt.SeriesInstanceUID, '', '#'..man)
Data.SeriesDescription = man

Data.FrameOfReferenceUID = tgt.FrameOfReferenceUID
Data.PatientID = tgt.PatientID
Data.PatientName = tgt.PatientName
Data.DoseComment = man..nr
Data.InstanceNumber = nr

-- just to make sure it is unique (use updated dgate64.exe!)
Data.SOPInstanceUID = changeuid(Data.SOPInstanceUID, '', '#'..tgt.PatientID)

local fixed = [[C:\Data\ESTRO_ATP_2023\fixed\]]..cas..[[\]]..man..[[\\]]
mkdir(fixed)
Data:Write(fixed..nr..[[.dcm]])

--call destroy if you do not want to load data into the server
--destroy()
