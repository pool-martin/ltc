paths.dofile('dataset.lua')

-- This file contains the data-loading logic and details.
-- It is run by each data-loader thread.
------------------------------------------

-- a cache file of the training metadata (if doesnt exist, will be created)
local trainCache = paths.concat(opt.cache, 'trainCache.t7')
local testCache = paths.concat(opt.cache, 'testCache.t7')
local meanstdCache = paths.concat(opt.cache, 'meanstdCache.t7')

-- Check for existence of opt.data
if not os.execute('cd ' .. opt.data) then
    error(("could not chdir to '%s'"):format(opt.data))
end

local loadSize   = opt.loadSize               
local sampleSize = opt.sampleSize                                      
   
local mean,std

local function getInterval(chunkNo)
    return (chunkNo - 1)*opt.slide + 1
end

-- Get Height and Width for video file
local function getDimensions(video_name)
   if string.match(video_name, "NonPorn") then
       video_name = video_name:sub(1, 14)
   else
       video_name = video_name:sub(1, 11)
   end
--    print(video_name) 
   paths.dofile('utils.lua')
   local lines = lines_from(paths.concat(opt.dimensionsDir, video_name .. '.etf'))
--    print(video_name .. '  ' .. lines[1]) 
   local dimensions = split_string(lines[1],'x')
   return tonumber(dimensions[1]), tonumber(dimensions[2])
end

local function getNumberOfFrames(video_name)
   if string.match(video_name, "_") then
       video_name = video_name:sub(1, -8)
   end
--    print(video_name) 
   paths.dofile('utils.lua')
   local lines = lines_from(paths.concat(opt.dimensionsDir .. '/number_of_frames_video', video_name .. '.etf'))
--    print(video_name .. '  ' .. lines[1]) 
   return tonumber(lines[1])
end

local function getVideoFPS(video_name)
   if string.match(video_name, "_") then
       video_name = video_name:sub(1, -8)
   end
--    print(video_name) 
   paths.dofile('utils.lua')
   local lines = lines_from(paths.concat(opt.dimensionsDir .. '/video_fps', video_name .. '.etf'))
--    print(video_name .. '  ' .. lines[1]) 
   return tonumber(lines[1])
end

-- Load a sequence of rgb images
local function loadRGB(path, set)
    local _className = paths.basename(paths.dirname(path))
    local _videoName = paths.basename(path)
    local matched = _videoName:match('.mp4_%d%d%d%d')
    local video
    if(opt.nott7 == false) then
        if(matched) then
            video = torch.load(paths.concat(opt.framesRoot, _className, string.sub(_videoName:match("(.*".. '_'..")"), 1, -2) ..'.t7'))
        else
            video = torch.load(paths.concat(opt.framesRoot, _className, _videoName..'.t7'))
        end
    end
    
    -- Overwrite default height and width for video based values
    if(opt.dimensionsDir ~= '') then
        loadSize[3], loadSize[4] = getDimensions(_videoName)
    end
    local N
    local offset
    if(opt.nott7 == false) then
        N = #video -- #frames
        offset = 1e-2
    else
        N = tonumber(string.sub(_videoName, -9, -5))
        offset = tonumber(string.sub(_videoName, -15,-11))
    end
--    print('_videoName ' .. _videoName)
--    print('N ' .. N)
--    print('offset ' .. offset)
    local t_beg, t_end

    if(opt.framestep = 'fps_based') then
       opt.framestep = (getVideoFPS(_videoName) * opt.time_window)/loadSize[2]
    end

    if(matched == nil) then -- during training epochs (i.e. one clip per video)
        if(set == 'train') then -- random clip
            t_beg = math.ceil(torch.uniform( offset, N-(loadSize[2] * opt.framestep) +1))
        elseif(set == 'test') then
            t_beg = offset -- first clip, one can change it to middle clip etc
        end
    else -- final test (i.e. all clips)
        t_beg = getInterval(tonumber(matched:sub(6, 9)))
        -- If the chunk is the last bit with some frames overlapped from the previous
        if(t_beg + (loadSize[2] * opt.framestep) - 1 > N) then
            t_beg = N - (loadSize[2] * opt.framestep) + 1
        end
    end

    local nPad = 0
	if(opt.nott7 == false) then
		if(N < loadSize[2] or t_beg <= 0) then -- Not enough frames
			nPad = loadSize[2] - N
			t_beg = 1
		end
	else
		if((N - offset + 1) < (loadSize[2] * opt.framestep) or t_beg <= 0) then -- Not enough frames
			opt.framestep = (N - offset +1)/ loadSize[2]
			--nPad = (loadSize[2] * opt.framestep) - (N - offset + 1)
			nPad = 0
			t_beg = tonumber(string.sub(_videoName, -15,-11))
		end
	end

    t_end = t_beg + (loadSize[2] * opt.framestep) - 1
   
    -- Allocate memory
    local input
    if(opt.cropbeforeresize) then
        if(loadSize[3] > loadSize[4]) then
            loadSize[3] = loadSize[4]
		end
        if(loadSize[4] > loadSize[3]) then
            loadSize[4] = loadSize[3]
		end
        input = torch.FloatTensor(loadSize[1], loadSize[2], loadSize[3], loadSize[4])
    else
        input = torch.FloatTensor(loadSize[1], loadSize[2], loadSize[3], loadSize[4])
    end
   
    -- Read/process frames
    for tt = t_beg,t_end - nPad, opt.framestep do
        if(opt.nott7 == false) then
            img = image.decompressJPG(video[tt]:byte())-- [0, 1]
        else
            file_name = paths.concat(opt.framesRoot .. '/../jpg', string.sub(_videoName,1, -17), string.sub(_videoName,1, -17) .. string.format('.mp4_%05d.jpg', math.ceil(tt)))
            if not file_exists(file_name) then
                print(file_name .. ' not exist')
				print(t_beg)
				print(t_end)
				print(nPad)
            end
--            print(opt.framesRoot)
                img = image.decompressJPG(readJpgAsBinary(file_name):byte())
        end
        if(opt.cropbeforeresize) then
            input[{{}, {tt - t_beg + 1}, {}, {}}] = image.crop(img, 'c', loadSize[4], loadSize[3]):float():mul(opt.coeff)
        else
            input[{{}, {tt - t_beg + 1}, {}, {}}] = image.scale(img, loadSize[4], loadSize[3]):float():mul(opt.coeff)
        end
    end
   if(opt.nott7 == false) then
    if(nPad > 0) then
        if(opt.padType == 'copy') then  
            local nCopies = math.ceil(nPad / N)

            for nc = 1, nCopies do
                if(N*(nc+1) > loadSize[2]) then
                    input[{{}, {N*nc+1, loadSize[2]}, {}, {}}] = input[{{}, {N*(nc+1) - loadSize[2] +1, N}, {}, {}}]
                else
                    input[{{}, {N*nc+1, N*(nc+1)}, {}, {}}] = input[{{}, {1, N}, {}, {}}]
                end
            end
        elseif(opt.padType == 'zero') then
            input[{{}, {N+1, N+nPad}, {}, {}}] = 0
        end
    end
   else
    if(nPad > 0) then
        if(opt.padType == 'copy') then  
            local nCopies = math.ceil(nPad / (N - offset + 1))

            for nc = 1, nCopies do
                if((N - offset + 1)*(nc+1) > loadSize[2]) then
                    input[{{}, {(N - offset + 1)*nc+1, loadSize[2]}, {}, {}}] = input[{{}, {(N - offset + 1)*(nc+1) - loadSize[2] +1, (N - offset + 1)}, {}, {}}]
                else
                    input[{{}, {(N - offset + 1)*nc+1, (N - offset + 1)*(nc+1)}, {}, {}}] = input[{{}, {1, (N - offset + 1)}, {}, {}}]
                end
            end
        elseif(opt.padType == 'zero') then
            input[{{}, {(N - offset + 1)+1, (N - offset + 1)+nPad}, {}, {}}] = 0
        end
    end
   end
   
    if opt.bgr then input = input:index(1, torch.LongTensor{3, 2, 1}) end
    return input
end  

-- Load a sequence of flow images
local function loadFlow(path, set)
    local _className = paths.basename(paths.dirname(path))
    local _videoName = paths.basename(path)

--    print('video ' .. _videoName)

    -- Overwrite default height and width for video based values
    if(opt.dimensionsDir ~= '') then
        loadSize[3], loadSize[4] = getDimensions(_videoName)
    end

    local matched = _videoName:match('.avi_%d%d%d%d')
    local video, minmaxfile
    if(opt.nott7 == false) then
        if(matched) then
            video = torch.load(paths.concat(opt.framesRoot, _className, string.sub(_videoName:match("(.*".. '_'..")"), 1, -2) ..'.t7'))
            minmaxfile = paths.concat(opt.framesRoot, _className, string.sub(_videoName:match("(.*".. '_'..")"), 1, -2) ..'_minmax.txt')
        else
            video = torch.load(paths.concat(opt.framesRoot, _className, _videoName..'.t7'))
            minmaxfile = paths.concat(opt.framesRoot, _className, _videoName) .. '_minmax.txt'
        end
    else
        if(matched) then
            minmaxfile = paths.concat(opt.framesRoot, _className, string.sub(_videoName:match("(.*".. '_'..")"), 1, -2) ..'_minmax.txt')
        else
            minmaxfile = paths.concat(opt.framesRoot, _className, _videoName) .. '_minmax.txt'
        end

    end

    local N
    local offset
    if(opt.nott7 == false) then
        N = #video.x -- #frames
        offset = 1e-2
    else
        N = tonumber(string.sub(_videoName, -9, -5))
        offset = tonumber(string.sub(_videoName, -15,-11))
    end
    local t_beg, t_end

    if(matched == nil) then -- during training epochs (i.e. one clip per video)
        if(set == 'train') then -- random clip
            t_beg = math.ceil(torch.uniform( offset, N-loadSize[2]+1))
        elseif(set == 'test') then
            t_beg = offset -- first clip, one can change it to middle clip etc
        end
    else -- final test (i.e. all clips)
        t_beg = getInterval(tonumber(matched:sub(6, 9)))
        -- If the chunk is the last bit with some frames overlapped from the previous
        if(t_beg + loadSize[2] - 1 > N) then
            t_beg = N - loadSize[2] + 1
        end
    end

	local nPad = 0
	if(opt.nott7 == false) then
		if(N < loadSize[2] or t_beg <= 0) then -- Not enough frames
			nPad = loadSize[2] - N
			t_beg = 1
		end
	else
		if((N - offset + 1) < loadSize[2] or t_beg <= 0) then -- Not enough frames
			nPad = loadSize[2] - (N - offset + 1)
			t_beg = tonumber(string.sub(_videoName, -15,-11))
			if(N == offset) then
			end
		end
	end

    t_end = t_beg + loadSize[2] - 1
--    print('LoadFlow 2 ' .. t_beg .. ' ' .. t_end .. ' ' .. N .. ' ' .. minmaxfile)

    local minmax
    if(opt.minmax) then
        minmax = torch.Tensor(N, 4) -- (minx, maxx, miny, maxy)
        local ii = 1
        for l in io.lines(minmaxfile) do   
            local jj = 1
            for word in string.gmatch(l, "%g+") do
                minmax[{ii, jj}] = word
                jj = jj + 1
            end
            ii = ii + 1
        end
    end

    -- Allocate memory
    local input = torch.FloatTensor(loadSize[1], loadSize[2], loadSize[3], loadSize[4])
   
    -- Read/process frames
    for tt = t_beg,t_end - nPad do
        if(opt.nott7 == false) then
            imgx = image.decompressJPG(video.x[tt]:byte())
            imgy = image.decompressJPG(video.y[tt]:byte())
        else
            file_imgx = paths.concat(opt.framesRoot .. '/../jpg', string.sub(_videoName,1, -17), string.sub(_videoName,1, -17) .. string.format('.mp4_%05d_x.jpg', tt))
            file_imgy = paths.concat(opt.framesRoot .. '/../jpg', string.sub(_videoName,1, -17), string.sub(_videoName,1, -17) .. string.format('.mp4_%05d_y.jpg', tt))
            if not file_exists(file_imgx) or not file_exists(file_imgy) then
                print(file_imgx .. ' not exist')
                print(file_imgy .. ' not exist')
				print(t_beg)
				print(t_end)
				print(nPad)
				break;
            else
--            print(opt.framesRoot)
            imgx = image.decompressJPG(readJpgAsBinary(file_imgx):byte())
            imgy = image.decompressJPG(readJpgAsBinary(file_imgy):byte())
			end
        end

        local iH = imgx:size(2)
        local iW = imgx:size(3)
        imgx = image.scale(imgx, loadSize[4], loadSize[3])
        imgy = image.scale(imgy, loadSize[4], loadSize[3])
        local T = tt - t_beg + 1

        -- to-do: if not minmax will be always nil
        if(opt.minmax) then
            input[{{1}, {T}, {}, {}}] = (torch.mul(imgx, minmax[{tt, 2}] - minmax[{tt, 1}]) + minmax[{tt, 1}]):mul(opt.coeff*loadSize[4]/iW)
            input[{{2}, {T}, {}, {}}] = (torch.mul(imgy, minmax[{tt, 4}] - minmax[{tt, 3}]) + minmax[{tt, 3}]):mul(opt.coeff*loadSize[3]/iH)
        end

        if(opt.perframemean) then
            input[{{1}, {T}, {}, {}}] = input[{{1}, {T}, {}, {}}] - torch.mean(input[{{1}, {T}, {}, {}}]);
            input[{{2}, {T}, {}, {}}] = input[{{2}, {T}, {}, {}}] - torch.mean(input[{{2}, {T}, {}, {}}]);
        end
    end
   
   if(opt.nott7 == false) then
    if(nPad > 0) then
        if(opt.padType == 'copy') then  
            local nCopies = math.ceil(nPad / N)

            for nc = 1, nCopies do
                if(N*(nc+1) > loadSize[2]) then
                    input[{{}, {N*nc+1, loadSize[2]}, {}, {}}] = input[{{}, {N*(nc+1) - loadSize[2] +1, N}, {}, {}}]
                else
                    input[{{}, {N*nc+1, N*(nc+1)}, {}, {}}] = input[{{}, {1, N}, {}, {}}]
                end
            end
        elseif(opt.padType == 'zero') then
            input[{{}, {N+1, N+nPad}, {}, {}}] = 0
        end
    end
   else
    if(nPad > 0) then
        if(opt.padType == 'copy') then  
            local nCopies = math.ceil(nPad / (N - offset + 1))
			print('LoadFlow 2 t_beg ' .. t_beg .. ' t_end' .. t_end .. ' nPad ' .. nPad .. '  nCopies ' .. nCopies .. ' N ' .. N .. ' offset ' .. offset .. minmaxfile)

            for nc = 1, nCopies do
                if((N - offset + 1)*(nc+1) > loadSize[2]) then
                    input[{{}, {(N - offset + 1)*nc+1, loadSize[2]}, {}, {}}] = input[{{}, {(N - offset + 1)*(nc+1) - loadSize[2] +1, (N - offset + 1)}, {}, {}}]
                else
                    input[{{}, {(N - offset + 1)*nc+1, (N - offset + 1)*(nc+1)}, {}, {}}] = input[{{}, {1, (N - offset + 1)}, {}, {}}]
                end
            end
        elseif(opt.padType == 'zero') then
            input[{{}, {(N - offset + 1)+1, (N - offset + 1)+nPad}, {}, {}}] = 0
        end
    end
   end

    return input
end


local trainHook = function(self, path)
    collectgarbage()
    local input

    if(opt.stream == 'flow') then
        input = loadFlow(path, 'train')
    else
        input = loadRGB(path, 'train')
    end

    if(input == nil) then
        print(path .. ' is nil.')
        return nil
    else
        iW = input:size(4)
        iH = input:size(3)

        local oW
        local oH
        local sc_w
        local sc_h
        if(opt.scales) then
        -- do random multiscale crop
            sc_w = opt.scales[torch.random(#opt.scales)]
            sc_h = opt.scales[torch.random(#opt.scales)]
            oW = math.ceil(loadSize[3]*sc_w)
            oH = math.ceil(loadSize[3]*sc_h)
        else
            oW = sampleSize[4]
            oH = sampleSize[3]
        end
        local h1 = math.ceil(torch.uniform(1e-2, iH-oH))
        local w1 = math.ceil(torch.uniform(1e-2, iW-oW))
		local out
		if(opt.cropbeforeresize) then
            out = input[{{}, {}, {}, {}}]
		else
            out = input[{{}, {}, {h1, h1+oH-1}, {w1, w1+oW-1}}]
		end

        -- resize to sample size
        if(out:size(1) ~= sampleSize[1] or out:size(2) ~= sampleSize[2] or out:size(3) ~= sampleSize[3] or out:size(4) ~= sampleSize[4]) then
            out_res = torch.Tensor(sampleSize[1], sampleSize[2], sampleSize[3], sampleSize[4])
            for jj = 1, sampleSize[1] do
                for ii = 1, sampleSize[2] do
                    out_res[{{jj}, {ii}, {}, {}}] = image.scale(out[{{jj}, {ii}, {}, {}}]:squeeze(), sampleSize[4], sampleSize[3])
                end
            end
            out = out_res

            -- multiply the flow by the scale factor
            if(opt.stream == 'flow') then
                out[{{1},{},{},{}}]:mul(sampleSize[4]/oW)
                out[{{2},{},{},{}}]:mul(sampleSize[3]/oH)
            end
        end

        assert(out:size(4) == sampleSize[4])
        assert(out:size(3) == sampleSize[3])

        out:add(-mean)
        -- do hflip with probability 0.5
        if torch.uniform() > 0.5 then out = image.flip(out:contiguous(), 4); end

        return out
    end
end

if paths.filep(trainCache) then
    print('Loading train metadata from cache')
    trainLoader = torch.load(trainCache)
    trainLoader.sampleHookTrain = trainHook
    assert(trainLoader.paths[1] == paths.concat(opt.data, 'train'),
          'cached files dont have the same path as opt.data. Remove your cached files at: '
             .. trainCache .. ' and rerun the program')
else
    print('Creating train metadata')

    trainLoader = dataLoader{
        paths = {paths.concat(opt.data, 'train')},                                     
        split = 100,
        verbose = true, 
        forceClasses = opt.forceClasses
    }
    torch.save(trainCache, trainLoader)
    trainLoader.sampleHookTrain = trainHook
end
collectgarbage()

-- do some sanity checks on trainLoader
do
    local class = trainLoader.imageClass
    local nClasses = #trainLoader.classes
    assert(class:max() <= nClasses, "class logic has error")
    assert(class:min() >= 1, "class logic has error")
end

-- End of train loader section
--------------------------------------------------------------------------------

-- function to load 4 corners and the center
local testHook = function(self, path, region, hflip)
    collectgarbage()
    local input

    if(opt.stream == 'flow') then
        input = loadFlow(path, 'test')
    else
        input = loadRGB(path, 'test')
    end

    if(input == nil) then
        print(path .. ' is nil.')
        return nil
    else 
        local oH = sampleSize[3]
        local oW = sampleSize[4];
        iW = input:size(4)
        iH = input:size(3)
        local w1
        local h1
        if(region == 1) then        -- center 
            w1 = math.ceil((iW-oW)/2)
            h1 = math.ceil((iH-oH)/2)
        elseif(region == 2) then    -- top-left corner
            w1 = 1
            h1 = 1
        elseif(region == 3) then    -- top-right corner
            w1 = iW-oW+1
            h1 = 1
        elseif(region == 4) then    -- bottom-left corner
            w1 = 1
            h1 = iH-oH+1
        elseif(region == 5) then    -- bottom-right corner
            w1 = iW-oW+1
            h1 = iH-oH+1
        end

        local out
        if(opt.cropbeforeresize) then
			print('cropbeforeresize 2 ' .. sampleSize[4] .. ' ' .. sampleSize[3])
            out = input[{{}, {}, {}, {}}]
        else
            out = input[{{}, {}, {h1, h1+oH-1}, {w1, w1+oW-1}}]
        end

        -- resize to sample size
        if(out:size(1) ~= sampleSize[1] or out:size(2) ~= sampleSize[2] or out:size(3) ~= sampleSize[3] or out:size(4) ~= sampleSize[4]) then
			print('sample different from out. Sample: ' .. sampleSize[4] .. 'x' .. sampleSize[3] .. ' out: ' .. out:size(4) .. 'x' .. out:size(3))
            out_res = torch.Tensor(sampleSize[1], sampleSize[2], sampleSize[3], sampleSize[4])
            for jj = 1, sampleSize[1] do
                for ii = 1, sampleSize[2] do
                    out_res[{{jj}, {ii}, {}, {}}] = image.scale(out[{{jj}, {ii}, {}, {}}]:squeeze(), sampleSize[4], sampleSize[3])
                end
            end
            out = out_res

            -- multiply the flow by the scale factor
            if(opt.stream == 'flow') then
                out[{{1},{},{},{}}]:mul(sampleSize[4]/oW)
                out[{{2},{},{},{}}]:mul(sampleSize[3]/oH)
            end
        end

        assert(out:size(4) == sampleSize[4])
        assert(out:size(3) == sampleSize[3])

        out:add(-mean)

        if hflip then out = image.flip(out:contiguous(), 4); end
        return out
    end
end

if paths.filep(testCache) then
    print('Loading test metadata from cache')
    testLoader = torch.load(testCache)
    testLoader.sampleHookTest = testHook
    assert(testLoader.paths[1] == paths.concat(opt.data, opt.testDir),
          'cached files dont have the same path as opt.data. Remove your cached files at: '
             .. testCache .. ' and rerun the program')
else
    print('Creating test metadata')
    testLoader = dataLoader{
        paths = {paths.concat(opt.data, opt.testDir)},                                 
        split = 0,
        verbose = true,
        forceClasses = trainLoader.classes -- force consistent class indices between trainLoader and testLoader
    }
    torch.save(testCache, testLoader)
    testLoader.sampleHookTest = testHook
end
collectgarbage()
-- End of test loader section

if paths.filep(meanstdCache) then
    local meanstd = torch.load(meanstdCache)
    mean = meanstd.mean
    std = meanstd.std
    print('Loaded mean and std from cache.')
else
    mean = opt.mean
    std = 1 -- not used for now

    local cache = {}
    cache.mean = mean
    cache.std = std

    torch.save(meanstdCache, cache)
end
