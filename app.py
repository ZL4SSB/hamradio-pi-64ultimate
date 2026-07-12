#!/usr/bin/env python3
from main_window import MainWindow


def main() -> int:
    app = MainWindow()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
