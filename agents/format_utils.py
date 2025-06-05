def stringify(output) -> str:
    if isinstance(output, str):
        return output
    elif isinstance(output, dict) and "messages" in output:
        return "\n".join(
            m.content for m in output["messages"] if hasattr(m, "content") and m.content
        )
    elif isinstance(output, list):
        return "\n".join(str(o) for o in output)
    return str(output)
