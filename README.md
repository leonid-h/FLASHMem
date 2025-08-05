To run FLASHMem Memory System Simulator:

1. Go to the project root folder FLASHMem ` cd .\FLASHMem\`
2. Install the project requirements: `pip install -r .\requirements.txt`
3. Run FLASHMem.py with a config file as a command-line argument, for example:
`python .\FLASHMem.py .\PatternConfigs\InputConfigs\SystemFailureFlows\failure_pattern_after_successful.yaml`

In case of pattern failure, check the logs in FLASHMem\Logs

Please pay attention that I changed the structure of the YAML input files slightly:

- changed "writing_pattern" to "writing_patterns" - to not have re-declarations of the same key (writing_pattern)
- changed "memory_write" to "memory_writes" - to not have re-declarations of the same key (memory_write)
- added "name" (only used in log filenames and not for logic) to list multiple patterns in one file like so:
    
```
  writing_patterns:
    - name: FAST_WRITE_BELOW_TH
      threshold: 26     # number of writes
      delta: 50         # seconds
      memory_writes:
        -
        -
        -
    - name: SLOW_WRITE_BELOW_TH
      threshold: 26     # number of writes
      delta: 50         # seconds
      memory_writes:
        -
        -
        -
```
Please find examples of input files in .\PatternConfigs\InputConfigs\SystemFailureFlows 
and .\PatternConfigs\InputConfigs\SuccessFlows

See the overview of PatternGenerator, WritingPatternDetector, and FrameTransmitter in 
FLASHMem\Documentation\Task1.pdf and FLASHMem\Documentation\Task2.pdf 