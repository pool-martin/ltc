
-- see if the file exists
function file_exists(file)
  local f = io.open(file, "rb")
  if f then f:close() end
  return f ~= nil
end

-- get all lines from a file, returns an empty 
-- list/table if the file does not exist
function lines_from(file)
  if not file_exists(file) then return {} end
  lines = {}
  for line in io.lines(file) do 
    lines[#lines + 1] = line
  end
  return lines
end

function split_string(inputstr, sep)
        if sep == nil then
                sep = "%s"
        end
        local t={} ; i=1
        for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
                t[i] = str
                i = i + 1
        end
        return t
end

function readJpgAsBinary(imfile)
    if not file_exists(imfile) then return {} end
    local fin = torch.DiskFile(imfile, 'r')
    fin:binary()
    fin:seekEnd()
    local file_size_bytes = fin:position() - 1
    fin:seek(1)
    local img_binary = torch.ByteTensor(file_size_bytes)
    fin:readByte(img_binary:storage())
    fin:close()
    return img_binary
end

function writeBinaryAsJpg(imfile, img_binary)
    local fin = torch.DiskFile(imfile, 'w')
    fin:binary()
    fin:writeByte(img_binary:storage())
    fin:close()
end
