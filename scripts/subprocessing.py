import subprocess
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="A CLI wrapper to run Ollama commands."
    )
    parser.add_argument(
        "command",
        help="The Ollama command to execute (e.g., 'start', 'stop', 'pull', 'run', 'rm').",
    )
    parser.add_argument(
        "model",
        nargs="?",
        default=None,
        help="The name of the model for the command (if applicable).",
    )

    args = parser.parse_args()

    # Validate that commands requiring a model have one
    commands_requiring_model = {"pull", "run", "rm", "stop"}
    if args.command in commands_requiring_model and not args.model:
        parser.error(f"The '{args.command}' command requires a model name.")

    try:
        command = ["ollama", args.command]
        if args.model:
            command.append(args.model)
        print(f"Executing: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
    except FileNotFoundError:
        print(
            "Error: 'ollama' command not found. Make sure Ollama is installed and in your PATH.",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
