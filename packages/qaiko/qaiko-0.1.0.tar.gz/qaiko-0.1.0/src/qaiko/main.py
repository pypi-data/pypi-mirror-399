def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}! Welcome to my awesome package!"


def main():
    """Entry point for the application."""
    print(greet("World"))


if __name__ == "__main__":
    main()
