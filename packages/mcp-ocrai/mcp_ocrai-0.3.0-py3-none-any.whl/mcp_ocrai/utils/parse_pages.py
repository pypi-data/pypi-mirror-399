def parse_pages(pages: str) -> set:
    """
    Given a string representing a range of pages, return a set of integers representing the individual pages.
    For example, the string "1,3-5,7" should return the set {1, 3, 4, 5, 7}
    """
    pages_set = set()
    groups = pages.split(",")

    for group in groups:
        if "-" in group:
            range = group.split("-")
            start = int(range[0])
            end = int(range[1])
            pages_set.update(range(start, end + 1))  # pyright: ignore[reportCallIssue]
        else:
            pages_set.add(int(group))

    return pages_set
