import ast, glob, json

en = json.load(open("locales/en.json", encoding="utf-8-sig"))
faltam = []

for f in glob.glob("*.py") + glob.glob("cogs/*.py"):
    for n in ast.walk(ast.parse(open(f, encoding="utf-8").read())):
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "tr" and n.args:
            a = n.args[0]
            if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value not in en:
                faltam.append((f, a.value[:60]))

print("Sem tradução:", len(faltam))
for x in faltam:
    print(x)