
# a stupid template engine

class Template:
    def __init__(self, template, var_env=None, escape_var="$", escape="%"):
        self.template = template
        self.var_env = var_env or dict()
        self.escape_var = escape_var
        self.escape = escape



if __name__ == "__main__":
    t1 = Template(\
    """\
    %{for n in range(1,11):
        %the value is $n\n%
    %}""")

    print(t1.generate(var_env=None))

    #the value is 1  the value is 2 ...
