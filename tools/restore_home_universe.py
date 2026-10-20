from pathlib import Path
from bs4 import BeautifulSoup as BS
import subprocess
p=Path("index.html")
current=BS(p.read_text(),"html.parser")
old_html=subprocess.check_output(["git","show","10f55abb46928576368d4ec156bb482947bf31d5:index.html"],text=True)
old=BS(old_html,"html.parser")
oldhero=old.select_one("section.focused-home-hero")
newhero=current.select_one("section.wf-launch-hero")
assert oldhero and newhero and oldhero.select_one("#scene-panel")
# Keep original animated Universe and all its functional scripts. Change only commercial hero copy.
content=oldhero.select_one(".hero-content")
content.clear()
for child in list(BS(str(newhero.select_one(".wrap")),"html.parser").select_one(".wrap").contents):
    content.append(child)
# Layout stays original with a readable commercial hero, fade and responsive controls.
oldhero["class"]=["hero","commercial-hero","focused-home-hero","wf-restored-universe"]
oldhero["data-theme"]="ink"
oldheader=old.select_one("header.masthead")
newheader=current.select_one("header.masthead")
oldheader.replace_with(newheader)
newheader["data-theme"]="ink"
newheader["data-universe-surface"]=""
oldmain=old.select_one("main")
newmain=current.select_one("main")
oldmain.replace_with(newmain)
oldfooter=old.select_one("footer.footer")
newfooter=current.select_one("footer.footer")
oldfooter.replace_with(newfooter)
# Maintain copy, CTA, schema, metadata and new CSS from current preview.
old.title.string=current.title.string
for name in ["description"]:
  a=old.select_one(f'meta[name="{name}"]')
  b=current.select_one(f'meta[name="{name}"]')
  if a and b:a["content"]=b["content"]
for name in ["og:title","og:description"]:
  a=old.select_one(f'meta[property="{name}"]')
  b=current.select_one(f'meta[property="{name}"]')
  if a and b:a["content"]=b["content"]
for s in list(old.select('script[type="application/ld+json"]')):s.decompose()
for s in current.select('script[type="application/ld+json"]'):
    old.head.append(BS(str(s),"html.parser"))
for link in current.select('link[href^="/assets/wf-"]'):
  if not old.select_one(f'link[href="{link.get("href")}"]'):old.head.append(BS(str(link),"html.parser"))
# Restore controls that belong to the original animated hero (not to the page copy).
assert old.select_one("#scene-panel") is not None
assert old.select_one("#network") is not None
# Ensure original launch layout does not obscure the CTA or the buyer cards.
style=old.new_tag("style")
style.string="""
.wf-restored-universe{min-height:680px}
.wf-restored-universe .hero-content{padding-top:70px;padding-bottom:125px}
.wf-restored-universe .hero-content h1{font-size:clamp(54px,6.3vw,90px);max-width:880px}
.wf-restored-universe .wf-launch-audience{font-size:18px;font-weight:650;margin:0 0 10px}
.wf-restored-universe .wf-launch-copy{font-size:18px;max-width:645px;margin:0 0 24px}
.wf-restored-universe .wf-launch-actions{display:flex;align-items:center;gap:22px}
.wf-restored-universe .wf-launch-fee{font-size:12px;margin-top:17px}
.wf-restored-universe .wf-launch-hero{background:none}
.wf-restored-universe .scene-veil{background:linear-gradient(90deg,var(--paper) 0%,rgba(251,251,248,.97) 25%,rgba(251,251,248,.86) 44%,rgba(251,251,248,.15) 70%,transparent 87%)}
@media(max-width:600px){.wf-restored-universe{min-height:600px}.wf-restored-universe .hero-content{padding-top:30px;padding-bottom:165px}.wf-restored-universe .hero-content h1{font-size:clamp(34px,9vw,53px)}.wf-restored-universe .wf-launch-copy{font-size:15px;max-width:340px}.wf-restored-universe .wf-launch-audience{font-size:14px}.wf-restored-universe .wf-launch-actions{flex-direction:column;align-items:flex-start;gap:16px}.wf-restored-universe .scene-veil{background:linear-gradient(180deg,var(--paper),rgba(251,251,248,.90) 64%,rgba(251,251,248,.38) 100%)}}
"""
old.head.append(style)
output=str(old)
assert 'id="scene-panel"' in output and 'id="network"' in output
assert 'Senior commercial leadership, without the hire.' in output
assert 'Build your next' in output
assert 'Win new brand business, or build the partner channel' in output
assert 'All upside. No overhead.' not in output
assert '/review/' not in output
p.write_text(output)
print("Restored animated Universe and preserved all approved copy.")
