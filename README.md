To run FLASHMem Memory System Simulator:

1. Got to the project root foldr FLASHMem ` cd .\FLASHMem\`
2. Install the project requirements: `pip install -r .\requirements.txt`
3. Run FLASHMem.py with a config file as a command line argument, for example:
`python .\FLASHMem.py .\PatternConfigs\InputConfigs\SystemFailureFlows\failure_pattern_after_successful.yaml`

In case of pattern failure check the logs in FLASHMem\Logs

See overview of PatternGenerator, WritingPatternDetector and FrameTransmitter in 
FLASHMem\Documentation\Task1.pdf and FLASHMem\Documentation\Task2.pdf 