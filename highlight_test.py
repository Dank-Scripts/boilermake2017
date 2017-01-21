from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

code = "import numpy as np"

lines = ["import numpy as np" , "a = 1", "b = 2", "c = a + b", "print(\"c = \", c)"]

formatter = HtmlFormatter()
formatter.noclasses = True
for i in range(len(lines)):
    print (highlight(lines[i], PythonLexer(), formatter))
