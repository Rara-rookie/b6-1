import sys

from .errors import DrawerError
from .service import do_all, do_init, do_queries, do_seed


def parse_args(argv: list[str]) -> tuple[str, str]:
    default_db_path = "drawer.db"
    valid_commands = {"init", "seed", "queries", "all"}

    if not argv:
        return "all", default_db_path

    first = argv[0]
    if first in valid_commands:
        command = first
        db_path = argv[1] if len(argv) >= 2 else default_db_path
        if len(argv) > 2:
            raise DrawerError(
                "인자가 너무 많습니다.",
                "사용법: python -m drawer_db.main [init|seed|queries|all] [db_path]",
            )
        return command, db_path

    if len(argv) == 1:
        return "all", first

    raise DrawerError(
        "알 수 없는 명령입니다.",
        "사용법: python -m drawer_db.main [init|seed|queries|all] [db_path]",
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    try:
        command, db_path = parse_args(args)

        if command == "init":
            do_init(db_path)
        elif command == "seed":
            do_seed(db_path)
        elif command == "queries":
            print(do_queries(db_path))
        elif command == "all":
            print(do_all(db_path))
        else:
            raise DrawerError(
                "지원하지 않는 명령입니다.",
                "init, seed, queries, all 중 하나를 사용하세요.",
            )
        return 0
    except DrawerError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
