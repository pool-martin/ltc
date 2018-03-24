require 'torch'
require 'paths'

baseDir = '/data/torch/ltc/datasets/2kporn/flow/jpg/'
outputDir = '/data/torch/ltc/datasets/2kporn/flow/t7/'
etf_frame = '/DL/2kporn/etf_frame/'

target_videos = {'vNonPorn000459','vNonPorn000690','vNonPorn000641','vNonPorn000934','vNonPorn000755','vPorn000427','vPorn000716','vPorn000419','vPorn000456','vPorn000426','vNonPorn000941','vPorn000423','vNonPorn000987','vNonPorn000424','vPorn000445','vNonPorn000797','vNonPorn000433','vNonPorn000245','vPorn000438','vNonPorn000849','vNonPorn000814','vNonPorn000421','vNonPorn000010','vNonPorn000966','vNonPorn000620','vNonPorn000434','vNonPorn000856','vPorn000459','vNonPorn000993','vNonPorn000537','vNonPorn000604','vPorn000446','vNonPorn000649','vNonPorn000853','vPorn000410','vNonPorn000449','vNonPorn000629','vPorn000416','vPorn000408','vNonPorn000426','vNonPorn000960','vNonPorn000603'}

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

function lines_to(minmax_out_file_path, minmax_lines)
  local handle_file = io.open(minmax_out_file_path, "w")
  for k,v in pairs(minmax_lines) do
    handle_file:write(v, "\r\n")
  end
end

function table.slice(tbl, first, last, step)
  local sliced = {}

  for i = first or 1, last or #tbl, step or 1 do
    sliced[#sliced+1] = tbl[i]
  end

  return sliced
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
		local minmaxfile_path = paths.concat(baseDir,videoName, videoName..'.mp4_minmax.txt')
		local etf_lines = lines_from(video_etff)
		local minmax_file = lines_from(minmaxfile_path)

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

			videoTable.x={}
			videoTable.y={}
			local beg    = tonumber(tokens[2]) + 1
			local ending = tonumber(tokens[2]) + tonumber(tokens[3]) - 1
			for i=beg,ending do
				x_filename = paths.concat(videoPath, videoName..string.format('.mp4_%05d_x.jpg', i))
				y_filename = paths.concat(videoPath, videoName..string.format('.mp4_%05d_y.jpg', i))
				videoTable.x[i-beg+1]=readJpgAsBinary(x_filename)
				videoTable.y[i-beg+1]=readJpgAsBinary(y_filename)
				if videoTable.x[i-beg+1] == {} or videoTable.y[i-beg+1] == {} then
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
			minmax_out_file = paths.concat(outputDir, class, videoName..string.format('_%02d.mp4.minmax.txt',k))
			lines_to(minmax_out_file,table.slice(minmax_file, beg, beg+ending))

			local outFile = paths.concat(outputDir, class, videoName..string.format('_%02d.mp4.t7',k))
			torch.save(outFile, videoTable)

			local outPath = paths.concat(outputDir, class)
			os.execute('cp "'..minmaxfile_path..'" '..outPath)
		end
	end
end

