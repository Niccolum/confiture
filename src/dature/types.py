from typing import Annotated

type JSONValue = dict[str, JSONValue] | list[JSONValue] | str | int | float | bool | None

# Examples: "app", "app.database", "app.database.host"
type DotSeparatedPath = Annotated[str, "Dot-separated path for nested dictionary navigation"]
