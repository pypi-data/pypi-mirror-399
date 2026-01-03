from .load import load_example

examples = {
    i: load_example("activity_pub", i)
    for i in ["2", "4_part", "6_part", "7_part", "15"]
}

mastodon1 = load_example("mastodon", "1")
