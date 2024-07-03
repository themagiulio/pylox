import os
import sys
from io import TextIOWrapper


def main():
    if len(sys.argv) != 2:
        print("Usage generate-ast <output dir>")
        sys.exit(1)

    output_dir = sys.argv[1]

    define_ast(
        output_dir,
        "expr",
        [
            "Assign   : Token name, Expr value",
            "Binary   : Expr left, Token operator, Expr right",
            "Call     : Expr callee, Token paren, list[Expr] arguments",
            "Grouping : Expr expression",
            "Literal  : object value",
            "Logical  : Expr left, Token operator, Expr right",
            "Unary    : Token operator, Expr right",
            "Variable : Token name",
        ],
    )

    define_ast(
        output_dir,
        "stmt",
        [
            "Block      : list[Stmt] statements",
            "Break      :",
            "Expression : Expr expression",
            "Function   : Token name, list[Token] params, list[Stmt] body",
            "Class      : Token name, list[Function] methods",
            "If         : Expr condition, Stmt then_branch, Stmt|None else_branch",
            "Print      : Expr expression",
            "Return     : Token keyword, Expr value",
            "Var        : Token name, Expr initializer",
            "While      : Expr condition, Stmt body",
        ],
    )


def define_ast(output_dir: str, basename: str, types: list[str]):
    # Open file
    file_path = os.path.join(output_dir, f"{basename}.py")
    file_obj = open(file_path, "w", encoding="UTF-8")

    # Define imports
    define_imports(file_obj, basename)

    # Define baseclass
    define_baseclass(file_obj, basename)

    # Define subclasses
    for type in types:
        classname = type.split(":")[0].strip()
        fields = type.split(":")[1].strip()
        define_type(file_obj, basename, classname, fields)
        define_visitor(file_obj, classname, basename)

    # Close file
    file_obj.close()


def define_imports(file_obj: TextIOWrapper, basename: str):
    if basename == "expr":
        file_obj.write("from pylox.token import Token\n")
    else:
        file_obj.write("from pylox.token import Token\n")
        file_obj.write("from pylox.expr import Expr\n")


def define_baseclass(file_obj: TextIOWrapper, basename: str):
    # Define class
    file_obj.write(f"class {basename.title()}:\n")
    file_obj.write("\tpass\n")


def define_type(file_obj: TextIOWrapper, basename: str, classname: str, fields: str):
    # Define class
    file_obj.write(f"class {classname}({basename.title()}):\n")

    # Get field names and types
    field_list: list[str] = fields.split(", ")

    if field_list[0] != "":
        field_tuple = [
            (field.split(" ")[1], field.split(" ")[0]) for field in field_list
        ]

        for field_name, field_type in field_tuple:
            file_obj.write(f"\t{field_name}: {field_type}\n")

        # Field names as string
        field_names = str([field[0] for field in field_tuple])[1:-1].replace("'", "")

        # Init function
        file_obj.write(f"\tdef __init__(self, {field_names}):\n")

        for field in field_list:
            name: str = field.split(" ")[1]
            file_obj.write(f"\t\tself.{name} = {name}\n")


def define_visitor(file_obj: TextIOWrapper, classname: str, basename: str):
    file_obj.write("\tdef accept(self, visitor):\n")
    file_obj.write(
        f"\t\treturn visitor.visit_{classname.lower()}_{basename.lower()}(self)\n"
    )


if __name__ == "__main__":
    main()
