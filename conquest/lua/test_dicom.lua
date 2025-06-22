local i=0
for f in io.lines('c:/temp/searchmx4.txt') do
-- for f in io.lines('\\\\130.88.233.166\\c\\temp\\search.txt') do
  f = string.match(f, "^(.-)\009.+$")
  if true then -- and string.sub(f, 1, 2)~="E:" then
    d = DicomObject:new()
    print(f)
    d:Read(f)
    if not string.find((d.PatientName or "0"), "%d") then
      print(i, d.PatientName, f)
    end
  end
  i=i+1
--  if i>10 then break end
  if (i%1000)==0 then print(i) end
end
