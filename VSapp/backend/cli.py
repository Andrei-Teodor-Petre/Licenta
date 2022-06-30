from ast import Str
from email.policy import default
from tokenize import group
from unicodedata import name
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
def rmuser(name:Str):
	dbwrap.delete_user(name)
	#click.echo(f'user - {name}') 
	

@cli.command(name='sur')
@click.option('--args', required=True, type=click.Tuple([click.STRING,click.INT]), help="Set the user and its level <username> <level> e.g. andrei 4")
#@click.option('--setlevel', '-l', required=True, type=int)
def setUserLevel(args:click.Tuple([Str,int])):

	name, level = args
	click.echo(f'setting {name} to level {level}')
	if level>5:
		click.echo("User level can't be higher than 5 - admin")
		return

	if level<1:
		click.echo("User level can't be lower than 1 - banned from viewing")
		return 

	dbwrap.set_user_level(name,level)

@cli.command(name='dots')
@click.option('-n', type=int, default=1)
def dots(n):
    click.echo('.' * n)




cli.add_command(rmuser)
cli.add_command(dots)
cli.add_command(setUserLevel)

if __name__ == "__main__":
    cli()



rmuser('andrei')