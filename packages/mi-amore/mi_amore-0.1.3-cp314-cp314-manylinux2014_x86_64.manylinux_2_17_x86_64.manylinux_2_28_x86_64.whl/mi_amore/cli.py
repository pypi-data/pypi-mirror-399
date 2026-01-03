import typer

from mi_amore.minimize import minimize


app = typer.Typer()


@app.command()
def run(on_func: list[str],             
        verbose: bool = typer.Option(False, "--verbose", "-v", help="More log output"),):
    cubes_on = []

    for input in on_func:
        cube = []
        for char in input:
            match char:
                case "1":
                    cube += [0, 1]
                case "0":
                    cube += [1, 0]
                case "-":
                    cube += [1, 1]
                case _:
                    raise ValueError(f"Invalid character {char} only 1, 0, - are allowed")

        cubes_on.append(cube)
    n_binary = len(on_func[0])
    result = minimize(n_binary, [], cubes_on, [[]], int(verbose))

    for res in result:
        res_str = ""
        for i in range(0, len(res), 2):
            if res[i] == 1 and res[i + 1] == 1:
                res_str += "-"
            elif res[i] == 1 and res[i + 1] == 0:
                res_str += "0"
            elif res[i] == 0 and res[i + 1] == 1:
                res_str += "1"
            else:
                raise ValueError(f"Invalid binary pair {res[i]}{res[i + 1]}")
        print(res_str)
