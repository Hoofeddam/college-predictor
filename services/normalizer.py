EXAMS = {
    "jee advanced": "JEE Advanced",
    "advanced": "JEE Advanced",
    "jee adv": "JEE Advanced",

    "jee mains": "JEE Main",
    "jee main": "JEE Main",

    "bitsat": "BITSAT",

    "comedk": "COMEDK",

    "kcet": "KCET",

    "met": "MET",

    "viteee": "VITEEE",
}

CATEGORIES = {
    "general": "OPEN",
    "gen": "OPEN",
    "open": "OPEN",

    "obc": "OBC-NCL",
    "obc-ncl": "OBC-NCL",

    "ews": "EWS",

    "sc": "SC",

    "st": "ST",
}

QUOTAS = {
    "ai": "AI",
    "all india": "AI",

    "hs": "HS",
    "home state": "HS",

    "os": "OS",
    "other state": "OS",
}

BRANCHES = {
    "cse": "Computer Science and Engineering",
    "cs": "Computer Science and Engineering",
    "computer science": "Computer Science and Engineering",
    "computer science engineering": "Computer Science and Engineering",

    "ee": "Electrical Engineering",
    "electrical": "Electrical Engineering",

    "me": "Mechanical Engineering",
    "mechanical": "Mechanical Engineering"
}

def normalize_exam(value):

    if value is None:
        return None

    return EXAMS.get(value.lower().strip(), value)


def normalize_category(value):

    if value is None:
        return None

    return CATEGORIES.get(value.lower().strip(), value)


def normalize_quota(value):

    if value is None:
        return None

    return QUOTAS.get(value.lower().strip(), value)

def normalize_branch(value):

    if value is None:
        return None

    return BRANCHES.get(
        value.lower().strip(),
        value
    )