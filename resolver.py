from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


class ResolverHandler(RequestHandler):
    def post(self):
        raw = self.get_body_argument("raw")
        html = toHtml(prettyEachLine(raw))
        self.write({
            body: html
            raw: true})
        #body to html
        #convert raw... python to html formatted pretty.

        def prettyEachLine(raw):
        lines = raw.split("\n")
        formatter = HtmlFormatter()
        lex = PythonLexer()
        formatter.noclasses = True
        prettyLines = []
        for line in lines:
            pretty = highlight(line, lex, formatter)
            prettyLines.append(pretty)
        return prettyLines

    def toHtml(prettyLines):
        return "".join(prettyLines)
