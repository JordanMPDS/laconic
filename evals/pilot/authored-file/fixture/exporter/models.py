"""Account, as the read replica presents it.

`slug` is the human-facing short name. It is unique within a region, not
globally: eu-west and us-east each have an "acme", and they are different
customers. Anything that has to be globally unique uses `account_id`.
"""


class Account:
    def __init__(self, account_id, slug, region, changed_at):
        self.account_id = account_id
        self.slug = slug
        self.region = region
        self.changed_at = changed_at

    def rows(self):
        raise NotImplementedError("provided by the replica cursor")
