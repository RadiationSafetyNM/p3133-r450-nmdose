-- add  memo={} to association event in dicom.ini
memo = memo or {}
if true or memo.ukcatID and memo.christieID and Data.PatientID==memo.christieID then
  Data["9999,1234"]=memo.ukcatID
  return
end
local patid = string.gsub(Data.PatientID, 'RBV', '')
local l = require("luasql_postgres")
local env = l.postgres()
local con = env:connect("key_db", "key_admin", "**********************")
local cur = con:execute("SELECT patient_id from key_value where key_value = '"..patid.."'")
local row = cur:fetch ({}, "a") -- the rows will be indexed by field names
if not row then
  cur:close()
  con:close()
  env:close()
  print('*** No UKCAT ID found for '..Data.PatientID)
  reject()
  return
else
  Data["9999,1234"]= tostring(row.patient_id)
  memo.ukcatID     = tostring(row.patient_id)
  memo.christieID  = Data.PatientID
end
cur:close()
con:close()
env:close()