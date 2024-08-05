from . import items, merchants, wallets, transactions


def init_routers(app):
    app.include_router(items.router)
    app.include_router(merchants.router)
    app.include_router(wallets.router)
    app.include_router(transactions.router)
