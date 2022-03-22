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
python3 test.py
```



### Output:

The output includes 3 sections for each test:

* intermediate mcprocess.py
* vertices and edges which describe the graph by text
* the graph itself 

