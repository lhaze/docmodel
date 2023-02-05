def by_class(class_name: str) -> str:
    return f"[contains(concat(' ', normalize-space(@class), ' '), ' {class_name} ')]"


def by_id(id_name: str) -> str:
    return f"[@id='{id_name}']"
