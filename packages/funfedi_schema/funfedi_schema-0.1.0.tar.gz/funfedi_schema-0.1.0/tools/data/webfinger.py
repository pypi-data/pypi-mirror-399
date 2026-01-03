from dataclasses import dataclass


@dataclass
class ex:
    name: str
    acct: str


webfinger_data = [
    ex(name="cattle_grid", acct="acct:cow_says_moo@dev.bovine.social"),
    ex(name="mitra", acct="acct:weekinfediverse@mitra.social"),
    ex(name="mastodon", acct="acct:Mastodon@mastodon.social"),
    ex(name="sharkey", acct="acct:julia@eepy.moe"),
    ex(name="wordpress", acct="acct:pfefferle@notiz.blog"),
    ex(name="piefed", acct="acct:casualconversation@piefed.social"),
]
