from . import items, merchants, wallets, transactions, users, authentication, root


def init_routers(app):
    app.include_router(root.router)
    app.include_router(items.router)
    app.include_router(merchants.router)
    app.include_router(wallets.router)
    app.include_router(transactions.router)
    app.include_router(users.router)
    app.include_router(authentication.router)
