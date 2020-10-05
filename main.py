import os

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
                allPages = [
                    it.get('query', {}).get('allpages')
                    for it in site.get("query", "apcontinue", {
                        "list": "allpages",
                        "apnamespace": "10000",
                        "aplimit": "max",
                    })
                ]
                    it["query"]?->get("allpages")
                }.map {
                    it->get("title")
                }

                print("Comparing to $allPages.size existing wiki pages for $gameFile.typeof.name")
                # Get Failed Inserts
                failedInserts = wikiBot.batchReq("query", "cmcontinue", {
                    "list": "categorymembers",
                    "cmtitle": "Category:Data_pages_that_failed_a_table_insert",
                    "cmlimit": "max",
                }) {
                    it["query"]?->get("categorymembers")
                }.map {
                    it->get("title")
                }
                # failedInserts.clear()

                while wikiFiles:
                    wikiBot.edit(wikiFiles, | uri | {print("Updated $uri")}, allPages, failedInserts)

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