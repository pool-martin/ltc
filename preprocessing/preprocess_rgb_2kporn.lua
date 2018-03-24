require 'torch'
require 'paths'

baseDir = '/data/torch/ltc/datasets/2kporn/rgb/jpg/'
outputDir = '/data/torch/ltc/datasets/2kporn/rgb/t7/'
etf_frame = '/DL/2kporn/etf_frame/'

--target_videos = {'vNonPorn000459','vNonPorn000690','vNonPorn000641','vNonPorn000934','vNonPorn000755','vPorn000427','vPorn000716','vPorn000419','vPorn000456','vPorn000426','vNonPorn000941','vPorn000423','vNonPorn000987','vNonPorn000424','vPorn000445','vNonPorn000797','vNonPorn000433','vNonPorn000245','vPorn000438','vNonPorn000849','vNonPorn000814','vNonPorn000421','vNonPorn000010','vNonPorn000966','vNonPorn000620','vNonPorn000434','vNonPorn000856','vPorn000459','vNonPorn000993','vNonPorn000537','vNonPorn000604','vPorn000446','vNonPorn000649','vNonPorn000853','vPorn000410','vNonPorn000449','vNonPorn000629','vPorn000416','vPorn000408','vNonPorn000426','vNonPorn000960','vNonPorn000603'}

target_videos = {'vPorn000446', 'vPorn000445', 'vPorn000438', 'vPorn000427', 'vPorn000426', 'vPorn000423', 'vPorn000416', 'vNonPorn000459', 'vNonPorn000434', 'vNonPorn000426'}
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

local function has_value (tab, val)
    for index, value in ipairs(tab) do
        if value == val then
            return true
        end
    end

    return false
end

for videoName in paths.iterdirs(baseDir) do
	if has_value( target_videos, videoName) then
		videoPath=paths.concat(baseDir,videoName)
		video_etff=paths.concat(etf_frame,videoName..'.etf')
		local etf_lines = lines_from(video_etff)

		print(videoPath)

		local exit_loop = 0
		for k,v in pairs(etf_lines) do
			print('line[' .. k .. ']', v)
			local tokens = {}
			for word in v:gmatch("%S+") do table.insert(tokens, word) end
			if(tokens[4] == 't') then
				class='Porn'
			else
				class='NonPorn'
			end

			local videoTable={}

			local beg    = tonumber(tokens[2]) + 1
			local ending = tonumber(tokens[2]) + tonumber(tokens[3])
			for i=beg,ending do
				filename = paths.concat(videoPath, videoName..string.format('.mp4_%05d.jpg', i))
				videoTable[i-beg+1]=readJpgAsBinary(filename)
				if videoTable[i-beg+1] == {} then
					print(videoName..' with troubles to process!!!')
					exit_loop = 1
					break
				end
			end

			if exit_loop == 1 then
				exit_loop = 0
				break
			end

			os.execute('mkdir -p '..paths.concat(outputDir, class))
			local outFile = paths.concat(outputDir, class, videoName..string.format('_%02d.mp4.t7',k))
			torch.save(outFile, videoTable)
		end
	end
end