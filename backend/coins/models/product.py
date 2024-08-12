class ProductMixin:
    @property
    def name(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError

    @property
    def price(self) -> int:
        raise NotImplementedError

    def buy(self, user):
        raise NotImplementedError
