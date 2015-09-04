#!/usr/bin/env python

import csv
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--big', default=500)
@click.option('--period', default='all')
@click.option('--checkmin', default=0)
@click.option('--ignore', multiple=True, default=[])
@click.argument('fname', nargs=1)
def stats(big, period, fname, checkmin, ignore):
    with open(fname) as f:
        r = csv.reader(f)
        oldperiod = ''
        money = 0
        bigs = []
        ignorebig = ['ZEC', 'ANTEKLAB']
        for row in r:
            if row[0].startswith('conto') is False:
                continue
            (conto, datacontabile, datavaluta, causale, segno, importo, categoria, note) = row
            (day, month, year) = datacontabile.split('/')
            newperiod = month + "/" + year
            if newperiod != oldperiod:
                if oldperiod != "":
                    print oldperiod, money - checkmin
                    if (checkmin == 0)or(money <= checkmin):
                        for b in bigs:
                            print " - ", b
                oldperiod = newperiod
                money = 0
                bigs = []
            if (period != 'all')and(period != newperiod):
                oldperiod = ""
                continue
            importo = float(importo.replace("\"", "").replace(",", "."))
            ii = False
            for i in ignore:
                if i in causale:
                    ii = True
            if ii is False:
                if importo >= big:
                    ii = False
                    for i in ignorebig:
                        if i in causale:
                            ii = True
                    if ii is False:
                        bigs.append("%s%0.1f - %s" % (segno, importo, causale))
                if segno == "-":
                    importo *= -1
                money += importo


if __name__ == '__main__':
    cli()
