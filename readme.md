8 Nov 2024

1. clean-code - 
    intent revealing, 
    small functions - each function should do only one job
    test cases (unit), - should in run in pipelines as well
    static code analysis should pass, 
    typings in python
    folder - src / tests

2. read the textfiles from GCP cloud storage using gcp python sdk, textfile names should have a convention (wld.txt)
    1 bucket
        wld
            knowledge.txt
            system_prompt.txt
            user_prompt.txt
        t1d
        ...

3. fn - i/p sepciality o/p - fielpaths as tuple

4. building a pipeline
    slugs - input
    read from dx
    cleanup
    1 text per slug including the citation links

    text combiner


5. server start - scan the text files (from gcp - both knowlege and prompts) and cache it locally -in-memory 
        - retrieve_and_cache_prompts
        - retrieve_and_cache_knowlege

6. end to end testing
------

RAG Experiments
- semantic chunking - test dataset restuls on WLD - summary
- hierarchial chunking - test dataset results on WLD -symmary
    - vannila
    - with query expansion (intent based)
    
TODO
- chunk sizes for hierarchial chunking
- replace pubmedmert with someother model
- Graph RAG
    - content - graph model

