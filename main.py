import os

import mwclient
from gamefile import GameFile

class Main:
    wikiBot = WikiBot('https://thealchemistcode.gamepedia.com/')

    def main():
        curDir = os.getcwd()
        for gameFile in GameFile.gameFiles:
            try:
                wikiFiles = gameFile.generate({
                    server: gameFile.parse(remotePath, server)
                    for server, remotePath in {
                        "jp": 'Japan/',
                        "gl": 'Global/',
                    }.items()
                })
                print("Getting list of every existing wiki page")

                # Get all pages, which we will reduce to get pages to be deleted
                ap = wikiBot.allpages(namespace="10000", limit="max")
                allPages = [p.name for p in ap]

                print("Comparing to $allPages.size existing wiki pages for $gameFile.typeof.name")
                # Get Failed Inserts
                site = mwclient.Site('thealchemistcode.gamepedia.com', path='/')
                cat = site.categories.get('Data_pages_that_failed_a_table_insert')
                failedInserts = [p.name for p in cat.members()]
                # failedInserts.clear()

                def edit(titlesWithContent,
                         cb=None,
                         allPages=[],
                         purgeTitles=[]):
                    site.login(username=username, password=password)

                    print(f"titlesWithContent.size: {len(titlesWithContent.keys())}")
                    titles = titlesWithContent.keys()
                    if len(titles) > 500:
                        titles1 = titles[:500]
                    titlesWithContent = {}

                    result =


                while wikiFiles:
                    wikiBot.edit(wikiFiles,
                                 (lambda uri: print(f"Updated {uri}")),
                                 allPages,
                                 failedInserts)

                # Delete unused pages
                x = True
                allPages.exclude {
                    split('/').size != 4 | |
                    "Ability,Item,Unit".split(',').contains(split('/')[2]).not
                }.each {
                    y = wikiBot.apiReq("delete", {}, {
                        "title": it,
                        "reason": "Removed from Data",
                        "watchlist": "unwatch",
                        "token": wikiBot.csrfToken,
                    })
                    print("Deleted page $it")
                    if x:
                        print(y)
                        x = false
                }
                print('\n'.join(sorted(allPages.findAll {
                    split('/').size != 4 || "Ability,Item,Unit,Skill".split(',').contains(split('/')[2]).not
                }))
            } catch(Err e) {e.trace}
            print("Wiki updating complete!")
        }
    }
}