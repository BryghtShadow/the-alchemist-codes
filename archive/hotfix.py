# Emergency. We need this script ASAP
import mwclient
import gitlab

site = mwclient.Site('wikisandbox-ucp.gamepedia.com', path='/')
site.login(username='BryghtShadow@Manjaro', password="ciqdln5a62ruoodogff7ainsk098i3rt")

gl = gitlab.Gitlab('https://gitlab.com')

p = gl.projects.get('the-alchemist-codes/Global', lazy=True)
p = gl.projects.get('the-alchemist-codes/Japan', lazy=True)
