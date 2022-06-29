from ast import Str
from email.policy import default
from tokenize import group
import click

from DBWrapper import DBWrapper

__author__ = "Oyetoke Toby"
dbwrap = DBWrapper()
@click.group()
def cli():
    """
    Simple CLI for querying books on Google Books by Oyetoke Toby
    """
    pass

@cli.command(name='rmu')
@click.option('--name', '-n', required=True, type=Str)
def rmuser(name):
	dbwrap.delete_user(name)
	#click.echo(f'user - {name}') 
	

@cli.command(name='dots')
@click.option('-n', type=int, default=1)
def dots(n):
    click.echo('.' * n)




cli.add_command(rmuser)
cli.add_command(dots)

if __name__ == "__main__":
    cli()



rmuser('andrei')