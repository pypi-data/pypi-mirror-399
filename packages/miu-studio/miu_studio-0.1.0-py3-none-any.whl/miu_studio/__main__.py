"""Entry point for python -m miu_studio."""


def main(port: int = 8000) -> None:
    """Run the miu-studio server."""
    import uvicorn

    from miu_studio.main import create_app

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=port)


async def main_async(port: int = 8000) -> None:
    """Run the miu-studio server asynchronously."""
    import uvicorn

    from miu_studio.main import create_app

    app = create_app()
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    main()
