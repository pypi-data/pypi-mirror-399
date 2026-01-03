import argparse
import importlib
import importlib.metadata
import os
import sys
from pathlib import Path
from typing import Any, Type

from jinja2 import Environment, FileSystemLoader, Template

from .utils import camel_to_snake, format_docstring, snake_to_camel, stl

__version__ = importlib.metadata.version('gr8gen')

TEMPLATES_PATH = Path(__file__).parent / 'templates'
environment = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATES_PATH), trim_blocks=True, autoescape=True
)


PROMPT = '❱'


def get_proto(service: Any) -> str:
    service.methods_and_messages()
    template: Template = environment.get_template(name='service.proto.jinja')
    return template.render(
        service=service,
        camel_to_snake=camel_to_snake,
        snake_to_camel=snake_to_camel,
        format_docstring=format_docstring,
    )


def validate_output_path(path: str) -> str:
    """Validates that the output path is a directory, creating it if it doesn't exist."""
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError(f"Output path '{path}' exists but is not a directory.")
    else:
        print(f"The output path '{path}' does not exist and will be created.")
    return path


def validate_service_path(service: str) -> Any:
    """Validates a Python-like import path by attempting to import it."""
    module_name, _, class_name = service.rpartition('.')
    if not module_name or not class_name:
        raise argparse.ArgumentTypeError(
            f"Service path '{service}' is not a valid Python-like import path."
        )

    # Add the current directory to sys.path for module discovery
    sys.path.insert(0, os.getcwd())

    try:
        module = importlib.import_module(module_name)
        service_class = getattr(module, class_name)
    except (ModuleNotFoundError, AttributeError) as e:
        raise argparse.ArgumentTypeError(
            f"Service '{service}' could not be found or is invalid: {e}"
        )
    finally:
        # Clean up sys.path after import attempt
        sys.path.pop(0)

    return service_class


def create_protos(output: str, services: list[Type]) -> None:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    for service in services:
        proto = get_proto(service=service)
        path: Path = output / f'{camel_to_snake(string=service.__name__)}.proto'
        with open(path, 'w') as file:
            file.write(proto)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='A CLI tool for processing paths and services.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument(
        '-o',
        '--out',
        default='./proto',
        type=validate_output_path,
        required=False,
        help='Path for output. Must be an existing or new directory.',
    )
    parser.add_argument(
        '-s',
        '--svcs',
        type=validate_service_path,
        nargs='+',  # Allow multiple services
        required=True,
        # default=argparse.SUPPRESS,
        help="Python-like import path(s) for service(s). Example: 'path.to.class.Class'.",
    )

    args = parser.parse_args()

    services_classes_names = map(lambda service: stl(service.__name__, 'green'), args.svcs)

    print(
        f'{stl(PROMPT, "bright_magenta")} Creating proto files at:'
        f' {stl(args.out, "green", "underline")} for services:'
    )

    print('\n'.join(f'    {stl("-", "dim")} {service}' for service in services_classes_names))

    create_protos(output=args.out, services=args.svcs)


if __name__ == '__main__':
    main()
