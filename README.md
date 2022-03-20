# MODEL CHECKER
The model checker exhaustive all states to judge the correctness of your program. The program assumes that your function statements are atomic.



### Requirements:
* Python 3.7+, 
* python package inspect, ast, astor, graphviz

And make sure you have input
```shell
sudo apt install graphviz
```

before you run this program.



### Executing examples:

```shell
python3 mc.py ./mutex-bad.py
```



### Output:

The output includes 2 sections for each test:

* vertices and edges which describe the graph by text
* the graph itself 

