testLogger = optim.Logger(paths.concat(opt.save, opt.testDir .. '.log'))

local batchNumber
local acc, loss, bacc, true_nonporn, total_nonporn, true_porn, total_porn
local timer = torch.Timer()

function save_to_file(file, text)
  local f = io.open(file, "a")
  if f then 
    f:write(text)
    f:close()
  end
  return f ~= nil
end

local dump = function(vec)
    vec = vec:view(vec:nElement())
    local t = {}
    for i=1,vec:nElement() do
        t[#t+1] = string.format('%.4f', vec[i])
    end
    return table.concat(t, '  ')
end

function test()
    local optimState 
    batchNumber = 0
    cutorch.synchronize()
    timer:reset()

    -- set the dropouts to evaluate mode
    model:evaluate()
    if(opt.crops10) then nDiv = 10 else nDiv = 1 end
    local N = nTest/torch.floor(opt.batchSize/nDiv) -- nTest is set in data.lua
    print("N: " .. N)

    if(opt.evaluate) then
        print('==> testing final predictions')
        clipScores = torch.Tensor(N, nClasses):zero()
--        print('clipScores size: '.. clipScores:dim() .. ' ' .. clipScores:size(1) .. ' ' .. clipScores:size(2))
        print('clipScores size: '.. clipScores:dim() )
    else
        optimState = torch.load(paths.concat(opt.save, 'optimState_' .. epoch .. '.t7'))
        print('==> validation epoch # ' .. epoch)
    end

    acc  = 0
    loss = 0
    bacc = 0
    true_nonporn = 0
    total_nonporn = 0
    true_porn = 0
    total_porn = 0

    for i=1, N do
        local indexStart = (i-1) * torch.floor(opt.batchSize/nDiv) + 1
        local indexEnd = (indexStart + torch.floor(opt.batchSize/nDiv) - 1)
        donkeys:addjob(
            -- work to be done by donkey thread
            function()
                local inputs, labels, indices, video_paths = testLoader:get(indexStart, indexEnd)
                --print('inputs: ['.. inputs:dim() .. ' ' .. inputs:size(1) .. ' ' .. inputs:size(2) .. ' ' .. inputs:size(3) .. ' ' .. inputs:size(4) .. ' ' .. inputs:size(5) .. '] labels: ['.. labels:dim()  .. ' ' .. labels:size(1) .. '] indices: [' .. indices:dim() .. ' ' .. indices:size(1) .. ']')
                return inputs, labels, indices, video_paths
            end,
        -- callback that is run in the main thread once the work is done
        testBatch
        )
    end

    donkeys:synchronize()
    cutorch.synchronize()

    acc  = acc * 100 / nTest
    loss = loss / (nTest/torch.floor(opt.batchSize/nDiv)) -- because loss is calculated per batch
    bacc = ((true_nonporn / total_nonporn) + (true_porn / total_porn)) * 100 / 2

    if(not opt.evaluate) then
        testLogger:add{
            ['epoch'] = epoch,
            ['acc'] = acc,
            ['bacc'] = bacc,
            ['loss'] = loss,
            ['LR'] = optimState.learningRate
        }
        opt.plotter:add('accuracy', 'test', epoch, acc)
        opt.plotter:add('balanced_accuracy', 'test', epoch, bacc)
        opt.plotter:add('loss', 'test', epoch, loss)
        print(string.format('Epoch: [%d][TESTING SUMMARY] Total Time(s): %.2f \t Loss: %.2f \t Acc: %.2f \t Bacc: %.2f\n',
            epoch, timer:time().real, loss, acc, bacc))
    else
        paths.dofile('donkey.lua')
        local videoAcc = testLoader:computeAccuracy(clipScores)
        local result = {}
        result.accuracy = videoAcc
        result.balanced_clip_accuracy = bacc
        result.clip_accuracy = bacc
        result.scores = clipScores
        torch.save(paths.concat(opt.save, 'result.t7'), result)
        testLogger:add{
            ['clipAcc'] = acc,
            ['clipBacc'] = bacc,
            ['videoAcc'] = videoAcc
        }
        print(string.format('[TESTING SUMMARY] Total Time(s): %.2f \t Loss: %.2f \t Clip Acc: %.2f \t Clip Bacc: %.2f \t Video Acc: %.2f\n',
            timer:time().real, loss, acc, bacc, videoAcc))
    end
end -- of test()
-----------------------------------------------------------------------------

local inputs = torch.CudaTensor()
local labels = torch.CudaTensor()

function testBatch(inputsCPU, labelsCPU, indicesCPU, video_paths)
--     print('inputsCPU: ['.. inputsCPU:dim() .. ' ' .. inputsCPU:size(1) .. ' ' .. inputsCPU:size(2) .. ' ' .. inputsCPU:size(3) .. ' ' .. inputsCPU:size(4) .. ' ' .. inputsCPU:size(5) .. '] labelsCPU: ['.. labelsCPU:dim()  .. ' ' .. labelsCPU:size(1) .. '] indicesCPU: [' .. indicesCPU:dim() .. ' ' .. indicesCPU:size(1) .. ']')
--     print('video_paths')
--     print(video_paths)
	 
    if(opt.crops10) then
        batchNumber = batchNumber + torch.floor(opt.batchSize/10)
    else
        batchNumber = batchNumber + torch.floor(opt.batchSize)
    end
    inputs:resize(inputsCPU:size()):copy(inputsCPU)
--    print('inputs: ['.. inputs:dim() .. ' ' .. inputs:size(1) .. ' ' .. inputs:size(2) .. ' ' .. inputs:size(3) .. ' ' .. inputs:size(4) .. ' ' .. inputs:size(5) .. ']')

    local outputs
    if(opt.finetune == 'last') then
        outputs = model:forward(features:forward(inputs))
    else
        outputs = model:forward(inputs)
		feats = model.modules[22].output
    end
--    print('A outputs: ['.. outputs:dim()  .. ' ' .. outputs:size(1) .. ']')
--    for teste = 1, outputs:size(1) do
--        print ("outputs")
--        print (outputs)
--    end

    if(opt.crops10) then
        outputs     = torch.reshape(outputs, outputs:size(1)/10, 10, outputs:size(2))
        outputs     = torch.mean(outputs, 2):view(opt.batchSize/10, -1) -- mean over 10 crops
        labelsCPU   = labelsCPU:index(1, torch.range(1,  labelsCPU:size(1), 10):long())
        indicesCPU  = indicesCPU:index(1, torch.range(1, indicesCPU:size(1), 10):long())
    else
        outputs = outputs:view(opt.batchSize, -1) -- useful for opt.batchSize == 1
    end
    
--    print('outputs: ['.. outputs:dim()  .. ' ' .. outputs:size(1) .. ' ' .. outputs:size(2) .. ']')
    
    labels:resize(labelsCPU:size()):copy(labelsCPU)
    local lossBatch = criterion:forward(outputs, labels) 
    cutorch.synchronize()
    loss = loss + lossBatch

    local scoresCPU = outputs:float() -- N x 101
  --  print ("scoresCPU")
--    print (scoresCPU)
    local gt, pred
--    print('scoresCPU: ['.. scoresCPU:dim()  .. ' ' .. scoresCPU:size(1) .. ' ' .. scoresCPU:size(2) .. ']')
    
    local _, scores_sorted = scoresCPU:sort(2, true)
--    print("scores_sorted")
--    print(scores_sorted)
    for i=1,labelsCPU:size(1) do
        gt = labelsCPU[i]                    -- ground truth class
        pred = scores_sorted[i][1]           -- predicted class
--        print("gt")
--        print(gt)
--        print("pred")
--        print(pred)
--        print("indicesCPU[i]")
--        print(indicesCPU)

        if pred == gt then  -- correct prediction
            acc = acc + 1
            if labelsCPU[i] == 1 then
                true_nonporn = true_nonporn + 1
                total_nonporn = total_nonporn + 1
            else
                true_porn = true_porn + 1
                total_porn = total_porn + 1
            end
        else
            if gt == 1 then
                total_nonporn = total_nonporn + 1
            else
                total_porn = total_porn + 1
            end
        end

		if unexpected_condition then print("error saving clipScores!") end
        if(opt.evaluate) then
		    save_to_file(paths.concat(opt.save, 'feats.txt'), string.format('p %s i %d l %d s %s f %s\n', video_paths[i], indicesCPU[i], labelsCPU[i], dump(scoresCPU[i]), dump(feats)))
            if indicesCPU[i] then
                clipScores[indicesCPU[i]] = scoresCPU[i]
            else
                print(string.format('indicedCPU invalid i %d - (indicesCPU) %d] \t scoresCPU[i] %f \t Acc %.2f', i, #indicesCPU, scoresCPU[i]))
            end
        end
        collectgarbage()
    end

	print(true_nonporn, total_nonporn, true_porn, total_porn)
    bacc = ((true_nonporn / total_nonporn) + (true_porn / total_porn)) * 100 / 2
    if(opt.evaluate) then
        print(string.format('Testing [%d/%d] \t Loss %.4f \t Acc %.2f \t Bacc %.2f', batchNumber, nTest, lossBatch, 100*acc/batchNumber, bacc))
    else
        print(string.format('Epoch: Testing [%d][%d/%d] \t Loss %.4f \t Acc %.2f \t Bacc %.2f', epoch, batchNumber, nTest, lossBatch, 100*acc/batchNumber, bacc))
    end
    collectgarbage()
end