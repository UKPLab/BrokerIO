from eventlet import monkey_patch  # mandatory! leave at the very top

monkey_patch()

from .cli import main

if __name__ == "__main__":
    main()
