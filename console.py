"""
CLI tool to handle common tasks over the database or related
with the server config. For example, we give an option to
create a new USER (an admin in the future)
"""
import click


@click.group()
def main():
    pass


async def create_user(username, password):
    from src.dataaccess.repository.repository import UserRepository
    from src.dtos.models import User
    from src.services.crypto import CryptoService
    hashed_password = CryptoService.get_password_hash(password)
    user = User(username=username, hashed_password=hashed_password)
    repo = UserRepository()
    new_id = await repo.add(user.dict(exclude_unset=True))
    return new_id


@main.command()
@click.option("--username", prompt="Enter username", type=str)
@click.option("--password", prompt="Enter password", type=str)
def createuser(username, password):
    import asyncio
    loop = asyncio.get_event_loop()
    new_id = loop.run_until_complete(create_user(username, password))
    print(f"User {new_id} created successfully")


if __name__ == '__main__':
    main()
