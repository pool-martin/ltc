require 'torch'
require 'paths'

outputFile = 'forceClasses.t7'
outputDir =  '/Exp/torch/ltc/datasets/2kporn/annot'

classTable = {}
classTable[1] = 'NonPorn'
classTable[2] = 'Porn'

os.execute('mkdir -p '..outputDir)
outFile = paths.concat(outputDir, outputFile)
torch.save(outFile, classTable)
