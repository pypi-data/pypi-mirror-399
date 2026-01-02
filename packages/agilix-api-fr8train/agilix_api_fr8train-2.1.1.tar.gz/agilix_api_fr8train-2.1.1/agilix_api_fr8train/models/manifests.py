class GetItemListDefinition:
    entity_id: int
    item_id: int
    query: str
    all_versions: bool

    def __init__(
        self,
        entity_id: int,
        item_id: int = None,
        query: str = "",
        all_versions: bool = False,
    ):
        self.entity_id = entity_id
        self.item_id = item_id
        self.query = query
        self.all_versions = all_versions

    def __iter__(self):
        yield "entityid", self.entity_id
        if self.item_id:
            yield "itemid", self.item_id
        if self.query:
            yield "query", self.query
        yield "allversions", self.all_versions
